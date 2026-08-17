import base64
import logging
import os
import secrets

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from starlette.routing import Route

METRICS_USER = os.getenv("METRICS_USER")
METRICS_PASS = os.getenv("METRICS_PASS")

log = logging.getLogger(__name__)


def check_basic_auth(auth_header: str | None) -> bool:
    if not auth_header or not auth_header.startswith("Basic "):
        return False

    try:
        encoded_credentials: str = auth_header.split(" ", 1)[1]
        decoded_bytes: bytes = base64.b64decode(encoded_credentials)
        decoded_str: str = decoded_bytes.decode("utf-8")
        username: str
        password: str
        username, password = decoded_str.split(":", 1)

        is_user_correct: bool = secrets.compare_digest(username, METRICS_USER)
        is_pass_correct: bool = secrets.compare_digest(password, METRICS_PASS)

        return is_user_correct and is_pass_correct
    except Exception:
        return False


async def metrics_endpoint(request: Request) -> PlainTextResponse | Response:
    auth_header: str | None = request.headers.get("Authorization")

    if not check_basic_auth(auth_header):
        return PlainTextResponse(
            "401 Unauthorized",
            status_code=401,
            headers={"WWW-Authenticate": "Basic realm='Prometheus Metrics'"}
        )

    data: bytes = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)


metrics_app = Starlette(routes=[
    Route("/metrics", endpoint=metrics_endpoint, methods=["GET"])
])
