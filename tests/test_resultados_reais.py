"""Confere os CSVs produzidos pelo notebook com as topologias reais."""

from pathlib import Path

import pandas as pd
import pytest

from src.carregar_redes import carregar_redes


RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / "output" / "resultados"


@pytest.fixture(scope="module")
def resultados():
    if not (RESULTADOS / "resiliencia_detalhes.csv").is_file():
        pytest.skip("Execute primeiro notebooks/analise_redes.ipynb")
    redes = carregar_redes(RAIZ / "data", baixar=False)
    detalhes = pd.read_csv(RESULTADOS / "resiliencia_detalhes.csv", dtype={"id_removido": str})
    nos = pd.read_csv(RESULTADOS / "metricas_nos.csv", dtype={"id_original": str})
    alvos = pd.read_csv(RESULTADOS / "resiliencia_alvos.csv", dtype={"id_original": str})
    return redes, detalhes, nos, alvos


@pytest.mark.parametrize("nome,kmax,n_kmax", [("Facebook", 115, 158), ("Power Grid", 5, 12)])
def test_nucleos_e_alvos_reais(resultados, nome, kmax, n_kmax):
    redes, detalhes, nos, alvos = resultados
    g = redes[nome]
    tabela = nos[nos["rede"] == nome].set_index("id_original").loc[g.vs["name"]]
    cores = g.coreness()
    assert tabela["coreness"].tolist() == cores
    assert max(cores) == kmax
    assert sum(c == kmax for c in cores) == n_kmax
    nucleo = g.induced_subgraph([i for i, c in enumerate(cores) if c == kmax])
    assert min(nucleo.degree()) >= kmax
    assert g.k_core(kmax + 1).vcount() == 0
    ranking = sorted(g.vs["name"], key=lambda id_: (-tabela.loc[id_, "betweenness"], id_))[:10]
    assert alvos[alvos["rede"] == nome]["id_original"].tolist() == ranking
    ataque = detalhes[(detalhes["rede"] == nome) & (detalhes["estrategia"] == "Ataque direcionado")]
    assert ataque.sort_values("passo")["id_removido"].dropna().tolist() == ranking


@pytest.mark.parametrize("nome", ["Facebook", "Power Grid"])
def test_reconstroi_cada_remocao_real(resultados, nome):
    redes, detalhes, _, _ = resultados
    tabela = detalhes[detalhes["rede"] == nome]
    assert len(tabela) == 66
    for _, grupo in tabela.groupby(["estrategia", "repeticao"]):
        atual = redes[nome].copy()
        for linha in grupo.sort_values("passo").itertuples():
            if linha.passo:
                atual.delete_vertices(atual.vs.find(name=linha.id_removido).index)
            cores = atual.coreness()
            kmax_atual = max(cores)
            assert linha.n_vertices == atual.vcount()
            assert linha.lcc == max(atual.connected_components().sizes())
            assert linha.kmax == kmax_atual
            assert linha.n_kmax == sum(c == kmax_atual for c in cores)
