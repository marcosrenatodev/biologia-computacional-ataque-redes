# Revisão dos dados gerados

## Facebook: por que o núcleo quase não muda?

| Trajetória | Passos | k-max | Nós no núcleo máximo |
| --- | --- | ---: | ---: |
| Ataque direcionado | 0 a 3 | 115 | 158 |
| Ataque direcionado | 4 a 10 | 114 | 157 |
| Cada uma das cinco falhas aleatórias | 0 a 10 | 115 | 158 |

O ataque usa os dez maiores valores de **betweenness inicial**, seguindo o
Script 2. Só um desses alvos, `1912`, pertence ao núcleo máximo original.
Ele é removido no passo 4. Antes da exclusão, ligava-se aos outros 157 membros
do núcleo; o grau interno mínimo desse subgrafo era 115. Após a exclusão,
o grau interno mínimo passa a 114. O 115-core fica vazio e os 157 sobreviventes
formam o novo núcleo máximo, de ordem 114.

Nas falhas aleatórias, **nenhuma das cinco amostras de dez vértices atingiu
o núcleo original**. Assim, suas arestas internas foram preservadas e o
115-core continuou com os mesmos 158 membros em todas as repetições. A
constância ocorre em cada repetição, antes de calcular a média.

Como referência matemática, o núcleo contém 158/4.039 = 3,91% dos vértices.
Em cinco amostras independentes, cada uma com dez sorteios sem reposição,
a probabilidade de não atingir esse conjunto é
`[C(3881, 10) / C(4039, 10)]^5 ≈ 13,57%`. Portanto, o resultado observado
é compatível com o sorteio uniforme; a semente 123 fixa quais nós são removidos.

Ao final do ataque, os 157 sobreviventes do núcleo original ainda são
exatamente o núcleo máximo e estão todos na LCC de 3.220 vértices. A LCC
cai de 4.039 para 3.220 (20,28%), enquanto o núcleo denso sofre alteração
pequena. Isso mostra que estabilidade do núcleo e conectividade global
são propriedades diferentes. A constância de k-max e do tamanho do núcleo
também não afirma que o coreness dos demais vértices permaneça igual.

Um exemplo concreto é a remoção de `567`, no passo 8: a LCC cai de 3.763
para 3.223 nós, enquanto k-max continua em 114 e o núcleo mantém 157 membros.
Esse alvo tinha coreness original 31 e ficava fora do núcleo máximo original.

## Power Grid

O k-max fica em 5 e o núcleo máximo mantém 12 membros em todas as trajetórias.
Nenhum dos dez alvos de ataque nem dos nós removidos nas cinco falhas
pertence ao núcleo original. Sua estrutura interna é preservada.

O ataque termina com LCC de 4.930 nós e a falha aleatória com média de 4.928.
As reduções proporcionais são 0,2226% e 0,2631%, respectivamente. Neste recorte,
a perda média de LCC nas falhas é ligeiramente maior. Já o ataque aumenta
o caminho médio na LCC de 18,989 para 24,594: a comparação entre estratégias
depende do indicador. Dez remoções correspondem a cerca de 0,20% dessa rede.

## Conferências realizadas

- SHA-256 dos dois arquivos originais conferido com `data/fontes.json`.
- Caracterização recalculada: nós, arestas, orientação, densidade, diâmetro,
  transitividade global, componentes e tamanho da LCC.
- Graus e coreness dos 8.980 vértices conferidos com `metricas_nos.csv`.
- Densidade dos núcleos, assortatividade e os cinco maiores graus internos
  conferidos, incluindo IDs, desempates e graus relativos.
- Cada um dos 132 estados foi reconstruído pelas remoções registradas.
  K-max e tamanho do núcleo coincidiram com os CSVs.
- Em todos os estados, uma segunda validação por **remoção iterativa dos
  vértices com grau menor que k** confirmou o conjunto do núcleo em k-max
  e que o núcleo de ordem k-max + 1 é vazio. Essa verificação não chama
  `igraph.coreness()`.
- As 44 médias foram recalculadas a partir das trajetórias. A maior diferença
  numérica foi `7,11 × 10⁻¹⁵`, compatível com arredondamento de ponto flutuante.
- As quatro linhas do diagnóstico conferem com os estados inicial e final,
  incluindo a normalização da LCC e os nós remanescentes fora dela.
- A betweenness inicial foi recalculada exatamente, sem aproximações, para
  verificar o ranking e os atributos dos 20 alvos. As amostras aleatórias
  foram reproduzidas com `random.Random(123)` e conferem com os IDs registrados.
- Os 120 estados após remoções foram recalculados diretamente das fontes,
  sem chamar `src.simulacao`; os dois estados iniciais foram calculados uma
  vez por rede e reutilizados nas repetições. As 132 linhas detalhadas e as
  44 médias conferem, incluindo LCC, `apl` e `apl_lcc`, com tolerância absoluta
  `2 × 10⁻⁸` e relativa `2 × 10⁻¹⁰`.
- Para conferir `apl` de maneira independente, os caminhos médios exatos de
  cada componente foram ponderados pelo número de pares `n(n-1)/2`.
  Os pares inalcançáveis não entram no denominador, como no script R.
- **23 testes passaram**, incluindo dois testes novos para assegurar que
  mudanças de uma unidade no núcleo apareçam nos gráficos ampliados.

Não foram detectadas divergências nos itens conferidos. Quando uma rede
desconectada tem apenas vértices isolados fora da LCC, `apl` e `apl_lcc`
podem ser iguais: os isolados não acrescentam pares alcançáveis. A igualdade
dessas duas colunas, nesses estados, é coerente com suas definições.

## Ajuste dos gráficos

A escala comum às redes comprimia a queda de 115 para 114 e de 158 para 157.
Os gráficos individuais de k-max e tamanho do núcleo agora têm dois painéis:
à esquerda, a escala comum; à direita, o eixo Y ampliado da própria rede.
As legendas informam os valores inicial e final. Curvas aleatórias usam linha
tracejada para facilitar a leitura quando coincidem com o ataque.

Os dados numéricos dos CSVs foram preservados. O notebook e o README receberam
a explicação estrutural e referências às figuras atualizadas.
