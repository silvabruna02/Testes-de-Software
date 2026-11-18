"""Aula 4: API REST, resposta HTTP e estado persistido no banco."""
from decimal import Decimal

import pytest


def criar_titulo(cliente, *, tipo="receber", valor="1000.00", vencimento="2026-11-10"):
    resposta = cliente.post(
        "/api/titulos",
        json={
            "tipo": tipo,
            "descricao": "Título de integração",
            "pessoa": "Cliente",
            "valor": valor,
            "vencimento": vencimento,
        },
    )
    assert resposta.status_code == 201
    return resposta.get_json()


def test_get_titulos_retorna_lista_vazia(cliente):
    resposta = cliente.get("/api/titulos")

    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_post_titulo_retorna_e_persiste_titulo(cliente):
    criado = criar_titulo(cliente)

    assert criado["tipo"] == "receber"
    assert criado["descricao"] == "Título de integração"
    assert criado["valor"] == "1000.00"
    assert criado["saldo"] == "1000.00"
    assert criado["status"] == "aberto"

    consultado = cliente.get(f"/api/titulos/{criado['id']}")
    assert consultado.status_code == 200
    assert consultado.get_json() == criado


@pytest.mark.parametrize(
    "alteracao",
    [
        {"valor": "0.00"},
        {"valor": "-1.00"},
        {"descricao": "   "},
        {"tipo": "inválido"},
        {"vencimento": "data-inválida"},
    ],
)
def test_post_titulo_invalido_retorna_400_sem_persistir(cliente, alteracao):
    dados = {
        "tipo": "receber",
        "descricao": "Título inválido",
        "pessoa": "Cliente",
        "valor": "100.00",
        "vencimento": "2026-11-10",
    }
    dados.update(alteracao)

    resposta = cliente.post("/api/titulos", json=dados)

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()
    assert cliente.get("/api/titulos").get_json() == []


def test_get_titulo_inexistente_retorna_404(cliente):
    resposta = cliente.get("/api/titulos/999999")

    assert resposta.status_code == 404
    assert "não encontrado" in resposta.get_json()["erro"]


def test_baixa_parcial_em_atraso_confere_resposta_e_estado(cliente):
    titulo = criar_titulo(cliente)

    resposta = cliente.post(
        f"/api/titulos/{titulo['id']}/baixas",
        json={"valor": "400.00", "data_pagamento": "2026-11-11"},
    )

    assert resposta.status_code == 201
    assert resposta.get_json() == {
        "encargos": "8.13",
        "total_pago": "408.13",
        "saldo_restante": "600.00",
        "status": "parcial",
    }
    consultado = cliente.get(f"/api/titulos/{titulo['id']}")
    assert consultado.status_code == 200
    assert consultado.get_json()["saldo"] == "600.00"
    assert consultado.get_json()["status"] == "parcial"


def test_baixa_total_quita_titulo(cliente):
    titulo = criar_titulo(cliente, vencimento="2026-11-20")

    resposta = cliente.post(
        f"/api/titulos/{titulo['id']}/baixas",
        json={"valor": "1000.00", "data_pagamento": "2026-11-20"},
    )

    assert resposta.status_code == 201
    assert resposta.get_json()["status"] == "quitado"
    estado = cliente.get(f"/api/titulos/{titulo['id']}").get_json()
    assert estado["saldo"] == "0.00"
    assert estado["status"] == "quitado"


def test_baixa_de_titulo_inexistente_retorna_404(cliente):
    resposta = cliente.post(
        "/api/titulos/999999/baixas",
        json={"valor": "10.00", "data_pagamento": "2026-11-10"},
    )

    assert resposta.status_code == 404
    assert "não encontrado" in resposta.get_json()["erro"]


def test_baixa_acima_do_saldo_retorna_400_sem_alterar_estado(cliente):
    titulo = criar_titulo(cliente)

    resposta = cliente.post(
        f"/api/titulos/{titulo['id']}/baixas",
        json={"valor": "1000.01", "data_pagamento": "2026-11-10"},
    )

    assert resposta.status_code == 400
    assert "saldo" in resposta.get_json()["erro"]
    estado = cliente.get(f"/api/titulos/{titulo['id']}").get_json()
    assert estado["saldo"] == "1000.00"
    assert estado["status"] == "aberto"


def test_fluxo_caixa_considera_saldos_e_datas_limite(cliente):
    criar_titulo(cliente, tipo="receber", valor="250.00", vencimento="2026-11-01")
    parcial = criar_titulo(cliente, tipo="receber", valor="100.00", vencimento="2026-11-30")
    criar_titulo(cliente, tipo="pagar", valor="100.00", vencimento="2026-11-15")
    cliente.post(
        f"/api/titulos/{parcial['id']}/baixas",
        json={"valor": "40.00", "data_pagamento": "2026-11-10"},
    )

    resposta = cliente.get(
        "/api/fluxo-caixa?inicio=2026-11-01&fim=2026-11-30"
    )

    assert resposta.status_code == 200
    assert resposta.get_json() == {
        "inicio": "2026-11-01",
        "fim": "2026-11-30",
        "saldo_projetado": "210.00",
    }

