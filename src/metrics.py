import base64
import logging
import secrets

import prometheus_client
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from starlette.routing import Route

from src.config import env

log = logging.getLogger(__name__)


def is_authenticated(auth_header: str | None) -> bool:
    if not auth_header or not auth_header.startswith("Basic "):
        return False

    try:
        encoded_credentials = auth_header[len("Basic "):]
        decoded_str = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_str.split(":", 1)

        is_user_correct: bool = secrets.compare_digest(username, env.METRICS_USER)
        is_pass_correct: bool = secrets.compare_digest(password, env.METRICS_PASS)

        return is_user_correct and is_pass_correct
    except Exception:
        return False


async def metrics_endpoint(request: Request) -> PlainTextResponse | Response:
    auth_header: str | None = request.headers.get("Authorization")

    if not is_authenticated(auth_header):
        return PlainTextResponse(
            "401 Unauthorized",
            status_code=401,
            headers={"WWW-Authenticate": "Basic realm='Prometheus Metrics'"}
        )

    return Response(prometheus_client.generate_latest(), media_type=CONTENT_TYPE_LATEST)


metrics_app = Starlette(routes=[
    Route("/metrics", endpoint=metrics_endpoint, methods=["GET"])
])
