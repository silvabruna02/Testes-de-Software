# Aula 1 — casos e relato de defeito

## Relato: cobrança de multa no próprio vencimento

- **Identificador:** `d01` (defeito injetado para a atividade).
- **Severidade:** média; altera o valor cobrado e pode causar divergência financeira.
- **Pré-condição:** título de R$ 1.000,00 com vencimento em 10/11/2026.
- **Passos:** executar `DEFEITO=d01 python -m pytest tests/unit/test_regras.py -k no_vencimento -q`.
- **Resultado esperado:** no vencimento não há atraso; encargos de R$ 0,00.
- **Resultado obtido:** a versão defeituosa aplica multa de 2% (R$ 20,00) no dia do vencimento.
- **Evidência automatizada:** `test_calcular_encargos_no_vencimento_sem_multa` falha com `d01` e passa com as regras corretas.

A planilha de casos está em [`aula1-casos.csv`](aula1-casos.csv). São cenários derivados das regras e executados contra a implementação corrigida desta branch; o defeito histórico é reproduzido pelo injetor `d01`, não pela interface original da primeira aula.
