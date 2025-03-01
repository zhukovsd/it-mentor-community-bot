import logging
from collections import Counter
from jinja2 import Environment, FunctionLoader

from src.config import env
from src.github import github_client
from src.google_sheet.dto.review_dto import Review
from src.google_sheet.dto.project_with_review_dto import ProjectWithReview

log = logging.getLogger(__name__)


def _get_java_template(name: str) -> str | None:
    file = github_client.get_file_content(
        f"/templates/{name}.md", repo=env.JAVA_BACKEND_COURSE_SITE_REPO_NAME
    )
    if file is None:
        return None

    return file[0]


def _get_python_template(name: str) -> str | None:
    file = github_client.get_file_content(
        f"/templates/{name}.md", repo=env.PYTHON_BACKEND_COURSE_SITE_REPO_NAME
    )
    if file is None:
        return None

    return file[0]


def _to_correct_language_spelling(language: str) -> str:
    language = language.lower()

    if language == "php":
        return language.upper()
    if language == "ocaml":
        return "OCaml"
    if language == "javascript":
        return "JavaScript"

    return language.capitalize()


def _unique_languages(projects: list[ProjectWithReview]) -> str:
    languages = [project.language.lower() for project in projects]
    normalized_languages = list(map(_to_correct_language_spelling, languages))

    counter = Counter(normalized_languages)

    unique_languages = set(normalized_languages)

    # sorting by number of occurrences then alphabetically
    unique_languages_sorted = sorted(
        unique_languages, key=lambda lang: (-counter[lang], lang)
    )

    return ", ".join(unique_languages_sorted)


def _review_count(projects: list[ProjectWithReview]) -> str:
    return str(sum(len(project.reviews) for project in projects))


def _project_count(projects: list[ProjectWithReview]) -> str:
    return str(len(projects))


def _repo(project: ProjectWithReview) -> str:
    return f"[{project.repo_name}]({project.repo_link})"


def _author(project: ProjectWithReview) -> str:
    return f"[{project.author_name}]({project.author_link})"


def _language(project: ProjectWithReview) -> str:
    return _to_correct_language_spelling(project.language)


def _review(project: ProjectWithReview) -> str:
    """Если ревью нет - значение пустое
    Если ревью одно, и оно текстовое - 📝 [Заметки]($review_link)
    Если ревью одно, и это видео - 🎬 [Видео]($review_link)
    Если ревью два, это именно 1 видео + 1 текстовое - 🎬 [Видео]($review_link), 📝 [Заметки]($review_link)
    Если ревью два (кроме комбинации 1 видео + 1 текстовое) или больше, формируем следующую строку со всеми ревью - 📝 [#1]($review_link), 📝 [#2]($review_link), 🎬 [#3]($review_link)
    """

    def to_review_link(review: Review, name: str | None = None) -> str:
        icon = ""
        link = review.review_link

        if review.review_type.lower() == "заметки":
            icon = "📝"
            if name == None:
                name = review.review_type
        elif review.review_type.lower() == "видео":
            icon = "🎬"
            if name == None:
                name = review.review_type
        else:
            log.error(
                f"Unknown review type encountered: {review.review_type}, skipping review rendering"
            )
            return ""

        return f"{icon} [{name}]({link})"

    reviews = project.reviews

    if len(reviews) == 0:
        return ""

    if len(reviews) == 1:
        return to_review_link(reviews[0])

    if len(reviews) == 2:
        review_types = {review.review_type.lower() for review in reviews}

        if len(review_types) == 2:
            if reviews[0].review_type.lower() == "видео":
                return f"{to_review_link(reviews[0])}, {to_review_link(reviews[1])}"
            else:
                return f"{to_review_link(reviews[1])}, {to_review_link(reviews[0])}"

    review_links: list[str] = []

    for i, review in enumerate(reviews):
        review_link = to_review_link(review, name=f"#{i + 1}")
        review_links.append(review_link)

    return ", ".join(review_links)


def _review_author(project: ProjectWithReview) -> str:
    unique_authors: set[str] = set()

    def to_author_link(review: Review) -> str | None:
        if review.author_tg_link == "":
            return f"{review.author_name}"

        if review.author_tg_nick in unique_authors:
            return None

        unique_authors.add(review.author_tg_nick)
        return (
            f"{review.author_name} [{review.author_tg_nick}]({review.author_tg_link})"
        )

    return ", ".join(filter(None, map(to_author_link, project.reviews)))


java_templates = Environment(loader=FunctionLoader(_get_java_template))
python_templates = Environment(loader=FunctionLoader(_get_python_template))

java_templates.filters["unique_languages"] = _unique_languages
java_templates.filters["review_count"] = _review_count
java_templates.filters["project_count"] = _project_count
java_templates.filters["repo"] = _repo
java_templates.filters["author"] = _author
java_templates.filters["language"] = _language
java_templates.filters["review"] = _review
java_templates.filters["review_author"] = _review_author

python_templates.filters["review_count"] = _review_count
python_templates.filters["project_count"] = _project_count
python_templates.filters["repo"] = _repo
python_templates.filters["author"] = _author
python_templates.filters["language"] = _language
python_templates.filters["review"] = _review
python_templates.filters["review_author"] = _review_author


def render_java_template(projects: list[ProjectWithReview], project_name: str) -> str:
    projects = list(
        filter(lambda x: x.project_name.lower() == project_name.lower(), projects)
    )

    template = java_templates.get_template(project_name.lower())

    return template.render(projects=projects)


def render_python_template(projects: list[ProjectWithReview]) -> str:
    projects = list(filter(lambda x: x.language.lower() == "python", projects))

    template = python_templates.get_template("finished-projects")

    return template.render(projects=projects)
