# Exercício 3 — Redes complexas (UFPR)

Análise de robustez, resiliência e hierarquia de duas redes reais com
python-igraph. A implementação segue os scripts R preservados em `professor/`.
Os arquivos desta atividade estão restritos a este diretório.

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

No VS Code, abra `notebooks/analise_redes.ipynb`, selecione o interpretador
da `.venv` como kernel e execute todas as células em ordem. O notebook funciona
com o diretório de trabalho na raiz do exercício ou em `notebooks/`.

Para executar sem a interface do Jupyter, com a `.venv` ativada:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/analise_redes.ipynb --ExecutePreprocessor.timeout=900
python -m pytest -q
```

Os cálculos são exatos. O cálculo de caminhos e as simulações podem levar
alguns minutos. As métricas estáticas são calculadas uma vez por execução,
reutilizadas nos módulos e salvas em CSV para consulta sem novo processamento.
Reexecutar todas as células refaz a análise e sobrescreve os resultados.

## Dados e metodologia

- **Facebook**: [SNAP](https://snap.stanford.edu/data/ego-Facebook.html),
  arquivo `data/facebook_combined.txt.gz`, lista de arestas com IDs iniciados em 0.
- **Western US Power Grid**: [Network Repository](https://networkrepository.com/inf-power.php),
  arquivo oficial `data/inf-power.zip`, contendo `inf-power.mtx`, matriz de
  adjacência esparsa simétrica com IDs iniciados em 1.

O carregador baixa arquivos ausentes e registra os arquivos efetivamente
utilizados em `data/fontes.json`. Sem acesso externo, coloque os dois arquivos
oficiais nos caminhos acima; nenhum grafo sintético substitui os datasets.
Os IDs originais ficam em `g.vs['name']`, inclusive após exclusões.
Loops e arestas múltiplas são removidos. Redes direcionadas não são convertidas
silenciosamente. O cabeçalho da matriz é respeitado, inclusive para vértices
isolados declarados no formato.

O Script 1 orienta coreness, núcleo máximo, betweenness e layout de força.
O Script 2 orienta as dez remoções, cinco falhas aleatórias e semente 123.
O ataque usa um ranking fixo de betweenness exata da rede original simplificada.
Empates usam a ordem lexicográfica dos IDs originais. Cada falha usa dez nós
distintos e reinicia na rede original. O sorteador `random.Random(123)` reproduz
a execução Python; sua sequência difere de `sample()` do R.

O passo 0 é registrado nas seis trajetórias de cada rede: são 66 registros por
rede e 22 médias por rede. A LCC normalizada é dividida pelo número original
de vértices. O coreness é recalculado após cada remoção. O diâmetro de redes
desconectadas é medido na maior componente conectada.

Há duas definições de caminho médio, apresentadas em figuras distintas:

- `apl`: média das distâncias entre pares alcançáveis de toda a rede,
  `directed=False, unconn=True`, seguindo o professor.
- `apl_lcc`: média das distâncias somente na maior componente conectada.

Um aumento no número de nós do núcleo máximo após redução de k-max não significa
melhora da resiliência. Uma redução do caminho médio pode resultar da perda de
pares alcançáveis. As dez remoções permitem avaliar este recorte do experimento;
a análise da rede elétrica considera conectividade topológica, sem modelar
fluxo de energia ou falhas elétricas reais.

## Organização e resultados

```text
data/                     datasets oficiais e proveniência
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

O notebook produz tabelas de caracterização, núcleos, cinco maiores graus internos,
métricas por nó, alvos, trajetórias detalhadas, médias e diagnóstico estrutural.
As figuras incluem as duas redes com coreness/betweenness, cinco curvas por rede
e cinco comparações entre redes, sempre separando `apl` de `apl_lcc`.
Os gráficos de k-max e quantidade de nós no núcleo são normalizados pelo estado
inicial nas comparações entre redes. Figuras equivalentes usam escalas comuns.
Nos gráficos individuais de k-max e tamanho do núcleo, um segundo painel
amplia o eixo Y da própria rede, para tornar visíveis mudanças de uma unidade.
A legenda informa os valores inicial e final; o primeiro painel preserva a
escala comum entre redes.

Os testes cobrem importação dos arquivos reais quando presentes, formatos
inválidos, métricas conhecidas, reinício das repetições, ranking fixo, IDs,
reprodutibilidade e invariantes das remoções. O notebook também verifica
contagens e invariantes nos resultados reais.

As figuras e tabelas apoiam o relatório posterior, de 3 a 5 páginas, com
identificação do grupo e capa da UFPR, a ser redigido no Google Docs.
O relatório final PDF não é gerado nesta entrega.

## Resultados estruturais calculados

| Rede | Nós | Arestas | Diâmetro | k-max | Nós no núcleo máximo | Densidade do núcleo | Assortatividade |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Facebook | 4.039 | 88.234 | 8 | 115 | 158 | 0,898492 | 0,063577 |
| Power Grid | 4.941 | 6.594 | 46 | 5 | 12 | 0,545455 | 0,003457 |

