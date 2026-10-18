"""Testes de formatos e proveniência dos loaders de redes."""

import gzip
import json
import sys
import zipfile
from pathlib import Path

import igraph as ig
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.carregar_redes import (
    ErroFormatoRede,
    carregar_facebook,
    carregar_power_grid,
    carregar_redes,
)


RAIZ = Path(__file__).resolve().parents[1]


def test_carrega_snap_gzip_e_simplifica_preservando_ids(tmp_path):
    arquivo = tmp_path / "facebook_combined.txt.gz"
    with gzip.open(arquivo, "wt", encoding="utf-8") as saida:
        saida.write("17 8\n8 17\n5 5\n5 17\n")

    grafo = carregar_facebook(arquivo, baixar=False)

    assert isinstance(grafo, ig.Graph)
    assert grafo.is_directed() is False
    assert grafo["name"] == "Facebook"
    assert set(grafo.vs["name"]) == {"5", "8", "17"}
    assert grafo.vcount() == 3
    assert grafo.ecount() == 2
    assert all(grau >= 0 for grau in grafo.degree())
    fontes = json.loads((tmp_path / "fontes.json").read_text(encoding="utf-8"))
    assert fontes["Facebook"]["arquivo"] == "facebook_combined.txt.gz"
    assert fontes["Facebook"]["sha256"]


def test_carrega_matrix_market_zip_e_preserva_isolados(tmp_path):
    arquivo = tmp_path / "inf-power.zip"
    conteudo = (
        "%%MatrixMarket matrix coordinate pattern symmetric\n"
        "% exemplo pequeno\n"
        "4 4 3\n"
        "2 1\n"
        "3 2\n"
        "1 2\n"
    )
    with zipfile.ZipFile(arquivo, "w") as zf:
        zf.writestr("inf-power.mtx", conteudo)
        zf.writestr("readme.html", "metadados")

    grafo = carregar_power_grid(arquivo, baixar=False)

    assert grafo.is_directed() is False
    assert grafo["name"] == "Power Grid"
    assert grafo.vcount() == 4
    assert grafo.ecount() == 2
    assert grafo.vs["name"] == ["1", "2", "3", "4"]
    assert grafo.degree("4") == 0
    fontes = json.loads((tmp_path / "fontes.json").read_text(encoding="utf-8"))
    assert fontes["Power Grid"]["arquivo"] == "inf-power.zip"


def test_nao_converte_matrix_market_geral_em_nao_direcionada(tmp_path):
    arquivo = tmp_path / "inf-power.mtx"
    arquivo.write_text(
        "%%MatrixMarket matrix coordinate pattern general\n2 2 1\n1 2\n",
        encoding="utf-8",
    )

    with pytest.raises(ErroFormatoRede, match="não será convertida silenciosamente"):
        carregar_power_grid(arquivo, baixar=False)


def test_arquivo_ausente_tem_mensagem_de_download(tmp_path):
    with pytest.raises(FileNotFoundError, match="Baixe-o"):
        carregar_facebook(tmp_path / "ausente.gz", baixar=False)


@pytest.mark.parametrize(
    ("arquivo", "vertices", "arestas"),
    [
        ("facebook_combined.txt.gz", 4039, 88234),
        ("inf-power.zip", 4941, 6594),
    ],
)
def test_loader_dos_datasets_reais_se_presentes(arquivo, vertices, arestas):
    caminho = RAIZ / "data" / arquivo
    if not caminho.is_file():
        pytest.skip(f"dataset real não encontrado: {caminho}")

    redes = carregar_redes(RAIZ / "data", baixar=False)
    nome = "Facebook" if arquivo.startswith("facebook") else "Power Grid"
    grafo = redes[nome]
    assert not grafo.is_directed()
    assert (grafo.vcount(), grafo.ecount()) == (vertices, arestas)
    assert all(isinstance(identificador, str) for identificador in grafo.vs["name"])
    assert grafo["name"] == nome
