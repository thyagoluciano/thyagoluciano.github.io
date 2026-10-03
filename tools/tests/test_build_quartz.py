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
    assert (publico / "posts" / "como-uso-ia.html").exists()
    for arq in amb.content.rglob("*"):
        if arq.is_file():
            assert b"SEGREDO-" not in arq.read_bytes(), f"vazamento em {arq}"
    artigo = (publico / "posts" / "como-uso-ia.html").read_text(encoding="utf-8")
    assert 'href="../posts/contexto-importa"' in artigo  # wikilink reescrito vira link interno
    assert '<html lang="pt-BR"' in artigo
    # troca de slug: o endereço antigo redireciona para o novo
    nota = amb.vault / "50-Conteudo/Site/Site - Contexto importa.md"
    nota.write_text(nota.read_text().replace("slug: contexto-importa", "slug: contexto-e-tudo"))
    amb.exportar()
    build(amb.content, publico)
    assert (publico / "posts" / "contexto-e-tudo.html").exists()
    antigo = (publico / "posts" / "contexto-importa.html").read_text(encoding="utf-8")
    assert "contexto-e-tudo" in antigo and "refresh" in antigo
    # a segunda barreira: página sem publish: true não sai
    (amb.content / "posts" / "sem-publish.md").write_text("---\ntitle: X\n---\nSEGREDO-sem-publish\n")
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

    artigo, radar, sobre, home = ler("posts/como-uso-ia.html"), ler("radar/quartz.html"), ler("sobre.html"), ler("index.html")
    # SEO e compartilhamento
    assert '<link rel="canonical" href="https://thyagoluciano.com.br/posts/como-uso-ia"' in artigo
    assert 'og:type" content="article"' in artigo and 'og:type" content="website"' in radar
    assert 'og:image" content="https://thyagoluciano.com.br/assets/' in artigo  # capa da nota
    assert 'og:image" content="https://thyagoluciano.com.br/static/og-padrao.png"' in radar  # padrão
    assert 'twitter:card" content="summary_large_image"' in radar
    assert artigo.count('rel="alternate" type="application/rss+xml"') == 1
    assert 'name="description" content="Um relato prático' in artigo
    assert "fonts.googleapis.com" not in artigo  # fontes hospedadas no próprio site
    assert (publico / "static" / "og-padrao.png").exists()
    assert "Sitemap: https://thyagoluciano.com.br/sitemap.xml" in ler("robots.txt")
    assert "<loc>https://thyagoluciano.com.br/posts/como-uso-ia</loc>" in ler("sitemap.xml")
    # 404 em português
    assert "Esta página é privada ou não existe." in ler("404.html")
    # blocos do layout
    assert "Receba a newsletter" not in artigo and "Receba a newsletter" not in sobre  # bloco removido do site
    assert 'href="https://thyagoluciano.substack.com/subscribe" aria-label="Substack" title="Substack" target="_blank"' in artigo  # ícone na barra lateral
    assert "Mencionado em" not in artigo and "Mencionado em" not in radar  # seção removida do site
    assert "Backlinks" not in artigo
    for html in (artigo, radar, home):
        assert "grafo-container" not in html and "Mapa de conexões" not in html  # sem grafo no site
    for antiga in ("artigos", "ideias", "clube", "temas"):
        assert not (publico / antiga).exists(), f"/{antiga}/ não deveria existir"
    # T1 (SPEC-TEMA-CHIRPY): barra lateral, barra superior e gaveta mobile
    assert 'id="barra-lateral"' in home and 'aria-label="Principal"' in home
    secoes = ("Início", "Posts", "Radar", "Leituras", "Tags", "Arquivo", "Sobre", "Newsletter")
    for secao in secoes:
        assert f"<span>{secao}</span></a>" in home
    ordem = [home.index(f"<span>{secao}</span></a>") for secao in secoes]
    assert ordem == sorted(ordem)  # na ordem do menu
    for antiga in ("Artigos", "Ideias", "Clube", "Temas"):
        assert f"<span>{antiga}</span></a>" not in home
    assert home.count('aria-current="page"') == 1  # só o item da página atual
    assert 'aria-current="page"' in radar and "<span>Radar</span>" in radar
    assert 'class="menu-botao"' in home and 'aria-controls="barra-lateral"' in home
    assert 'class="pular" href="#conteudo"' in home and 'id="conteudo"' in home
    assert 'class="voltar-ao-topo"' in home
    assert (publico / "static" / "avatar.png").exists() and (publico / "arquivo.html").exists()
    assert "/index.xml" in home  # RSS na barra lateral
    # home em vitrines (Posts, Leituras e Radar), sem o texto de apresentação nem o título "Início"
    assert all(f'<h2>{v}</h2>' in home for v in ("Posts", "Leituras", "Radar")) and 'class="article-title"' not in home
    assert "Como uso IA no dia a dia" in home.split("<h2>Posts</h2>")[1]
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
    posts_home, resto = home.split("<h2>Leituras</h2>")
    leituras_home, radar_home = resto.split("<h2>Radar</h2>")
    assert cards(posts_home) == ["Como uso IA no dia a dia", "Contexto importa", "Agendado passado"]  # mais recente primeiro
    assert sorted(cards(leituras_home)) == ["A Arte da Guerra", "Setembro 2026"]
    assert cards(radar_home) == ["Quartz"]
    assert posts_home.count('class="card-capa"') == 1  # só o artigo com capa mostra imagem
    assert 'class="card-tipo">Post</span>' in home and "1 min" in home
    assert home.count("Ver todos") == 3 and 'href="./posts/"' in home

    assert cards(ler("posts/index.html")) == ["Como uso IA no dia a dia", "Contexto importa", "Agendado passado"]
    assert sorted(cards(ler("leituras/index.html"))) == ["A Arte da Guerra", "Setembro 2026"]  # resenha e encontro
    assert cards(ler("leituras/encontros/index.html")) == ["Setembro 2026"]
    assert cards(ler("radar/index.html")) == ["Quartz"]
    # card do Radar: estado, autor, categoria, "por que" e link externo em nova aba
    radar = ler("radar/index.html")
    assert re.search(r'class="card-estado estado-testando">Testando</span>', radar)
    assert "Jacky Zhao" in radar and "publicação" in radar and "Publica um vault do Obsidian" in radar
    assert 'href="https://quartz.jzhao.xyz" target="_blank" rel="noopener noreferrer"' in radar
    assert 'class="card-tipo">Ferramenta</span>' in radar
    for pasta in ("posts", "radar", "leituras"):
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
    for tipo in ("Encontro", "Resenha", "Ferramenta", "Post"):
        assert f'class="arquivo-tipo">{tipo}</span>' in arquivo
    assert "Inteligência Artificial" not in arquivo  # mapas não vão ao site

    todos = "".join(ler(p) for p in ("index.html", "arquivo.html", "posts/index.html", "tags/index.html", "tags/ia.html"))
    for proibido in ("Rascunho", "Segredo", "Sem descricao", "Agendado futuro", "Duplicado"):
        assert proibido not in todos
    for fixa in ("Sobre", "Newsletter"):  # páginas fixas nunca viram card
        assert fixa not in cards(home) + cards(ler("posts/index.html"))
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
    artigo, antigo = ler("posts/como-uso-ia.html"), ler("posts/agendado-passado.html")
    contexto, radar = ler("posts/contexto-importa.html"), ler("radar/quartz.html")

    def painel(html):
        m = re.search(r'<aside class="painel".*?</aside>', html, re.S)
        return m.group(0) if m else ""

    # painel direito: só notas exportadas, ordenado por atualização; tags por contagem
    p = painel(artigo)
    titulos = re.findall(r'class="painel-lista">(.*?)</ul>', p, re.S)[0]
    ordem = re.findall(r'class="internal"[^>]*>([^<]+)</a>', titulos)
    assert ordem == ["Setembro 2026", "Quartz", "Como uso IA no dia a dia", "Contexto importa", "A Arte da Guerra"]
    assert p.index(">ia</a>") < p.index(">contexto</a>") < p.index(">produtividade</a>")
    for html in (ler("index.html"), ler("posts/index.html"), ler("tags/ia.html"), ler("arquivo.html")):
        assert 'class="painel"' in html
    for html in (ler("sobre.html"), ler("newsletter.html")):
        assert 'class="painel"' not in html  # páginas fixas sem painel
    for bloqueado in ("Rascunho", "Segredo", "Sobre", "Newsletter"):
        assert bloqueado not in titulos

    # sumário só em nota exportada com 2 ou mais títulos
    assert 'class="toc' in artigo and 'class="toc' not in contexto and 'class="toc' not in ler("index.html")

    # metadados e capa
    assert "Atualizado em" in artigo and "1 min de leitura" in artigo and 'class="post-tipo">Post<' in artigo
    assert "Atualizado em" not in antigo  # sem `modified` no frontmatter, não mostra
    assert artigo.count('class="capa-post"') == 1 and 'class="capa-post"' not in antigo
    assert artigo.index('class="capa-post"') < artigo.index("<h1")  # capa antes do título

    # tags no fim do texto e compartilhar com o endereço canônico
    assert artigo.index("</article>") < artigo.index('class="tags"') < artigo.index('class="compartilhar"')
    url = "https%3A%2F%2Fthyagoluciano.com.br%2Fposts%2Fcomo-uso-ia"
    assert f"linkedin.com/sharing/share-offsite/?url={url}" in artigo
    assert f"x.com/intent/post?url={url}" in artigo
    assert 'data-url="https://thyagoluciano.com.br/posts/como-uso-ia"' in artigo and 'class="copiar-link"' in artigo

    # leia também: mesmo tipo, nunca a própria página
    leia = re.search(r'<section class="leia-tambem">.*?</section>', artigo, re.S).group(0)
    assert "Contexto importa" in leia and "Agendado passado" in leia and "Como uso IA no dia a dia" not in leia
    assert leia.index("Contexto importa") < leia.index("Agendado passado")  # tag em comum primeiro
    assert 'class="leia-tambem"' not in radar  # o Radar não tem "leia também"

    # anterior e próximo dentro da seção
    assert 'class="internal ap-anterior"' in artigo and "Contexto importa" in artigo.split("ap-anterior")[1][:300]
    assert "ap-proximo" not in artigo  # é o mais recente
    assert "ap-proximo" in antigo and "Contexto importa" in antigo.split("ap-proximo")[1][:300]
    assert "ap-anterior" not in antigo  # é o mais antigo
    assert "ap-anterior" in contexto and "ap-proximo" in contexto

    # sem páginas de tema
    assert "Notas neste tema" not in artigo
