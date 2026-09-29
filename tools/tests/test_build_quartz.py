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
    assert 'aria-label="Principal"' in home
    for secao in ("Artigos", "Ideias", "Clube", "Temas", "Sobre", "Newsletter"):
        assert f">{secao}</a>" in home
    assert "Artigos recentes" in home and "Como uso IA no dia a dia" in home.split("Artigos recentes")[1]
    # orçamento de JS (RNF3): o grafo do Quartz (d3 + pixi) passava de 600 KB e derrubava o Lighthouse mobile
    assert (publico / "postscript.js").stat().st_size < 250_000
