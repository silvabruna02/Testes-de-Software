# Aula 2 — testes de regras e mutação

A suíte `tests/unit/test_regras.py` verifica encargos, datas de vencimento e prorrogação de fim de semana, divisão de parcelas, validação de títulos e baixas e transição de status. Os casos cobrem entradas válidas e inválidas, fronteiras e valores monetários fracionários.

Execute `python -m pytest tests/unit -q` para a suíte. Execute `python validar_testes.py` para rodar os testes contra cada defeito injetado das regras (`d01` a `d10`). Na execução local realizada durante a preparação desta entrega, todos os 10 defeitos foram detectados. O workflow repete essa validação em cada push e pull request.
