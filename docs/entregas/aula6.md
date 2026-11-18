# Aula 6 — caixa-preta, TDD, caixa-branca e aceitação

## Classes de equivalência e fronteiras

| Classe | Representante | Fronteira | Resultado esperado |
|---|---|---|---|
| Pagamento com pelo menos 10 dias de antecedência | Vencimento 10/11, pagamento 31/10, R$ 1.000,00 | 10 dias antes | R$ 950,00 |
| Pagamento antecipado por menos de 10 dias | Vencimento 10/11, pagamento 01/11 | 9 dias antes | R$ 1.000,00 |
| Pagamento no vencimento | Vencimento e pagamento em 10/11 | 0 dia | R$ 1.000,00 |
| Pagamento após vencimento | Vencimento 10/11, pagamento 11/11 | 1 dia de atraso | Valor mais encargos da regra 4 |
| Vencimento em fim de semana pago na prorrogação | Vencimento sábado 14/11, pagamento segunda 16/11 | Data útil prorrogada | Valor cheio |
| Vencimento em fim de semana pago após a prorrogação | Vencimento sábado 14/11, pagamento terça 17/11 | Um dia após prorrogação | Valor mais encargos da regra 4 |
| Arredondamento monetário | R$ 0,10 com 10 dias de antecedência | Meio centavo de desconto | R$ 0,09 (half-up) |

## Artefatos e reprodução

A regra está em `app/regras.py`; testes unitários em `tests/unit/test_desconto.py`; cenário de negócio em `tests/aceitacao/desconto.feature` e passos em `tests/aceitacao/test_desconto_aceitacao.py`.

```sh
python -m pytest tests/unit/test_desconto.py -v
python -m pytest -m aceitacao -v
python -m pytest tests/unit --cov=app.regras --cov-branch --cov-report=term-missing
```

A história de TDD pode ser conferida em `git log --oneline` na branch `meu-trabalho`; os commits de teste e implementação da regra 9 permanecem preservados.
