from dataclasses import dataclass


@dataclass
class TestResult:
    name: str
    status: str
    output: str
    description: str
    time: int
    elapsed: int
    request: str
    response: str


@dataclass
class TestRun:
    id: str
    deploy_base_url: str
    project_name: str
    status: str
    created_at: int
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    telegram_username: str | None = None
    telegram_user_id: int | None = None
    github_username: str | None = None
    github_repository: str | None = None
    project_language: str | None = None
    completed_at: int | None = None
    error: str | None = None
    report: list[TestResult] | None = None
