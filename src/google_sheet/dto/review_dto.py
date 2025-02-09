from dataclasses import dataclass


@dataclass
class Review:
    period: str
    project_name: str
    language: str
    repo_link: str
    review_type: str
    review_link: str
    author_name: str
    author_tg_nick: str
    author_tg_link: str
