from dataclasses import dataclass


@dataclass(frozen=True)
class InterviewQuestionCategory:
    name: str
    link: str
    popularity: float
