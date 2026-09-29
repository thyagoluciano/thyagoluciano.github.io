"""Teste de vazamento de ponta a ponta: exporta o vault de exemplo e roda o build do Quartz."""

import shutil
import subprocess

import pytest

from conftest import TOOLS

RAIZ = TOOLS.parent

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None or not (RAIZ / "node_modules").exists(),
    reason="Node ou node_modules ausente (rode npm ci)",
)


def build(content, saida):
    r = subprocess.run(
        ["node", "quartz/bootstrap-cli.mjs", "build", "-d", str(content), "-o", str(saida)],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_nada_secreto_em_content_nem_em_public(amb, tmp_path):
    # páginas fixas reais do repositório + notas exportadas do vault de exemplo
    for arq in [*RAIZ.joinpath("content").rglob("*.md"), RAIZ / "content" / "robots.txt"]:
        destino = amb.content / arq.relative_to(RAIZ / "content")
        if not destino.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(arq, destino)
    amb.exportar()

    publico = tmp_path / "public"
    build(amb.content, publico)
    assert (publico / "artigos" / "como-uso-ia.html").exists()
    for arq in amb.content.rglob("*"):
        if arq.is_file():
            assert b"SEGREDO-" not in arq.read_bytes(), f"vazamento em {arq}"
    artigo = (publico / "artigos" / "como-uso-ia.html").read_text(encoding="utf-8")
    assert 'href="../ideias/contexto-importa"' in artigo  # wikilink reescrito vira link interno
    assert '<html lang="pt-BR"' in artigo
    # troca de slug: o endereço antigo redireciona para o novo
    nota = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    nota.write_text(nota.read_text().replace("slug: contexto-importa", "slug: contexto-e-tudo"))
    amb.exportar()
    build(amb.content, publico)
    assert (publico / "ideias" / "contexto-e-tudo.html").exists()
    antigo = (publico / "ideias" / "contexto-importa.html").read_text(encoding="utf-8")
    assert "contexto-e-tudo" in antigo and "refresh" in antigo
    # a segunda barreira: página sem publish: true não sai
    (amb.content / "ideias" / "sem-publish.md").write_text("---\ntitle: X\n---\nSEGREDO-sem-publish\n")
    build(amb.content, publico)

    for arq in publico.rglob("*"):
        if arq.is_file():
            assert b"SEGREDO-" not in arq.read_bytes(), f"vazamento em {arq}"


def test_layout_seo_e_desempenho(amb, tmp_path):
    """Regressões do M4: idioma, canonical, imagens de compartilhamento, newsletter, grafo, 404 e peso do JS."""
    for arq in [*RAIZ.joinpath("content").rglob("*.md"), RAIZ / "content" / "robots.txt"]:
        destino = amb.content / arq.relative_to(RAIZ / "content")
        if not destino.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(arq, destino)
    amb.exportar()
    publico = tmp_path / "public"
    build(amb.content, publico)
    ler = lambda rel: (publico / rel).read_text(encoding="utf-8")

    artigo, ideia, sobre, home = ler("artigos/como-uso-ia.html"), ler("ideias/contexto-importa.html"), ler("sobre.html"), ler("index.html")
    # SEO e compartilhamento
    assert '<link rel="canonical" href="https://thyagoluciano.com.br/artigos/como-uso-ia"' in artigo
    assert 'og:type" content="article"' in artigo and 'og:type" content="website"' in ideia
    assert 'og:image" content="https://thyagoluciano.com.br/assets/' in artigo  # capa da nota
    assert 'og:image" content="https://thyagoluciano.com.br/static/og-padrao.png"' in ideia  # padrão
    assert 'twitter:card" content="summary_large_image"' in ideia
    assert artigo.count('rel="alternate" type="application/rss+xml"') == 1
    assert 'name="description" content="Um relato prático' in artigo
    assert "fonts.googleapis.com" not in artigo  # fontes hospedadas no próprio site
    assert (publico / "static" / "og-padrao.png").exists()
    assert "Sitemap: https://thyagoluciano.com.br/sitemap.xml" in ler("robots.txt")
    assert "<loc>https://thyagoluciano.com.br/artigos/como-uso-ia</loc>" in ler("sitemap.xml")
    # 404 em português
    assert "Esta página é privada ou não existe." in ler("404.html")
    # blocos do layout
    assert "Receba os novos textos" in artigo and "Receba os novos textos" not in sobre
    assert "<h2>Mencionado em</h2>" in artigo and "Contexto importa" in artigo.split("Mencionado em")[1]  # a ideia cita o artigo
    assert "Backlinks" not in artigo
    assert 'class="grafo-container"' in ideia and "grafo-container" not in artigo.split("</article>")[1]
    # T1 (SPEC-TEMA-CHIRPY): barra lateral, barra superior e gaveta mobile
    assert 'id="barra-lateral"' in home and 'aria-label="Principal"' in home
    for secao in ("Início", "Artigos", "Ideias", "Clube", "Temas", "Tags", "Arquivo", "Sobre", "Newsletter"):
        assert f"<span>{secao}</span></a>" in home
    assert home.count('aria-current="page"') == 1  # só o item da página atual
    assert 'aria-current="page"' in ideia and "<span>Ideias</span>" in ideia
    assert 'class="menu-botao"' in home and 'aria-controls="barra-lateral"' in home
    assert 'class="pular" href="#conteudo"' in home and 'id="conteudo"' in home
    assert 'class="voltar-ao-topo"' in home
    assert (publico / "static" / "avatar.png").exists() and (publico / "arquivo.html").exists()
    assert "/index.xml" in home  # RSS na barra lateral
    assert "Artigos recentes" in home and "Como uso IA no dia a dia" in home.split("Artigos recentes")[1]
    # orçamento de JS (RNF3): o grafo do Quartz (d3 + pixi) passava de 600 KB e derrubava o Lighthouse mobile
    assert 'getElementById("conteudo")' in (publico / "postscript.js").read_text(encoding="utf-8")  # foco após "pular"
    assert "popover-inner" not in (publico / "postscript.js").read_text(encoding="utf-8")  # sem prévia ao passar o mouse
    assert (publico / "postscript.js").stat().st_size < 250_000


def test_cards_listas_tags_e_arquivo(amb, tmp_path):
    """T2 (SPEC-TEMA-CHIRPY): cards na home, pastas e tags; arquivo por ano e mês."""
    import re

    for arq in [*RAIZ.joinpath("content").rglob("*.md"), RAIZ / "content" / "robots.txt"]:
        destino = amb.content / arq.relative_to(RAIZ / "content")
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(arq, destino)  # sempre as páginas fixas reais (com os títulos ## das seções)
    amb.exportar()
    publico = tmp_path / "public"
    build(amb.content, publico)
    ler = lambda rel: (publico / rel).read_text(encoding="utf-8")

    def cards(html):
        """Títulos dos cards, na ordem em que aparecem."""
        return re.findall(r'<li class="card[^"]*">.*?<h3><a class="internal" href="[^"]*">([^<]+)</a></h3>', html, re.S)

    home = ler("index.html")
    assert cards(home) == ["Como uso IA no dia a dia", "Agendado passado"]  # mais recente primeiro
    assert home.count('class="card-capa"') == 1  # só o artigo com capa mostra imagem
    assert 'class="card-tipo">Artigo</span>' in home and "1 min" in home
    assert 'href="./arquivo"' in home and "Ver todos" in home

    assert cards(ler("artigos/index.html")) == ["Como uso IA no dia a dia", "Agendado passado"]
    assert cards(ler("ideias/index.html")) == ["Contexto importa"]
    assert sorted(cards(ler("clube/index.html"))) == ["A Arte da Guerra", "Setembro 2026"]  # resenha e encontro
    assert cards(ler("temas/index.html")) == ["Inteligência Artificial"]
    assert cards(ler("clube/encontros/index.html")) == ["Setembro 2026"]
    for pasta in ("artigos", "ideias", "clube", "temas"):
        pagina = ler(f"{pasta}/index.html")
        assert 'class="section-li' not in pagina  # a lista padrão do Quartz foi substituída
        assert "<h2 " in pagina and pagina.index("<h2") < pagina.index('class="cards"')  # h1 > h2 > h3

    # tags: contagem no índice e cards na página da tag
    indice = ler("tags/index.html")
    assert re.search(r'>ia</a><span class="nuvem-contagem">2</span>', indice)
    assert indice.index(">ia</a>") < indice.index(">contexto</a>")  # mais usadas primeiro
    assert cards(ler("tags/ia.html")) == ["Como uso IA no dia a dia", "Contexto importa"]
    assert "2 publicações" in ler("tags/ia.html") and "1 publicação<" in ler("tags/contexto.html")

    # arquivo: ano e mês em ordem decrescente, sem páginas fixas nem notas bloqueadas
    arquivo = ler("arquivo.html")
    assert arquivo.index("<h2>2026</h2>") < arquivo.index("<h2>2020</h2>")
    assert arquivo.index("<h3>Setembro</h3>") < arquivo.index("<h3>Março</h3>") < arquivo.index("<h3>Janeiro</h3>")
    assert 'class="arquivo-tipo">Encontro</span>' in arquivo and 'class="arquivo-tipo">Resenha</span>' in arquivo
    assert "Inteligência Artificial" not in arquivo.split('class="arquivo"')[1].split("<aside")[0]  # temas ficam de fora da linha do tempo

    todos = "".join(ler(p) for p in ("index.html", "arquivo.html", "artigos/index.html", "tags/index.html", "tags/ia.html"))
    for proibido in ("Rascunho", "Segredo", "Sem descricao", "Agendado futuro", "Duplicado"):
        assert proibido not in todos
    for fixa in ("Sobre", "Newsletter"):  # páginas fixas nunca viram card
        assert fixa not in cards(home) + cards(ler("artigos/index.html"))
    assert (publico / "postscript.js").stat().st_size < 250_000


def test_painel_e_post_completo(amb, tmp_path):
    """T3 (SPEC-TEMA-CHIRPY): painel direito, metadados, capa, compartilhar, leia também, anterior/próximo, temas."""
    import re

    for arq in [*RAIZ.joinpath("content").rglob("*.md"), RAIZ / "content" / "robots.txt"]:
        destino = amb.content / arq.relative_to(RAIZ / "content")
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(arq, destino)
    amb.exportar()
    publico = tmp_path / "public"
    build(amb.content, publico)
    ler = lambda rel: (publico / rel).read_text(encoding="utf-8")
    artigo, antigo = ler("artigos/como-uso-ia.html"), ler("artigos/agendado-passado.html")
    ideia, tema = ler("ideias/contexto-importa.html"), ler("temas/inteligencia-artificial.html")

    def painel(html):
        m = re.search(r'<aside class="painel".*?</aside>', html, re.S)
        return m.group(0) if m else ""

    # painel direito: só notas exportadas, ordenado por atualização; tags por contagem
    p = painel(artigo)
    titulos = re.findall(r'class="painel-lista">(.*?)</ul>', p, re.S)[0]
    ordem = re.findall(r'class="internal"[^>]*>([^<]+)</a>', titulos)
    assert ordem == ["Setembro 2026", "Como uso IA no dia a dia", "Contexto importa", "Inteligência Artificial", "A Arte da Guerra"]
    assert p.index(">ia</a>") < p.index(">contexto</a>") < p.index(">produtividade</a>")
    for html in (ler("index.html"), ler("artigos/index.html"), ler("tags/ia.html"), ler("arquivo.html")):
        assert 'class="painel"' in html
    for html in (ler("sobre.html"), ler("newsletter.html")):
        assert 'class="painel"' not in html  # páginas fixas sem painel
    for bloqueado in ("Rascunho", "Segredo", "Sobre", "Newsletter"):
        assert bloqueado not in titulos

    # sumário só em nota exportada com 2 ou mais títulos
    assert 'class="toc' in artigo and 'class="toc' not in ideia and 'class="toc' not in ler("index.html")

    # metadados e capa
    assert "Atualizado em" in artigo and "1 min de leitura" in artigo and 'class="post-tipo">Artigo<' in artigo
    assert "Atualizado em" not in antigo  # sem `modified` no frontmatter, não mostra
    assert artigo.count('class="capa-post"') == 1 and 'class="capa-post"' not in antigo
    assert artigo.index('class="capa-post"') < artigo.index("<h1")  # capa antes do título

    # tags no fim do texto e compartilhar com o endereço canônico
    assert artigo.index("</article>") < artigo.index('class="tags"') < artigo.index('class="compartilhar"')
    url = "https%3A%2F%2Fthyagoluciano.com.br%2Fartigos%2Fcomo-uso-ia"
    assert f"linkedin.com/sharing/share-offsite/?url={url}" in artigo
    assert f"x.com/intent/post?url={url}" in artigo
    assert 'data-url="https://thyagoluciano.com.br/artigos/como-uso-ia"' in artigo and 'class="copiar-link"' in artigo

    # leia também: mesmo tipo, nunca a própria página
    leia = re.search(r'<section class="leia-tambem">.*?</section>', artigo, re.S).group(0)
    assert "Agendado passado" in leia and "Como uso IA no dia a dia" not in leia
    assert 'class="leia-tambem"' not in ideia  # só existe uma ideia: sem candidatas
    assert 'class="leia-tambem"' not in tema

    # anterior e próximo dentro da seção
    assert 'class="internal ap-anterior"' in artigo and "Agendado passado" in artigo.split("ap-anterior")[1][:300]
    assert "ap-proximo" not in artigo  # é a mais recente
    assert "ap-proximo" in antigo and "Como uso IA no dia a dia" in antigo.split("ap-proximo")[1][:300]
    assert "ap-anterior" not in antigo
    assert 'class="anterior-proximo"' not in tema

    # página de tema lista as notas que a citam
    assert "Notas neste tema" in tema and "Como uso IA no dia a dia" in tema.split("Notas neste tema")[1]
    assert "Notas neste tema" not in artigo
