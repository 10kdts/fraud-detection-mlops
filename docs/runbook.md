# Runbook operacional

## Alertas

| Sinal | Warning | Crítico |
|---|---:|---:|
| PSI por feature/score | >= 0,10 | >= 0,25 |
| Erros HTTP 5xx | >= 1% | >= 5% |
| Latência p95 | >= 150 ms | >= 300 ms |
| Queda de recall confirmado | >= 10% | >= 20% |

## Diagnóstico

1. Verificar `/health`, erros e latência.
2. Confirmar versão e SHA do modelo ativo.
3. Comparar esquema e nulls com o contrato esperado.
4. Medir PSI por feature e por score.
5. Quando labels estiverem disponíveis, recalcular Average Precision, precisão, recall e custo.
6. Separar falha de dados, mudança legítima de comportamento e regressão do modelo.

## Mitigação e rollback

Se houver impacto crítico, direcionar decisões ao último modelo aprovado ou ao fluxo de revisão manual. Rollback consiste em restaurar o artefato anterior, reiniciar a API, confirmar `/health`, testar casos conhecidos e acompanhar erros e distribuição de scores por 30 minutos.

## Retreino

Retreinar somente com janela fechada, labels maduros e aprovação. Comparar challenger e champion no mesmo período. Nunca promover automaticamente apenas porque uma métrica agregada melhorou.

