from decimal import Decimal

import pytest

from stejar_transfers.domain import (
    Currency,
    CustomerSegment,
    FeeCalculator,
    FeeRequest,
    TransferType,
    UnsupportedTransferError,
)


def test_instant_transfer_is_rejected_by_the_calculator(calculator: FeeCalculator):
    request = FeeRequest(
        Decimal("2000.00"), Currency.MDL, TransferType.INSTANT, CustomerSegment.RETAIL
    )

    with pytest.raises(UnsupportedTransferError, match="instant transfers not supported yet"):
        calculator.calculate(request)


@pytest.mark.parametrize("currency", ["MDL", "EUR"])
@pytest.mark.parametrize("segment", ["retail", "premium"])
def test_post_fees_returns_422_for_an_instant_transfer(client, currency, segment):
    body = {"amount": 2000.00, "currency": currency, "type": "instant", "customer_segment": segment}

    response = client.post("/fees", json=body)

    assert response.status_code == 422
    assert response.json() == {"error": "instant transfers not supported yet"}
