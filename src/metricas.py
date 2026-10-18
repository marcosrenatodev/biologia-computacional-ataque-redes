"""Medidas da estrutura das redes e dos seus núcleos k-core."""

from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List, Tuple

import igraph as ig
import pandas as pd


def _validar_grafo(grafo: ig.Graph) -> None:
    if not isinstance(grafo, ig.Graph):
        raise TypeError("grafo deve ser uma instância de igraph.Graph")
    if "name" not in grafo.vs.attributes() and grafo.vcount():
        grafo.vs["name"] = [str(indice) for indice in range(grafo.vcount())]


def _exigir_nao_direcionado(grafo: ig.Graph, operacao: str) -> None:
    if grafo.is_directed():
        raise ValueError(
            f"{operacao} foi definida para redes não direcionadas; "
            "o grafo recebido é direcionado e não será convertido"
        )


def _assinatura_estrutura(grafo: ig.Graph) -> str:
    """Confere se as medidas guardadas ainda servem para as mesmas ligações."""
    digest = hashlib.sha256()
    digest.update(b"D" if grafo.is_directed() else b"U")
    digest.update(str(grafo.vcount()).encode("ascii"))
    for origem, destino in grafo.get_edgelist():
        digest.update(f"{origem},{destino};".encode("ascii"))
    return digest.hexdigest()


def _valor_finito(valor: Any) -> Any:
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return numero if math.isfinite(numero) else None


def caracterizar_rede(grafo: ig.Graph) -> Dict[str, Any]:
    """Calcula medidas gerais; o diâmetro é medido na maior componente (LCC).

    Em uma rede direcionada, componentes fracas ignoram o sentido das ligações,
    mas o diâmetro respeita esse sentido e considera apenas pares alcançáveis
    dentro da LCC. A transitividade (medida de fechamento de triângulos) não é
    calculada para redes direcionadas e retorna ``None``. Nas redes não
    direcionadas do exercício, as medidas usam o grafo original simplificado.
    """
    _validar_grafo(grafo)
    n_vertices = grafo.vcount()
    n_arestas = grafo.ecount()
    dirigida = grafo.is_directed()
    if n_vertices == 0:
        densidade = 0.0
        componentes = []
        diametro = None
        transitividade = None if dirigida else 0.0
    else:
        densidade = float(grafo.density(loops=False))
        modo = "weak" if dirigida else "weak"
        componentes = grafo.connected_components(mode=modo)
        if componentes:
            maior = max(componentes, key=len)
            lcc_grafo = grafo.induced_subgraph(maior)
            diametro = (
                int(lcc_grafo.diameter(directed=True, unconn=True))
                if dirigida
                else int(lcc_grafo.diameter(directed=False, unconn=True))
            )
        else:
            diametro = None
        transitividade = (
            None
            if dirigida
            else _valor_finito(grafo.transitivity_undirected(mode="zero"))
        )
        if not dirigida and transitividade is None:
            transitividade = 0.0

    return {
        "n_vertices": n_vertices,
        "n_arestas": n_arestas,
        "direcionada": dirigida,
        "densidade": densidade,
        "diametro": diametro,
        "transitividade_global": transitividade,
        "n_componentes": len(componentes),
        "lcc": max((len(componente) for componente in componentes), default=0),
    }


def _coreness_e_betweenness(grafo: ig.Graph) -> Tuple[List[int], List[float]]:
    assinatura = _assinatura_estrutura(grafo)
    atributos = grafo.vs.attributes()
    if (
        "_metricas_cache_assinatura" in grafo.attributes()
        and grafo["_metricas_cache_assinatura"] == assinatura
        and "coreness" in atributos
        and "betweenness" in atributos
        and len(grafo.vs["coreness"]) == grafo.vcount()
        and len(grafo.vs["betweenness"]) == grafo.vcount()
    ):
        try:
            coreness = [int(valor) for valor in grafo.vs["coreness"]]
            betweenness = [float(valor) for valor in grafo.vs["betweenness"]]
            if all(math.isfinite(valor) for valor in betweenness):
                return coreness, betweenness
        except (TypeError, ValueError):
            pass

    coreness = [int(valor) for valor in grafo.coreness()]
    # O script EaD3_Script1.R também calcula essa medida sem direção.
    betweenness = [float(valor) for valor in grafo.betweenness(directed=False)]
    grafo.vs["coreness"] = coreness
    grafo.vs["betweenness"] = betweenness
    grafo["_metricas_cache_assinatura"] = assinatura
    return coreness, betweenness


def analisar_kcore(grafo: ig.Graph) -> Dict[str, Any]:
    """Calcula o núcleo máximo (k-max) e medidas dos seus nós.

    A assortatividade de grau indica se vértices tendem a se ligar a outros com
    grau parecido; ela é medida na rede original simplificada. ``grau_relativo``
    no DataFrame é o número de ligações dentro do núcleo dividido por
    ``n_kmax - 1``. Se o núcleo tiver menos de dois vértices, o valor é zero.
    A betweenness (intermediação) é calculada exatamente na rede original.
    """
    _validar_grafo(grafo)
    _exigir_nao_direcionado(grafo, "decomposição k-core e betweenness")
    if not grafo.is_simple():
        raise ValueError(
            "decomposição k-core e betweenness exigem um grafo simples; "
            "remova loops e arestas múltiplas antes da análise"
        )
    coreness, _ = _coreness_e_betweenness(grafo)
    kmax = max(coreness, default=0)
    indices = [indice for indice, valor in enumerate(coreness) if valor == kmax]
    subgrafo = grafo.induced_subgraph(indices)
    subgrafo["name"] = grafo["name"] if "name" in grafo.attributes() else "Rede"
    graus = subgrafo.degree()
    n_kmax = subgrafo.vcount()
    divisor = n_kmax - 1
    registros = []
    for indice, grau in enumerate(graus):
        identificador = str(subgrafo.vs[indice]["name"])
        registros.append(
            {
                "id_original": identificador,
                "grau_interno": int(grau),
                "grau_relativo": float(grau / divisor) if divisor > 0 else 0.0,
            }
        )
    registros.sort(key=lambda item: (-item["grau_interno"], item["id_original"]))
    top5 = pd.DataFrame(
        registros[:5], columns=["id_original", "grau_interno", "grau_relativo"]
    )

    if grafo.ecount() == 0:
        assortatividade = None
    else:
        assortatividade = _valor_finito(grafo.assortativity_degree(directed=False))

    densidade_kmax = (
        float(subgrafo.density(loops=False)) if n_kmax > 1 else 0.0
    )
    return {
        "kmax": kmax,
        "n_kmax": n_kmax,
        "densidade_kmax": densidade_kmax,
        "assortatividade": assortatividade,
        "subgrafo": subgrafo,
        "top5": top5,
    }
