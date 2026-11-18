# Aula 5 — testes ponta a ponta

`tests/e2e/test_fluxo_baixa.py` cobre dois fluxos no navegador: baixa parcial bem-sucedida, conferindo saldo, status e fluxo de caixa; e tentativa acima do saldo, conferindo a mensagem de erro e que o título continua inalterado. Os seletores usam rótulos, papéis acessíveis e atributos `data-campo`; as asserções aguardam condições observáveis do Playwright sem pausas fixas.

O workflow `.github/workflows/testes.yml` instala Chromium, sobe o Flask contra PostgreSQL migrado e executa `python -m pytest -m e2e -v`. Localmente, configure banco, dependências e `BASE_URL`, inicie a aplicação e rode o mesmo comando. A execução de navegador local não foi confirmada neste ambiente.
