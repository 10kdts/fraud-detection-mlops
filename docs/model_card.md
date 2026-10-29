# Model Card — Fraud Risk v1

## Uso pretendido

Priorizar transações para revisão manual em uma demonstração educacional. Não deve bloquear clientes, conceder crédito ou operar em produção sem calibração, revisão jurídica, segurança e validação com dados reais.

## Modelo e dados

- Regressão logística ponderada
- Dados totalmente sintéticos
- Divisão temporal 70/15/15
- Classe positiva rara
- Limiar escolhido na validação por custo FN:FP de 20:1

## Métricas

Average Precision é a métrica de ranking principal. Precisão, recall, matriz de confusão e custo completam a avaliação. Acurácia foi omitida como critério principal devido ao desbalanceamento.

## Limitações e riscos

- A distribuição sintética não representa fraude real.
- Labels reais normalmente chegam com atraso e podem conter viés de investigação.
- Grupos mais investigados podem receber mais rótulos de fraude.
- PSI detecta mudança de distribuição, não queda causal de desempenho.
- Nenhum atributo sensível é usado, mas proxies ainda precisam ser auditados.

## Aprovação

O modelo somente deve ser promovido quando CI, qualidade de dados, métricas offline, análise por segmento e plano de rollback forem aprovados por responsáveis de risco, dados e negócio.

