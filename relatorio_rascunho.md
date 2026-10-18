# Robustez, resiliência e hierarquia em redes complexas

> **Rascunho para o Google Docs.** Preencher a identificação e substituir as
> indicações de figuras pelas imagens. O texto foi organizado para um relatório
> de 3 a 5 páginas, mas o total deve ser conferido após a formatação. Remover
> esta nota da versão de entrega.

## 1. Identificação do Grupo

**Instituição:** Universidade Federal do Paraná — UFPR  
**Disciplina:** Biologia Computacional  
**Integrantes:** [Nome 1]; [Nome 2, se houver]; [Nome 3, se houver]  
**Turma:** [Preencher]  
**Data:** [Preencher]

## 2. Introdução

Analisamos dois conjuntos de dados: um recorte de amizades do Facebook,
disponível no SNAP [2], e a Western US Power Grid, uma rede de infraestrutura
elétrica disponível no Network Repository [3, 4]. O objetivo é comparar sua
resistência à remoção de nós e o papel dos núcleos mais densos.

Nós representam usuários ou pontos da infraestrutura; arestas são suas
ligações. Ambas as redes são não direcionadas e inicialmente conectadas.
Usamos Python com igraph [1] e os exemplos do professor [5]. Aplicamos a
simplificação para eliminar ligações repetidas e de um nó consigo mesmo,
preservando os IDs originais. As duas redes atendem à faixa recomendada
de 2.000 a 10.000 nós.

**Tabela 1 — Caracterização das redes antes das remoções.**

| Rede | Nós | Arestas | Densidade (%) | Diâmetro | Transitividade global |
| --- | ---: | ---: | ---: | ---: | ---: |
| Facebook | 4.039 | 88.234 | 1,0820 | 8 | 0,519174 |
| Power Grid | 4.941 | 6.594 | 0,0540 | 46 | 0,103153 |

Densidade é a parcela das ligações possíveis que existe; diâmetro é a maior
distância mínima entre dois nós. A transitividade mede com que frequência
dois vizinhos de um nó também estão ligados. O Facebook tem maior densidade
e fechamento de triângulos; o Power Grid tem caminhos mais longos.

## 3. Decomposição de Redes

Um k-core é o maior subgrafo em que cada nó tem pelo menos `k` ligações
internas. Coreness é o maior `k` para o qual um nó permanece em um k-core;
k-max é o maior coreness da rede. Seus nós formam o núcleo máximo.

**Tabela 2 — Núcleos máximos e assortatividade das redes originais.**

| Rede | k-max | Nós no núcleo | Densidade do núcleo (%) | Assortatividade |
| --- | ---: | ---: | ---: | ---: |
| Facebook | 115 | 158 | 89,85 | 0,063577 |
| Power Grid | 5 | 12 | 54,55 | 0,003457 |

O grau relativo divide o número de ligações de um nó dentro do núcleo por
`n-1`, o máximo de vizinhos possíveis nesse núcleo. A tabela apresenta os
cinco maiores valores; empates seguem a ordem dos IDs como texto.

**Tabela 3 — Cinco nós de maior grau relativo em cada núcleo máximo.**

| Facebook: ID | Grau interno | Grau relativo | Power Grid: ID | Grau interno | Grau relativo |
| --- | ---: | ---: | --- | ---: | ---: |
| 1912 | 157 | 1,0000 | 4353 | 7 | 0,6364 |
| 2206 | 157 | 1,0000 | 4382 | 7 | 0,6364 |
| 2340 | 157 | 1,0000 | 4403 | 7 | 0,6364 |
| 2507 | 157 | 1,0000 | 4333 | 6 | 0,5455 |
| 2088 | 156 | 0,9936 | 4385 | 6 | 0,5455 |

> **Inserir Figura 1 — Dois painéis lado a lado:**
> [Facebook](output/graficos/facebook_kcore.png) e
> [Power Grid](output/graficos/power_grid_kcore.png).
>
> **Legenda:** redes originais coloridas pelo coreness. O contorno destaca
> o núcleo máximo; o tamanho dos nós acompanha sua intermediação.

O catálogo do Power Grid [4] informa k-max 6, mas o arquivo utilizado produz 5.
A conferência por remoção sucessiva de nós de grau menor que `k` confirmou
que o 6-core é vazio; usamos o valor calculado no arquivo.

## 4. Simulação e Análise de Resiliência

Em cada rede, removemos dez nós, um por vez. No ataque, a ordem foi definida
pela intermediação (betweenness) calculada exatamente na rede original e
mantida durante todo o experimento. Ela mede a participação do nó nos
caminhos mais curtos entre outros nós.

Nas falhas, sorteamos dez nós diferentes e repetimos o processo cinco vezes,
sempre recomeçando na rede original. Usamos a semente 123 no Python e a
média dos resultados de cada passo. Registramos também o passo inicial.

A LCC é o maior grupo em que qualquer nó consegue alcançar os demais por
algum caminho. Após cada remoção, medimos seu tamanho, o caminho médio entre
pares ainda alcançáveis na rede inteira e, separadamente, o caminho médio
apenas na LCC. Pares sem caminho foram ignorados, como no script R. Também
acompanhamos as mudanças do núcleo máximo.

