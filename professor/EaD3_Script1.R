
#' Este script acompanha o "Exercício 3", carregando no RStudio 
#' sugestões de dados indicados na tarefa EaD3, juntamente com 
#' sugestões de análise.

#############################################################
### Script Mínimo: Decomposição K-core
#############################################################
library(igraph)
library(RGraphSpace)
library(ggplot2)

#-----------------------------------------------
# Exemplo de redes para teste:
#-----------------------------------------------

# A social network of friendships 
g <- make_graph("Zachary")

# Random graph using preferential attachment
g <- sample_pa(100)

# Small-world model
g <- sample_smallworld(1, 100, 1, 1)

# Random graph according Erdős-Rényi model
g <- sample_gnm(100, 500)

g$name

#-----------------------------------------------
# --- CÁLCULO DE MÉTRICAS ---
#-----------------------------------------------

# Calcular o 'coreness' de cada nó: O  k-core de um grafo é 
# o maior subgrafo no qual cada vértice tem grau pelo menos k
v_coreness <- coreness(g)

# Identificar o valor do K-core máximo (o "núcleo" da rede)
k_max_val <- max(v_coreness)
cat("O valor do K-core máximo desta rede é:", k_max_val, "\n")

# Filtrar os nós que pertencem ao K-core máximo
nodes_in_core <- V(g)[v_coreness == k_max_val]
cat("Número de nós no núcleo máximo:", length(nodes_in_core), "\n")

# Cálcular Betweenness (INTERMEDIAÇÃO)
# O Betweenness mede quantas vezes um nó está no caminho mais 
# curto entre outros dois. É a métrica ideal para identificar 
# "pontes" e gargalos na rede.
v_betweenness <- betweenness(g, directed = FALSE)

#-----------------------------------------------
# Adicionar variáveis no objeto igraph
V(g)$coreness <- v_coreness
V(g)$betweenness <- v_betweenness

#-----------------------------------------------
# --- VISUALIZAÇÃO COM GGPLOT2 + RGRAPHSPACE ---
#-----------------------------------------------

# Criar o espaço do grafo com layout de força (Fruchterman-Reingold)
gs <- GraphSpace(g, layout = layout_with_fr(g))

# Plotagem customizada
ggplot() +
    geom_edgespace(data = gs) +
    geom_nodespace(mapping = aes(fill = coreness, size = betweenness),
        data = gs) +
    scale_fill_viridis_c() +
    scale_size(range = c(2, 10)) +
    theme_gspace_coords() +
    labs(title = g$name, 
      subtitle = paste("K-max identificado:", k_max_val))

#-----------------------------------------------
# --- VISUALIZAÇÃO COM O REDER
#-----------------------------------------------

library(RedeR)
library(viridisLite)

# Inicializa a interface R-Java
startRedeR()
resetRedeR()

# Define o tamanho dos nodos proporcionalmente ao betweenness
# (escala relativa, ajustar visualmente)
V(g)$nodeSize <- (rank(V(g)$betweenness)/5)

# Define a cor dos nodos com base no coreness
x <- V(g)$coreness
V(g)$nodeColor <- viridisLite::viridis(max(x))[x]

# Plota o grafo no RedeR
addGraphToRedeR(g=g)

# Ajusta o layout da rede (relaxamento padrão)
relaxRedeR(p1=100, p2=100, p3=100, p4=100, p5=100)

# Ajusta o layout da rede (relaxamento reduzido)
relaxRedeR(p1=50, p2=50, p3=50, p4=50, p5=50)

# Experimente deletar alguns nodos centrais e observe 
# o que ocorre com a rede!
