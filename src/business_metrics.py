from prometheus_client import Counter

telegram_command_usage_total = Counter(
    "telegram_command_usage_total",
    "Total number of times a telegram command was used",
    ["command"]
)

openai_tokens_usage_total = Counter(
    "openai_tokens_usage_total",
    "Total number of OpenAI tokens consumed",
    ["token_type", "model"]
)