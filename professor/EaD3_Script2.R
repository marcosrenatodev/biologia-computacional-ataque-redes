#' Este script acompanha o "Exercício 3", carregando no RStudio 
#' sugestões de dados indicados na tarefa EaD3, juntamente com 
#' sugestões de análise.

#############################################################
### Escolha uma rede!
#############################################################
library(igraph)
library(RGraphSpace)
library(ggplot2)

# A social network of friendships 
g <- make_graph("Zachary")

# Random graph using preferential attachment
g <- sample_pa(100)

# Small-world model
g <- sample_smallworld(1, 100, 1, 1)

# Random graph according Erdős-Rényi model
g <- sample_gnm(100, 500)

g$name

#############################################################
### Análise de resiliência
#############################################################

#-----------------------------------------------
# PASSO 0: PREPARAÇÃO DA REDE
#-----------------------------------------------

# A simulação usa uma rede simples
g <- simplify(g)   # remove loops e arestas múltiplas

# Cada vez que um nó é removido, o igraph renumera os nós restantes.
# Por isso damos um NOME fixo a cada nó, para saber quem foi removido.
V(g)$name <- as.character(1:vcount(g))

# Recalcular as métricas na rede já simplificada
V(g)$coreness <- coreness(g)
V(g)$betweenness <- betweenness(g, directed = FALSE)
k_max_val <- max(V(g)$coreness)

# Parâmetros do experimento
n_remover  <- 10          # quantos nós remover
n_rep <- 5                # repetições da falha aleatória
n_original <- vcount(g)   # tamanho original da rede
set.seed(123)             # para os sorteios serem reproduzíveis

# Tabela vazia onde vamos guardar TODOS os resultados
resultados <- data.frame()

#-----------------------------------------------
# PASSO 1: ATAQUE DIRECIONADO (maior betweenness)
#-----------------------------------------------

# Ordenar os nós do maior para o menor betweenness
# e pegar os nomes dos 10 primeiros
ordem <- order(V(g)$betweenness, decreasing = TRUE)
alvos <- V(g)$name[ordem[1:n_remover]]
cat("Nós que serão atacados:", alvos, "\n")

# Começamos com uma cópia da rede original
g_atual <- g

# Guardar a situação ANTES de qualquer remoção (passo 0)
cores <- coreness(g_atual)
resultados <- rbind(resultados, data.frame(
  estrategia = "Ataque direcionado",
  repeticao = 1, passo = 0,
  lcc = max(components(g_atual)$csize),           # tamanho da LCC
  apl = mean_distance(g_atual, directed = FALSE), # caminho médio
  kmax = max(cores),                              # valor do k-core máximo
  n_kmax = sum(cores == max(cores))               # nós no k-core máximo
))

# Remover os alvos um a um
for (i in 1:n_remover) {
  g_atual <- delete_vertices(g_atual, alvos[i])
  # mede a rede que sobrou
  tamanho_lcc  <- max(components(g_atual)$csize)
  caminho_medio <- mean_distance(g_atual, directed = FALSE)
  cores <- coreness(g_atual)
  # guarda o resultado em uma nova linha da tabela
  resultados <- rbind(resultados, data.frame(
    estrategia = "Ataque direcionado",
    repeticao = 1, passo = i,
    lcc = tamanho_lcc,
    apl = caminho_medio,
    kmax = max(cores),
    n_kmax = sum(cores == max(cores))
  ))
}

#-----------------------------------------------
# PASSO 2: FALHA ALEATÓRIA (repetida 5 vezes)
#-----------------------------------------------

for (r in 1:n_rep) {
  # sortear 10 nós quaisquer
  sorteados <- sample(V(g)$name, n_remover)
  # recomeçar sempre da rede original
  g_atual <- g
  # situação antes das remoções (passo 0)
  cores <- coreness(g_atual)
  resultados <- rbind(resultados, data.frame(
    estrategia = "Falha aleatória",
    repeticao = r, passo = 0,
    lcc = max(components(g_atual)$csize),
    apl = mean_distance(g_atual, directed = FALSE),
    kmax = max(cores),
    n_kmax = sum(cores == max(cores))
  ))
  # remover os sorteados um a um
  for (i in 1:n_remover) {
    g_atual <- delete_vertices(g_atual, sorteados[i])
    cores <- coreness(g_atual)
    resultados <- rbind(resultados, data.frame(
      estrategia = "Falha aleatória", repeticao  = r, passo = i,
      lcc = max(components(g_atual)$csize),
      apl = mean_distance(g_atual, directed = FALSE),
      kmax = max(cores),
      n_kmax = sum(cores == max(cores))
    ))
  }
}

# LCC como fração da rede original (1 = rede inteira conectada)
resultados$lcc_frac <- resultados$lcc / n_original

# Olhar a tabela
head(resultados, 15)

#-----------------------------------------------
# MÉDIA DAS 5 REPETIÇÕES ALEATÓRIAS
# aggregate() calcula a média de lcc_frac, apl, kmax e n_kmax para
# cada passo e cada estratégia. No ataque há só 1 repetição, então
# a "média" é o próprio valor.
medias <- aggregate(cbind(lcc_frac, apl, kmax, n_kmax) ~ estrategia + passo,
  data = resultados, FUN = mean)
medias

#############################################################
### RESULTADOS
#############################################################

# Declínio da Maior Componente Conectada (LCC)
ggplot(medias, aes(x = passo, y = lcc_frac, color = estrategia)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  scale_x_continuous(breaks = 0:n_remover) +
  labs(title = g$name,
    x = "Número de nós removidos",
    y = "LCC (fração da rede original)",
    color = "Estratégia") +
  theme_bw()

# Variação do Caminho Médio
ggplot(medias, aes(x = passo, y = apl, color = estrategia)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  scale_x_continuous(breaks = 0:n_remover) +
  labs(title = g$name,
    x = "Número de nós removidos",
    y = "Caminho médio",
    color = "Estratégia") +
  theme_bw()

# Evolução do K-core máximo (k-max)
# Se o k-max cai, o "núcleo duro" da rede foi atingido.
ggplot(medias, aes(x = passo, y = kmax, color = estrategia)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  scale_x_continuous(breaks = 0:n_remover) +
  labs(title = g$name,
    x = "Número de nós removidos",
    y = "K-core máximo (k-max)",
    color = "Estratégia") +
  theme_bw()

# Tamanho do núcleo máximo (nós no k-max)
# ATENÇÃO: quando o k-max cai (ex.: de 5 para 4), o novo núcleo
# pode ser MAIOR, porque a exigência de grau ficou menor.
# Por isso, leia este gráfico junto com o do k-max.
ggplot(medias, aes(x = passo, y = n_kmax, color = estrategia)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  scale_x_continuous(breaks = 0:n_remover) +
  labs(title = g$name,
    x = "Número de nós removidos",
    y = "Nós no núcleo máximo",
    color = "Estratégia") +
  theme_bw()

#############################################################
### VISUALIZAÇÃO CORENESS x BETWEENNESS
#############################################################
gs <- GraphSpace(g, layout = layout_with_fr(g))
ggplot() +
  geom_edgespace(data = gs) +
  geom_nodespace(mapping = aes(fill = coreness, size = betweenness),
    data = gs) +
  scale_fill_viridis_c() +
  scale_size(range = c(2, 10)) +
  theme_gspace_coords() +
  labs(title = g$name,
    subtitle = paste("K-max identificado:", k_max_val))

