from datetime import datetime
import logging
import re
import textwrap
from re import Match
from src.github import github_client
from src.google_sheet.google_sheet_service import GSheetService
from src.config import env


log = logging.getLogger(__name__)

# 1. `##\s{1}` matches header level 2 and exactly one space
# 2. `\[(.*?)\]` matches name of the link inside [], but not the brackets itself, first capturing group
# 3. `\(.*?\)` matches link inside ()
# 4. `\s*` matches the optional space
# 5. `\[([^%]*?)%*\]` matches anything inside second pair of [], but not brackets and % sign itself, second capturing group
# Example of matched string: ## [ООП](Основы-Java/oop/#ооп) [12.5%]
# First capturing group = ООП
# Second capturing group = 12.5
CATEGORY_PATTERN = r"##\s{1}\[(.*?)\]\(.*?\)\s*\[([^%]*?)%*\]"


# 1. `##\s{1}` matches header level 4 and exactly one space
# 2. `\d*\.*\s*` matches optional question number with dot and space
# 2. `\[(.*?)\]` matches name of the link inside [], but not the brackets itself, first capturing group
# 4. `\s*` matches the optional space
# 5. `\[([^%]*?)%*\]` matches anything inside second pair of [], but not brackets and % sign itself, second capturing group
# Example of matched string: #### 1. [Что такое ООП?](Основы-Java/oop/#1-что-такое-ооп) [4%]
# First capturing group = Что такое ООП?
# Second capturing group = 4
QUESTION_PATTERN = r"#{4}\s{1}\d*\.*\s*\[(.*?)\]\(.*?\)\s*\[([^%]*?)%*\]"

categories_popularity_change: dict[str, tuple[float, float]] = {}
questions_popularity_change: dict[str, tuple[float, float]] = {}

json_google_api_key = env.JSON_KEY_GOOGLE_API

google_sheet_service = GSheetService(json_google_api_key)


def update_questions_popularity() -> str:
    log.info("Updating popularity percents in the /content/questions.md file")

    file = github_client.get_file_content("/content/questions.md")

    if file is None:
        log.error("/content/questions.md is None, cannot continue")
        raise Exception("Ошибка чтения файла `/content/questions.md` из репозитория")

    gh_questions = file[0]
    questions_file_sha = file[1]

    gs_questsions = google_sheet_service.get_interview_questions()
    gs_question_categories = set(map(lambda x: x.category, gs_questsions))

    gs_question_popularity: dict[str, float] = {
        str.lower(q.question): q.popularity for q in gs_questsions
    }
    gs_queston_category_popularity: dict[str, float] = {
        str.lower(c.name): c.popularity for c in gs_question_categories
    }

    updated_questions = re.sub(
        CATEGORY_PATTERN,
        lambda m: _update_category_popularity(m, gs_queston_category_popularity),
        gh_questions,
    )
    updated_questions = re.sub(
        QUESTION_PATTERN,
        lambda m: _update_question_popularity(m, gs_question_popularity),
        updated_questions,
    )

    last_master_commit_sha = github_client.get_last_commit_sha_of_branch("master")

    if last_master_commit_sha is None:
        log.error(
            "Hash of the last commit in the master branch is unknown, cannot continue"
        )
        raise Exception("Ошибка при создании новой ветки для изменений")

    timestamp = datetime.now().strftime("%Y-%m-%d")

    branch_name = f"questions-popularity-update-{timestamp}"
    commit_message = f"questions: popularity updated by bot at {timestamp}"

    branch_created = github_client.create_branch(branch_name, last_master_commit_sha)

    if not branch_created:
        log.error(f"Branch {branch_name} was not created, cannot continue")
        raise Exception(
            f"Ошибка при создании `{branch_name}` ветки для коммита изменений списка вопросов"
        )

    file_content_updated = github_client.update_file_content(
        sha=questions_file_sha,
        path="/content/questions.md",
        content=updated_questions,
        branch=branch_name,
        commit_message=commit_message,
    )

    if not file_content_updated:
        log.error(
            f"Content of file /content/questions.md in the branch {branch_name} was not updated, cannot continue"
        )
        raise Exception(
            f"Ошибка при попытке создать коммит с обновленным списком вопросов в ветке `{branch_name}`"
        )

    stats = _generate_stats_message()

    pr_title = branch_name.replace("-", " ", 3).capitalize()

    pr_link = github_client.create_pull_request(
        head=branch_name, base="master", title=pr_title, body=stats
    )

    if pr_link is None:
        log.error(
            f"Pull request from {branch_name} to master was not created, cannot continue"
        )
        raise Exception(
            f"Ошибка при попытке создать PR из ветки `{branch_name}` в master"
        )

    return stats + "\n---\n\n" + pr_link


