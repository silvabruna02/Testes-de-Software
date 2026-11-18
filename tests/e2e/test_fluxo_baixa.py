"""Aula 5: fluxo positivo e negativo da baixa pela interface web."""
import pytest
from playwright.sync_api import expect


@pytest.fixture
def usuario_logado(page, base_url):
    page.goto(f"{base_url}/login")
    page.get_by_label("Usuário").fill("admin")
    page.get_by_label("Senha").fill("admin123")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("heading", name="Títulos")).to_be_visible()
    return page


def cadastrar_titulo_receber(page, descricao, valor="1000.00"):
    page.get_by_role("link", name="Novo título").click()
    page.get_by_label("Tipo").select_option("receber")
    page.get_by_label("Descrição").fill(descricao)
    page.get_by_label("Pessoa (fornecedor ou cliente)").fill("Cliente E2E")
    page.get_by_label("Valor").fill(valor)
    page.get_by_label("Vencimento").fill("2026-11-30")
    page.get_by_label("Parcelas").fill("1")
    page.get_by_role("button", name="Salvar").click()


def localizar_titulo(page, descricao):
    return page.get_by_role("row").filter(has_text=descricao)


def test_fluxo_positivo_baixa_parcial_e_fluxo_de_caixa(usuario_logado, base_url):
    page = usuario_logado
    descricao = "E2E recebimento parcial"
    cadastrar_titulo_receber(page, descricao)

    titulo = localizar_titulo(page, descricao)
    expect(titulo).to_be_visible()
    titulo.get_by_role("link", name="Baixar").click()
    page.get_by_label("Valor da baixa").fill("400.00")
    page.get_by_label("Data do pagamento").fill("2026-11-18")
    page.get_by_role("button", name="Registrar baixa").click()

    expect(page.get_by_role("status")).to_contain_text("Baixa registrada")
    page.goto(f"{base_url}/")
    titulo = localizar_titulo(page, descricao)
    expect(titulo.locator('[data-campo="saldo"]')).to_have_text("600.00")
    expect(titulo.locator('[data-campo="status"]')).to_have_text("parcial")

    page.get_by_role("link", name="Fluxo de caixa").click()
    page.get_by_label("Início").fill("2026-11-01")
    page.get_by_label("Fim").fill("2026-11-30")
    page.get_by_role("button", name="Calcular").click()
    expect(page.locator('[data-campo="saldo-projetado"]')).to_have_text("600.00")


def test_fluxo_negativo_baixa_acima_do_saldo_nao_altera_titulo(usuario_logado, base_url):
    page = usuario_logado
    descricao = "E2E baixa acima do saldo"
    cadastrar_titulo_receber(page, descricao)

    titulo = localizar_titulo(page, descricao)
    titulo.get_by_role("link", name="Baixar").click()
    page.get_by_label("Valor da baixa").fill("1200.00")
    page.get_by_label("Data do pagamento").fill("2026-11-18")
    page.get_by_role("button", name="Registrar baixa").click()

    expect(page.get_by_role("alert")).to_contain_text(
        "O valor da baixa não pode ser maior que o saldo"
    )
    page.goto(f"{base_url}/")
    titulo = localizar_titulo(page, descricao)
    expect(titulo.locator('[data-campo="saldo"]')).to_have_text("1000.00")
    expect(titulo.locator('[data-campo="status"]')).to_have_text("aberto")
