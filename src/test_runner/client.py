import logging

import requests

from src.config import constants, env
from src.test_runner import dto

headers = {
    "Authorization": f"Bearer {env.TEST_RUNNER_API_KEY}",
    "Content-Type": "application/json",
}

log = logging.getLogger(__name__)

TEST_RUNNER_PROJECT_NAMES = {
    constants.PROJECT_CURRENCY_EXCHANGE: "CURRENCY_EXCHANGE",
}


def post_test_run(deploy_base_url: str, project_name: str) -> dto.TestRun | str:
    resp = requests.post(
        url=f"{env.TEST_RUNNER_URL}/api/tests",
        headers=headers,
        json={
            "deploy_base_url": deploy_base_url,
            "project_name": TEST_RUNNER_PROJECT_NAMES[project_name],
        },
    )

    if resp.status_code != 201:
        log.error(f"Failed to create test run: {resp.text}")
        return "Failed to create test run"

    return dto.TestRun(**resp.json())


def get_test_run(id: str) -> dto.TestRun | str:
    resp = requests.get(
        url=f"{env.TEST_RUNNER_URL}/api/tests/{id}",
        headers=headers,
    )
    if resp.status_code != 200:
        log.error(f"Failed to get test run: {resp.text}")
        return "Failed to get test run"

    return dto.TestRun(**resp.json())
