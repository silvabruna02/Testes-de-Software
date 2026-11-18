# Entregas das aulas 1 a 6

Este diretório reúne os artefatos das seis primeiras aulas. Os testes ficam separados por camada. O workflow [Testes](../../.github/workflows/testes.yml) executa as suítes em PostgreSQL e Chromium no GitHub Actions.

| Aula | Artefatos | Como conferir |
|---|---|---|
| 1 | [Casos de teste](aula1-casos.csv), [relato de defeito](aula1.md), `tests/unit/test_regras.py` | `python -m pytest tests/unit -q` |
| 2 | [Mutação das regras](aula2.md), `tests/unit/test_regras.py` | `python validar_testes.py` |
| 3 | [Serviço e cobertura](aula3.md), `tests/unit/test_servico_baixa.py` | `python -m pytest tests/unit --cov=app.servicos --cov=app.regras --cov-branch --cov-report=term-missing` |
| 4 | [Banco e integração](aula4.md), `tests/banco/test_funcoes.py`, `tests/integracao/test_api.py` | `python -m pytest -m 'banco or integracao' -v` e `python validar_testes.py banco` |
| 5 | [Relatório E2E](aula5.md), `tests/e2e/test_fluxo_baixa.py` | `python -m pytest -m e2e -v` |
| 6 | [Caixa-preta e aceitação](aula6.md), `tests/unit/test_desconto.py`, `tests/aceitacao/` | `python -m pytest tests/unit/test_desconto.py tests/aceitacao -v` |

Os testes de banco, integração e navegador precisam de PostgreSQL e aplicação configurados; o workflow provisiona esses serviços. Os relatórios distinguem resultados observados de verificações pendentes.
