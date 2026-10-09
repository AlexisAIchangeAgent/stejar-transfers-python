from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

import pytest

from stejar_transfers.clients.exchange_rate import ExchangeRate, FixedRateClient
from stejar_transfers.domain import (
    Currency,
    CustomerSegment,
    FeeCalculator,
    FeeRequest,
    TransferType,
)


def eur_request(amount: str, segment: CustomerSegment = CustomerSegment.RETAIL) -> FeeRequest:
    return FeeRequest(Decimal(amount), Currency.EUR, TransferType.STANDARD, segment)


@dataclass
class RecordingRateClient:
    rate: Decimal
    calls: list[tuple[str, str]] = field(default_factory=list)

    def get_rate(self, from_currency: str, to_currency: str) -> ExchangeRate:
        self.calls.append((from_currency, to_currency))
        return ExchangeRate(from_currency, to_currency, self.rate, date(2026, 10, 19))


@pytest.mark.parametrize(
    ("amount_eur", "expected_fee"),
    [
        ("100.00", "10.00"),
        ("300.00", "30.00"),
        ("10.00", "5.00"),
        ("1000.00", "50.00"),
    ],
)
def test_standard_eur_fee_converts_to_mdl_then_applies_the_mdl_rule(
    calculator: FeeCalculator, amount_eur, expected_fee
):
    fee = calculator.calculate(eur_request(amount_eur))

    assert fee.amount == Decimal(expected_fee)
    assert fee.currency is Currency.MDL
    assert fee.rule == "standard-eur"


def test_standard_eur_fee_asks_the_eur_to_mdl_rate():
    rates = RecordingRateClient(rate=Decimal("20.0000"))

    FeeCalculator(rates).calculate(eur_request("100.00"))

    assert rates.calls == [("EUR", "MDL")]


def test_standard_eur_fee_with_the_published_rate():
    calculator = FeeCalculator(FixedRateClient())

    # EUR 100.00 at 19.8765 is MDL 1,987.65, and 0.5% of it is 9.93825
    assert calculator.calculate(eur_request("100.00")).amount == Decimal("9.94")


def test_mdl_transfer_does_not_ask_for_a_rate():
    rates = RecordingRateClient(rate=Decimal("20.0000"))

    FeeCalculator(rates).calculate(
        FeeRequest(Decimal("100.00"), Currency.MDL, TransferType.STANDARD, CustomerSegment.RETAIL)
    )

    assert rates.calls == []
