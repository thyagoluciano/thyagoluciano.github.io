import yaml

import exportar


def frontmatter(texto):
    return yaml.safe_load(exportar.FRONTMATTER.match(texto).group(1))


def test_frontmatter_lista_de_permissao(amb):
    amb.exportar()
    fm = frontmatter(amb.ler("posts/como-uso-ia.md"))
    assert set(fm) <= set(exportar.CAMPOS_PERMITIDOS)
    assert fm["title"] == "Como uso IA no dia a dia"
    assert fm["description"].startswith("Um relato prático")
    assert fm["date"] == fm["published"] == "2026-03-10"
    assert fm["modified"] == "2026-03-12"
    assert fm["tags"] == ["ia", "produtividade"]
    assert fm["publish"] is True and fm["gerado"] is True
    for privado in ("prioridade", "notas_internas", "url", "canal", "status", "slug", "temas"):
        assert privado not in fm


def test_frontmatter_do_radar(amb):
    amb.exportar()
    fm = frontmatter(amb.ler("radar/quartz.md"))
    assert set(fm) <= set(exportar.CAMPOS_PERMITIDOS)
    assert fm["title"] == "Quartz" and fm["tipo"] == "ferramenta"
    assert fm["url"] == "https://quartz.jzhao.xyz"
    assert fm["repositorio"] == "https://github.com/jackyzha0/quartz"
    assert fm["autor_projeto"] == "Jacky Zhao" and fm["categoria"] == "publicação"
    assert fm["estado"] == "testando" and fm["licenca"] == "MIT"
    assert fm["por_que"].startswith("Publica um vault")
    assert fm["date"] == "2026-09-01" and fm["tags"] == ["obsidian", "site"]
    assert "segredo_interno" not in fm and "SEGREDO" not in amb.ler("radar/quartz.md")


def test_campos_do_radar_nao_vazam_para_outros_tipos(amb):
    amb.exportar()
    assert "url" not in frontmatter(amb.ler("posts/como-uso-ia.md"))
    assert "estado" not in frontmatter(amb.ler("leituras/a-arte-da-guerra.md"))


def test_data_cai_para_criado_e_tags_sem_hash(amb):
    amb.exportar()
    fm = frontmatter(amb.ler("posts/contexto-importa.md"))
    assert fm["date"] == "2026-02-02"
    assert fm["tags"] == ["ia", "contexto"]


def test_resenha_tem_autor_e_nota(amb):
    amb.exportar()
    fm = frontmatter(amb.ler("leituras/a-arte-da-guerra.md"))
    assert fm["autor_livro"] == "Sun Tzu" and fm["nota"] == 5
    assert "autor_livro" not in frontmatter(amb.ler("posts/contexto-importa.md"))


def test_nota_fora_do_intervalo_e_ignorada(amb):
    nota = amb.vault / "10-Fontes/Livros/A Arte da Guerra/Livro - A Arte da Guerra.md"
    nota.write_text(nota.read_text().replace("nota: 5", "nota: 9"))
    res = amb.exportar()
    assert "nota" not in frontmatter(amb.ler("leituras/a-arte-da-guerra.md"))
    assert any("fora de 1–5" in a for a in res.avisos)


def test_comentarios_removidos(amb):
    amb.exportar()
    texto = amb.ler("posts/como-uso-ia.md")
    assert "%%" not in texto and "<!--" not in texto and "SEGREDO" not in texto


def test_secoes_vazias_e_marcadores_removidos(amb):
    amb.exportar()
    texto = amb.ler("posts/como-uso-ia.md")
    assert "Seção vazia" not in texto and "Subseção vazia" not in texto and "Fim vazio" not in texto
    assert "## Contexto" in texto and "## Imagens" in texto


def test_placeholders_de_template_removidos(amb):
    amb.exportar()
    texto = amb.ler("posts/agendado-passado.md")
    assert "<%" not in texto and "{{" not in texto
    assert "## Passos" in texto and "Texto real do artigo." in texto


