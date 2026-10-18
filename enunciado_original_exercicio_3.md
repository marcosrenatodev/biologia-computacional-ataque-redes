**Aberto:** Tuesday, 29 Sep 2026, 00:00

**Vencimento:** Wednesday, 21 Oct 2026, 23:59

# EXERCÍCIO 3: ROBUSTEZ, RESILIÊNCIA E HIERARQUIA EM REDES COMPLEXAS

O objetivo deste exercício é aprofundar a análise de redes complexas, investigando sua capacidade de manter a conectividade sob estresse e explorando métricas avançadas de monitoramento. A atividade deve ser realizada em grupos de até três alunos.

O exercício deve ser realizado em grupos de até três alunos.

Cada grupo deverá selecionar e baixar ao menos **2 *datasets*** de redes de domínios distintos (ex: uma rede social e uma rede tecnológica) disponíveis nos repositórios listados abaixo. Estes repositórios reúnem redes de diferentes domínios disponibilizadas pela comunidade acadêmica.

- **Network Repository** ([https://networkrepository.com/](https://networkrepository.com/))
- **Snap** ([https://snap.stanford.edu/data/index.html](https://snap.stanford.edu/data/index.html))
- **Kaggle** ([https://www.kaggle.com/datasets/](https://www.kaggle.com/datasets/))

**Recomendação**: selecionar redes entre **2.000** e **10.000** nós, contendo *hubs* de variados graus de conectividade para permitir uma comparação rica entre as estruturas.

# O DESAFIO: SIMULAÇÃO DE FALHAS E ATAQUES

Utilizando a biblioteca *igraph* (em **R** ou **Python**), desenvolvam um *script* que execute as seguintes etapas para **ambas as redes**:

## Etapa 1. Importação, Limpeza e Caracterização

– Importar o *dataset* e convertê-lo em um objeto de grafo.

– Identificar se a rede é **direcionada** ou **não-direcionada**.

– Realizar a simplificação da rede: Remover loops (arestas que ligam um nó a ele mesmo) e arestas múltiplas.

– Realizar a caracterização básica da rede com as métricas estudas no exercício anterior: Ordem, Densidade, Diâmetro e Transitividade.

## Etapa 2. Decomposição de Redes

A decomposição em **K-core** é uma técnica hierárquica que permite identificar o núcleo central e mais resiliente de uma rede através de um processo de "descascamento" (*pruning*). Diferente do grau simples, que mede apenas conexões diretas, o **K-core** identifica subgrafos onde todos os nós possuem, no mínimo, grau k, garantindo que os nós remanescentes estejam imersos em vizinhanças também densamente conectadas. Ao remover progressivamente nós de baixo grau, restará apenas o **K-core** máximo (k-max), que representa a espinha dorsal da rede. Complementarmente, a **Assortatividade** mede a tendência de nós se conectarem a outros com graus semelhantes, revelando se a rede possui um "clube de elite" (*assortativa*) ou se os *hubs* servem como centros de distribuição para nós periféricos (*desassortativa*).

– Calcule o número de *coreness* para cada nó da rede.

– Determine o valor de **k** do núcleo máximo (**k-max**) e contabilize quantos nós estão nesta camada.

– Identifique os 5 nós pertencentes ao **K-core** máximo que possuem o maior grau relativo dentro desse subgrafo.

– Gere um gráfico da rede onde a cor de cada nó seja definida pelo seu valor de *coreness*, destacando visualmente a transição da periferia para o núcleo.

Dica: use o script de demonstração (EaD3_Script1.R) disponível no Material de Apoio.

## Etapa 3. Simulação e Análise de Resiliência

Para cada rede, realize um experimento de “**Remoção de Nós**” para testar sua robustez:

– Ataque Direcionado: Removam os 10 nós com maior ***Betweenness*** progressivamente (um a um).

– Falha Aleatória: Removam 10 nós escolhidos aleatoriamente. Para evitar viés, repitam este processo 5 vezes e utilizem a média dos resultados.

– Monitoramento: Após cada remoção, calculem e armazenem o tamanho da **Maior Componente Conectada** (LCC) e o **Caminho Médio (Average Path Length).**

## Etapa 4. Comparação e Diagnóstico Estrutural

Confronte os dados estáticos com os resultados da simulação para diagnosticar as vulnerabilidades. Verifiquem se os nós utilizados no “Ataque Direcionado” fazem parte do núcleo (k-max). Analisem qual das duas redes fragmentou-se mais rapidamente e se o Caminho Médio aumentou significativamente antes do colapso. Compare as duas redes: qual delas possui um núcleo mais denso e como isso afetou a resiliência final?

# RELATÓRIO DE ENTREGA

O relatório **(3 a 5 páginas)** deve ser organizado obrigatoriamente a seguintes seções:

- Identificação do Grupo
- Introdução
- Decomposição de Redes
- Simulação e Análise de Resiliência
- Comparação e Diagnóstico Estrutural
- Conclusão
- Referências Bibliográficas

**Pontos fundamentais para observar no relatório:**

- **Análise de Robustez:** Apresentar gráficos comparando o declínio da conectividade (LCC) e a variação do Caminho Médio entre o “Ataque Direcionado” e a “Falha Aleatória”. Qual rede é mais resiliente? Qual tipo de remoção causou mais dano à estrutura?
- **Diagnóstico de Vulnerabilidade**: Os nós que “derrubaram” as redes na Etapa 3 são os mesmos que compunham o núcleo na Etapa 2? Discutam se a topologia das redes as torna “robustas mas frágeis”.
- **Comparação entre Domínios**: Como a natureza das redes (ex: social vs. biológica) influenciou os resultados de *assortatividade* e a resistência aos ataques direcionados?

# FORMA DE ENVIO:

- Relatório em PDF e Script contendo o código (comentado).

# REFERÊNCIAS

CSARDI, Gabor; NEPUSZ, Tamas. The igraph software package for complex network research. InterJournal, Complex Systems, v. 1695, n. 5, p. 1-9, 2006. Disponível em: <https://igraph.org>
