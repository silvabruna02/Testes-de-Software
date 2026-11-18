from datetime import date
from decimal import Decimal

from app.regras import calcular_valor_pagamento

VENCIMENTO = date(2026, 11, 10)


def test_pagamento_no_vencimento_e_valor_cheio():
    valor = calcular_valor_pagamento(Decimal("1000.00"), VENCIMENTO, VENCIMENTO)

    assert valor == Decimal("1000.00")
