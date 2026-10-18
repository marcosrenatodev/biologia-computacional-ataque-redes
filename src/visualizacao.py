"""Gráficos e exportação dos resultados da atividade."""

from __future__ import annotations

from pathlib import Path
import random
from typing import List, Optional

import igraph as ig
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize
import pandas as pd


_CORES_ESTRATEGIA = {"Ataque direcionado": "#c43c39", "Falha aleatória": "#2468a2"}


def _caminho_layout(g: ig.Graph, semente: int):
    """Calcula um layout FR com inicialização e gerador reprodutíveis."""
    estado_rng = random.Random(semente)
    ig.set_random_number_generator(estado_rng)
    try:
        return g.layout_fruchterman_reingold(niter=500, grid="auto")
    finally:
        # Retorna o gerador ao padrão da biblioteca para evitar efeitos
        # sobre outras partes do notebook.
        ig.set_random_number_generator(None)


def plotar_rede(g: ig.Graph, nome: str, arquivo: Path, semente: int = 123) -> Path:
    """Salva a rede com coreness, betweenness e núcleo máximo destacados."""
    if g.is_directed():
        raise ValueError("A visualização exige um grafo não direcionado")
    if not g.is_simple():
        raise ValueError("A visualização exige um grafo simplificado")
    if "coreness" not in g.vs.attributes():
        raise ValueError("A rede precisa conter g.vs['coreness']")
    if "betweenness" not in g.vs.attributes():
        raise ValueError("A rede precisa conter g.vs['betweenness']")

    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    if g.vcount() == 0:
        raise ValueError("Não é possível plotar uma rede vazia")

    cores = [float(v) for v in g.vs["coreness"]]
    between = [max(0.0, float(v)) for v in g.vs["betweenness"]]
    kmax = max(cores)
    layout = _caminho_layout(g, semente)
    coords = layout.coords
    fig, ax = plt.subplots(figsize=(12, 9), constrained_layout=True)

    # A área cresce linearmente com a betweenness relativa.
    maior = max(between, default=0.0)
    tamanhos = [12 + 80 * (v / maior) for v in between] if maior else [12] * len(between)
    x = [p[0] for p in coords]
    y = [p[1] for p in coords]
    if g.ecount():
        segmentos = [[coords[e.source], coords[e.target]] for e in g.es]
        from matplotlib.collections import LineCollection

        ax.add_collection(LineCollection(segmentos, colors="#667085", linewidths=0.28, alpha=0.17, zorder=1))
    cmap = plt.get_cmap("viridis")
    norm = Normalize(vmin=min(cores), vmax=max(cores) if max(cores) > min(cores) else min(cores) + 1)
    pontos = ax.scatter(x, y, c=cores, s=tamanhos, cmap=cmap, norm=norm, alpha=0.82,
                        linewidths=0.35, edgecolors="#273142", zorder=2)
    no_core = [i for i, cor in enumerate(cores) if cor == kmax]
    if no_core:
        ax.scatter([x[i] for i in no_core], [y[i] for i in no_core], s=[tamanhos[i] * 1.8 for i in no_core],
                   facecolors="none", edgecolors="#e63946", linewidths=0.8, zorder=3)
    barra = fig.colorbar(pontos, ax=ax, shrink=0.78, pad=0.02)
    barra.set_label("Coreness")
    legenda = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#888888", markeredgecolor="#273142",
               markersize=5, label="Área dos nós escalada pela betweenness"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="none", markeredgecolor="#e63946",
               markeredgewidth=1.4, markersize=8, label=f"Núcleo máximo (k-max = {int(kmax)})"),
    ]
    ax.legend(handles=legenda, loc="best", frameon=True, fontsize=9)
    ax.set_title(f"{nome}\nDecomposição k-core e betweenness (k-max = {int(kmax)})")
    ax.autoscale()
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    fig.savefig(arquivo, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return arquivo


def _salvar_linhas(
    dados: pd.DataFrame,
    x: str,
    y: str,
    arquivo: Path,
    titulo: str,
    ylabel: str,
    limite_y: Optional[tuple] = None,
) -> Path:
    # As escalas comuns permitem comparar redes, mas podem esconder mudanças
    # de uma unidade. Nos indicadores de núcleo, mostramos também um detalhe.
    detalhar = y in {"kmax", "n_kmax"}
    fig, eixos = plt.subplots(
        1, 2 if detalhar else 1,
        figsize=(12, 5.2) if detalhar else (8.6, 5.2),
        constrained_layout=True, squeeze=False,
    )
    eixos = list(eixos[0])
    for estrategia, grupo in dados.groupby("estrategia", sort=False):
        grupo = grupo.sort_values(x)
        legenda = estrategia
        if detalhar:
            legenda += f" ({grupo[y].iloc[0]:g} → {grupo[y].iloc[-1]:g})"
        for ax in eixos:
            ax.plot(grupo[x], grupo[y], marker="o", linewidth=2, markersize=4,
                    linestyle="--" if estrategia == "Falha aleatória" else "-",
                    color=_CORES_ESTRATEGIA.get(estrategia), label=legenda)
    for indice, ax in enumerate(eixos):
        ax.set(xlabel="Nós removidos", ylabel=ylabel)
        ax.set_xticks(sorted(dados[x].dropna().unique()))
        limites = _limite_comparativo(dados, y) if indice else limite_y
        if limites is not None:
            ax.set_ylim(*limites)
        ax.grid(True, alpha=0.25)
    if detalhar:
        eixos[0].set_title("Escala comum às redes")
        eixos[1].set_title("Detalhe da variação (eixo Y ampliado)")
        fig.suptitle(titulo)
    else:
        eixos[0].set_title(titulo)
    eixos[-1].legend(frameon=False, loc="best")
    fig.savefig(arquivo, dpi=240, bbox_inches="tight")
    plt.close(fig)
    return arquivo


def plotar_resiliencia(medias: pd.DataFrame, diretorio: Path) -> List[Path]:
    """Gera gráficos por rede e comparações com escalas compartilhadas."""
    colunas = {"rede", "estrategia", "passo", "lcc_frac", "apl", "apl_lcc", "kmax", "n_kmax"}
    faltando = colunas - set(medias.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes em medias: {', '.join(sorted(faltando))}")
    diretorio = Path(diretorio)
    diretorio.mkdir(parents=True, exist_ok=True)
    arquivos: List[Path] = []
    medidas = [
        ("lcc_frac", "LCC (fração da rede original)", (0.0, 1.05)),
        ("apl", "Caminho médio (pares alcançáveis)", _limite_comparativo(medias, "apl")),
        ("apl_lcc", "Caminho médio na LCC", _limite_comparativo(medias, "apl_lcc")),
        ("kmax", "K-core máximo (k-max)", _limite_comparativo(medias, "kmax")),
        ("n_kmax", "Nós no núcleo máximo", _limite_comparativo(medias, "n_kmax")),
    ]
    redes = list(pd.unique(medias["rede"]))
    for rede in redes:
        recorte = medias[medias["rede"] == rede]
        slug = str(rede).strip().lower().replace(" ", "_").replace("/", "_")
        for medida, ylabel, limite in medidas:
            arquivos.append(_salvar_linhas(
                recorte, "passo", medida, diretorio / f"{slug}_{medida}.png",
                f"{rede}: {ylabel}", ylabel, limite,
            ))

    # Os mesmos indicadores compartilham limites entre redes. k-max e n-kmax
    # são normalizados pelo valor inicial de cada rede para comparação.
    comparacao = medias.copy()
    comparacao["kmax_norm"] = _normalizar_por_inicial(comparacao, "kmax")
    comparacao["n_kmax_norm"] = _normalizar_por_inicial(comparacao, "n_kmax")
    limites = {
        "lcc_frac": (0.0, 1.05),
        "apl": _limite_comparativo(medias, "apl"),
        "apl_lcc": _limite_comparativo(medias, "apl_lcc"),
        "kmax_norm": _limite_comparativo(comparacao, "kmax_norm"),
        "n_kmax_norm": _limite_comparativo(comparacao, "n_kmax_norm"),
    }
    for medida, ylabel, limite in [
        ("lcc_frac", "LCC (fração da rede original)", limites["lcc_frac"]),
        ("apl", "Caminho médio (pares alcançáveis)", limites["apl"]),
        ("apl_lcc", "Caminho médio na LCC", limites["apl_lcc"]),
        ("kmax_norm", "k-max / k-max inicial", limites["kmax_norm"]),
        ("n_kmax_norm", "n-kmax / n-kmax inicial", limites["n_kmax_norm"]),
    ]:
        arquivo = diretorio / f"comparativo_{medida}.png"
        arquivos.append(_salvar_comparativo(comparacao, medida, ylabel, arquivo, limite))
    return arquivos


def _limite_comparativo(dados: pd.DataFrame, coluna: str):
    valores = dados[coluna].dropna()
    if valores.empty:
        return None
    minimo, maximo = float(valores.min()), float(valores.max())
    if minimo == maximo:
        return (max(0.0, minimo - 0.5), maximo + 0.5)
    folga = (maximo - minimo) * 0.06
    return (max(0.0, minimo - folga), maximo + folga)


def _normalizar_por_inicial(dados: pd.DataFrame, coluna: str) -> pd.Series:
    iniciais = dados[dados["passo"] == 0].groupby("rede")[coluna].first()
    denominadores = dados["rede"].map(iniciais)
    return dados[coluna].div(denominadores.where(denominadores != 0))


def _salvar_comparativo(dados: pd.DataFrame, medida: str, ylabel: str, arquivo: Path, limite) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    redes = list(pd.unique(dados["rede"]))
    estrategias = list(pd.unique(dados["estrategia"]))
    paleta = plt.get_cmap("tab10")
    cor_por_rede = {rede: paleta(i % 10) for i, rede in enumerate(redes)}
    estilos = {estrategia: ("-" if estrategia == "Ataque direcionado" else "--") for estrategia in estrategias}
    for (rede, estrategia), grupo in dados.groupby(["rede", "estrategia"], sort=False):
        grupo = grupo.sort_values("passo")
        ax.plot(grupo["passo"], grupo[medida], linestyle=estilos[estrategia], marker="o", markersize=3.5,
                linewidth=1.8, color=cor_por_rede[rede], alpha=0.95)
    handles_redes = [Line2D([0], [0], color=cor_por_rede[r], lw=2, label=str(r)) for r in redes]
    handles_estrategias = [
        Line2D([0], [0], color="#444444", lw=2, linestyle=estilos[e], label=e) for e in estrategias
    ]
    legenda_rede = ax.legend(
        handles=handles_redes,
        title="Rede",
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        borderaxespad=0.0,
        frameon=False,
    )
    ax.add_artist(legenda_rede)
    ax.legend(
        handles=handles_estrategias,
        title="Estratégia",
        loc="lower left",
        bbox_to_anchor=(1.02, 0.0),
        borderaxespad=0.0,
        frameon=False,
    )
    ax.set(title=f"Comparação entre redes: {ylabel}", xlabel="Nós removidos", ylabel=ylabel)
    ax.set_xticks(sorted(dados["passo"].dropna().unique()))
    if limite is not None:
        ax.set_ylim(*limite)
    ax.grid(True, alpha=0.25)
    fig.savefig(arquivo, dpi=240, bbox_inches="tight")
    plt.close(fig)
    return arquivo


def exportar_resultados(detalhes: pd.DataFrame, medias: pd.DataFrame, alvos: pd.DataFrame, diretorio: Path) -> List[Path]:
    """Exporta as três tabelas em CSV UTF-8 e devolve os caminhos salvos."""
    diretorio = Path(diretorio)
    diretorio.mkdir(parents=True, exist_ok=True)
    tabelas = [
        (detalhes, diretorio / "resiliencia_detalhes.csv"),
        (medias, diretorio / "resiliencia_medias.csv"),
        (alvos, diretorio / "resiliencia_alvos.csv"),
    ]
    for tabela, arquivo in tabelas:
        tabela.to_csv(arquivo, index=False, encoding="utf-8")
    return [arquivo for _, arquivo in tabelas]
