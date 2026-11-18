from datetime import date
from decimal import Decimal

import pytest

from app.regras import calcular_valor_pagamento

VENCIMENTO = date(2026, 11, 10)


def test_pagamento_no_vencimento_e_valor_cheio():
    valor = calcular_valor_pagamento(Decimal("1000.00"), VENCIMENTO, VENCIMENTO)

    assert valor == Decimal("1000.00")


def test_pagamento_com_dez_dias_de_antecedencia_tem_cinco_por_cento_de_desconto():
    valor = calcular_valor_pagamento(Decimal("1000.00"), VENCIMENTO, date(2026, 10, 31))

    assert valor == Decimal("950.00")


@pytest.mark.parametrize(
    ("vencimento", "pagamento", "esperado"),
    [
        (date(2026, 11, 10), date(2026, 11, 1), Decimal("1000.00")),
        (date(2026, 11, 10), date(2026, 11, 11), Decimal("1020.33")),
        (date(2026, 11, 14), date(2026, 11, 16), Decimal("1000.00")),
        (date(2026, 11, 14), date(2026, 11, 17), Decimal("1020.33")),
    ],
)
def test_limites_de_valor_cheio_e_encargos(vencimento, pagamento, esperado):
    valor = calcular_valor_pagamento(Decimal("1000.00"), vencimento, pagamento)

    assert valor == esperado


def test_desconto_de_meio_centavo_arredonda_para_cima():
    valor = calcular_valor_pagamento(Decimal("0.10"), VENCIMENTO, date(2026, 10, 31))

    assert valor == Decimal("0.09")
