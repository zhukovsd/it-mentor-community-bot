import logging
import re

special_chars = [
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
]
MAX_MESSAGE_LENGTH = 4096

log = logging.getLogger(__name__)


def escape_special_chars(text: str) -> str:
    pattern = "[" + re.escape("".join(special_chars)) + "]"

    escaped_text = re.sub(pattern, r"\\\g<0>", text)

    return escaped_text


def compress_messages(messages: list[str]) -> list[str]:
    compressed_messages: list[str] = []

    compressed_message = ""
    for message in messages:
        updated_compressed_message = compressed_message + "\n\n" + message

        if len(updated_compressed_message) < MAX_MESSAGE_LENGTH:
            compressed_message = updated_compressed_message
            continue

        if (
            len(updated_compressed_message) >= MAX_MESSAGE_LENGTH
            and len(compressed_message) < MAX_MESSAGE_LENGTH
        ):
            compressed_messages.append(compressed_message)
            compressed_message = message
            continue

    compressed_messages.append(compressed_message)

    return compressed_messages
