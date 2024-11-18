from dataclasses import dataclass

from src.google_sheet.dto.interview_question_timestamp_dto import (
    InterviewQuestionTimestamp,
)


@dataclass
class InterviewQuestion:
    id: int
    question: str
    popularity: float
    timestamps: list[InterviewQuestionTimestamp]