# Fraud Detection MLOps

[![CI](https://github.com/10kdts/fraud-detection-mlops/actions/workflows/ci.yml/badge.svg)](https://github.com/10kdts/fraud-detection-mlops/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Neste projeto eu tratei detecção de fraude como uma decisão de negócio, não como uma disputa por acurácia. O modelo precisa encontrar fraude, mas também precisa explicar o custo de revisar uma compra legítima, funcionar sem informação do futuro e deixar um caminho seguro para rollback.

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

## O que eu coloquei em prática

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

## Resultado de referência

Na execução determinística com 6.000 transações, o período de teste obteve Average Precision de **0,144**, recall de **60%** e limiar de decisão de **0,64**. A precisão de 2,94% reflete deliberadamente a raridade da classe e o custo 20 vezes maior atribuído a fraudes não detectadas; por isso, o modelo encaminha casos para revisão em vez de bloquear automaticamente.

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
| 8 | Publicação no GitHub | Concluída |

Consulte a [arquitetura](docs/architecture.md), o [model card](docs/model_card.md), o [runbook](docs/runbook.md) e o [relatório de validação](docs/validation_report.md).

