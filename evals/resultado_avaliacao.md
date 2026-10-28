# Relatório Inicial de Testes e Avaliação da IA — C2

## 1. Testes unitários

Foram implementados três testes automatizados utilizando PyTest, no arquivo `tests/test_n8n_client.py`.

| Teste | Objetivo | Resultado |
|---|---|---|
| `test_uf_obrigatoria` | Verificar se o sistema rejeita uma UF vazia | PASSED |
| `test_municipio_obrigatorio` | Verificar se o sistema rejeita um município vazio | PASSED |
| `test_resposta_sucesso_n8n` | Verificar o tratamento de uma resposta simulada de sucesso do n8n | PASSED |

**Resultado:** 3 testes executados e 3 aprovados.

## 2. Avaliação inicial da IA

Foi preparado um cenário de avaliação com os seguintes dados:

- UF: ES
- Município: Vitória
- Meio de transporte: Transporte público
- Acompanhantes: Crianças
- Período: Noite
- Objetivo: Turismo

No arquivo `evals/avaliacao_ia.py`, foi implementado um programa para avaliação manual das respostas da IA.

Foram definidos quatro critérios de avaliação:

1. **Transporte:** verificar se a IA considera o uso de transporte público.
2. **Acompanhantes:** verificar se apresenta recomendações adequadas para crianças.
3. **Período:** verificar se considera os cuidados necessários durante a noite.
4. **Objetivo:** verificar se oferece orientações relacionadas ao turismo.

Cada critério recebe uma nota de 0 a 2, totalizando até 8 pontos.

## 3. Teste de integração com o n8n

Durante a primeira tentativa de comunicação com o n8n, utilizando o município `Vitória`, o servidor retornou:

- Código HTTP: 200
- Corpo da resposta: vazio

A função `analisar_criminalidade()` apresentou a mensagem:

`N8NError: O n8n retornou uma resposta que não é JSON válido.`

Após investigação, foi identificado que os nomes dos municípios estavam cadastrados em letras maiúsculas no banco de dados.

Uma nova requisição foi realizada utilizando o município `VITÓRIA`.

**Resultado:** a integração funcionou e o n8n retornou uma resposta JSON válida contendo:

- `success: True`
- Análise textual gerada pela IA
- Modelo utilizado: `qwen/qwen3.8-27b`
- Informações do destino e do município alternativo
- Contexto informado pelo usuário

**Status da integração:** funcionamento confirmado para o cenário com município em letras maiúsculas.

## 4. Análise preliminar da resposta da IA

A resposta recebida demonstrou que a IA considerou informações do cenário, mencionando o uso de transporte público, a presença de crianças, o período noturno e o objetivo turístico.

Entretanto, foram identificados dois problemas:

**Resposta incompleta:** o texto retornado terminou no meio de uma recomendação, indicando possível truncamento da saída.

**Interpretação inadequada dos dados:** a IA classificou o risco de crimes violentos como extremamente baixo ou nulo com base na ausência de registros dessas categorias nos dados consultados. Essa ausência não permite concluir que o risco real seja inexistente.

Esses problemas demonstram a necessidade de aprimorar a qualidade e a confiabilidade das recomendações.

## 5. Situação da avaliação

**Status: avaliação inicial executada parcialmente.**

Foi realizada uma avaliação manual utilizando um trecho resumido
de uma resposta real produzida pela IA.

| Critério | Nota |
|---|---|
| Transporte | 2/2 |
| Acompanhantes | 1/2 |
| Período | 2/2 |
| Objetivo (Turismo) | 1/2 |
| **Total** | **6/8 (75%)** |

A IA demonstrou capacidade de personalizar recomendações
considerando o transporte e o período da viagem.

Entretanto, apresentou recomendações limitadas para crianças
e para o objetivo turístico.

**Limitação:** a pontuação foi atribuída a um trecho resumido
da resposta real, não à resposta completa. Portanto, o resultado
não representa uma avaliação integral da qualidade da IA.

Também foram identificados problemas de truncamento da resposta
e interpretação inadequada dos dados de criminalidade,
que deverão ser investigados na C3.

## 6. Melhorias previstas para a C3

- Ajustar a consulta SQL do n8n para aceitar nomes de municípios independentemente de letras maiúsculas ou minúsculas.
- Investigar o motivo do truncamento das respostas da IA.
- Melhorar as instruções do modelo para evitar conclusões de segurança não sustentadas pelos dados.
- Executar e registrar a avaliação completa com pontuação por critério.
- Ampliar os cenários de testes e avaliações da IA.

## 7. Conclusão

Na entrega C2, foram implementados e aprovados três testes unitários, desenvolvido um programa inicial de avaliação da IA e realizado um teste de integração com o n8n.

O processo permitiu identificar e reproduzir um problema na consulta por município, confirmar o funcionamento da integração utilizando o nome em letras maiúsculas e identificar limitações na qualidade da resposta gerada.

Os problemas encontrados foram comunicados ao grupo para aprimoramento na etapa C3.