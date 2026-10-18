# Exercício 3 — Redes complexas (UFPR)

Este projeto compara duas redes reais com python-igraph. Uma rede é formada por
**nós** (as pessoas ou estações estudadas) e **arestas** (as ligações entre
elas). O código segue os dois scripts R do professor, guardados em `professor/`.

## Termos usados

Um subgrafo é uma parte de uma rede.

- **Grau:** número de ligações de um nó.
- **Maior componente conectada (LCC):** maior grupo de nós em que qualquer par
  pode ser ligado por um caminho. A sigla vem do inglês *Largest Connected
  Component*.
- **K-core e coreness:** um k-core é o maior subgrafo em que cada nó tem pelo
  menos `k` ligações com outros nós desse mesmo subgrafo. O coreness de um nó é
  o maior valor de `k` para o qual ele permanece em um k-core. **k-max** é o
  maior coreness da rede; os nós com esse valor formam o núcleo máximo.
- **Betweenness (intermediação):** mede a participação de um nó nos caminhos
  mais curtos entre pares. Se houver vários caminhos igualmente curtos, a
  participação é dividida entre eles. O ataque remove primeiro os nós com os
  maiores valores dessa medida.
- **Assortatividade de grau:** mede se nós ligados tendem a ter graus parecidos.
  Um valor perto de zero indica pouca relação; um valor positivo indica que
  nós ligados tendem a ter graus mais parecidos. Um valor negativo indica
  tendência de ligação entre nós de graus diferentes.
- **Caminho médio:** média das distâncias mais curtas entre pares conectados.
  `apl` considera todos os pares que continuam conectados na rede; `apl_lcc`
  considera somente os nós da LCC.

## Instalação e execução

Use Python 3.9 ou superior e execute os comandos na raiz de `exercicio3`.
As versões diretas das dependências estão fixadas em `requirements.txt`.

Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m notebook notebooks/analise_redes.ipynb
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m notebook notebooks/analise_redes.ipynb
```

No VS Code, abra `notebooks/analise_redes.ipynb`, escolha o interpretador da
`.venv` como kernel e execute as células na ordem. O notebook funciona com o
diretório de trabalho na raiz do exercício ou dentro de `notebooks/`.

Para executar sem abrir a interface do Jupyter, com a `.venv` ativa:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/analise_redes.ipynb --ExecutePreprocessor.timeout=900
python -m pytest -q
```

Os cálculos são exatos. O cálculo dos caminhos e as simulações podem levar alguns
minutos. Cada execução calcula as medidas da rede original uma vez, guarda-as nos
nós e salva os resultados em CSV. Executar todas as células novamente refaz a
análise e substitui os resultados anteriores.

## Dados e método

