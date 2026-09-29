import json

import yaml

import exportar
from conftest import HOJE, hashes


def manifesto(amb):
    return json.loads(amb.manifesto.read_text())


def aliases(amb, rel):
    return yaml.safe_load(exportar.FRONTMATTER.match(amb.ler(rel)).group(1)).get("aliases", [])


def test_manifesto_registra_slug_destino_e_hash(amb):
    amb.exportar()
    e = manifesto(amb)["20-Ideias/Ideia - Contexto importa.md"]
    assert e["slug"] == "contexto-importa" and e["destino"] == "ideias/contexto-importa.md"
    assert e["slugs_anteriores"] == [] and len(e["sha256"]) == 64


def test_segunda_execucao_nao_muda_nada(amb):
    amb.exportar()
    antes = hashes(amb.content), amb.manifesto.read_text()
    res = amb.exportar()
    assert not res.novas and not res.alteradas and not res.removidas
    assert (hashes(amb.content), amb.manifesto.read_text()) == antes


def test_troca_de_slug_gera_alias(amb):
    amb.exportar()
    nota = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    nota.write_text(nota.read_text().replace("slug: contexto-importa", "slug: contexto-e-tudo"))
    res = amb.exportar()
    assert (amb.content / "ideias/contexto-e-tudo.md").exists()
    assert not (amb.content / "ideias/contexto-importa.md").exists()
    assert aliases(amb, "ideias/contexto-e-tudo.md") == ["ideias/contexto-importa"]
    assert manifesto(amb)["20-Ideias/Ideia - Contexto importa.md"]["slugs_anteriores"] == ["contexto-importa"]
    assert "[[ideias/contexto-e-tudo|" in amb.ler("artigos/como-uso-ia.md")
    assert [n["caminho"] for n in res.novas] == ["ideias/contexto-e-tudo.md"]
    assert [r["caminho"] for r in res.removidas] == ["ideias/contexto-importa.md"]  # o endereço antigo segue vivo pelo alias
    # o alias persiste nas execuções seguintes
    amb.exportar()
    assert aliases(amb, "ideias/contexto-e-tudo.md") == ["ideias/contexto-importa"]


def test_mover_a_nota_no_vault_nao_muda_a_url(amb):
    amb.exportar()
    origem = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    (amb.vault / "25-Novo").mkdir()
    origem.rename(amb.vault / "25-Novo" / "Ideia - Contexto importa.md")
    res = amb.exportar()
    assert not res.novas and not res.removidas
    assert (amb.content / "ideias/contexto-importa.md").exists()
    m = manifesto(amb)
    assert "25-Novo/Ideia - Contexto importa.md" in m and "20-Ideias/Ideia - Contexto importa.md" not in m
    assert "removida" not in m["25-Novo/Ideia - Contexto importa.md"]


def test_renomear_arquivo_mantem_url_pelo_slug(amb):
    amb.exportar()
    origem = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    origem.rename(amb.vault / "20-Ideias" / "Ideia - Outro nome.md")
    res = amb.exportar()
    assert not res.novas and not res.removidas
    assert (amb.content / "ideias/contexto-importa.md").exists()


def test_nota_que_deixa_de_ser_elegivel_e_removida(amb):
    amb.exportar()
    nota = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    nota.write_text(nota.read_text().replace("publicar: true", "publicar: false"))
    res = amb.exportar()
    assert not (amb.content / "ideias/contexto-importa.md").exists()
    assert [r["caminho"] for r in res.removidas] == ["ideias/contexto-importa.md"]
    entrada = manifesto(amb)["20-Ideias/Ideia - Contexto importa.md"]
    assert entrada["removida"] == HOJE.isoformat()
    # links para ela viram texto
    assert "ideias/contexto-importa" not in amb.ler("artigos/como-uso-ia.md")
    # e a remoção não se repete
    assert not amb.exportar().removidas


def test_mudar_de_tipo_gera_alias_do_endereco_antigo(amb):
    amb.exportar()
    nota = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    nota.write_text(nota.read_text().replace("tipo: ideia", "tipo: mapa"))
    amb.exportar()
    assert aliases(amb, "temas/contexto-importa.md") == ["ideias/contexto-importa"]


def test_arquivo_gerado_orfao_e_removido_mas_fixo_nao(amb):
    amb.exportar()
    (amb.content / "ideias" / "orfao.md").write_text("---\ntitle: Órfão\ngerado: true\npublish: true\n---\n")
    (amb.content / "ideias" / "manual.md").write_text("---\ntitle: Manual\npublish: true\n---\n")
    res = amb.exportar()
    assert not (amb.content / "ideias/orfao.md").exists()
    assert (amb.content / "ideias/manual.md").exists()
    assert [r["caminho"] for r in res.removidas] == ["ideias/orfao.md"]


def test_imagem_que_deixa_de_ser_usada_e_removida(amb):
    amb.exportar()
    nota = amb.vault / "50-Conteudo/Site/Site - Como uso IA no dia a dia.md"
    nota.write_text(nota.read_text().replace("![[usada.png]]", "").replace("![[usada.png|300]]", ""))
    amb.exportar()
    assert not any(p.name.endswith("-usada.png") for p in (amb.content / "assets").iterdir())
