from dataclasses import dataclass

from src.google_sheet.dto.interview_info_dto import InterviewInfo


@dataclass
class InterviewQuestionTimestamp:
    timestamp: str
    interview: InterviewInfo