Ambas as redes originais são conectadas. O Facebook apresentou o maior k-max
e o núcleo mais denso. A assortatividade de grau é positiva e pequena nas duas
redes, especialmente próxima de zero no Power Grid.

O [catálogo do Power Grid](https://networkrepository.com/inf-power.php) informa
k-core máximo 6. Para o arquivo oficial baixado, `igraph.coreness()` calcula
**5**; os testes também verificam que o 6-core é vazio. Os resultados desta
atividade correspondem ao cálculo no arquivo identificado pelo SHA-256 em
`data/fontes.json`, sem substituir valores pelos resumos do catálogo.

Após dez remoções, os resultados foram:

| Rede | Redução proporcional da LCC — ataque | Redução proporcional da LCC — falha média | Alvos no núcleo original |
| --- | ---: | ---: | ---: |
| Facebook | 20,2773% | 0,2476% | 1/10 |
| Power Grid | 0,2226% | 0,2631% | 0/10 |

No Facebook, o ataque deixou 809 nós remanescentes fora da LCC e reduziu k-max
de 115 para 114. Nas falhas aleatórias, os remanescentes permaneceram conectados
nas cinco repetições. No Power Grid, as falhas tiveram perda média da LCC
ligeiramente maior neste recorte, enquanto o ataque elevou o caminho médio
da LCC de 18,989 para 24,594. O k-max permaneceu em 5. Portanto, a diferença
entre estratégias depende do indicador e da rede; não se presume uma conclusão
universal de fragilidade aos ataques.

## Validação da entrega

Execução realizada no Linux com Python 3.9.0 e as versões de `requirements.txt`:

- Notebook inteiro executado sequencialmente em kernel Jupyter: oito células de
  código, sem erros.
- **23 testes passaram**, incluindo os dois datasets reais e a reconstrução
  independente das 132 linhas de trajetória para conferir LCC, IDs e k-core.
- **132 registros detalhados**, **44 médias** e **20 alvos** exportados.
- **17 PNGs** gerados; as duas visualizações estruturais e o comparativo da LCC
  foram inspecionados visualmente.
- Dependências conferidas com `pip check`, sem incompatibilidades.

Os testes emitem avisos de depreciação da integração Matplotlib/pyparsing;
esses avisos não impediram a execução. Os comandos para Windows foram preparados,
mas a execução foi validada somente no Linux.

Os nove CSVs em `output/resultados/` são:

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

`parametros.json` registra a semente, os parâmetros, as definições dos caminhos
médios e as versões utilizadas. Os arquivos permanecem disponíveis no projeto;
a `.venv` e os caches estão excluídos pelo `.gitignore`.

## Revisão das curvas quase constantes

No Facebook, o ataque mantém k-max 115 e 158 nós no núcleo nos passos 0 a 3.
No passo 4, a remoção de `1912` reduz esses valores para 114 e 157; eles
permanecem assim até o passo 10. A escala comum com o Power Grid escondia
visualmente essa pequena queda; os gráficos agora incluem um painel ampliado.

Nas cinco repetições de falha aleatória do Facebook, nenhum dos dez nós
sorteados por repetição pertencia ao núcleo original. As arestas internas
desse núcleo não mudaram, explicando os valores constantes 115 e 158.
O ataque por betweenness prioriza intermediação entre caminhos; apenas um
dos dez alvos estava no núcleo máximo. Ao final, os 157 sobreviventes do
núcleo original ainda estão na LCC de 3.220 nós. Portanto, a estabilidade
do núcleo não implica estabilidade da conectividade global.

O Power Grid manteve k-max 5 e 12 nós no núcleo nas duas estratégias:
nenhuma remoção atingiu esse núcleo original. A revisão detalhada dos dados
está em [output/resultados/revisao_dados.md](output/resultados/revisao_dados.md).
A conferência independente dos caminhos médios, das amostras aleatórias e
do ranking dos alvos também não encontrou divergências nos 132 registros
e nas 44 médias.

## Divisão do trabalho

Foram utilizados exatamente dois subagentes **Luna**, com esforço de raciocínio
**XHIGH**, trabalhando simultaneamente após a definição dos contratos:

- Agente 1: leitura do Script 1, download e validação dos dados, carregadores,
  métricas estruturais, k-core, betweenness e testes correspondentes.
- Agente 2: leitura do Script 2, simulações, gráficos, exportações e testes
  correspondentes.
- Agente principal: contratos, ambiente, revisão, integração, notebook,
  documentação e validação final dos resultados e testes.

## Referências

- Scripts do professor: `professor/EaD3_Script1.R` e `professor/EaD3_Script2.R`.
- McAuley, J.; Leskovec, J. *Learning to Discover Social Circles in Ego Networks*.
  NIPS, 2012. [SNAP](https://snap.stanford.edu/data/ego-Facebook.html).
- Watts, D. J.; Strogatz, S. H. *Collective dynamics of small-world networks*.
  Nature, 393, 440–442, 1998.
- Rossi, R. A.; Ahmed, N. K. *The Network Data Repository with Interactive Graph
  Analytics and Visualization*. AAAI, 2015.
  [Network Repository](https://networkrepository.com/inf-power.php).
