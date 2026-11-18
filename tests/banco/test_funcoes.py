"""Aula 4: funções, restrições e triggers em PostgreSQL real."""
from datetime import date
from decimal import Decimal

import psycopg
import pytest

from app.regras import calcular_encargos


def criar_titulo(
    conexao,
    *,
    tipo="receber",
    valor=Decimal("100.00"),
    vencimento=date(2026, 11, 10),
    status="aberto",
    descricao="Título de teste",
):
    return conexao.execute(
        "INSERT INTO titulos (tipo, descricao, pessoa, valor, vencimento, status) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (tipo, descricao, "Cliente", valor, vencimento, status),
    ).fetchone()[0]


def inserir_baixa(conexao, titulo_id, valor, data=date(2026, 11, 10)):
    return conexao.execute(
        "INSERT INTO baixas (titulo_id, valor, encargos, data_baixa) "
        "VALUES (%s, %s, 0, %s) RETURNING id",
        (titulo_id, valor, data),
    ).fetchone()[0]


@pytest.mark.parametrize(
    ("baixas", "esperado"),
    [
        ([], Decimal("100.00")),
        ([Decimal("40.00")], Decimal("60.00")),
        ([Decimal("30.00"), Decimal("20.00")], Decimal("50.00")),
        ([Decimal("100.00")], Decimal("0.00")),
    ],
)
def test_fn_saldo_titulo_soma_todas_as_baixas(conexao, baixas, esperado):
    titulo_id = criar_titulo(conexao)
    for valor in baixas:
        inserir_baixa(conexao, titulo_id, valor)

    saldo = conexao.execute("SELECT fn_saldo_titulo(%s)", (titulo_id,)).fetchone()[0]

    assert saldo == esperado


def test_fn_saldo_titulo_retorna_null_para_id_inexistente(conexao):
    assert conexao.execute("SELECT fn_saldo_titulo(-1)").fetchone()[0] is None


@pytest.mark.parametrize("valor", [Decimal("0.00"), Decimal("-0.01")])
def test_restricao_rejeita_titulo_com_valor_nao_positivo(conexao, valor):
    with pytest.raises(psycopg.errors.CheckViolation):
        criar_titulo(conexao, valor=valor)


def test_restricao_aceita_titulo_de_um_centavo(conexao):
    titulo_id = criar_titulo(conexao, valor=Decimal("0.01"))

    assert titulo_id > 0


def test_trigger_permite_baixa_igual_ao_saldo_e_quita_titulo(conexao):
    titulo_id = criar_titulo(conexao)

    inserir_baixa(conexao, titulo_id, Decimal("100.00"))

    status = conexao.execute(
        "SELECT status FROM titulos WHERE id = %s", (titulo_id,)
    ).fetchone()[0]
    assert status == "quitado"


def test_trigger_rejeita_baixa_um_centavo_acima_do_saldo(conexao):
    titulo_id = criar_titulo(conexao)

    with pytest.raises(psycopg.errors.RaiseException):
        inserir_baixa(conexao, titulo_id, Decimal("100.01"))


def test_trigger_rejeita_baixa_zero(conexao):
    titulo_id = criar_titulo(conexao)

    with pytest.raises(psycopg.errors.RaiseException):
        inserir_baixa(conexao, titulo_id, Decimal("0.00"))


@pytest.mark.parametrize("status", ["cancelado", "quitado"])
def test_trigger_rejeita_baixa_em_titulo_cancelado_ou_quitado(conexao, status):
    titulo_id = criar_titulo(conexao, status=status)

    with pytest.raises(psycopg.errors.RaiseException):
        inserir_baixa(conexao, titulo_id, Decimal("10.00"))


def test_trigger_muda_titulo_aberto_para_parcial(conexao):
    titulo_id = criar_titulo(conexao)

    inserir_baixa(conexao, titulo_id, Decimal("40.00"))

    status, saldo = conexao.execute(
        "SELECT status, fn_saldo_titulo(id) FROM titulos WHERE id = %s", (titulo_id,)
    ).fetchone()
    assert status == "parcial"
    assert saldo == Decimal("60.00")


def test_trigger_muda_titulo_parcial_para_quitado(conexao):
    titulo_id = criar_titulo(conexao)
    inserir_baixa(conexao, titulo_id, Decimal("40.00"))

    inserir_baixa(conexao, titulo_id, Decimal("60.00"))

    status = conexao.execute(
        "SELECT status FROM titulos WHERE id = %s", (titulo_id,)
    ).fetchone()[0]
    assert status == "quitado"


@pytest.mark.parametrize(
    ("valor", "vencimento", "pagamento"),
    [
        (Decimal("1000.00"), date(2026, 11, 10), date(2026, 11, 10)),
        (Decimal("1000.00"), date(2026, 11, 10), date(2026, 11, 11)),
        (Decimal("1000.00"), date(2026, 11, 10), date(2026, 12, 10)),
        (Decimal("150.01"), date(2026, 11, 14), date(2026, 11, 17)),
        (Decimal("333.33"), date(2026, 11, 15), date(2026, 11, 16)),
    ],
)
def test_fn_encargos_corresponde_a_regra_python(conexao, valor, vencimento, pagamento):
    no_banco = conexao.execute(
        "SELECT fn_encargos(%s, %s, %s)", (valor, vencimento, pagamento)
    ).fetchone()[0]

    assert no_banco == calcular_encargos(valor, vencimento, pagamento)


def test_fn_proximo_dia_util_leva_sabado_ate_segunda(conexao):
    assert conexao.execute(
        "SELECT fn_proximo_dia_util(%s)", (date(2026, 11, 14),)
    ).fetchone()[0] == date(2026, 11, 16)


def test_fn_fluxo_caixa_retorna_zero_em_periodo_vazio(conexao):
    saldo = conexao.execute(
        "SELECT fn_fluxo_caixa(%s, %s)",
        (date(2026, 12, 1), date(2026, 12, 31)),
    ).fetchone()[0]

    assert saldo == Decimal("0.00")


def test_fn_fluxo_caixa_soma_saldos_e_inclui_datas_limite(conexao):
    receber = criar_titulo(
        conexao, tipo="receber", valor=Decimal("250.00"), vencimento=date(2026, 11, 1)
    )
    parcial = criar_titulo(
        conexao, tipo="receber", valor=Decimal("100.00"), vencimento=date(2026, 11, 30)
    )
    pagar = criar_titulo(
        conexao, tipo="pagar", valor=Decimal("100.00"), vencimento=date(2026, 11, 15)
    )
    cancelado = criar_titulo(
        conexao, tipo="receber", valor=Decimal("500.00"), vencimento=date(2026, 11, 15), status="cancelado"
    )
    quitado = criar_titulo(
        conexao, tipo="receber", valor=Decimal("300.00"), vencimento=date(2026, 11, 15)
    )
    inserir_baixa(conexao, parcial, Decimal("40.00"))
    inserir_baixa(conexao, quitado, Decimal("300.00"))

    saldo = conexao.execute(
        "SELECT fn_fluxo_caixa(%s, %s)",
        (date(2026, 11, 1), date(2026, 11, 30)),
    ).fetchone()[0]

    assert saldo == Decimal("210.00")

