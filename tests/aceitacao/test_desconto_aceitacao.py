from datetime import date
from decimal import Decimal

from pytest_bdd import given, parsers, scenarios, then, when

from app.regras import calcular_valor_pagamento

scenarios("desconto.feature")


@given(parsers.parse("um título de {valor} com vencimento em {vencimento}"), target_fixture="titulo")
def titulo(valor, vencimento):
    return {"valor": Decimal(valor), "vencimento": date.fromisoformat(vencimento)}


@when(parsers.parse("o pagamento é feito em {pagamento}"), target_fixture="valor_a_pagar")
def pagar(titulo, pagamento):
    return calcular_valor_pagamento(
        titulo["valor"], titulo["vencimento"], date.fromisoformat(pagamento)
    )


@then(parsers.parse("o valor a pagar é {esperado}"))
def conferir_valor(valor_a_pagar, esperado):
    assert valor_a_pagar == Decimal(esperado)
