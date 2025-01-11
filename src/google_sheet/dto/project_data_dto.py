from dataclasses import dataclass


@dataclass
class ProjectData:
    period: str | None
    project_name: str
    language: str
    repo_name: str
    repo_link: str
    author_name: str
    author_link: str
