from enum import Enum
import logging

from src.mcp import openai

log = logging.getLogger(__name__)


CHAT_TYPE = Enum("CHAT_TYPE", ["EMPLOYMENT_MENTORING", "GLOBAL", "UNKNOWN"])


def get_result(user_input: str, chat_type: CHAT_TYPE) -> str:
    if chat_type == CHAT_TYPE.UNKNOWN:
        return "Неизвестный тип чата для текущего запроса"
    return openai.call_llm(user_input, to_open_ai_chat_type(chat_type))


def to_open_ai_chat_type(chat_type: CHAT_TYPE) -> openai.CHAT_TYPE:
    if chat_type == CHAT_TYPE.EMPLOYMENT_MENTORING:
        return openai.CHAT_TYPE.EMPLOYMENT_MENTORING
    return openai.CHAT_TYPE.GLOBAL
