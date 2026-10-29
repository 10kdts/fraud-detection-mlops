# Fraud Detection MLOps

Projeto de portfólio para vagas de Analista, Cientista, Engenheiro e Especialista de Dados. Implementa detecção de fraude reproduzível, explicável e operável, com foco em decisões de negócio — não apenas em acurácia.

## Problema

Fraude é um problema desbalanceado: aprovar fraude gera perda financeira, mas bloquear compras legítimas prejudica clientes. O projeto treina um modelo com divisão temporal, escolhe o limiar pelo custo relativo de falsos negativos e falsos positivos e monitora mudança na população.

## Arquitetura

```text
Transações -> validação -> features point-in-time -> treino temporal
                                                      |
                                                      v
                                        modelo + métricas + hash
                                                      |
                                  API /score <--------+
                                      |
                                      v
                         logs, PSI, alertas e retreino
```

## Competências demonstradas

- Modelagem de classificação desbalanceada
- Prevenção de data leakage e look-ahead bias
- Split temporal 70/15/15
- Regressão logística ponderada e explicável
- Average Precision, precisão, recall e matriz de confusão
- Limiar orientado a custo de negócio
- Versionamento do modelo por SHA-256
- API de inferência com health check
- Monitoramento de drift com PSI
- Testes determinísticos, Docker e GitHub Actions
- Model card, runbook, governança e estratégia de rollback

## Executar

Requer somente Python 3.11 ou superior.

```bash
python -m src.fraudml.generate
python -m src.fraudml.model
python -m unittest discover -s tests -v
python -m src.fraudml.api
```

Exemplo de requisição:

```bash
curl -X POST http://127.0.0.1:8080/score \
  -H "Content-Type: application/json" \
  -d '{"amount":950,"hour":2,"account_age_days":12,"transactions_24h":9,"distance_from_home_km":850,"card_present":0,"is_foreign":1,"merchant_category":"electronics"}'
```

## Decisões importantes

- Acurácia não é usada como métrica principal porque pode mascarar falhas na classe rara.
- O conjunto de teste é o período mais recente e não participa da escolha do limiar.
- O custo padrão considera um falso negativo 20 vezes mais caro que um falso positivo.
- Nenhuma variável criada depois da decisão de fraude entra no treinamento.
- Dados são sintéticos; resultados não representam uma instituição financeira real.

## Roadmap

| Fase | Entrega | Status |
|---|---|---|
| 1 | Escopo, riscos e arquitetura | Concluída |
| 2 | Dados sintéticos e validação | Concluída |
| 3 | Features e prevenção de leakage | Concluída |
| 4 | Treino, métricas e limiar de custo | Concluída |
| 5 | API e empacotamento | Concluída |
| 6 | Drift, observabilidade e rollback | Concluída |
| 7 | Testes e CI/CD | Concluída |
| 8 | Publicação no GitHub | Pendente |

Consulte a [arquitetura](docs/architecture.md), o [model card](docs/model_card.md), o [runbook](docs/runbook.md) e o [relatório de validação](docs/validation_report.md).

