# Relatório de validação

## Avaliação geral: pronto para compartilhar como projeto de portfólio, com ressalvas

## Metodologia

- População, classe positiva e custo estão definidos.
- Split temporal evita embaralhar futuro e passado.
- Features são point-in-time e não usam resultado posterior.
- Limiar é escolhido na validação; teste permanece independente.
- Execuções são determinísticas e verificadas por testes.

## Verificações

- Contagem e taxa de fraude registradas em manifesto.
- Métricas recalculadas a partir das previsões.
- Matriz de confusão fecha com o total de teste.
- Artefato recebe hash para rastreabilidade.
- PSI idêntico é estável e distribuição deslocada é crítica.

## Ressalvas obrigatórias

- Dados sintéticos não validam eficácia em produção.
- Correlação entre sinais simulados e fraude decorre do gerador.
- Não há afirmação causal nem garantia financeira.
- Fairness precisa ser avaliada com grupos legalmente apropriados em dados reais.

