import math

# Per 1M tokens: (input_price_usd, output_price_usd)
PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "claude-sonnet-4": (3.00, 15.00),
    "claude-3.5-haiku": (1.00, 5.00),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-1.5-pro": (1.25, 10.00),
    "gemini-1.5-flash": (0.15, 0.60),
}


def avg_price(model: str) -> float:
    inp, out = PRICING[model]
    return (inp + out) / 2


def calculate_exchange(
    offered_model: str, offered_tokens: int, wanted_model: str
) -> int:
    return math.floor(
        offered_tokens * avg_price(offered_model) / avg_price(wanted_model)
    )


def is_known_model(model: str) -> bool:
    return model in PRICING
