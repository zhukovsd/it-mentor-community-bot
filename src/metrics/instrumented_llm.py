from src.config import env
from src.metrics.business_metrics import openai_tokens_usage_total, openai_spend_usd_total

PRICING = {
    env.DEFAULT_LLM_MODEL: {"input": 0.85, "output": 7.00},
    env.BIGGER_CONTEXT_LLM_MODEL: {"input": 2.50, "output": 15.00},
}


def track_llm_metrics(model: str, input_tokens: int, output_tokens: int) -> None:
    openai_tokens_usage_total.labels(token_type="input", model=model).inc(input_tokens)
    openai_tokens_usage_total.labels(token_type="output", model=model).inc(output_tokens)

    costs = PRICING.get(model, {"input": 0.0, "output": 0.0})
    input_cost = (input_tokens / 1_000_000) * costs["input"]
    output_cost = (output_tokens / 1_000_000) * costs["output"]
    total_cost = input_cost + output_cost

    if total_cost > 0:
        openai_spend_usd_total.labels(model=model).inc(total_cost)
