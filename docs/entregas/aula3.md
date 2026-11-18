# Aula 3 — serviço de baixa

`tests/unit/test_servico_baixa.py` testa `ServicoBaixa` isolando persistência, relógio e notificador com mocks. Os cenários cobrem baixa total e parcial, cálculo de encargos, precedência da data explícita, título inexistente e tentativas acima do saldo. Também exercitam as implementações padrão de relógio e notificação.

Comando de cobertura:

```sh
python -m pytest tests/unit --cov=app.servicos --cov=app.regras --cov-branch --cov-report=term-missing -q
```

Na execução local registrada durante a preparação da entrega, a cobertura de linhas e branches foi 100% para `app.servicos` e `app.regras`. O relatório detalhado é reproduzível pelo comando acima.
