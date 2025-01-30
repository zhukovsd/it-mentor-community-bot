from dataclasses import dataclass

from src.google_sheet.dto.interview_question_category_dto import (
    InterviewQuestionCategory,
)
from src.google_sheet.dto.interview_question_timestamp_dto import (
    InterviewQuestionTimestamp,
)


@dataclass
class InterviewQuestion:
    id: int
    question: str
    popularity: float
    timestamps: list[InterviewQuestionTimestamp]
    category: InterviewQuestionCategory