- **Facebook**, uma rede social: [SNAP](https://snap.stanford.edu/data/ego-Facebook.html),
  arquivo `data/facebook_combined.txt.gz`. O arquivo contém uma lista de ligações;
  os IDs começam em 0.
- **Western US Power Grid**, uma rede de infraestrutura elétrica:
  [Network Repository](https://networkrepository.com/inf-power.php), arquivo
  oficial `data/inf-power.zip`. Dentro dele, `inf-power.mtx` declara uma matriz
  de adjacência esparsa e simétrica; os IDs começam em 1.

O carregador baixa os arquivos que faltam. Para cada um, registra em
`data/fontes.json` a fonte, o nome e um código SHA-256 que identifica seu
conteúdo. Sem acesso à internet, coloque os arquivos oficiais nos caminhos
acima. O projeto não troca esses dados por
redes sintéticas. Os IDs originais ficam em `g.vs['name']`, inclusive depois das
remoções. Loops (ligações de um nó com ele mesmo) e ligações duplicadas são
removidos. A orientação dos dados é respeitada; uma matriz não simétrica não é
convertida silenciosamente em rede não direcionada.

Os graus variam bastante dentro de cada rede: no Facebook vão de 1 a 1.045,
com mediana 25; no Power Grid vão de 1 a 19, com mediana 2. Esses valores
descrevem os arquivos analisados e não explicam por si só como as redes se
formaram.

Na caracterização, a ordem é o número de nós. A densidade é a proporção das
ligações existentes entre todas as ligações possíveis. O diâmetro é a maior
distância mínima entre dois nós. Se uma rede tiver mais de um componente, o
diâmetro é calculado na LCC. A transitividade global mede com que frequência
dois vizinhos de um nó também estão ligados entre si. Ela considera os trios
da rede toda, sem fazer a média dos coeficientes de cada nó.

A decomposição em k-core segue o Script 1. O programa calcula o coreness de cada
nó, identifica o k-max e escolhe os cinco nós com maior grau **dentro** do
núcleo. O grau relativo divide esse grau interno por `n_kmax - 1`, o máximo de
ligações que um nó pode ter com os demais membros do núcleo. Empates são
resolvidos ordenando os IDs como texto: por exemplo, `10` vem antes de `2`.
A betweenness usada no ataque é calculada de forma exata na rede original
simplificada.

A simulação segue o Script 2: remove dez nós por ataque direcionado e dez nós
por falha aleatória, em cinco repetições com semente 123. O ataque mantém o
ranking calculado no início; cada falha começa de novo na rede original. Os
resultados incluem o passo 0, antes de qualquer remoção. A sequência sorteada
por `random.Random(123)` em Python não é a mesma sequência de `sample()` do R.

Há duas medidas de caminho médio, mostradas em gráficos separados:

- `apl` usa os pares que continuam conectados na rede toda, com
  `directed=False, unconn=True`, como no script do professor.
- `apl_lcc` usa somente os pares da maior componente conectada.

Como `apl` deixa de contar pares que se tornaram inalcançáveis, seu valor pode
cair depois de uma fragmentação forte. Uma queda isolada do caminho médio não
significa que a rede melhorou. O experimento testa a conectividade; para a rede
elétrica, ele não simula fluxo de energia nem uma falha elétrica real.

## Arquivos e resultados

```text
data/                     arquivos reais e fontes dos dados
professor/                scripts R originais
src/carregar_redes.py      importação e limpeza
src/metricas.py            caracterização, k-core e betweenness
src/simulacao.py           ataque fixo e falhas aleatórias
src/visualizacao.py        gráficos e exportação CSV
notebooks/analise_redes.ipynb
tests/                    testes dos módulos e da integração
output/resultados/        tabelas, métricas por nó e parâmetros
output/graficos/          PNGs das redes e da resiliência
```

O notebook cria **9 arquivos CSV** em `output/resultados/`:

```text
caracterizacao.csv
nucleos.csv
top5_nucleo.csv
metricas_nos.csv
resiliencia_detalhes.csv
resiliencia_medias.csv
resiliencia_alvos.csv
comparacao_estrutural.csv
diagnostico_resiliencia.csv
```

Também cria `parametros.json`, com a semente, as versões dos programas e as
definições dos caminhos médios. A execução registrada produziu 132 linhas de
trajetórias, 44 médias, 20 alvos e 17 imagens PNG. As figuras mostram as redes
com cor por coreness e tamanho dos nós conforme a betweenness. Um contorno marca
o núcleo máximo. Os gráficos de k-max e de tamanho do núcleo têm um painel com
escala comum entre redes e outro ampliado para mostrar mudanças pequenas.
Nos gráficos comparativos, k-max e tamanho do núcleo são divididos pelos
valores iniciais de cada rede.

### Resultados calculados

| Rede | Nós | Arestas | Densidade | Diâmetro | Transitividade global |
| --- | ---: | ---: | ---: | ---: | ---: |
| Facebook | 4.039 | 88.234 | 0,010820 | 8 | 0,519174 |
| Power Grid | 4.941 | 6.594 | 0,000540 | 46 | 0,103153 |

| Rede | k-max | Nós no núcleo máximo | Densidade do núcleo | Assortatividade |
| --- | ---: | ---: | ---: | ---: |
| Facebook | 115 | 158 | 0,898492 | 0,063577 |
| Power Grid | 5 | 12 | 0,545455 | 0,003457 |

Ambas as redes originais são conectadas. O núcleo máximo do Facebook tem
k-max e densidade maiores que o do Power Grid. A assortatividade é positiva e
pequena nas duas redes, mais próxima de zero no Power Grid. Estes valores
resumem uma rede de cada domínio; eles não mostram que o domínio, por si só,
causou essas diferenças.

O catálogo do Network Repository informa k-core máximo 6 para o Power Grid.
No arquivo oficial baixado, `igraph.coreness()` retorna **5** e o 6-core fica
vazio quando conferido por remoção iterativa. Os resultados deste projeto usam
o valor calculado no arquivo registrado em `data/fontes.json`.

Depois de dez remoções, a redução da LCC foi:

| Rede | Ataque direcionado | Média das falhas aleatórias | Alvos do ataque no núcleo original |
| --- | ---: | ---: | ---: |
| Facebook | 20,2773% | 0,2476% | 1 de 10 |
| Power Grid | 0,2226% | 0,2631% | 0 de 10 |

O Facebook sofreu uma separação global maior no ataque, mas não entrou em
colapso total: a LCC final tem 3.220 nós, e os 157 sobreviventes do núcleo
original continuam nela. O caminho médio `apl` do Facebook começa em 3,692507,
atinge o pico de 5,972941 no passo 6 (+61,76%) e cai depois das maiores perdas
da LCC: 198 nós entre os passos 6 e 7, e 540 entre os passos 7 e 8.

No Power Grid, a LCC final do ataque tem 4.930 nós; também não houve colapso
total. O caminho médio na LCC (`apl_lcc`) passa de 18,989 para 24,594 no passo
10 (+29,51%). Neste recorte, a falha aleatória reduz a LCC um pouco mais, em
média, que o ataque.
Por isso, a comparação entre estratégias depende da rede e da medida usada.

A densidade maior do núcleo do Facebook não impediu a fragmentação de outras
partes da rede. O núcleo pode continuar conectado enquanto nós de fora dele se
separam. O experimento mostra esse resultado nestes dados; não prova uma regra
para todas as redes sociais ou de infraestrutura.

## Testes e entrega do relatório

Os **23 testes passaram**, incluindo os dois arquivos reais. O notebook foi
executado do início ao fim no Linux, com Python 3.9.0: oito células de código,
sem erros. O `pip check` não encontrou incompatibilidades. Os avisos emitidos
pelo Matplotlib e pelo pyparsing não impediram a execução. Os comandos de
Windows estão disponíveis acima, mas a execução foi conferida somente no Linux.

As figuras e tabelas servem de base para o relatório do exercício. O relatório
final deve ter de 3 a 5 páginas, ser entregue em PDF e conter identificação do
grupo, introdução, decomposição de redes, simulação e análise de resiliência,
comparação e diagnóstico estrutural, conclusão e referências. O PDF fica para
uma etapa posterior; nenhum nome de grupo foi preenchido nesta entrega.

O texto inicial está em [relatorio_rascunho.md](relatorio_rascunho.md), com
as sete seções do enunciado e a indicação das figuras para usar no Google Docs.

## Divisão do trabalho

Dois agentes Luna, ambos com raciocínio XHIGH, e o agente principal trabalharam
no projeto. Um agente cuidou dos datasets, das métricas e dos testes; o outro,
das simulações, dos gráficos, das tabelas e dos testes. O principal integrou o
trabalho, preparou o notebook e a documentação e conferiu os resultados finais.

## Referências

- CSARDI, Gabor; NEPUSZ, Tamas. The igraph software package for complex network research. InterJournal, Complex Systems, v. 1695, n. 5, p. 1-9, 2006. Disponível em: <https://igraph.org>
- Scripts do professor: `professor/EaD3_Script1.R` e `professor/EaD3_Script2.R`.
- McAuley, J.; Leskovec, J. *Learning to Discover Social Circles in Ego Networks*.
  NIPS, 2012. [SNAP](https://snap.stanford.edu/data/ego-Facebook.html).
- Watts, D. J.; Strogatz, S. H. *Collective dynamics of small-world networks*.
  Nature, 393, 440–442, 1998.
- Rossi, R. A.; Ahmed, N. K. *The Network Data Repository with Interactive Graph
  Analytics and Visualization*. AAAI, 2015.
  [Network Repository](https://networkrepository.com/inf-power.php).
