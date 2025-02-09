from jinja2 import Environment, PackageLoader

from src.project_with_review_dto import ProjectWithReview


def _to_correct_language_spelling(language: str) -> str:
    if language == "php":
        return language.upper()
    if language == "ocaml":
        return "OCaml"
    if language == "javascript":
        return "JavaScript"

    return language.capitalize()


def _unique_languages(projects: list[ProjectWithReview]) -> str:
    unique_languages: set[str] = {project.language.lower() for project in projects}

    unique_languages = set(map(_to_correct_language_spelling, unique_languages))

    return ", ".join(unique_languages)


def _review_count(projects: list[ProjectWithReview]) -> str:
    return str(sum(len(project.reviews) for project in projects))


def _project_count(projects: list[ProjectWithReview]) -> str:
    return str(len(projects))


templates = Environment(loader=PackageLoader("src"))

templates.filters["unique_languages"] = _unique_languages
templates.filters["review_count"] = _review_count
templates.filters["project_count"] = _project_count


def render_java_hangman_template(projects: list[ProjectWithReview]) -> str:
    projects = list(filter(lambda x: x.project_name == "hangman", projects))

    template = templates.get_template("java/hangman.md")

    return template.render(projects=projects)
