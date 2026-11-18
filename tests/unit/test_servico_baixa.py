"""Aula 3: testes do serviço com dublês, sem acesso ao banco."""
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.regras import RegraVioladaError
from app.servicos import (
    NotificadorLog,
    RelogioSistema,
    ServicoBaixa,
    TituloNaoEncontradoError,
)


@pytest.fixture
def titulo():
    return {
        "id": 17,
        "tipo": "receber",
        "descricao": "Mensalidade",
        "pessoa": "Cliente",
        "valor": Decimal("1000.00"),
        "vencimento": date(2026, 11, 10),
        "status": "aberto",
        "saldo": Decimal("1000.00"),
    }


@pytest.fixture
def repositorio(titulo):
    repositorio = Mock()
    repositorio.buscar_titulo.return_value = titulo
    return repositorio


@pytest.fixture
def relogio():
    relogio = Mock()
    relogio.hoje.return_value = date(2026, 11, 11)
    return relogio


@pytest.fixture
def notificador():
    return Mock()


@pytest.fixture
def servico(repositorio, relogio, notificador):
    return ServicoBaixa(repositorio, relogio, notificador)


def test_baixa_total_no_prazo_atualiza_status_e_notifica(
    servico, repositorio, relogio, notificador
):
    resultado = servico.baixar(17, Decimal("1000.00"), date(2026, 11, 10))

    assert resultado.encargos == Decimal("0.00")
    assert resultado.total_pago == Decimal("1000.00")
    assert resultado.saldo_restante == Decimal("0.00")
    assert resultado.status == "quitado"
    repositorio.registrar_baixa.assert_called_once_with(
        17, Decimal("1000.00"), Decimal("0.00"), date(2026, 11, 10)
    )
    repositorio.atualizar_status.assert_called_once_with(17, "quitado")
    notificador.titulo_quitado.assert_called_once_with(17, "Mensalidade")
    relogio.hoje.assert_not_called()


def test_baixa_parcial_nao_notifica_quitacao(servico, repositorio, notificador):
    resultado = servico.baixar(17, Decimal("400.00"), date(2026, 11, 10))

    assert resultado.status == "parcial"
    assert resultado.saldo_restante == Decimal("600.00")
    repositorio.atualizar_status.assert_called_once_with(17, "parcial")
    notificador.titulo_quitado.assert_not_called()


def test_sem_data_explicita_usa_relogio_e_calcula_encargos(
    servico, repositorio, relogio, notificador
):
    resultado = servico.baixar(17, Decimal("400.00"))

    assert resultado.encargos == Decimal("8.13")
    assert resultado.total_pago == Decimal("408.13")
    relogio.hoje.assert_called_once_with()
    repositorio.registrar_baixa.assert_called_once_with(
        17, Decimal("400.00"), Decimal("8.13"), date(2026, 11, 11)
    )
    notificador.titulo_quitado.assert_not_called()


def test_data_informada_tem_prioridade_sobre_relogio(
    servico, repositorio, relogio
):
    resultado = servico.baixar(17, Decimal("400.00"), date(2026, 11, 10))

    assert resultado.encargos == Decimal("0.00")
    repositorio.registrar_baixa.assert_called_once_with(
        17, Decimal("400.00"), Decimal("0.00"), date(2026, 11, 10)
    )
    relogio.hoje.assert_not_called()


def test_titulo_inexistente_nao_grava_nem_atualiza(
    servico, repositorio, notificador
):
    repositorio.buscar_titulo.return_value = None

    with pytest.raises(TituloNaoEncontradoError):
        servico.baixar(999, Decimal("10.00"))

    repositorio.registrar_baixa.assert_not_called()
    repositorio.atualizar_status.assert_not_called()
    notificador.titulo_quitado.assert_not_called()


def test_baixa_maior_que_saldo_nao_grava(servico, repositorio, notificador):
    with pytest.raises(RegraVioladaError):
        servico.baixar(17, Decimal("1000.01"), date(2026, 11, 10))

    repositorio.registrar_baixa.assert_not_called()
    repositorio.atualizar_status.assert_not_called()
    notificador.titulo_quitado.assert_not_called()


def test_relogio_de_producao_devolve_data_atual():
    assert isinstance(RelogioSistema().hoje(), date)


def test_notificador_de_producao_registra_quitacao_no_log(caplog):
    with caplog.at_level("INFO", logger="contas"):
        NotificadorLog().titulo_quitado(17, "Mensalidade")

    assert "Título 17 quitado: Mensalidade" in caplog.text