def _update_category_popularity(
    category_match: Match[str], gs_categories_popularity: dict[str, float]
) -> str:
    full_match = category_match.group(0)
    category_name = category_match.group(1)
    gh_category_popularity = category_match.group(2)

    gs_category_popularity = gs_categories_popularity.get(str.lower(category_name))

    if gs_category_popularity is None:
        log.warn(
            f"Popularity percents for category '{category_name}' not found in data from Google sheet"
        )
        return full_match

    gs_category_popularity = round(gs_category_popularity)

    log.debug(
        f"Updating category '{category_name}' popularity: {gh_category_popularity} -> {gs_category_popularity}"
    )

    popularity_delta = gs_category_popularity - float(gh_category_popularity)

    categories_popularity_change[category_name] = (
        popularity_delta,
        gs_category_popularity,
    )

    return full_match.replace(gh_category_popularity, str(gs_category_popularity))


def _update_question_popularity(
    quesiton_match: Match[str], gs_questions_popularity: dict[str, float]
) -> str:
    full_match = quesiton_match.group(0)
    question_name = quesiton_match.group(1)
    gh_question_popularity = quesiton_match.group(2)

    gs_question_popularity = gs_questions_popularity.get(str.lower(question_name))

    if gs_question_popularity is None:
        log.warn(
            f"Popularity percents for question '{question_name}' not found in data from Google sheet"
        )
        return full_match

    gs_question_popularity = round(gs_question_popularity)

    log.debug(
        f"Updating question '{question_name}' popularity: {gh_question_popularity} -> {gs_question_popularity}"
    )

    popularity_delta = gs_question_popularity - float(gh_question_popularity)

    questions_popularity_change[question_name] = (
        popularity_delta,
        gs_question_popularity,
    )

    return full_match.replace(
        f"{gh_question_popularity}%", f"{str(gs_question_popularity)}%"
    )


def _generate_stats_message() -> str:
    questions_popularity_stats = sorted(
        questions_popularity_change.items(), key=lambda x: x[1]
    )
    categories_popularity_stats = sorted(
        categories_popularity_change.items(), key=lambda x: x[1]
    )

    top_questions_incr_popularity = questions_popularity_stats[-5:]
    top_questions_decr_popularity = questions_popularity_stats[:5]

    top_category_incr_popularity = categories_popularity_stats[-3:]
    top_category_decr_popularity = categories_popularity_stats[:3]

    top_questions_incr_popularity.reverse()
    top_category_incr_popularity.reverse()

    def generate_ordered_list(
        popularity_data: list[tuple[str, tuple[float, float]]]
    ) -> str:
        question_bullets: list[str] = list()

        for i, (text, (delta, new_percent)) in enumerate(popularity_data):
            old_percent = new_percent - delta

            question_bullet = (
                f"{i + 1}. {text} [{round(old_percent)}% -> {round(new_percent)}%]"
            )

            question_bullets.append(question_bullet)

        return "\n".join(question_bullets)

    return textwrap.dedent(
        f"""Топ вопросов популярность которых увеличилась:

{generate_ordered_list(top_questions_incr_popularity)}

Топ вопросов популярность которых уменьшилась:

{generate_ordered_list(top_questions_decr_popularity)}

---

Категории набравшие больше всего популярности:

{generate_ordered_list(top_category_incr_popularity)}

Категории потерявшие больше всего популярности:

{generate_ordered_list(top_category_decr_popularity)}
"""
    )
