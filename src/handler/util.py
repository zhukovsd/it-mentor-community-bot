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


def escape_special_chars(text: str) -> str:
    pattern = "[" + re.escape("".join(special_chars)) + "]"

    escaped_text = re.sub(pattern, r"\\\g<0>", text)

    return escaped_text