**Tabela 4 — Resultados após dez remoções.**

| Rede e estratégia | LCC final (nós) | Redução da LCC (%) | Caminho médio na rede | Caminho médio na LCC |
| --- | ---: | ---: | ---: | ---: |
| Facebook — ataque | 3.220 | 20,2773 | 4,842 | 4,889 |
| Facebook — falha média | 4.029 | 0,2476 | 3,693 | 3,693 |
| Power Grid — ataque | 4.930 | 0,2226 | 24,594 | 24,594 |
| Power Grid — falha média | 4.928 | 0,2631 | 19,054 | 19,054 |

Os valores estão arredondados. As linhas de falha mostram médias das cinco
repetições. A redução usa a LCC inicial como referência e inclui tanto os
nós removidos quanto os que se separaram do maior grupo. Nas figuras,
a LCC é dividida pelo total original de nós.

> **Inserir Figura 2:**
> [Comparação da LCC](output/graficos/comparativo_lcc_frac.png).
>
> **Legenda:** tamanho da maior componente em relação ao número original
> de nós, comparando ataque e média das falhas nas duas redes.

> **Inserir Figura 3:**
> [Comparação do caminho médio](output/graficos/comparativo_apl.png).
>
> **Legenda:** caminho médio entre pares alcançáveis na rede inteira,
> comparando ataque e média das falhas.

## 5. Comparação e Diagnóstico Estrutural

O ataque fragmentou mais o Facebook: a LCC terminou com 79,72% dos nós
originais, contra 99,75% nas falhas. Seu caminho médio subiu de 3,693 para
5,973 no passo 6 (+61,76%), antes das maiores quedas da LCC nos passos 7 e 8.
Depois ele caiu, em parte porque pares separados deixaram de entrar na
média. Essa queda não representa recuperação da rede.

Apesar disso, o núcleo mudou pouco: k-max passou de 115 para 114 e seus
membros, de 158 para 157. Apenas `1912`, quarto alvo do ataque, estava no
núcleo original. Os 157 sobreviventes continuaram na LCC, enquanto 809
outros nós restantes ficaram fora dela. Nenhuma falha sorteada atingiu o
núcleo. Preservar esse grupo denso não bastou para manter toda a rede unida.

No Power Grid, as perdas da LCC foram 0,2226% no ataque e 0,2631% nas falhas.
Mesmo com pouca fragmentação, o caminho médio do ataque aumentou de 18,989
para 24,594 (+29,51%); nas falhas, terminou em 19,054. Ao final do ataque,
apenas um nó restante ficou isolado. Nenhuma remoção atingiu o núcleo
original, que manteve k-max 5 e 12 membros.

O núcleo do Facebook era mais denso (89,85% contra 54,55%), mas a rede sofreu
maior fragmentação no ataque. Isso sugere a importância das conexões entre
grupos, além das ligações internas. A assortatividade mede se nós ligados
tendem a ter graus parecidos: a tendência foi fraca no Facebook (0,063577)
e quase nula no Power Grid (0,003457). O recorte social tem maior fechamento
de triângulos; a infraestrutura tem menor densidade e caminhos mais longos.
Uma rede de cada domínio não permite atribuir essas diferenças ao domínio
nem generalizar os resultados.

## 6. Conclusão

O Facebook resistiu às falhas sorteadas e mostrou maior fragilidade à
fragmentação no ataque. No Power Grid, o ataque aumentou as distâncias sem
separar a maior parte dos nós. Nenhuma rede sofreu colapso total, portanto
não identificamos um ponto de colapso.

As redes têm caminhos alternativos, mas um núcleo denso não garante
redundância entre todas as partes. As conclusões se limitam às dez remoções
e às cinco repetições. Na rede elétrica, estudamos apenas as conexões;
não modelamos fluxo de energia, sobrecarga ou apagões.

## 7. Referências Bibliográficas

1. CSARDI, Gabor; NEPUSZ, Tamas. **The igraph software package for complex
   network research**. InterJournal, Complex Systems, artigo 1695, 2006.
   Disponível em: [igraph](https://igraph.org).
2. MCAULEY, Julian; LESKOVEC, Jure. **Learning to Discover Social Circles in
   Ego Networks**. NIPS, 2012. Dados disponíveis em:
   [SNAP — Social circles: Facebook](https://snap.stanford.edu/data/ego-Facebook.html).
3. WATTS, Duncan J.; STROGATZ, Steven H. **Collective dynamics of small-world
   networks**. Nature, v. 393, p. 440–442, 1998.
   DOI: [10.1038/30918](https://doi.org/10.1038/30918).
4. ROSSI, Ryan A.; AHMED, Nesreen K. **The Network Data Repository with
   Interactive Graph Analytics and Visualization**. AAAI, 2015. Dados disponíveis
   em: [Network Repository — inf-power](https://networkrepository.com/inf-power.php).
5. MATERIAL DA DISCIPLINA. **EaD3_Script1.R e EaD3_Script2.R**. Scripts
   fornecidos pelo professor para o Exercício 3, disponíveis em `professor/`.
