import logging
from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from openai.types.shared_params.responses_model import ResponsesModel

from src.config import env

client = OpenAI()
model: ResponsesModel = "gpt-5.2"

log = logging.getLogger(__name__)


def call_llm(user_input: str, is_admin: bool) -> str:
    allowed_tools = ["find_interviews"]
    if is_admin:
        allowed_tools.append("sync_interviews")

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

    except APIConnectionError as e:
        log.error(f"OpenAI API connection error: {e}")
        return (
            "Не удалось подключиться к сервису LLM. Проверьте подключение к интернету."
        )

    except RateLimitError as e:
        headers = getattr(e.response, "headers", {}) if hasattr(e, "response") else {}

        limit = headers.get("x-ratelimit-limit-requests")
        remaining = headers.get("x-ratelimit-remaining-requests")
        reset = headers.get("x-ratelimit-reset-requests")
        retry_after = headers.get("retry-after")

        log.error(
            f"Rate limit error status_code={e.status_code} limit={limit} remaining={remaining} reset={reset} retry_after={retry_after} body={e.body}"
        )
        return f"Превышен лимит запросов. limit = {limit}; remaining = {remaining}, reset = {reset}, retry_after = {retry_after}"

    except AuthenticationError as e:
        log.error(f"OpenAI authentication error: {e}")
        return "Ошибка аутентификации при обращении к сервису LLM."

    except APIStatusError as e:
        respone_text = (
            e.response.text
            if hasattr(e, "response") and hasattr(e.response, "text")
            else "No response body"
        )
        body = e.body if hasattr(e, "body") else "No error body"
        log.error(
            f"OpenAI API status error status_code={e.status_code} response={e.response} response_text={respone_text} error_body={body}"
        )
        return (
            f"Ошибка подключения к сервису LLM. OpenAI API status_code: {e.status_code}"
        )

    except APIError as e:
        log.error(f"OpenAI API error: {e}")
        return "Произошла ошибка при обработке запроса."

    except Exception as e:
        log.error(f"Unexpected error in call_llm: {e}")
        return "Произошла непредвиденная ошибка."
