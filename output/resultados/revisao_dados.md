# Revisão dos resultados

## Termos usados

Uma **rede** tem nós (itens como pessoas ou estações) e arestas (ligações entre
os nós). O **grau** de um nó é o número de ligações que ele tem. Um **k-core**
é o maior subgrafo em que cada nó tem pelo menos `k` ligações com outros nós do
mesmo subgrafo. O **coreness** de um nó é o maior valor `k` para o qual ele
permanece em um k-core. **k-max** é o maior coreness da rede, e seus nós formam
o núcleo máximo.

A **LCC** (*Largest Connected Component*) é a maior parte da rede em que cada
par de nós continua ligado por algum caminho. O **caminho médio** é a média das
distâncias mais curtas entre pares conectados. `apl` considera todos os pares
que ainda são alcançáveis na rede; `apl_lcc` considera apenas os nós da LCC.
Por isso, `apl` pode cair depois de uma fragmentação: os pares que ficaram
separados deixam de entrar na média.

**Betweenness**, ou intermediação, mede a participação de um nó nos caminhos
mais curtos entre pares. Se houver caminhos igualmente curtos, a participação
é dividida entre eles. **Assortatividade de grau** mede se nós conectados
tendem a ter graus parecidos. Valores próximos de zero indicam pouca relação
entre os graus; não explicam por que essa relação ocorre.

## O que aconteceu com o núcleo do Facebook

| Trajetória | Passos | k-max | Nós no núcleo máximo |
| --- | --- | ---: | ---: |
| Ataque direcionado | 0 a 3 | 115 | 158 |
| Ataque direcionado | 4 a 10 | 114 | 157 |
| Cada uma das cinco falhas aleatórias | 0 a 10 | 115 | 158 |

O ataque remove os dez nós com maior betweenness calculada antes das remoções.
Só `1912` desses dez estava no núcleo máximo original. Ele foi removido no
passo 4. Antes da remoção, seu grau total era 755 e ele se ligava aos outros
157 membros do núcleo. O menor grau dentro do núcleo era 115, sem margem acima
de k-max. Depois da remoção, o 115-core fica vazio; os 157 sobreviventes formam
o novo núcleo máximo, com k-max 114 e grau interno mínimo 114. Assim, o k-max
cai uma unidade e o tamanho do núcleo cai de 158 para 157.

Nas cinco falhas aleatórias, nenhuma repetição removeu um nó do núcleo original.
Por isso, as ligações entre seus 158 membros foram preservadas e k-max e
tamanho do núcleo ficaram em 115 e 158 em todos os passos. Isso não quer dizer
que o coreness de todos os outros nós ficou igual.

O núcleo tinha 158 dos 4.039 nós da rede (3,91%). Se cada repetição escolhe dez
nós uniformemente, a chance de nenhuma das cinco repetições atingir o núcleo é
cerca de 13,57%. Portanto, o resultado observado é possível; a semente 123 fixa
quais nós foram sorteados.

O caminho médio `apl` começa em 3,692507 e chega ao pico de 5,972941 no passo 6,
um aumento de 61,76%. As maiores quedas da LCC vêm depois: ela perde 198 nós
entre os passos 6 e 7, e mais 540 entre os passos 7 e 8. A partir daí, `apl`
cai, em parte porque pares separados deixam de entrar no cálculo. Essa queda não
significa que a rede voltou a melhorar.

Ao final do ataque, a LCC tem 3.220 nós e 809 nós restantes estão fora dela.
Os 157 sobreviventes do núcleo original são exatamente o núcleo máximo final e
continuam todos na LCC. Portanto, o núcleo denso ficou quase intacto enquanto
outras partes da rede se separaram. Isso mostra que um núcleo preservado não
garante que toda a rede permaneça conectada.

## O que aconteceu com o Power Grid

O núcleo máximo do Power Grid tem k-max 5, 12 nós e densidade 0,545455. Nenhum
dos dez alvos do ataque nem dos nós das cinco falhas aleatórias estava nesse
núcleo. Seus 12 nós e suas ligações internas permaneceram iguais em todas as
trajetórias.

