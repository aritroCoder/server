import asyncio
import secrets
from server.models import Offer, Pairing
from server.pricing import (
    calculate_exchange,
    calculate_input_exchange,
    calculate_output_exchange,
)


class Matcher:
    def __init__(self) -> None:
        self._offers: list[Offer] = []
        self._lock = asyncio.Lock()

    async def add_offer(self, offer: Offer) -> Pairing | None:
        async with self._lock:
            for i, existing in enumerate(self._offers):
                if (
                    existing.provider == offer.want_provider
                    and existing.model == offer.want_model
                    and existing.want_provider == offer.provider
                    and existing.want_model == offer.model
                ):
                    self._offers.pop(i)
                    return self._make_pairing(existing, offer)
            self._offers.append(offer)
            return None

    def _make_pairing(self, a: Offer, b: Offer) -> Pairing:
        input_tokens_a_serves = 0
        output_tokens_a_serves = 0
        input_tokens_b_serves = 0
        output_tokens_b_serves = 0

        if a.advanced and b.advanced:
            input_tokens_a_serves = min(
                a.input_tokens_offered,
                calculate_input_exchange(b.model, b.input_tokens_offered, a.model),
            )
            output_tokens_a_serves = min(
                a.output_tokens_offered,
                calculate_output_exchange(b.model, b.output_tokens_offered, a.model),
            )
            input_tokens_b_serves = min(
                b.input_tokens_offered,
                calculate_input_exchange(a.model, a.input_tokens_offered, b.model),
            )
            output_tokens_b_serves = min(
                b.output_tokens_offered,
                calculate_output_exchange(a.model, a.output_tokens_offered, b.model),
            )
            tokens_a_serves = input_tokens_a_serves + output_tokens_a_serves
            tokens_b_serves = input_tokens_b_serves + output_tokens_b_serves
        else:
            tokens_a_serves = min(
                a.tokens_offered,
                calculate_exchange(b.model, b.tokens_offered, a.model),
            )
            tokens_b_serves = min(
                b.tokens_offered,
                calculate_exchange(a.model, a.tokens_offered, b.model),
            )

        return Pairing(
            offer_a=a,
            offer_b=b,
            temp_key_a=secrets.token_urlsafe(32),
            temp_key_b=secrets.token_urlsafe(32),
            tokens_a_serves=tokens_a_serves,
            tokens_b_serves=tokens_b_serves,
            input_tokens_a_serves=input_tokens_a_serves,
            output_tokens_a_serves=output_tokens_a_serves,
            input_tokens_b_serves=input_tokens_b_serves,
            output_tokens_b_serves=output_tokens_b_serves,
        )

    async def remove_by_ws(self, ws) -> None:
        async with self._lock:
            self._offers = [o for o in self._offers if o.ws is not ws]