def test_h1_repetido_removido_mas_outros_ficam(amb):
    amb.exportar()
    assert "# Como uso IA no dia a dia" not in amb.ler("posts/como-uso-ia.md").split("---")[2]
    nota = amb.vault / "50-Conteudo/Site/Site - Contexto importa.md"
    nota.write_text(nota.read_text().replace("# Contexto importa\n", "# Outro título\n"))
    amb.exportar()
    assert "# Outro título" in amb.ler("posts/contexto-importa.md")


def test_wikilinks(amb):
    amb.exportar()
    texto = amb.ler("posts/como-uso-ia.md")
    assert "[[posts/contexto-importa|Contexto importa]]" in texto  # sem prefixo
    assert "[[posts/contexto-importa|o contexto]]" in texto  # apelido
    assert "[[posts/contexto-importa#Detalhe|ver o detalhe]]" in texto  # seção
    assert "Ideia que fica só no Obsidian: Contexto importa e minha ideia." in texto  # ideia vira texto
    assert "[[#Imagens]]" in texto  # própria nota
    assert "Nota privada de trabalho, Segredo e inexistente Não existe." in texto
    assert "meu caderno" in texto and "[[Nota" not in texto
    assert "[[leituras/a-arte-da-guerra|A Arte da Guerra]]" in amb.ler("posts/contexto-importa.md")
    assert "[[leituras/a-arte-da-guerra|" in amb.ler("leituras/encontros/encontro-setembro-2026.md")


def test_codigo_nao_e_reescrito(amb):
    amb.exportar()
    texto = amb.ler("posts/como-uso-ia.md")
    assert "`[[nao-link]]`" in texto and "[[tambem-nao-link]]" in texto


def test_links_externos_ficam(amb):
    amb.exportar()
    assert "[exemplo](https://example.com)" in amb.ler("posts/como-uso-ia.md")


def test_embeds_de_imagem_e_de_nota(amb):
    res = amb.exportar()
    texto = amb.ler("posts/como-uso-ia.md")
    assets = sorted(p.name for p in (amb.content / "assets").iterdir())
    assert len(assets) == 2  # usada.png (uma cópia só) e a capa
    usada = next(a for a in assets if a.endswith("-usada.png"))
    assert f"![[assets/{usada}]]" in texto and f"![[assets/{usada}|300]]" in texto
    assert "nao-usada" not in "".join(assets)
    assert "Nota privada de trabalho" not in texto.split("Nota privada:")[1].split("\n", 1)[1]
    assert any("nao-existe.png" in a for a in res.avisos)
    assert exportar.FRONTMATTER.match(texto)  # sanidade
    assert f"capa: assets/{next(a for a in assets if 'capa' in a)}" in texto


def test_nome_do_asset_tem_hash_do_conteudo(amb):
    amb.exportar()
    nome = next(p.name for p in (amb.content / "assets").iterdir() if p.name.endswith("-usada.png"))
    import hashlib

    esperado = hashlib.sha256((amb.vault / "_anexos" / "usada.png").read_bytes()).hexdigest()[:8]
    assert nome == f"{esperado}-usada.png"


def test_lendo_agora(amb):
    amb.exportar()
    texto = amb.ler("leituras/index.md")
    assert "- [[leituras/a-arte-da-guerra|A Arte da Guerra]], de Sun Tzu" in texto
    assert "Outro livro" not in texto  # privado
    assert "TODO: leituras" in texto  # resto da página fixa intacto


def test_lendo_agora_vazio(amb):
    nota = amb.vault / "10-Fontes/Livros/A Arte da Guerra/Livro - A Arte da Guerra.md"
    nota.write_text(nota.read_text().replace("status_leitura: lendo", "status_leitura: lido"))
    amb.exportar()
    assert "Nenhum livro em leitura no momento." in amb.ler("leituras/index.md")


def test_paginas_fixas_nunca_sao_sobrescritas(amb):
    antes = {p: (amb.content / p).read_text() for p in ("index.md", "posts/index.md", "radar/index.md")}
    amb.exportar()
    assert {p: (amb.content / p).read_text() for p in antes} == antes


def test_lendo_agora_sem_marcadores_gera_aviso(amb):
    (amb.content / "leituras" / "index.md").write_text("---\ntitle: Leituras\npublish: true\n---\n")
    res = amb.exportar()
    assert any("marcadores" in a for a in res.avisos)