No ataque, a LCC termina com 4.930 nós de 4.941 originais: não houve colapso
total. O caminho médio na LCC (`apl_lcc`) passa de 18,989 para 24,594 ao final,
um aumento de 29,51%. A redução da LCC é 0,2226%; nas falhas aleatórias, a
redução média é 0,2631%. Neste recorte, a falha aleatória teve uma perda um
pouco maior da LCC, embora o caminho médio aumente mais no ataque.

## Domínio e assortatividade

O Facebook representa uma rede social e o Power Grid, uma infraestrutura
elétrica. A assortatividade de grau é 0,063577 no Facebook e 0,003457 no Power
Grid: ambos os valores são pequenos e positivos, e o valor do Power Grid é mais
próximo de zero. Isso descreve os dois arquivos analisados. Como há uma rede de
cada domínio, não permite concluir que o tipo de domínio causou a diferença.

A densidade do núcleo do Facebook (0,898492) é maior que a do núcleo do Power
Grid (0,545455). Mesmo assim, a rede social perdeu mais conectividade global no
ataque: a densidade de um núcleo e o tamanho da LCC medem partes diferentes da
estrutura. Os resultados não mostram colapso total em nenhuma das redes após
dez remoções.

O catálogo do Network Repository informa k-core máximo 6 para o Power Grid.
No arquivo oficial baixado, `igraph.coreness()` retorna 5. Uma verificação
independente por remoção sucessiva de nós com grau menor que `k` confirmou que
o 5-core tem 12 nós e que o 6-core está vazio; por isso, os CSVs registram 5.

## Conferências realizadas

- Os dois arquivos oficiais e seus hashes SHA-256 (resumos que ajudam a
  identificar os arquivos) conferem com `data/fontes.json`.
- Nós, arestas, orientação, densidade, diâmetro e transitividade foram
  recalculados.
- Os graus e coreness dos 8.980 nós conferem com `metricas_nos.csv`.
- Densidade, assortatividade e os cinco maiores graus internos foram
  conferidos, incluindo IDs e graus relativos.
- Os 132 estados das trajetórias foram reconstruídos a partir dos IDs removidos.
  k-max e tamanho do núcleo conferem em todos eles.
- Uma verificação separada removeu repetidamente nós com menos de `k` ligações.
  Em cada estado, ela encontrou o mesmo núcleo de ordem k-max que o igraph e
  nenhum nó no núcleo k-max+1.
- As 44 médias foram recalculadas. A maior diferença foi `7,11 × 10⁻¹⁵`, que
  resulta do arredondamento numérico.
- As quatro linhas do diagnóstico conferem com os estados inicial e final.
- A betweenness foi recalculada sem aproximações; os 20 alvos conferem. As
  amostras aleatórias reproduzem os IDs registrados com `random.Random(123)`.
- Os 120 estados após remoções foram recalculados diretamente dos arquivos
  oficiais, sem chamar `src.simulacao`. LCC, `apl` e `apl_lcc` conferem nos
  detalhes e nas médias, com tolerância absoluta de `2 × 10⁻⁸` e relativa de
  `2 × 10⁻¹⁰`.
- Para conferir `apl`, as distâncias de cada componente foram ponderadas pelo
  número de pares possíveis. Pares inalcançáveis não entram na média, como no
  script R.
- **23 testes passaram**. A entrega tem **132 linhas detalhadas**, **44 médias**,
  **20 alvos**, **17 PNGs** e **9 CSVs**.

Não foram encontradas diferenças nos itens conferidos. Se os únicos nós fora
da LCC forem isolados, `apl` e `apl_lcc` podem ter o mesmo valor: esses nós não
acrescentam pares alcançáveis às distâncias.

## Figuras

A escala comum entre redes escondia a queda de uma unidade no k-max do
Facebook. Os gráficos individuais de k-max e de tamanho do núcleo têm dois
painéis: um mantém a escala comum e o outro amplia o eixo vertical. As legendas
mostram os valores inicial e final. A linha tracejada facilita ver onde a média
das falhas aleatórias coincide com o ataque.

A redação e o PDF final, de 3 a 5 páginas, ficam para a etapa posterior. Esta
revisão não preenche identificação nem nomes de grupo.

## Referência

CSARDI, Gabor; NEPUSZ, Tamas. The igraph software package for complex network research. InterJournal, Complex Systems, v. 1695, n. 5, p. 1-9, 2006. Disponível em: <https://igraph.org>
