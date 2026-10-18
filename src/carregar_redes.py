"""Leitura e conferência das redes reais usadas no Exercício 3."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import IO, Optional, Tuple

import igraph as ig

URL_FACEBOOK = "https://snap.stanford.edu/data/facebook_combined.txt.gz"
URL_POWER_GRID = "https://nrvis.com/download/data/inf/inf-power.zip"


class ErroFormatoRede(ValueError):
    """Indica que o arquivo não segue o formato esperado para uma rede."""


def _baixar_arquivo(url: str, caminho: Path) -> None:
    """Baixa o arquivo sem deixar uma cópia incompleta no destino."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(
        prefix=f".{caminho.name}.", suffix=".part", dir=str(caminho.parent)
    )
    try:
        with os.fdopen(fd, "wb") as destino:
            requisicao = urllib.request.Request(
                url, headers={"User-Agent": "exercicio3-redes/1.0"}
            )
            with urllib.request.urlopen(requisicao, timeout=60) as resposta:
                while True:
                    bloco = resposta.read(1024 * 1024)
                    if not bloco:
                        break
                    destino.write(bloco)
        if os.path.getsize(temporario) == 0:
            raise OSError("o servidor retornou um arquivo vazio")
        os.replace(temporario, caminho)
    except (OSError, urllib.error.URLError) as erro:
        try:
            os.unlink(temporario)
        except FileNotFoundError:
            pass
        raise OSError(f"não foi possível baixar {url}: {erro}") from erro


def _garantir_arquivo(caminho: Path, url: str, baixar: bool) -> None:
    if caminho.is_file():
        return
    if not baixar:
        raise FileNotFoundError(
            f"arquivo não encontrado: {caminho}. Baixe-o de {url} ou use baixar=True."
        )
    _baixar_arquivo(url, caminho)


def _sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _registrar_fonte(
    diretorio_dados: Path, chave: str, url: str, arquivo: Path
) -> None:
    """Guarda a origem e a soma de verificação do arquivo lido."""
    manifest = diretorio_dados / "fontes.json"
    dados = {}
    if manifest.is_file():
        try:
            with manifest.open("r", encoding="utf-8") as entrada:
                dados = json.load(entrada)
        except (json.JSONDecodeError, OSError) as erro:
            raise ErroFormatoRede(
                f"manifesto de fontes inválido em {manifest}: {erro}"
            ) from erro
        if not isinstance(dados, dict):
            raise ErroFormatoRede(f"manifesto de fontes inválido em {manifest}")

    try:
        arquivo_relativo = arquivo.resolve().relative_to(diretorio_dados.resolve())
        caminho_registrado = arquivo_relativo.as_posix()
    except ValueError:
        caminho_registrado = str(arquivo.resolve())
    dados[chave] = {
        "url": url,
        "arquivo": caminho_registrado,
        "sha256": _sha256(arquivo),
    }
    diretorio_dados.mkdir(parents=True, exist_ok=True)
    temporario = manifest.with_suffix(manifest.suffix + ".tmp")
    with temporario.open("w", encoding="utf-8", newline="\n") as saida:
        json.dump(dados, saida, ensure_ascii=False, indent=2, sort_keys=True)
        saida.write("\n")
    os.replace(temporario, manifest)


def _abrir_facebook(caminho: Path) -> IO[str]:
    if caminho.suffix == ".gz":
        return gzip.open(caminho, "rt", encoding="utf-8")
    return caminho.open("r", encoding="utf-8")


