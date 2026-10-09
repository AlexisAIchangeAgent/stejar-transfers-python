"""Fee calculation. The published tariff is in docs/fee-rules.md."""

from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

from stejar_transfers.clients.exchange_rate import ExchangeRateClient
from stejar_transfers.domain.models import (
    Currency,
    Fee,
    FeeRequest,
    TransferType,
    UnsupportedTransferError,
)

CENT = Decimal("0.01")
STANDARD_RATE = Decimal("0.005")
STANDARD_MIN_FEE = Decimal("5.00")
STANDARD_MAX_FEE = Decimal("50.00")


def _clamp(fee: Decimal) -> Decimal:
    return min(max(fee, STANDARD_MIN_FEE), STANDARD_MAX_FEE)


def standard_fee_mdl(amount_mdl: Decimal) -> Decimal:
    """Standard fee of an MDL amount: 0.5%, minimum MDL 5.00, maximum MDL 50.00."""
    fee = (amount_mdl * STANDARD_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    return _clamp(fee)


class FeeCalculator:
    def __init__(self, rates: ExchangeRateClient) -> None:
        self._rates = rates

    def calculate(self, request: FeeRequest) -> Fee:
        if request.type is TransferType.INSTANT:
            raise UnsupportedTransferError("instant transfers not supported yet")
        if request.currency is Currency.MDL:
            return Fee(amount=standard_fee_mdl(request.amount), rule="standard-mdl")
        return Fee(amount=self._standard_fee_eur(request.amount), rule="standard-eur")

    def _standard_fee_eur(self, amount_eur: Decimal) -> Decimal:
        rate = self._rates.get_rate(Currency.EUR, Currency.MDL).rate
        amount_mdl = (amount_eur * rate).quantize(CENT, rounding=ROUND_DOWN)
        fee = (amount_mdl * STANDARD_RATE).quantize(CENT, rounding=ROUND_HALF_EVEN)
        return _clamp(fee)
