"""Simula remoções de vértices em redes não direcionadas."""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Tuple

import igraph as ig
import pandas as pd


COLUNAS_DETALHES = [
    "rede",
    "estrategia",
    "repeticao",
    "passo",
    "id_removido",
    "n_vertices",
    "lcc",
    "lcc_frac",
    "apl",
    "apl_lcc",
    "kmax",
    "n_kmax",
]
COLUNAS_MEDIAS = ["rede", "estrategia", "passo", "n_vertices", "lcc", "lcc_frac", "apl", "apl_lcc", "kmax", "n_kmax"]
COLUNAS_ALVOS = ["rede", "ordem", "id_original", "betweenness", "coreness", "no_kmax_original"]
_METRICAS_MEDIA = ["n_vertices", "lcc", "lcc_frac", "apl", "apl_lcc", "kmax", "n_kmax"]


def _validar_grafo(grafo: ig.Graph) -> List[str]:
    if not isinstance(grafo, ig.Graph):
        raise TypeError("grafo deve ser um objeto igraph.Graph")
    if grafo.is_directed():
        raise ValueError("A simulação exige um grafo não direcionado")
    if not grafo.is_simple():
        raise ValueError("A simulação exige um grafo simplificado, sem loops ou arestas múltiplas")
    if "name" not in grafo.vs.attributes():
        raise ValueError("Cada vértice deve ter um ID original em g.vs['name']")
    nomes_brutos = grafo.vs["name"]
    if any(not isinstance(nome, str) for nome in nomes_brutos):
        raise ValueError("Os IDs originais em g.vs['name'] devem ser strings")
    nomes = list(nomes_brutos)
    if len(set(nomes)) != len(nomes):
        raise ValueError("Os IDs originais dos vértices devem ser únicos")
    return nomes


def _media_distancia(grafo: ig.Graph) -> float:
    """Calcula a distância média entre pares alcançáveis, como no script R."""
    if grafo.vcount() < 2:
        return math.nan
    return float(grafo.average_path_length(directed=False, unconn=True))


def _lcc(grafo: ig.Graph) -> ig.Graph:
    """Retorna a maior componente conectada; em empate, usa os IDs dos nós."""
    if grafo.vcount() == 0:
        return grafo.copy()
    componentes = grafo.connected_components()
    maior = max(len(c) for c in componentes)
    candidatos = [list(c) for c in componentes if len(c) == maior]
    if len(candidatos) == 1:
        indices = candidatos[0]
    else:
        nomes = grafo.vs["name"]
        indices = min(candidatos, key=lambda c: tuple(sorted(str(nomes[i]) for i in c)))
    return grafo.induced_subgraph(indices)


def _estado(grafo: ig.Graph, n_original: int, usar_coreness_inicial: bool = False) -> Dict[str, Any]:
    if grafo.vcount() == 0:
        lcc = 0
        apl = apl_lcc = math.nan
        kmax = n_kmax = 0
    else:
        tamanhos = grafo.connected_components().sizes()
        lcc = max(tamanhos)
        apl = _media_distancia(grafo)
        apl_lcc = apl if grafo.is_connected() else _media_distancia(_lcc(grafo))
        # O coreness muda com as remoções e é recalculado na rede atual.
        if usar_coreness_inicial and "coreness" in grafo.vs.attributes():
            cores = [int(c) for c in grafo.vs["coreness"]]
        else:
            cores = grafo.coreness()
        kmax = max(cores) if cores else 0
        n_kmax = sum(c == kmax for c in cores) if cores else 0
    return {
        "n_vertices": grafo.vcount(),
        "lcc": lcc,
        "lcc_frac": lcc / n_original if n_original else math.nan,
        "apl": apl,
        "apl_lcc": apl_lcc,
        "kmax": kmax,
        "n_kmax": n_kmax,
    }


