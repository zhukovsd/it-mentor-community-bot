from typing import Any
from jinja2 import Environment, PackageLoader

from src.project_with_review_dto import ProjectWithReview

templates = Environment(loader=PackageLoader("src"))


def render_java_hangman_template(data: list[ProjectWithReview]) -> str:
    template = templates.get_template("test-template.md")

    return template.render(projects=data)
