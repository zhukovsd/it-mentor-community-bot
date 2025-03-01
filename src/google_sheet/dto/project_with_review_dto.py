from dataclasses import dataclass

from src.google_sheet.dto.project_dto import Project
from src.google_sheet.dto.review_dto import Review


@dataclass
class ProjectWithReview(Project):
    reviews: list[Review]
