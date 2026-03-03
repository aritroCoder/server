import asyncio
import secrets
from server.models import Offer, Pairing, paired_message
from server.pricing import calculate_exchange


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
        )

    async def remove_by_ws(self, ws) -> None:
        async with self._lock:
            self._offers = [o for o in self._offers if o.ws is not ws]