def simular_resiliencia(
    g: ig.Graph,
    nome: str,
    n_remover: int = 10,
    n_rep: int = 5,
    semente: int = 123,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compara remoções por intermediação e falhas escolhidas ao acaso.

    O ataque segue a ordem da betweenness (intermediação) calculada uma única
    vez na rede original; empates são resolvidos pelo ID. Cada repetição aleatória
    também começa na rede original e escolhe vértices sem reposição. Um único
    ``random.Random(semente)`` é criado para a chamada e usado em sequência: o
    estado do gerador avança a cada repetição, em vez de reiniciar para cada uma.
    """
    nomes = _validar_grafo(g)
    if not isinstance(n_remover, int) or n_remover < 0:
        raise ValueError("n_remover deve ser um inteiro não negativo")
    if not isinstance(n_rep, int) or n_rep < 1:
        raise ValueError("n_rep deve ser um inteiro positivo")
    n_original = g.vcount()
    if n_remover > n_original:
        raise ValueError("n_remover não pode exceder o número de vértices")

    # As métricas entregues pelo estágio anterior são estáticas e podem ser
    # reutilizadas. Se faltarem, calculamos exatamente na rede original.
    if "betweenness" in g.vs.attributes():
        betweenness = [float(v) for v in g.vs["betweenness"]]
    else:
        betweenness = [float(v) for v in g.betweenness(directed=False)]
    if "coreness" in g.vs.attributes():
        coreness = [int(v) for v in g.vs["coreness"]]
    else:
        coreness = [int(v) for v in g.coreness()]
    kmax_original = max(coreness) if coreness else 0

    ordem_indices = sorted(range(n_original), key=lambda i: (-betweenness[i], nomes[i]))
    alvos_indices = ordem_indices[:n_remover]
    alvos_ids = [nomes[i] for i in alvos_indices]
    alvos = pd.DataFrame(
        [
            {
                "rede": nome,
                "ordem": ordem,
                "id_original": nomes[i],
                "betweenness": betweenness[i],
                "coreness": coreness[i],
                "no_kmax_original": coreness[i] == kmax_original,
            }
            for ordem, i in enumerate(alvos_indices, start=1)
        ],
        columns=COLUNAS_ALVOS,
    )

    registros: List[Dict[str, Any]] = []
    estado_inicial = _estado(g, n_original, usar_coreness_inicial=True)

    def executar(estrategia: str, repeticao: int, ids: List[str]) -> None:
        atual = g.copy()
        removidos = set()
        anterior_lcc = estado_inicial["lcc"]
        registros.append(
            {
                "rede": nome,
                "estrategia": estrategia,
                "repeticao": repeticao,
                "passo": 0,
                "id_removido": None,
                **estado_inicial,
            }
        )
        for passo, id_removido in enumerate(ids, start=1):
            if id_removido in removidos:
                raise RuntimeError(f"ID removido mais de uma vez: {id_removido}")
            vertices = atual.vs.select(name_eq=id_removido)
            if len(vertices) != 1:
                raise RuntimeError(f"ID a remover não está no grafo: {id_removido}")
            atual.delete_vertices(vertices[0].index)
            removidos.add(id_removido)
            estado = _estado(atual, n_original)
            if estado["lcc"] > anterior_lcc:
                raise RuntimeError("A LCC aumentou após a remoção de um vértice")
            if estado["n_vertices"] != n_original - passo:
                raise RuntimeError("A quantidade de vértices restantes não corresponde ao passo")
            registros.append(
                {
                    "rede": nome,
                    "estrategia": estrategia,
                    "repeticao": repeticao,
                    "passo": passo,
                    "id_removido": id_removido,
                    **estado,
                }
            )
            anterior_lcc = estado["lcc"]

    executar("Ataque direcionado", 1, alvos_ids)

    gerador = random.Random(semente)
    for repeticao in range(1, n_rep + 1):
        sorteados = gerador.sample(nomes, n_remover)
        executar("Falha aleatória", repeticao, sorteados)

    detalhes = pd.DataFrame(registros, columns=COLUNAS_DETALHES)
    medias = (
        detalhes.groupby(["rede", "estrategia", "passo"], as_index=False, sort=True)[_METRICAS_MEDIA]
        .mean()
        .reindex(columns=COLUNAS_MEDIAS)
    )
    esperados = (n_remover + 1) * (n_rep + 1)
    if len(detalhes) != esperados:
        raise RuntimeError(f"Esperados {esperados} registros, obtidos {len(detalhes)}")
    return detalhes, medias, alvos