def carregar_facebook(
    caminho: str | Path = "data/facebook_combined.txt.gz", baixar: bool = True
) -> ig.Graph:
    """Lê a lista de arestas (pares de IDs) do SNAP como rede simples.

    Como o arquivo registra apenas pares ligados, ele não informa sobre vértices
    isolados. Os IDs originais são guardados como texto no atributo ``name``.
    """
    caminho = Path(caminho)
    _garantir_arquivo(caminho, URL_FACEBOOK, baixar)
    arestas = []
    vertices = set()
    try:
        with _abrir_facebook(caminho) as entrada:
            for numero_linha, linha in enumerate(entrada, start=1):
                partes = linha.split()
                if not partes or partes[0].startswith("#"):
                    continue
                if len(partes) != 2:
                    raise ErroFormatoRede(
                        f"{caminho}:{numero_linha}: esperados dois IDs separados por espaço"
                    )
                origem, destino = partes
                vertices.update((origem, destino))
                if origem != destino:
                    arestas.append((origem, destino))
    except (OSError, EOFError, UnicodeError) as erro:
        raise ErroFormatoRede(
            f"não foi possível ler o edge list SNAP {caminho}: {erro}"
        ) from erro
    if not vertices:
        raise ErroFormatoRede(f"o arquivo {caminho} não contém arestas nem vértices")

    ids = sorted(
        vertices,
        key=lambda identificador: (0, int(identificador))
        if identificador.isdecimal()
        else (1, identificador),
    )
    posicoes = {identificador: indice for indice, identificador in enumerate(ids)}
    grafo = ig.Graph(
        n=len(ids),
        edges=[(posicoes[origem], posicoes[destino]) for origem, destino in arestas],
        directed=False,
    )
    grafo.vs["name"] = ids
    grafo.simplify(multiple=True, loops=True)
    grafo["name"] = "Facebook"
    _registrar_fonte(caminho.parent, "Facebook", URL_FACEBOOK, caminho)
    return grafo


def _ler_matrix_market(entrada: IO[str], identificacao: str) -> ig.Graph:
    cabecalho = entrada.readline().strip().split()
    if len(cabecalho) != 5 or cabecalho[0].lower() != "%%matrixmarket":
        raise ErroFormatoRede(
            f"{identificacao}: cabeçalho MatrixMarket ausente ou malformado"
        )
    _, objeto, armazenamento, formato, simetria = cabecalho
    objeto, armazenamento, formato, simetria = (
        objeto.lower(), armazenamento.lower(), formato.lower(), simetria.lower()
    )
    if objeto != "matrix" or armazenamento != "coordinate":
        raise ErroFormatoRede(
            f"{identificacao}: esperado MatrixMarket matrix coordinate"
        )
    if formato not in {"pattern", "integer", "real"}:
        raise ErroFormatoRede(
            f"{identificacao}: tipo de valores MatrixMarket não suportado: {formato}"
        )
    if simetria != "symmetric":
        raise ErroFormatoRede(
            f"{identificacao}: a matriz declara simetria '{simetria}'; "
            "não será convertida silenciosamente em rede não direcionada"
        )

    linha_dados = None
    for linha in entrada:
        conteudo = linha.strip()
        if conteudo and not conteudo.startswith("%"):
            linha_dados = conteudo
            break
    if linha_dados is None:
        raise ErroFormatoRede(f"{identificacao}: dimensões MatrixMarket ausentes")
    try:
        n_linhas, n_colunas, n_entradas = map(int, linha_dados.split())
    except ValueError as erro:
        raise ErroFormatoRede(
            f"{identificacao}: dimensões MatrixMarket inválidas"
        ) from erro
    if n_linhas < 0 or n_colunas < 0 or n_entradas < 0:
        raise ErroFormatoRede(f"{identificacao}: dimensões negativas")
    if n_linhas != n_colunas:
        raise ErroFormatoRede(
            f"{identificacao}: matriz {n_linhas}x{n_colunas} não é quadrada"
        )

    arestas = []
    registros = 0
    for numero_linha, linha in enumerate(entrada, start=3):
        conteudo = linha.strip()
        if not conteudo or conteudo.startswith("%"):
            continue
        partes = conteudo.split()
        campos_esperados = 2 if formato == "pattern" else 3
        if len(partes) != campos_esperados:
            raise ErroFormatoRede(
                f"{identificacao}:{numero_linha}: registro MatrixMarket inválido"
            )
        try:
            origem, destino = int(partes[0]), int(partes[1])
            valor = 1.0 if formato == "pattern" else float(partes[2])
        except ValueError as erro:
            raise ErroFormatoRede(
                f"{identificacao}:{numero_linha}: índice ou valor inválido"
            ) from erro
        if not (1 <= origem <= n_linhas and 1 <= destino <= n_colunas):
            raise ErroFormatoRede(
                f"{identificacao}:{numero_linha}: índice fora das dimensões declaradas"
            )
        if valor != 0 and origem != destino:
            arestas.append((origem - 1, destino - 1))
        registros += 1
    if registros != n_entradas:
        raise ErroFormatoRede(
            f"{identificacao}: cabeçalho declara {n_entradas} entradas, "
            f"mas foram lidas {registros}"
        )

    grafo = ig.Graph(n=n_linhas, edges=arestas, directed=False)
    grafo.vs["name"] = [str(indice) for indice in range(1, n_linhas + 1)]
    grafo.simplify(multiple=True, loops=True)
    return grafo


