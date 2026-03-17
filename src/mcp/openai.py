import logging
from typing import Any, cast
from openai import (
    APIError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from openai.types.shared_params.responses_model import ResponsesModel

from src.config import env

client = OpenAI()

log = logging.getLogger(__name__)


class ContextExceededError(Exception):
    pass


def call_llm(user_input: str, allowed_tools: list[str], model: ResponsesModel) -> str:
    try:
        resp = client.responses.create(
            instructions=(
                "Do not answer requests that do not require the MCP tool, just explain what you can do. "
                "Do not ask follow-up questions; your job is to answer, not to continue the dialogue. "
                "If you do not have enough data or capabilities to fulfill the request, explain it clearly without asking further questions."
            ),
            model=model,
            input=user_input,
            tools=[
                {
                    "type": "mcp",
                    "server_label": "interviews",
                    "server_description": "Server contains data about technical interview recordings for software engineer positions",
                    "server_url": env.MCP_SERVER_URL,
                    "authorization": env.MCP_SERVER_API_KEY,
                    "require_approval": "never",
                    "allowed_tools": allowed_tools,
                }
            ],
        )
        return resp.output_text

    except RateLimitError as e:
        headers = getattr(e.response, "headers", {}) if hasattr(e, "response") else {}

        limit = headers.get("x-ratelimit-limit-requests")
        remaining = headers.get("x-ratelimit-remaining-requests")
        reset = headers.get("x-ratelimit-reset-requests")
        retry_after = headers.get("retry-after")
        body = cast(dict[str, Any], e.body)

        log.error(
            f"Rate limit error status_code={e.status_code} limit={limit} remaining={remaining} reset={reset} retry_after={retry_after} body={e.body}"
        )
        return f"Превышен лимит запросов.\n\nmessage: {body['message']}\n\nlimit = {limit}; remaining = {remaining}, reset = {reset}, retry_after = {retry_after}"

    except AuthenticationError as e:
        log.error(f"OpenAI authentication error: {e}")
        body = cast(dict[str, Any], e.body)
        return f"Ошибка аутентификации при обращении к сервису LLM. message: {body['message']}"

    except APIStatusError as e:
        log.error(
            f"OpenAI API status error status_code={e.status_code} error_body={e.body}"
        )

        body = cast(dict[str, Any], e.body)

        if e.code == "context_length_exceeded":
            log.error(f"Context exceeded error: {body['message']}")
            raise ContextExceededError()

        return f"OpenAI API response status_code: {e.status_code}, message: {e.message}"

    except APIError as e:
        log.error(f"OpenAI API error: {e}")
        body = cast(dict[str, Any], e.body)
        return f"Произошла ошибка при обработке запроса. message: {body['message']}"

    except Exception as e:
        log.error(f"Unexpected error in call_llm: {e}")
        return "Произошла непредвиденная ошибка."
