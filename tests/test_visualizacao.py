"""Verifica a geração de figuras e CSVs a partir de redes reduzidas."""

import igraph as ig
import pandas as pd
import pytest
from matplotlib.figure import Figure

from src.simulacao import simular_resiliencia
from src.visualizacao import exportar_resultados, plotar_rede, plotar_resiliencia
from src.visualizacao import _salvar_linhas


def _rede_cliques(nome):
    g = ig.Graph.Full(4)
    g.add_vertices(3)
    g.add_edges([(4, 5), (5, 6), (4, 6)])
    g.vs["name"] = ["1", "2", "3", "4", "5", "6", "7"]
    g.vs["coreness"] = g.coreness()
    g.vs["betweenness"] = g.betweenness(directed=False)
    g["name"] = nome
    return g


def test_gera_graficos_separados_e_comparativos_e_exporta_csv(tmp_path):
    redes = [_rede_cliques("Rede A"), _rede_cliques("Rede B")]
    resultados = [
        simular_resiliencia(g, g["name"], n_remover=1, n_rep=2)
        for g in redes
    ]
    detalhes = pd.concat([r[0] for r in resultados], ignore_index=True)
    medias = pd.concat([r[1] for r in resultados], ignore_index=True)
    alvos = pd.concat([r[2] for r in resultados], ignore_index=True)

    figura_rede = plotar_rede(redes[0], "Rede A", tmp_path / "rede.png", semente=123)
    assert figura_rede.exists() and figura_rede.stat().st_size > 1000

    figuras = plotar_resiliencia(medias, tmp_path / "graficos")
    assert len(figuras) == 15  # Cinco medidas para cada rede e cinco comparativos.
    assert all(caminho.exists() and caminho.stat().st_size > 1000 for caminho in figuras)
    assert (tmp_path / "graficos" / "rede_a_apl.png").exists()
    assert (tmp_path / "graficos" / "rede_a_apl_lcc.png").exists()
    assert (tmp_path / "graficos" / "comparativo_n_kmax_norm.png").exists()

    csvs = exportar_resultados(detalhes, medias, alvos, tmp_path / "resultados")
    assert [p.name for p in csvs] == [
        "resiliencia_detalhes.csv", "resiliencia_medias.csv", "resiliencia_alvos.csv"
    ]
    assert all(p.exists() for p in csvs)
    recarregado = pd.read_csv(csvs[2], encoding="utf-8")
    assert recarregado["rede"].tolist() == ["Rede A", "Rede B"]


@pytest.mark.parametrize("medida,inicial,final,menor_rede", [
    ("kmax", 115, 114, 5), ("n_kmax", 158, 157, 12),
])
def test_detalhe_do_nucleo_mostra_queda_de_uma_unidade(
    tmp_path, monkeypatch, medida, inicial, final, menor_rede
):
    """A escala comparativa não deve esconder a mudança do Facebook."""
    capturadas = []
    monkeypatch.setattr(Figure, "savefig", lambda fig, *args, **kwargs: capturadas.append(fig))
    dados = pd.DataFrame({
        "estrategia": ["Ataque direcionado"] * 2 + ["Falha aleatória"] * 2,
        "passo": [0, 4, 0, 4], medida: [inicial, final, inicial, inicial],
    })
    _salvar_linhas(dados, "passo", medida, tmp_path / "nucleo.png", "Facebook",
                   medida, (menor_rede - 1, inicial + 1))
    comum, detalhe = capturadas[0].axes
    assert comum.get_ylim()[0] < menor_rede
    assert final - 1 < detalhe.get_ylim()[0] < final
    assert inicial < detalhe.get_ylim()[1] < inicial + 1
    assert detalhe.lines[0].get_ydata().tolist() == [inicial, final]
    assert detalhe.lines[1].get_ydata().tolist() == [inicial, inicial]
