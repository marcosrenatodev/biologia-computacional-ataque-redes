"""Casos pequenos para conferir ranking estático e métricas após remoções."""

import igraph as ig
import pandas as pd
import pytest

from src.simulacao import simular_resiliencia


def _caminho_rotulado(n=6):
    g = ig.Graph(n=n, edges=[(i, i + 1) for i in range(n - 1)], directed=False)
    g.vs["name"] = [f"id-{i}" for i in range(n)]
    g["name"] = "Caminho"
    return g


def test_ataque_fixo_empate_por_id_e_falhas_reproduziveis():
    g = _caminho_rotulado()
    detalhes, medias, alvos = simular_resiliencia(g, g["name"], n_remover=2, n_rep=2)
    detalhes2, _, _ = simular_resiliencia(g, g["name"], n_remover=2, n_rep=2)

    assert alvos["id_original"].tolist() == ["id-2", "id-3"]
    assert alvos["ordem"].tolist() == [1, 2]
    assert len(detalhes) == 9
    assert len(medias) == 6
    assert detalhes.equals(detalhes2)
    assert list(detalhes.columns) == [
        "rede", "estrategia", "repeticao", "passo", "id_removido", "n_vertices",
        "lcc", "lcc_frac", "apl", "apl_lcc", "kmax", "n_kmax",
    ]

    ataque = detalhes[detalhes["estrategia"] == "Ataque direcionado"].sort_values("passo")
    assert ataque["id_removido"].tolist()[1:] == ["id-2", "id-3"]
    assert ataque["n_vertices"].tolist() == [6, 5, 4]
    assert ataque["lcc"].tolist() == [6, 3, 2]
    assert ataque.iloc[0]["apl"] == pytest.approx(7 / 3)
    assert ataque.iloc[1]["apl"] != pytest.approx(ataque.iloc[1]["apl_lcc"])

    for _, repeticao in detalhes[detalhes["estrategia"] == "Falha aleatória"].groupby("repeticao"):
        removidos = repeticao.sort_values("passo")["id_removido"].dropna().tolist()
        assert len(removidos) == len(set(removidos)) == 2
        assert repeticao.sort_values("passo")["n_vertices"].tolist() == [6, 5, 4]
        assert (repeticao.sort_values("passo")["lcc"].diff().dropna() <= 0).all()

    assert g.vcount() == 6
    assert medias["n_vertices"].tolist()[:3] == [6.0, 5.0, 4.0]


def test_core_atual_e_contagem_podem_aumentar_apos_ataque():
    # K4 tem k-max 3 e quatro vértices; removendo um deles, o grafo restante
    # passa a ter seis vértices no k-max 2 (duas componentes K3).
    g = ig.Graph.Full(4)
    g.add_vertices(3)
    g.add_edges([(4, 5), (5, 6), (4, 6)])
    g.vs["name"] = ["a", "b", "c", "d", "e", "f", "g"]
    detalhes, _, alvos = simular_resiliencia(g, "Dois cliques", n_remover=1, n_rep=1)

    assert alvos.iloc[0]["id_original"] == "a"  # Empate por betweenness resolvido pelo ID.
    assert alvos.iloc[0]["no_kmax_original"]
    ataque = detalhes[detalhes["estrategia"] == "Ataque direcionado"].sort_values("passo")
    assert ataque["kmax"].tolist() == [3, 2]
    assert ataque["n_kmax"].tolist() == [4, 6]


def test_valida_entrada_e_limite_de_remocoes():
    g = _caminho_rotulado()
    with pytest.raises(ValueError, match="não pode exceder"):
        simular_resiliencia(g, "Caminho", n_remover=7)

    dirigido = ig.Graph(n=3, edges=[(0, 1), (1, 2)], directed=True)
    dirigido.vs["name"] = ["a", "b", "c"]
    with pytest.raises(ValueError, match="não direcionado"):
        simular_resiliencia(dirigido, "Dirigido", n_remover=1)
