"""Verifica os contratos entre módulos usando um caso pequeno conhecido."""

import igraph as ig
import pandas as pd

from src.metricas import analisar_kcore, caracterizar_rede
from src.simulacao import simular_resiliencia
from src.visualizacao import exportar_resultados


def test_fluxo_integrado(tmp_path):
    # K4 com uma folha: núcleo conhecido, betweenness sem aproximação.
    g = ig.Graph.Full(4)
    g.add_vertex()
    g.add_edge(0, 4)
    g.vs["name"] = ["10", "20", "30", "40", "50"]
    g["name"] = "Teste de integração"
    estrutura = caracterizar_rede(g)
    nucleo = analisar_kcore(g)
    assert estrutura["n_vertices"] == 5
    assert nucleo["kmax"] == 3
    assert nucleo["n_kmax"] == 4
    assert nucleo["densidade_kmax"] == 1
    assert set(nucleo["top5"]["id_original"]) == {"10", "20", "30", "40"}

    detalhes, medias, alvos = simular_resiliencia(
        g, g["name"], n_remover=2, n_rep=2, semente=123
    )
    assert len(detalhes) == 9
    assert len(medias) == 6
    assert alvos.iloc[0]["id_original"] == "10"
    assert g.vcount() == 5  # As simulações não alteram a rede de entrada.
    for _, grupo in detalhes.groupby(["estrategia", "repeticao"]):
        assert grupo["passo"].tolist() == [0, 1, 2]
        assert grupo["n_vertices"].tolist() == [5, 4, 3]
        assert (grupo["lcc"].diff().dropna() <= 0).all()
        assert grupo["id_removido"].dropna().nunique() == 2

    exportar_resultados(detalhes, medias, alvos, tmp_path)
    csvs = list(tmp_path.glob("*.csv"))
    assert len(csvs) == 3
    assert sorted(len(pd.read_csv(p)) for p in csvs) == [2, 6, 9]
