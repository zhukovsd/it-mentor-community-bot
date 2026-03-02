import logging

from src.mcp import openai

log = logging.getLogger(__name__)


def get_result(user_input: str, is_admin: bool) -> str:
    return openai.call_llm(user_input, is_admin)
