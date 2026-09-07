import io
import ipaddress
import logging
import asyncio
import textwrap
from typing import Any
from urllib.parse import urlparse

from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.config import constants
from src.handler import util
from src.test_runner import client, dto

RUN_TESTS_COMMAND_NAME = "runtests"

log = logging.getLogger(__name__)


async def run_tests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_member = update.effective_user
    command_message = update.effective_message

    assert (
        chat is not None
    ), f"{RUN_TESTS_COMMAND_NAME} command should be used in chat, it must not be None"
    assert (
        chat_member is not None
    ), f"{RUN_TESTS_COMMAND_NAME} command should be used by user, it must not be None"
    assert (
        command_message is not None
    ), f"{RUN_TESTS_COMMAND_NAME} command cannot be None"

    async def reply_with_error(text: str) -> None:
        error_message = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_to_message_id=command_message.id,
        )
        await asyncio.sleep(10)
        _ = await context.bot.delete_messages(
            chat_id=chat.id,
            message_ids=[command_message.id, error_message.id],
        )
        return

    command_text = command_message.text

    assert command_text is not None, "Command text cannot be None"

    message_text = command_text[len("/" + RUN_TESTS_COMMAND_NAME) :]

    if len(message_text.strip()) == 0:
        log.error(f"{RUN_TESTS_COMMAND_NAME} was called with no arguments, expected 2")
        await reply_with_error(
            f"Команда {RUN_TESTS_COMMAND_NAME} должна вызываться с двумя параметрами - название проекта и URL деплоя проекта"
        )
        return

    args: list[str] = message_text.strip().split(" ")

    if len(args) != 2:
        log.error(
            f"{RUN_TESTS_COMMAND_NAME} was called with {len(args)} arguments, expected 2"
        )
        await reply_with_error(
            f"Команда {RUN_TESTS_COMMAND_NAME} должна вызываться с двумя параметрами - название проекта и URL деплоя проекта"
        )
        return

    project_name, api_root = args

    if project_name not in constants.PROJECT_NAMES:
        log.error(
            f"{RUN_TESTS_COMMAND_NAME} was called with invalid project name '{project_name}' argument"
        )
        await reply_with_error(
            f"Неправильное название проекта; доступные значения: {constants.PROJECT_NAMES}"
        )
        return

    if project_name not in client.TEST_RUNNER_PROJECT_NAMES:
        await reply_with_error("Для данного проекта тестов нет")
        return

    if not is_valid_url(api_root):
        await reply_with_error("Неправильный URL деплоя проекта")
        return

    test_run = client.post_test_run(api_root.rstrip("/"), project_name)

    if isinstance(test_run, str):
        await reply_with_error("Не удалось запустить тесты для проекта")
        return

    test_run_message = await context.bot.send_message(
        chat_id=chat.id,
        text=util.escape_special_chars(to_status_message(test_run)),
        reply_to_message_id=command_message.id,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    while test_run.completed_at is None:
        await asyncio.sleep(1)

        updated_test_run = client.get_test_run(test_run.id)

        if isinstance(updated_test_run, str):
            await reply_with_error("Ошибка при прогоне тестов для проекта")
            return

        if updated_test_run == test_run:
            continue

        test_run = updated_test_run

        test_run_message = await test_run_message.edit_text(
            text=util.escape_special_chars(to_status_message(test_run)),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        assert isinstance(test_run_message, Message)

    _ = await context.bot.send_document(
        chat_id=chat.id,
        document=io.BytesIO(to_markdown_report(test_run).encode()),
        filename=f"test-run-report-{test_run.id}.md",
        reply_to_message_id=test_run_message.id,
    )


def to_status_message(test_run: dto.TestRun) -> str:
    executed = test_run.passed + test_run.skipped + test_run.failed
    total = test_run.total

    percents = (executed / total) * 100

    filled = round(percents / 10)
    empty = 10 - filled

    message = textwrap.dedent(f"""
    Тесты запущены

    URL: {test_run.deploy_base_url}
    Проект: {test_run.project_name}
    Статус: {test_run.status}

    Всего тестов: {test_run.total}
    Пройдено: {test_run.passed}
    Провалено: {test_run.failed}
    Пропущено: {test_run.skipped}

    Прогресс: {round(percents, 2)}%

    {"◽️" * filled}{"◼️" * empty}
    """).strip()
    return message


def is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    if hostname == "localhost" or hostname.endswith(".localhost"):
        return False

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_loopback:
            return False
    except ValueError:
        pass

    return True


def to_markdown_report(tr: dto.TestRun) -> str:
    assert tr.report is not None
    assert tr.completed_at is not None

    tree = {}

    for test in tr.report:
        parts = test.name.split("/")

        current = tree

        for part in parts:
            if part not in current:
                current[part] = {}

            current = current[part]

        current["test"] = test

    report = f"""
# Tests Report - {tr.project_name}

ID: {tr.id}  
Status: {tr.status}  
Tests: {tr.total} total · {tr.passed} passed · {tr.failed} failed · {tr.skipped} skipped  
Duration: {tr.completed_at - tr.created_at}s  
Deploy URL: {tr.deploy_base_url}

## Summary

| Status     | Count        |
|------------|--------------|
| ✅ Passed  | {tr.passed}  |
| ❌ Failed  | {tr.failed}  |
| ⏭️ Skipped | {tr.skipped} |

## Test Results

{render_tree(tree)}
""".strip()

    return report


def render_tree(tree: dict[Any, Any], level: int = 3) -> str:
    lines: list[str] = []

    for name, children in tree.items():

        child_names = [k for k in children if k != "test"]

        if len(child_names) == 0:
            lines.append(render_test(children["test"]))
            continue

        lines.append(f"{"#" * level} {name}")
        lines.append("")

        lines.append(render_tree(children, level + 1))
        lines.append("")

        pass

    return "\n".join(lines)


def render_test(test: dto.TestResult) -> str:
    lines: list[str] = []

    def render_details():
        lines.append(f"""
Test: {test.name}  
Output: {test.output}  
Elapsed: {test.elapsed}s  

**Request**

```http
{test.request}
```

**Response**

```http
{test.response}
```
""")

    match test.status.lower():
        case "passed":
            lines.append(f"- ✅ {test.description}")
        case "skipped":
            lines.append(f"- ⏭️ {test.description}")
            render_details()
        case "failed":
            lines.append(f"- ❌ {test.description}")
            render_details()
        case _:
            pass

    return "\n".join(lines)
