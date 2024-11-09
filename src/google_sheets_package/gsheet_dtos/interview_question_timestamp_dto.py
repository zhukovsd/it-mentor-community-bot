from dataclasses import dataclass

from .interview_info_dto import InterviewInfo


@dataclass
class InterviewQuestionTimestamp:
    timestamp: str
    interview: InterviewInfo
