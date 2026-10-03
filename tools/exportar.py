#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML"]
# ///
"""Exporta as notas públicas do vault do Obsidian para o `content/` do Quartz.

Regras na SPEC (specs/SPEC.md, seção 6). Resumo:
- lê o vault (somente leitura) e seleciona notas com `publicar: true` que cumpram as regras;
- escreve só em content/{posts,radar,leituras,assets}, sempre num diretório de
  preparação (staging); só copia para `content/` se a auditoria de privacidade passar;
- mantém `tools/manifesto.json` para URLs estáveis.

Códigos de saída: 0 ok · 1 erros de seleção no modo --estrito · 2 vault indisponível
(arquivos do iCloud não baixados) ou caminho inválido · 3 auditoria de privacidade falhou.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DOMINIO = "thyagoluciano.com.br"

PASTAS_EXCLUIDAS = {"00-Inbox", "90-Templates", "_sistema", ".obsidian", ".smart-env"}
PASTAS_GERADAS = ("posts", "radar", "leituras", "assets")
PASTAS_DE_NOTAS = PASTAS_GERADAS[:3]
EXT_IMAGEM = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

CAMPOS_PERMITIDOS = (
    "title",
    "description",
    "date",
    "published",
    "modified",
    "tags",
    "aliases",
    "publish",
    "gerado",
    "tipo",
    "capa",
    "autor_livro",
    "nota",
    # Radar (tipo: ferramenta)
    "url",
    "repositorio",
    "autor_projeto",
    "categoria",
    "estado",
    "por_que",
    "licenca",
)

# Radar: projetos de outras pessoas que o autor quer usar ou experimentar
ESTADOS_RADAR = ("quero-testar", "testando", "uso", "descartei")
CAMPOS_RADAR_OBRIGATORIOS = ("url", "autor_projeto", "categoria", "estado", "por_que")
CAMPOS_RADAR_OPCIONAIS = ("repositorio", "licenca")
TIPOS_SO_NO_OBSIDIAN = ("ideia", "mapa")  # continuam no vault, nunca vão para o site
URL_HTTP = re.compile(r"^https?://\S+$", re.I)

SF_DATALESS = 0x40000000  # arquivo do iCloud que ainda não foi baixado
TENTATIVAS_DOWNLOAD = 3
ESPERA_DOWNLOAD = 2.0  # segundos entre tentativas (os testes zeram)

MARCA_INICIO = "<!-- gerado:lendo-agora -->"
MARCA_FIM = "<!-- /gerado:lendo-agora -->"

PREFIXO = re.compile(
    r"^(?:Site|Livro|Mapa|Ideia|Encontro|Fonte|Conteúdo|Conteudo|Destaques|Clube|Artigo|Ferramenta) - "
)
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---[ \t]*\n(.*?)^---[ \t]*$\n?(.*)\Z", re.S | re.M)
PUBLICAR_NO_TEXTO = re.compile(r"^publicar:\s*(?:true|sim|yes)\b", re.M | re.I)


# ---------------------------------------------------------------------------
# Erros
# ---------------------------------------------------------------------------


class VaultIndisponivel(Exception):
    """Arquivos do iCloud que não puderam ser baixados (ou caminho inválido)."""

    def __init__(self, arquivos: list[str], mensagem: str | None = None):
        self.arquivos = arquivos
        super().__init__(mensagem or "Arquivos do vault não baixados do iCloud")


class ArquivoNaoBaixado(Exception):
    def __init__(self, caminho: str):
        self.caminho = caminho
        super().__init__(caminho)


# ---------------------------------------------------------------------------
# Leitura do vault (iCloud)
# ---------------------------------------------------------------------------


def _esta_offline(caminho: Path) -> bool:
    try:
        return bool(getattr(os.stat(caminho), "st_flags", 0) & SF_DATALESS)
    except OSError:
        return False


def _baixar(caminho: Path) -> None:
    try:
        subprocess.run(
            ["brctl", "download", str(caminho)], check=False, capture_output=True, timeout=60
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def ler_bytes(caminho: Path) -> bytes:
    """Lê um arquivo do vault; se estiver só na nuvem, pede o download e tenta de novo."""
    for tentativa in range(TENTATIVAS_DOWNLOAD + 1):
        try:
            if _esta_offline(caminho):
                raise OSError(errno.EDEADLK, "arquivo não baixado", str(caminho))
            with open(caminho, "rb") as f:
                return f.read()
        except OSError as e:
            if e.errno != errno.EDEADLK:
                raise
            if tentativa == TENTATIVAS_DOWNLOAD:
                break
            _baixar(caminho)
            time.sleep(ESPERA_DOWNLOAD)
    raise ArquivoNaoBaixado(str(caminho))


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------


def nfc(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


def chave(texto: str) -> str:
    return nfc(texto).strip().casefold()


def strip_prefixo(titulo: str) -> str:
    return PREFIXO.sub("", nfc(titulo).strip()).strip()


@dataclass
class Nota:
    caminho: str  # relativo ao vault, com "/"
    fm: dict | None
    corpo: str
    erro_yaml: str | None = None

    @property
    def stem(self) -> str:
        return nfc(Path(self.caminho).stem)

    @property
    def titulo(self) -> str:
        bruto = (self.fm or {}).get("titulo")
        return strip_prefixo(str(bruto)) if bruto else strip_prefixo(self.stem)


@dataclass
class Elegivel:
    nota: Nota
    slug: str
    pasta: str  # posts, radar, leituras, leituras/encontros
    tipo: str  # post, ferramenta, resenha, encontro
    titulo: str

    @property
    def rel_saida(self) -> str:
        return f"{self.pasta}/{self.slug}.md"

    @property
    def rota(self) -> str:
        return f"{self.pasta}/{self.slug}"

    @property
    def url(self) -> str:
        return f"https://{DOMINIO}/{self.rota}"


@dataclass
class Vault:
    raiz: Path
    notas: dict[str, Nota] = field(default_factory=dict)
    arquivos: dict[str, list[str]] = field(default_factory=dict)  # nome -> caminhos (fora das pastas excluídas)
    nao_baixados: list[str] = field(default_factory=list)


def _parse_nota(caminho: str, dados: bytes) -> Nota:
    texto = dados.decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    m = FRONTMATTER.match(texto)
    if not m:
        return Nota(caminho, {}, texto)
    bruto, corpo = m.group(1), m.group(2)
    try:
        fm = yaml.safe_load(bruto) or {}
        if not isinstance(fm, dict):
            raise yaml.YAMLError("frontmatter não é um mapa")
    except yaml.YAMLError as e:
        if PUBLICAR_NO_TEXTO.search(bruto):
            return Nota(caminho, None, corpo, erro_yaml=str(e).splitlines()[0])
        return Nota(caminho, {}, corpo)
    return Nota(caminho, fm, corpo)


def varrer_vault(raiz: Path) -> Vault:
    vault = Vault(raiz)
    for dirpath, dirnames, filenames in os.walk(raiz):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        rel_dir = Path(dirpath).relative_to(raiz)
        excluida = any(p in PASTAS_EXCLUIDAS for p in rel_dir.parts)
        for nome in sorted(filenames):
            if nome.startswith("."):
                continue
            rel = (rel_dir / nome).as_posix()
            if nome.lower().endswith(".md"):
                try:
                    vault.notas[rel] = _parse_nota(rel, ler_bytes(Path(dirpath) / nome))
                except ArquivoNaoBaixado:
                    vault.nao_baixados.append(rel)
            elif not excluida:
                vault.arquivos.setdefault(chave(nome), []).append(rel)
    return vault


# ---------------------------------------------------------------------------
# Seleção (6.1 e 6.2)
# ---------------------------------------------------------------------------


def para_data(valor) -> date | None:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor.strip()[:10])
        except ValueError:
            return None
    return None


def destino_de(fm: dict) -> tuple[str, str] | None:
    tipo, sub = fm.get("tipo"), fm.get("subtipo")
    if tipo == "conteudo" and fm.get("canal") == "site":
        return "posts", "post"
    if tipo == "ferramenta":
        return "radar", "ferramenta"
    if tipo == "fonte" and sub == "livro":
        return "leituras", "resenha"
    if tipo == "encontro":
        return "leituras/encontros", "encontro"
    return None


def verificar_ferramenta(fm: dict) -> list[str]:
    """Campos do Radar (PRD RF1): obrigatórios, estado válido e endereço http(s)."""
    motivos: list[str] = []
    for campo in CAMPOS_RADAR_OBRIGATORIOS:
        valor = fm.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            motivos.append(f"ferramenta sem '{campo}'")
    estado = fm.get("estado")
    if isinstance(estado, str) and estado.strip() and estado.strip() not in ESTADOS_RADAR:
        motivos.append(f"estado '{estado}' inválido (use {', '.join(ESTADOS_RADAR)})")
    for campo in ("url", "repositorio"):
        valor = fm.get(campo)
        if isinstance(valor, str) and valor.strip() and not URL_HTTP.match(valor.strip()):
            motivos.append(f"'{campo}' deve começar com http:// ou https://")
    return motivos


def verificar(nota: Nota, hoje: date) -> list[str]:
    """Motivos pelos quais uma nota com `publicar: true` não pode ser exportada."""
    if nota.erro_yaml:
        return [f"frontmatter inválido ({nota.erro_yaml})"]
    fm = nota.fm or {}
    motivos: list[str] = []
    if any(p in PASTAS_EXCLUIDAS for p in Path(nota.caminho).parts[:-1]):
        return ["nota em pasta que nunca é exportada (00-Inbox, 90-Templates, _sistema)"]
    if fm.get("subtipo") == "destaques":
        return ["subtipo 'destaques' nunca é exportado"]
    destino = destino_de(fm)
    if destino is None:
        if fm.get("tipo") == "conteudo":
            motivos.append(f"canal '{fm.get('canal')}' não é 'site'")
        elif fm.get("tipo") in TIPOS_SO_NO_OBSIDIAN:
            motivos.append(
                f"tipo '{fm.get('tipo')}' não é publicado no site (fica só no Obsidian); "
                "remova 'publicar: true'"
            )
        else:
            motivos.append(f"tipo '{fm.get('tipo')}' não é exportável")
    slug = fm.get("slug")
    if not isinstance(slug, str) or not slug:
        motivos.append("sem slug")
    elif not SLUG.match(slug):
        motivos.append(f"slug '{slug}' inválido (use a-z, 0-9 e hífens)")
    elif slug == "index":
        motivos.append("slug 'index' é reservado")
    elif destino and destino[0] == "leituras" and slug == "encontros":
        motivos.append("slug 'encontros' é reservado em leituras")
    descricao = fm.get("descricao")
    if not isinstance(descricao, str) or not descricao.strip():
        motivos.append("sem descricao")
    elif len(descricao.strip()) > 160:
        motivos.append(f"descricao com {len(descricao.strip())} caracteres (máximo 160)")
    if destino and destino[1] == "ferramenta":
        motivos.extend(verificar_ferramenta(fm))
    if fm.get("tipo") == "conteudo" and destino:
        status = fm.get("status")
        if status not in ("publicado", "agendado"):
            motivos.append(f"status '{status}' (esperado publicado ou agendado)")
        elif status == "agendado":
            quando = para_data(fm.get("data_publicacao"))
            if quando is None:
                motivos.append("agendado sem data_publicacao válida")
            elif quando > hoje:
                motivos.append(f"agendado para {quando.isoformat()} (ainda no futuro)")
    return motivos


def selecionar(vault: Vault, hoje: date) -> tuple[dict[str, Elegivel], list[dict]]:
    elegiveis: dict[str, Elegivel] = {}
    erros: list[dict] = []
    for caminho, nota in sorted(vault.notas.items()):
        valor = (nota.fm or {}).get("publicar")
        if nota.fm is not None and valor is not True:
            if isinstance(valor, str) and valor.strip().casefold() in ("true", "sim", "yes"):
                erros.append({"nota": caminho, "motivo": "publicar deve ser o booleano true, não texto"})
            continue
        if nota.fm is None and not nota.erro_yaml:
            continue
        motivos = verificar(nota, hoje)
        if motivos:
            erros.extend({"nota": caminho, "motivo": m} for m in motivos)
            continue
        pasta, tipo = destino_de(nota.fm)
        elegiveis[caminho] = Elegivel(nota, nota.fm["slug"], pasta, tipo, nota.titulo)
    # slugs duplicados entre as elegíveis
    por_slug: dict[str, list[str]] = {}
    for caminho, el in elegiveis.items():
        por_slug.setdefault(f"{el.pasta}/{el.slug}", []).append(caminho)
    for rota, caminhos in por_slug.items():
        if len(caminhos) > 1:
            for c in caminhos:
                outros = ", ".join(x for x in caminhos if x != c)
                erros.append({"nota": c, "motivo": f"slug duplicado '{rota}' (também em {outros})"})
                del elegiveis[c]
    return elegiveis, erros


# ---------------------------------------------------------------------------
# Transformação do corpo (6.4)
# ---------------------------------------------------------------------------

COMENTARIO_OBSIDIAN = re.compile(r"%%.*?(?:%%|\Z)", re.S)
COMENTARIO_HTML = re.compile(r"<!--.*?(?:-->|\Z)", re.S)
MARCADOR_VAZIO = re.compile(r"^\s*(?:[-*+]|\d+[.)]|>+)\s*$")
PLACEHOLDER = re.compile(r"^\s*(?:<%.*?%>|\{\{[^}]*\}\})\s*$")
CERCA = re.compile(r"^\s*(?:```|~~~)")
CABECALHO = re.compile(r"^(#{1,6})\s+\S")
H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$")
CODIGO = re.compile(r"(```.*?(?:```|\Z)|~~~.*?(?:~~~|\Z)|`[^`\n]+`)", re.S)
EMBED = re.compile(r"!\[\[([^\[\]|]+?)(?:\|([^\[\]]*))?\]\]")
WIKILINK = re.compile(r"(?<!!)\[\[([^\[\]|]*?)(?:\|([^\[\]]*))?\]\]")


def fora_de_codigo(texto: str, fn) -> str:
    partes = CODIGO.split(texto)
    return "".join(p if i % 2 else fn(p) for i, p in enumerate(partes))


def limpar_linhas(texto: str) -> str:
    """Passo 2: marcadores vazios, placeholders e cabeçalhos de seções vazias."""
    itens: list[tuple[str, bool]] = []
    em_codigo = False
    for linha in texto.split("\n"):
        if CERCA.match(linha):
            em_codigo = not em_codigo
            itens.append((linha, True))
        elif em_codigo:
            itens.append((linha, True))
        elif MARCADOR_VAZIO.match(linha) or PLACEHOLDER.match(linha):
            continue
        else:
            itens.append((linha, False))
    mudou = True
    while mudou:
        mudou = False
        for i, (linha, codigo) in enumerate(itens):
            m = None if codigo else CABECALHO.match(linha)
            if not m:
                continue
            j = i + 1
            while j < len(itens) and not itens[j][1] and not itens[j][0].strip():
                j += 1
            if j >= len(itens):
                vazio = True
            else:
                seguinte = None if itens[j][1] else CABECALHO.match(itens[j][0])
                vazio = bool(seguinte) and len(seguinte.group(1)) <= len(m.group(1))
            if vazio:
                del itens[i]
                mudou = True
                break
    return colapsar_brancos(itens)


def colapsar_brancos(itens: list[tuple[str, bool]]) -> str:
    saida: list[str] = []
    for linha, codigo in itens:
        if not codigo and not linha.strip() and saida and not saida[-1].strip():
            continue
        saida.append(linha)
    return "\n".join(saida).strip("\n")


def marcar_codigo(texto: str) -> list[tuple[str, bool]]:
    itens, em_codigo = [], False
    for linha in texto.split("\n"):
        if CERCA.match(linha):
            em_codigo = not em_codigo
            itens.append((linha, True))
        else:
            itens.append((linha, em_codigo))
    return itens


def remover_h1_repetido(texto: str, titulo: str, titulo_bruto: str | None) -> str:
    linhas = texto.split("\n")
    for i, linha in enumerate(linhas):
        if not linha.strip():
            continue
        m = H1.match(linha)
        if m:
            visto = nfc(m.group(1)).strip()
            if visto == titulo or strip_prefixo(visto) == titulo or visto == (titulo_bruto or ""):
                resto = linhas[i + 1 :]
                while resto and not resto[0].strip():
                    resto.pop(0)
                return "\n".join(linhas[:i] + resto)
        break
    return texto


class Indice:
    """Resolve alvos de wikilink para notas elegíveis."""

    def __init__(self, elegiveis: dict[str, Elegivel]):
        self.por_caminho: dict[str, Elegivel] = {}
        self.por_nome: dict[str, list[Elegivel]] = {}
        for caminho, el in sorted(elegiveis.items()):
            sem_ext = caminho[:-3] if caminho.lower().endswith(".md") else caminho
            self.por_caminho[chave(sem_ext)] = el
            self.por_nome.setdefault(chave(el.nota.stem), []).append(el)

    def resolver(self, alvo: str) -> Elegivel | None:
        alvo = alvo.strip()
        if alvo.lower().endswith(".md"):
            alvo = alvo[:-3]
        if "/" in alvo:
            achado = self.por_caminho.get(chave(alvo))
            if achado:
                return achado
        candidatos = self.por_nome.get(chave(alvo.rsplit("/", 1)[-1]), [])
        return candidatos[0] if candidatos else None


@dataclass
class Contexto:
    vault: Vault
    indice: Indice
    assets: dict[str, bytes] = field(default_factory=dict)  # "assets/x.png" -> bytes
    avisos: list[str] = field(default_factory=list)
    nao_baixados: list[str] = field(default_factory=list)


def _nome_seguro(nome: str) -> str:
    return re.sub(r"[^\w.\-]+", "-", nfc(nome)).strip("-") or "imagem"


def copiar_imagem(ref: str, origem: str, ctx: Contexto) -> str | None:
    """Copia a imagem citada para assets/ (na memória) e devolve o novo caminho."""
    ref = ref.strip()
    candidatos = ctx.vault.arquivos.get(chave(Path(ref).name), [])
    escolhido = next((c for c in candidatos if chave(c) == chave(ref)), None)
    if escolhido is None:
        sufixo = [c for c in candidatos if chave(c).endswith("/" + chave(ref))]
        escolhido = (sufixo or candidatos or [None])[0]
    if escolhido is None:
        ctx.avisos.append(f"{origem}: imagem '{ref}' não encontrada no vault; embed removido")
        return None
    caminho = ctx.vault.raiz / escolhido
    if not caminho.resolve().is_relative_to(ctx.vault.raiz.resolve()):
        ctx.avisos.append(f"{origem}: imagem '{ref}' aponta para fora do vault; embed removido")
        return None
    try:
        dados = ler_bytes(caminho)
    except ArquivoNaoBaixado:
        ctx.nao_baixados.append(escolhido)
        return None
    destino = f"assets/{hashlib.sha256(dados).hexdigest()[:8]}-{_nome_seguro(Path(escolhido).name)}"
    ctx.assets[destino] = dados
    return destino


def transformar_corpo(el: Elegivel, ctx: Contexto) -> str:
    texto = el.nota.corpo.replace("\r\n", "\n")
    texto = COMENTARIO_OBSIDIAN.sub("", texto)
    texto = COMENTARIO_HTML.sub("", texto)
    texto = limpar_linhas(texto)
    bruto = (el.nota.fm or {}).get("titulo")
    texto = remover_h1_repetido(texto, el.titulo, nfc(str(bruto)) if bruto else None)

    def embeds(m: re.Match) -> str:
        alvo, extra = m.group(1).split("#", 1)[0].strip(), m.group(2)
        if Path(alvo).suffix.lower() in EXT_IMAGEM:
            novo = copiar_imagem(alvo, el.nota.caminho, ctx)
            if novo:
                return f"![[{novo}{'|' + extra if extra else ''}]]"
        elif Path(alvo).suffix.lower() not in ("", ".md"):
            ctx.avisos.append(f"{el.nota.caminho}: embed '{alvo}' não é imagem; removido")
        return ""

    def links(m: re.Match) -> str:
        alvo, apelido = m.group(1), (m.group(2) or "").strip()
        nome, _, secao = alvo.partition("#")
        if not nome.strip():
            return m.group(0)  # link para a própria nota
        destino = ctx.indice.resolver(nome)
        if destino is None:
            return apelido or strip_prefixo(nome.strip().rsplit("/", 1)[-1])
        texto_link = apelido or destino.titulo
        return f"[[{destino.rota}{'#' + secao if secao else ''}|{texto_link}]]"

    def tudo(trecho: str) -> str:
        return WIKILINK.sub(links, EMBED.sub(embeds, trecho))

    texto = fora_de_codigo(texto, tudo)
    return colapsar_brancos(marcar_codigo(texto))


# ---------------------------------------------------------------------------
# Frontmatter de saída (6.3)
# ---------------------------------------------------------------------------


def para_iso(valor) -> str | None:
    if isinstance(valor, datetime):
        return valor.isoformat(timespec="minutes") if valor.time() != datetime.min.time() else valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, str) and para_data(valor):
        return valor.strip()
    return None


def _lista(valor) -> list:
    if valor is None:
        return []
    if isinstance(valor, str):
        return [v.strip() for v in valor.split(",") if v.strip()]
    if isinstance(valor, (list, tuple)):
        return list(valor)
    return [valor]


def _nome_do_link(valor) -> str:
    m = re.fullmatch(r"\s*!?\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]\s*", str(valor))
    return (m.group(1) if m else str(valor)).strip()


def montar_frontmatter(el: Elegivel, ctx: Contexto, aliases: list[str]) -> dict:
    fm = el.nota.fm or {}
    saida: dict = {"title": el.titulo, "description": fm["descricao"].strip()}
    data = para_iso(fm.get("data_publicacao")) or para_iso(fm.get("criado"))
    if data:
        saida["date"] = data
        saida["published"] = data
    modificado = para_iso(fm.get("atualizado"))
    if modificado:
        saida["modified"] = modificado
    tags = [str(t).lstrip("#").strip() for t in _lista(fm.get("tags"))]
    tags = [t for t in tags if t]
    if tags:
        saida["tags"] = tags
    if aliases:
        saida["aliases"] = aliases
    saida["publish"] = True
    saida["gerado"] = True
    saida["tipo"] = el.tipo
    if fm.get("capa"):
        nome = _nome_do_link(fm["capa"])
        if Path(nome).suffix.lower() in EXT_IMAGEM:
            capa = copiar_imagem(nome, el.nota.caminho, ctx)
            if capa:
                saida["capa"] = capa
        else:
            ctx.avisos.append(f"{el.nota.caminho}: capa '{nome}' não é imagem; ignorada")
    if el.tipo == "ferramenta":
        for campo in (*CAMPOS_RADAR_OBRIGATORIOS, *CAMPOS_RADAR_OPCIONAIS):
            valor = fm.get(campo)
            if isinstance(valor, str) and valor.strip():
                saida[campo] = valor.strip()
    if el.tipo == "resenha":
        if fm.get("autor"):
            saida["autor_livro"] = strip_prefixo(_nome_do_link(fm["autor"]))
            saida["autor_livro"] = re.sub(r"^Autor - ", "", saida["autor_livro"])
        nota = fm.get("nota")
        if isinstance(nota, int) and not isinstance(nota, bool) and 1 <= nota <= 5:
            saida["nota"] = nota
        elif nota not in (None, ""):
            ctx.avisos.append(f"{el.nota.caminho}: nota '{nota}' fora de 1–5; ignorada")
    return saida


def serializar(fm: dict, corpo: str) -> str:
    cabecalho = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10_000).rstrip("\n")
    return f"---\n{cabecalho}\n---\n\n{corpo}\n" if corpo else f"---\n{cabecalho}\n---\n"


# ---------------------------------------------------------------------------
# Manifesto (6.7)
# ---------------------------------------------------------------------------


def ler_manifesto(caminho: Path) -> dict:
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {}


def escrever_manifesto(caminho: Path, manifesto: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def reconciliar(antigo: dict, elegiveis: dict[str, Elegivel], hoje: date):
    """Devolve (novo manifesto sem sha256, aliases por nota, entradas recém-removidas)."""
    ativas = {k: e for k, e in antigo.items() if "removida" not in e}
    por_slug = {e["slug"]: k for k, e in antigo.items() if "removida" in e}
    por_slug.update({e["slug"]: k for k, e in ativas.items()})
    usadas: set[str] = set()
    novo: dict[str, dict] = {}
    aliases: dict[str, list[str]] = {}
    for caminho, el in sorted(elegiveis.items()):
        origem = caminho if caminho in antigo else por_slug.get(el.slug)
        if origem in usadas:
            origem = None
        herdada = antigo.get(origem) if origem else None
        slugs_ant = list(herdada.get("slugs_anteriores", [])) if herdada else []
        destinos_ant = list(herdada.get("destinos_anteriores", [])) if herdada else []
        if herdada:
            usadas.add(origem)
            if herdada["slug"] != el.slug:
                slugs_ant.append(herdada["slug"])
            anterior = herdada["destino"].removesuffix(".md")
            if anterior != el.rota:
                destinos_ant.append(anterior)
        slugs_ant = sorted({s for s in slugs_ant if s != el.slug})
        destinos_ant = sorted({d for d in destinos_ant if d != el.rota})
        aliases[caminho] = sorted(
            ({f"{el.pasta}/{s}" for s in slugs_ant} | set(destinos_ant)) - {el.rota}
        )
        entrada = {"slug": el.slug, "slugs_anteriores": slugs_ant, "destino": el.rel_saida}
        if destinos_ant:
            entrada["destinos_anteriores"] = destinos_ant
        novo[caminho] = entrada
    removidas: list[dict] = []
    for caminho, e in sorted(antigo.items()):
        if caminho in usadas or caminho in novo:
            continue
        if "removida" in e:
            novo[caminho] = e
        else:
            novo[caminho] = {**e, "removida": hoje.isoformat()}
            removidas.append(e)
    return novo, aliases, removidas


# ---------------------------------------------------------------------------
# Auditoria de privacidade (6.6)
# ---------------------------------------------------------------------------


def _ler_fm_arquivo(caminho: Path) -> dict | None:
    m = FRONTMATTER.match(caminho.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None
    try:
        dados = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None
    return dados if isinstance(dados, dict) else None


def _existe_pagina(content: Path, alvo: str) -> bool:
    alvo = alvo.strip().strip("/")
    if alvo.lower().endswith(".md"):
        alvo = alvo[:-3]
    return (
        (content / f"{alvo}.md").is_file()
        or (content / alvo / "index.md").is_file()
        or (content / alvo).is_file()
    )


def auditar(content: Path, produzidos: dict[str, Elegivel], hoje: date) -> list[str]:
    violacoes: list[str] = []
    gerados: dict[str, dict] = {}
    for pasta in PASTAS_DE_NOTAS:
        base = content / pasta
        for arq in sorted(base.rglob("*.md")) if base.exists() else []:
            fm = _ler_fm_arquivo(arq)
            if fm and fm.get("gerado") is True and arq.name != "index.md":
                gerados[arq.relative_to(content).as_posix()] = fm

    # 1. origem: só notas elegíveis
    for rel in sorted(gerados):
        if rel not in produzidos:
            violacoes.append(f"{rel}: arquivo gerado sem nota elegível correspondente")
    for rel, el in sorted(produzidos.items()):
        if rel not in gerados:
            violacoes.append(f"{rel}: arquivo esperado não foi gerado")
        motivos = verificar(el.nota, hoje)
        if motivos or (el.nota.fm or {}).get("publicar") is not True:
            violacoes.append(f"{rel}: origem '{el.nota.caminho}' não é elegível ({'; '.join(motivos)})")

    referencias: set[str] = set()
    todos_md = sorted(content.rglob("*.md"))
    for arq in todos_md:
        for m in re.finditer(r"assets/[^\]|)\s\"'#]+", arq.read_text(encoding="utf-8", errors="replace")):
            referencias.add(m.group(0))

    for rel in sorted(gerados):
        arquivo = content / rel
        texto = arquivo.read_text(encoding="utf-8")
        fm = gerados[rel]
        # 3. frontmatter
        for campo in fm:
            if campo not in CAMPOS_PERMITIDOS:
                violacoes.append(f"{rel}: campo '{campo}' fora da lista de permissão")
        # 4. resíduos
        for padrao in ("%%", "<!--", "Destaques - "):
            if padrao in texto:
                violacoes.append(f"{rel}: contém '{padrao}'")
        # 2. links
        sem_codigo = "".join(CODIGO.split(texto)[0::2])
        for m in WIKILINK.finditer(sem_codigo):
            nome = m.group(1).split("#", 1)[0].strip()
            if nome and not _existe_pagina(content, nome):
                violacoes.append(f"{rel}: link [[{nome}]] aponta para página inexistente")
        for m in EMBED.finditer(sem_codigo):
            nome = m.group(1).split("#", 1)[0].strip()
            if not (content / nome).is_file():
                violacoes.append(f"{rel}: embed ![[{nome}]] aponta para arquivo inexistente")
        if fm.get("capa") and not (content / str(fm["capa"])).is_file():
            violacoes.append(f"{rel}: capa '{fm['capa']}' inexistente")

    # 5. imagens sem referência
    pasta_assets = content / "assets"
    if pasta_assets.exists():
        for arq in sorted(p for p in pasta_assets.rglob("*") if p.is_file()):
            rel = arq.relative_to(content).as_posix()
            if rel not in referencias:
                violacoes.append(f"{rel}: imagem sem referência")

    # bloco gerado das páginas fixas
    for arq in todos_md:
        texto = arq.read_text(encoding="utf-8", errors="replace")
        bloco = _bloco(texto)
        if bloco is None:
            continue
        rel = arq.relative_to(content).as_posix()
        for padrao in ("%%", "Destaques - "):
            if padrao in bloco:
                violacoes.append(f"{rel}: bloco 'lendo agora' contém '{padrao}'")
        for m in WIKILINK.finditer(bloco):
            nome = m.group(1).split("#", 1)[0].strip()
            if nome and not _existe_pagina(content, nome):
                violacoes.append(f"{rel}: bloco 'lendo agora' com link [[{nome}]] inexistente")
    return violacoes


# ---------------------------------------------------------------------------
# Bloco "lendo agora" (6.8)
# ---------------------------------------------------------------------------

BLOCO = re.compile(re.escape(MARCA_INICIO) + r"(.*?)" + re.escape(MARCA_FIM), re.S)


def _bloco(texto: str) -> str | None:
    m = BLOCO.search(texto)
    return m.group(1) if m else None


def montar_lendo_agora(elegiveis: dict[str, Elegivel]) -> str:
    livros = sorted(
        (e for e in elegiveis.values() if e.tipo == "resenha" and (e.nota.fm or {}).get("status_leitura") == "lendo"),
        key=lambda e: e.titulo.casefold(),
    )
    if not livros:
        return "Nenhum livro em leitura no momento."
    linhas = []
    for livro in livros:
        autor = (livro.nota.fm or {}).get("autor")
        nome_autor = re.sub(r"^Autor - ", "", strip_prefixo(_nome_do_link(autor))) if autor else ""
        linha = f"- [[{livro.rota}|{livro.titulo}]]"
        linhas.append(f"{linha}, de {nome_autor}" if nome_autor else linha)
    return "\n".join(linhas)


def atualizar_lendo_agora(content: Path, elegiveis: dict[str, Elegivel], avisos: list[str]) -> None:
    alvo = content / "leituras" / "index.md"
    if not alvo.exists():
        avisos.append("leituras/index.md não existe; bloco 'lendo agora' não atualizado")
        return
    texto = alvo.read_text(encoding="utf-8")
    if not BLOCO.search(texto):
        avisos.append("leituras/index.md sem os marcadores de 'lendo agora'; bloco não atualizado")
        return
    novo = BLOCO.sub(
        lambda _: f"{MARCA_INICIO}\n{montar_lendo_agora(elegiveis)}\n{MARCA_FIM}", texto, count=1
    )
    if novo != texto:
        alvo.write_text(novo, encoding="utf-8")


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


@dataclass
class Resultado:
    novas: list[dict] = field(default_factory=list)
    alteradas: list[dict] = field(default_factory=list)
    removidas: list[dict] = field(default_factory=list)
    erros: list[dict] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    violacoes: list[str] = field(default_factory=list)
    abortado: bool = False
    aplicado: bool = False
    simulacao: bool = False

    def para_dict(self) -> dict:
        return {
            "novas": self.novas,
            "alteradas": self.alteradas,
            "removidas": self.removidas,
            "erros": self.erros,
            "avisos": self.avisos,
            "auditoria": {"ok": not self.violacoes, "violacoes": self.violacoes},
            "abortado": self.abortado,
            "aplicado": self.aplicado,
            "simulacao": self.simulacao,
        }


def _e_gerado(caminho: Path) -> bool:
    fm = _ler_fm_arquivo(caminho) if caminho.suffix == ".md" else None
    return bool(fm and fm.get("gerado") is True)


def _sincronizar(staging: Path, destino: Path) -> None:
    for pasta in PASTAS_GERADAS:
        origem, alvo = staging / pasta, destino / pasta
        arq_o = {p.relative_to(origem) for p in origem.rglob("*") if p.is_file()} if origem.exists() else set()
        arq_d = {p.relative_to(alvo) for p in alvo.rglob("*") if p.is_file()} if alvo.exists() else set()
        for rel in sorted(arq_o):
            novo, atual = origem / rel, alvo / rel
            if rel not in arq_d or novo.read_bytes() != atual.read_bytes():
                atual.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(novo, atual)
        for rel in sorted(arq_d - arq_o):
            (alvo / rel).unlink()
        if alvo.exists():
            for d in sorted((p for p in alvo.rglob("*") if p.is_dir()), reverse=True):
                if not any(d.iterdir()):
                    d.rmdir()


def exportar(
    vault_dir: Path,
    content: Path,
    manifesto_path: Path,
    *,
    simular: bool = False,
    estrito: bool = False,
    hoje: date | None = None,
) -> Resultado:
    hoje = hoje or date.today()
    res = Resultado(simulacao=simular)
    if not vault_dir.is_dir():
        raise VaultIndisponivel([], f"Vault não encontrado: {vault_dir}")

    vault = varrer_vault(vault_dir)
    if vault.nao_baixados:
        raise VaultIndisponivel(sorted(vault.nao_baixados))

    elegiveis, res.erros = selecionar(vault, hoje)

    # conflito com arquivos fixos (nunca sobrescrever o que não foi gerado)
    for caminho, el in sorted(elegiveis.items()):
        existente = content / el.rel_saida
        if existente.exists() and not _e_gerado(existente):
            res.erros.append(
                {"nota": caminho, "motivo": f"'{el.rel_saida}' já existe e não é arquivo gerado"}
            )
            del elegiveis[caminho]

    if estrito and res.erros:
        res.abortado = True
        return res

    manifesto_antigo = ler_manifesto(manifesto_path)
    manifesto, aliases, removidas_manifesto = reconciliar(manifesto_antigo, elegiveis, hoje)

    ctx = Contexto(vault, Indice(elegiveis))
    saidas: dict[str, str] = {}
    for caminho, el in sorted(elegiveis.items()):
        corpo = transformar_corpo(el, ctx)
        fm = montar_frontmatter(el, ctx, aliases[caminho])
        saidas[el.rel_saida] = serializar(fm, corpo)
    if ctx.nao_baixados:
        raise VaultIndisponivel(sorted(set(ctx.nao_baixados)))
    res.avisos = ctx.avisos
    for caminho, el in elegiveis.items():
        manifesto[caminho]["sha256"] = hashlib.sha256(saidas[el.rel_saida].encode()).hexdigest()

    with tempfile.TemporaryDirectory(prefix="exportar-") as tmp:
        staging = Path(tmp) / "content"
        if content.exists():
            shutil.copytree(content, staging)
        staging.mkdir(exist_ok=True)

        # arquivos gerados que deixaram de existir
        removidos: list[str] = []
        for pasta in PASTAS_DE_NOTAS:
            base = staging / pasta
            for arq in sorted(base.rglob("*.md")) if base.exists() else []:
                rel = arq.relative_to(staging).as_posix()
                if arq.name != "index.md" and rel not in saidas and _e_gerado(arq):
                    arq.unlink()
                    removidos.append(rel)
        # assets são 100% gerados
        shutil.rmtree(staging / "assets", ignore_errors=True)

        for rel, texto in sorted(saidas.items()):
            destino = staging / rel
            existia = (content / rel).exists()
            antes = (content / rel).read_text(encoding="utf-8") if existia else None
            item = {"titulo": _titulo_de(elegiveis, rel), "url": f"https://{DOMINIO}/{rel[:-3]}", "caminho": rel}
            if antes is None:
                res.novas.append(item)
            elif antes != texto:
                res.alteradas.append(item)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding="utf-8")
        for rel, dados in sorted(ctx.assets.items()):
            (staging / rel).parent.mkdir(parents=True, exist_ok=True)
            (staging / rel).write_bytes(dados)

        atualizar_lendo_agora(staging, elegiveis, res.avisos)

        for rel in removidos:
            res.removidas.append({"url": f"https://{DOMINIO}/{rel[:-3]}", "caminho": rel})
        conhecidas = {r["caminho"] for r in res.removidas}
        for entrada in removidas_manifesto:
            rel = entrada["destino"]
            if rel not in conhecidas:
                res.removidas.append({"url": f"https://{DOMINIO}/{rel[:-3]}", "caminho": rel})

        produzidos = {el.rel_saida: el for el in elegiveis.values()}
        res.violacoes = auditar(staging, produzidos, hoje)
        if res.violacoes:
            return res
        if not simular:
            _sincronizar(staging, content)
            escrever_manifesto(manifesto_path, manifesto)
            res.aplicado = True
    return res


def _titulo_de(elegiveis: dict[str, Elegivel], rel: str) -> str:
    return next(e.titulo for e in elegiveis.values() if e.rel_saida == rel)


# ---------------------------------------------------------------------------
# Linha de comando
# ---------------------------------------------------------------------------


def resolver_vault(arg: str | None) -> Path | None:
    if arg:
        return Path(arg).expanduser()
    if os.environ.get("SB_VAULT"):
        return Path(os.environ["SB_VAULT"]).expanduser()
    config = Path(__file__).resolve().parent / "config.toml"
    if config.exists():
        dados = tomllib.loads(config.read_text(encoding="utf-8"))
        if dados.get("vault"):
            return Path(dados["vault"]).expanduser()
    return None


def imprimir_resumo(res: Resultado) -> None:
    modo = "SIMULAÇÃO (nada foi escrito)" if res.simulacao else "Exportação"
    print(f"{modo}\n")

    def bloco(titulo: str, itens: list[dict], marca: str) -> None:
        print(f"{titulo} ({len(itens)})")
        for i in itens:
            rotulo = i.get("titulo") or i["caminho"]
            print(f"  {marca} {rotulo}\n      {i['url']}")

    bloco("Novas", res.novas, "+")
    bloco("Alteradas", res.alteradas, "~")
    bloco("Removidas", res.removidas, "-")
    print(f"Erros ({len(res.erros)})")
    for e in res.erros:
        print(f"  ! {e['nota']}: {e['motivo']}")
    if res.avisos:
        print(f"Avisos ({len(res.avisos)})")
        for a in res.avisos:
            print(f"  ? {a}")
    if res.abortado:
        print("\nModo --estrito: exportação abortada, nada foi escrito.")
    elif res.violacoes:
        print(f"\nAuditoria de privacidade: {len(res.violacoes)} ocorrência(s), nada foi escrito")
        for v in res.violacoes:
            print(f"  ✗ {v}")
    else:
        print("\nAuditoria de privacidade: sem ocorrências")
    print(
        f"\nResumo: {len(res.novas)} novas / {len(res.alteradas)} alteradas / "
        f"{len(res.removidas)} removidas / {len(res.erros)} erros"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Exporta as notas públicas do vault para content/")
    p.add_argument("--vault", help="caminho do vault (senão SB_VAULT ou tools/config.toml)")
    p.add_argument("--simular", action="store_true", help="mostra o resumo sem escrever nada")
    p.add_argument("--estrito", action="store_true", help="aborta tudo se qualquer nota tiver erro")
    p.add_argument("--json", action="store_true", help="resumo em JSON")
    p.add_argument("--saida-json", help="grava também o resumo em JSON neste arquivo")
    p.add_argument("--content", default=str(RAIZ / "content"), help=argparse.SUPPRESS)
    p.add_argument("--manifesto", default=str(RAIZ / "tools" / "manifesto.json"), help=argparse.SUPPRESS)
    p.add_argument("--hoje", help=argparse.SUPPRESS)
    args = p.parse_args(argv)

    vault = resolver_vault(args.vault)
    if vault is None:
        print("Vault não configurado: use --vault, SB_VAULT ou tools/config.toml", file=sys.stderr)
        return 2
    try:
        res = exportar(
            vault,
            Path(args.content),
            Path(args.manifesto),
            simular=args.simular,
            estrito=args.estrito,
            hoje=date.fromisoformat(args.hoje) if args.hoje else None,
        )
    except VaultIndisponivel as e:
        print(f"Erro: {e}", file=sys.stderr)
        for arq in e.arquivos:
            print(f"  - {arq}", file=sys.stderr)
        if e.arquivos:
            print("Nada foi publicado. Abra o Obsidian/Finder para baixar os arquivos e tente de novo.", file=sys.stderr)
        return 2

    if args.saida_json:
        Path(args.saida_json).write_text(json.dumps(res.para_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(res.para_dict(), ensure_ascii=False, indent=2))
    else:
        imprimir_resumo(res)
    if res.violacoes:
        return 3
    if res.abortado:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
