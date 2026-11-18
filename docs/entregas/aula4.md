# Aula 4 — banco e integração da API

- `tests/banco/test_funcoes.py`: funções SQL de saldo e fluxo de caixa, limites de datas, restrição de valor, trigger de validação da baixa, atualização de status e comparação dos encargos em Python e SQL.
- `tests/integracao/test_api.py`: API com PostgreSQL real, incluindo criação e consulta, entradas inválidas, baixa parcial e total, ausência de título, excesso de saldo e fluxo de caixa.

Execute em um banco PostgreSQL migrado:

```sh
python -m pytest -m 'banco or integracao' -v
python validar_testes.py banco
```

A verificação de mutação do banco aplica temporariamente cada SQL defeituoso, mede se a suíte acusa o problema e restaura a função correta ao final. A validação local depende de PostgreSQL disponível; o workflow automatizado cria o serviço e executa essas etapas.