def _abrir_matrix_market(caminho: Path) -> Tuple[IO[str], Optional[zipfile.ZipFile]]:
    if zipfile.is_zipfile(caminho):
        arquivo_zip = zipfile.ZipFile(caminho)
        candidatos = [
            nome
            for nome in arquivo_zip.namelist()
            if not nome.endswith("/") and nome.lower().endswith(".mtx")
        ]
        if len(candidatos) != 1:
            arquivo_zip.close()
            raise ErroFormatoRede(
                f"{caminho}: esperado exatamente um arquivo .mtx no ZIP, "
                f"encontrados {len(candidatos)}"
            )
        membro = arquivo_zip.open(candidatos[0], "r")
        return _decodificar_stream(membro), arquivo_zip
    if caminho.suffix.lower() != ".mtx":
        raise ErroFormatoRede(
            f"{caminho}: esperado arquivo ZIP de inf-power ou MatrixMarket .mtx"
        )
    return caminho.open("r", encoding="utf-8"), None


def _decodificar_stream(entrada: IO[bytes]) -> IO[str]:
    import io

    return io.TextIOWrapper(entrada, encoding="utf-8")


def carregar_power_grid(
    caminho: str | Path = "data/inf-power.zip", baixar: bool = True
) -> ig.Graph:
    """Lê a rede elétrica do oeste dos EUA em ZIP ou arquivo MatrixMarket.

    O cabeçalho informa que as ligações são simétricas, portanto a rede não tem
    direção. As dimensões da matriz também preservam vértices isolados. Os IDs
    originais (que começam em 1) são guardados como texto.
    """
    caminho = Path(caminho)
    _garantir_arquivo(caminho, URL_POWER_GRID, baixar)
    arquivo_zip = None
    try:
        entrada, arquivo_zip = _abrir_matrix_market(caminho)
        with entrada:
            grafo = _ler_matrix_market(entrada, str(caminho))
    except (OSError, UnicodeError, zipfile.BadZipFile, EOFError) as erro:
        raise ErroFormatoRede(
            f"não foi possível ler o dataset inf-power {caminho}: {erro}"
        ) from erro
    finally:
        if arquivo_zip is not None:
            arquivo_zip.close()
    grafo["name"] = "Power Grid"
    _registrar_fonte(caminho.parent, "Power Grid", URL_POWER_GRID, caminho)
    return grafo


def carregar_redes(
    diretorio: str | Path = "data", baixar: bool = True
) -> dict[str, ig.Graph]:
    """Lê as duas redes e devolve um dicionário com cada nome e seu grafo."""
    diretorio = Path(diretorio)
    facebook = carregar_facebook(diretorio / "facebook_combined.txt.gz", baixar=baixar)
    power_grid = carregar_power_grid(diretorio / "inf-power.zip", baixar=baixar)
    return {"Facebook": facebook, "Power Grid": power_grid}
