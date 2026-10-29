# Arquitetura e fluxo MLOps

## Dados e tempo

As transações estão ordenadas por `event_time`. Os primeiros 70% formam o treino, 15% seguintes a validação e os 15% finais o teste. Isso simula implantação futura e impede que observações posteriores influenciem o passado.

## Feature pipeline

As features usam apenas atributos existentes no instante da autorização: valor, horário, idade da conta, velocidade de transações, distância, presença do cartão, operação internacional e categoria do lojista. Chargeback, investigação e resultado posterior são deliberadamente excluídos.

## Treino e registro

O modelo é uma regressão logística ponderada implementada de forma transparente. O artefato JSON contém features, padronização, coeficientes, intercepto, limiar, métricas e SHA-256. Em produção, esse contrato pode ser registrado no MLflow sem alterar a lógica de decisão.

## Serving e operação

A API expõe `/health` e `/score`. O modelo é carregado uma vez na inicialização. O deploy recomendado é canário, com comparação entre distribuição de scores, latência, erros e métricas atrasadas de fraude antes da promoção.

