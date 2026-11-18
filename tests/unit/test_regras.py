"""Casos das aulas 1 e 2: limites e regras puras do domínio."""
from datetime import date
from decimal import Decimal

import pytest

from app.regras import (
    RegraVioladaError,
    calcular_encargos,
    gerar_parcelas,
    novo_status,
    proximo_dia_util,
    validar_baixa,
    validar_titulo,
    vencimentos_das_parcelas,
)


VENCIMENTO = date(2026, 11, 10)
VALOR = Decimal("1000.00")


@pytest.mark.parametrize(
    ("valor", "vencimento", "pagamento", "esperado"),
    [
        (VALOR, VENCIMENTO, date(2026, 11, 9), Decimal("0.00")),
        (VALOR, VENCIMENTO, VENCIMENTO, Decimal("0.00")),
        (VALOR, VENCIMENTO, date(2026, 11, 11), Decimal("20.33")),
        (VALOR, VENCIMENTO, date(2026, 12, 10), Decimal("29.90")),
        (VALOR, date(2026, 11, 14), date(2026, 11, 16), Decimal("0.00")),
        (VALOR, date(2026, 11, 14), date(2026, 11, 17), Decimal("20.33")),
        (Decimal("150.01"), VENCIMENTO, date(2026, 11, 11), Decimal("3.05")),
    ],
)
def test_calcular_encargos_nas_fronteiras_e_fim_de_semana(
    valor, vencimento, pagamento, esperado
):
    assert calcular_encargos(valor, vencimento, pagamento) == esperado


def test_calcular_encargos_no_vencimento_sem_multa():
    assert calcular_encargos(VALOR, VENCIMENTO, VENCIMENTO) == Decimal("0.00")


@pytest.mark.parametrize(
    ("valor", "quantidade", "esperado"),
    [
        (Decimal("100.00"), 3, [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]),
        (Decimal("10.00"), 2, [Decimal("5.00"), Decimal("5.00")]),
        (Decimal("10.00"), 1, [Decimal("10.00")]),
    ],
)
def test_gerar_parcelas_preserva_total_e_distribui_resto_na_primeira(
    valor, quantidade, esperado
):
    assert gerar_parcelas(valor, quantidade) == esperado


@pytest.mark.parametrize("quantidade", [0, -1])
def test_gerar_parcelas_rejeita_quantidade_invalida(quantidade):
    with pytest.raises(RegraVioladaError):
        gerar_parcelas(Decimal("10.00"), quantidade)


@pytest.mark.parametrize(
    ("tipo", "descricao", "valor"),
    [
        ("pagar", "Conta de luz", Decimal("1.00")),
        ("receber", "Mensalidade", Decimal("100.00")),
    ],
)
def test_validar_titulo_aceita_dados_validos(tipo, descricao, valor):
    validar_titulo(tipo, descricao, valor)


@pytest.mark.parametrize(
    ("tipo", "descricao", "valor"),
    [
        ("desconhecido", "Conta", Decimal("10.00")),
        ("pagar", "", Decimal("10.00")),
        ("receber", "   ", Decimal("10.00")),
        ("pagar", "Conta", Decimal("0.00")),
        ("pagar", "Conta", Decimal("-0.01")),
    ],
)
def test_validar_titulo_rejeita_tipo_descricao_ou_valor_invalido(tipo, descricao, valor):
    with pytest.raises(RegraVioladaError):
        validar_titulo(tipo, descricao, valor)


@pytest.mark.parametrize(
    ("saldo", "status", "valor"),
    [
        (Decimal("100.00"), "aberto", Decimal("100.00")),
        (Decimal("100.00"), "parcial", Decimal("40.00")),
    ],
)
def test_validar_baixa_aceita_valor_ate_o_saldo(saldo, status, valor):
    validar_baixa(saldo, status, valor)


@pytest.mark.parametrize(
    ("saldo", "status", "valor"),
    [
        (Decimal("100.00"), "cancelado", Decimal("10.00")),
        (Decimal("100.00"), "quitado", Decimal("10.00")),
        (Decimal("100.00"), "aberto", Decimal("0.00")),
        (Decimal("100.00"), "aberto", Decimal("-1.00")),
        (Decimal("100.00"), "aberto", Decimal("100.01")),
    ],
)
def test_validar_baixa_rejeita_status_valor_ou_saldo_invalido(saldo, status, valor):
    with pytest.raises(RegraVioladaError):
        validar_baixa(saldo, status, valor)


@pytest.mark.parametrize(
    ("valor_titulo", "saldo", "esperado"),
    [
        (Decimal("100.00"), Decimal("100.00"), "aberto"),
        (Decimal("100.00"), Decimal("40.00"), "parcial"),
        (Decimal("100.00"), Decimal("0.00"), "quitado"),
    ],
)
def test_novo_status_reflete_saldo(valor_titulo, saldo, esperado):
    assert novo_status(valor_titulo, saldo) == esperado


@pytest.mark.parametrize(
    ("data", "esperado"),
    [
        (date(2026, 11, 13), date(2026, 11, 13)),
        (date(2026, 11, 14), date(2026, 11, 16)),
        (date(2026, 11, 15), date(2026, 11, 16)),
    ],
)
def test_proximo_dia_util_prorroga_sabado_e_domingo(data, esperado):
    assert proximo_dia_util(data) == esperado


def test_vencimentos_das_parcelas_avancam_de_trinta_em_trinta_dias():
    assert vencimentos_das_parcelas(date(2026, 11, 10), 3) == [
        date(2026, 11, 10),
        date(2026, 12, 10),
        date(2027, 1, 9),
    ]
