"""Testes pequenos das métricas e da decomposição k-core."""

import math
import sys
from pathlib import Path

import igraph as ig
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metricas import analisar_kcore, caracterizar_rede


def _grafo(vertices, arestas, nome="Teste"):
    grafo = ig.Graph(n=len(vertices), edges=arestas, directed=False)
    grafo.vs["name"] = vertices
    grafo["name"] = nome
    return grafo


def test_caracterizacao_usa_maior_componente_para_diametro():
    grafo = _grafo(["a", "b", "c", "d", "e"], [(0, 1), (1, 2), (2, 0), (3, 4)])

    resultado = caracterizar_rede(grafo)

    assert resultado == {
        "n_vertices": 5,
        "n_arestas": 4,
        "direcionada": False,
        "densidade": 0.4,
        "diametro": 1,
        "transitividade_global": 1.0,
        "n_componentes": 2,
        "lcc": 3,
    }


def test_caracterizacao_grafo_vazio():
    resultado = caracterizar_rede(ig.Graph(directed=False))

    assert resultado["n_vertices"] == 0
    assert resultado["n_arestas"] == 0
    assert resultado["diametro"] is None
    assert resultado["n_componentes"] == 0
    assert resultado["lcc"] == 0


def test_grafo_direcionado_nao_e_convertido_na_caracterizacao():
    grafo = ig.Graph(n=3, edges=[(0, 1), (1, 2)], directed=True)
    grafo.vs["name"] = ["1", "2", "3"]

    resultado = caracterizar_rede(grafo)

    assert resultado["direcionada"] is True
    assert resultado["n_componentes"] == 1
    assert resultado["lcc"] == 3
    assert resultado["diametro"] == 2
    assert resultado["transitividade_global"] is None
    with pytest.raises(ValueError, match="não será convertido"):
        analisar_kcore(grafo)


def test_analisar_kcore_e_betweenness_exata_com_empates_estaveis():
    # Caminho de quatro nós: cada nó tem coreness 1; dois nós centrais têm
    # grau interno 2 e betweenness exata 2.
    grafo = _grafo(["10", "2", "1", "x"], [(0, 1), (1, 2), (2, 3)])

    resultado = analisar_kcore(grafo)

    assert resultado["kmax"] == 1
    assert resultado["n_kmax"] == 4
    assert resultado["subgrafo"].vs["name"] == ["10", "2", "1", "x"]
    assert math.isclose(resultado["densidade_kmax"], 0.5)
    assert grafo.vs["coreness"] == [1, 1, 1, 1]
    assert grafo.vs["betweenness"] == [0.0, 2.0, 2.0, 0.0]
    assert list(resultado["top5"].columns) == [
        "id_original",
        "grau_interno",
        "grau_relativo",
    ]
    assert resultado["top5"]["id_original"].tolist() == ["1", "2", "10", "x"]
    assert resultado["top5"]["grau_interno"].tolist() == [2, 2, 1, 1]
    assert resultado["top5"]["grau_relativo"].tolist() == [
        2 / 3,
        2 / 3,
        1 / 3,
        1 / 3,
    ]
    assert resultado["assortatividade"] is not None


def test_top5_limita_a_cinco_vertices_e_desempata_por_id():
    vertices = ["0", "1", "2", "3", "4", "5", "6", "10"]
    arestas = [(origem, destino) for origem in range(8) for destino in range(origem + 1, 8)]
    resultado = analisar_kcore(_grafo(vertices, arestas))

    assert resultado["kmax"] == 7
    assert resultado["n_kmax"] == 8
    assert resultado["top5"]["id_original"].tolist() == ["0", "1", "10", "2", "3"]
    assert all(resultado["top5"]["grau_interno"] == 7)
    assert all(resultado["top5"]["grau_relativo"] == 1.0)


def test_analisar_kcore_rejeita_grafo_com_arestas_multiplas():
    grafo = _grafo(["a", "b"], [(0, 1), (0, 1)])

    with pytest.raises(ValueError, match="grafo simples"):
        analisar_kcore(grafo)
