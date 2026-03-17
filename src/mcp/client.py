from collections.abc import Callable
from enum import Enum
import logging

from openai.types import ResponsesModel

from src.mcp import openai

log = logging.getLogger(__name__)

default_model: ResponsesModel = "gpt-5.2"
bigger_context_model: ResponsesModel = "gpt-5.4"

ToolSet = Enum("ToolSet", ["EMPLOYMENT_MENTORING", "GLOBAL"])

employment_mentoring_tools = ["find_interviews", "find_interview_questions"]
global_tools = ["find_interview_questions_limited"]


def get_result(
    user_input: str,
    tool_set: ToolSet,
    on_switch: Callable[[str], None] | None = None,
) -> str:
    allowed_tools: list[str] | None = None

    if tool_set == ToolSet.EMPLOYMENT_MENTORING:
        allowed_tools = employment_mentoring_tools
    if tool_set == ToolSet.GLOBAL:
        allowed_tools = global_tools

    if allowed_tools is None:
        return "Нет подходящих инструментов для текущего запроса"

    try:
        response = openai.call_llm(user_input, allowed_tools, default_model)
        return f"{response}\n\nИспользована модель: {default_model}"
    except openai.ContextExceededError as e:
        try:
            log.warning(f"{e}")
            if on_switch is not None:
                on_switch(
                    f"Модель {default_model} не выдержала контекста запроса, пробуем {bigger_context_model}"
                )
            response = openai.call_llm(user_input, allowed_tools, bigger_context_model)
            return f"{response}\n\nИспользована модель: {bigger_context_model}"
        except openai.ContextExceededError as e:
            return "Контекст запроса превышен"
