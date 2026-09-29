import pytest

import exportar
from conftest import HOJE


def preparar(amb):
    amb.exportar()
    produzidos = {}
    vault = exportar.varrer_vault(amb.vault)
    elegiveis, _ = exportar.selecionar(vault, HOJE)
    return {el.rel_saida: el for el in elegiveis.values()}


def violacoes(amb, produzidos):
    return exportar.auditar(amb.content, produzidos, HOJE)


def test_conteudo_limpo_passa(amb):
    assert violacoes(amb, preparar(amb)) == []


def test_arquivo_gerado_sem_nota_elegivel(amb):
    p = preparar(amb)
    (amb.content / "ideias" / "intruso.md").write_text("---\ntitle: X\ngerado: true\npublish: true\n---\n")
    assert any("sem nota elegível" in v and "intruso" in v for v in violacoes(amb, p))


def test_origem_deixou_de_ser_elegivel(amb):
    p = preparar(amb)
    for el in p.values():
        if el.slug == "contexto-importa":
            el.nota.fm["publicar"] = False
    assert any("não é elegível" in v for v in violacoes(amb, p))


def test_link_para_pagina_inexistente(amb):
    p = preparar(amb)
    arq = amb.content / "ideias" / "contexto-importa.md"
    arq.write_text(arq.read_text() + "\n[[ideias/nao-existe|x]]\n")
    assert any("página inexistente" in v for v in violacoes(amb, p))


def test_campo_fora_da_lista(amb):
    p = preparar(amb)
    arq = amb.content / "ideias" / "contexto-importa.md"
    arq.write_text(arq.read_text().replace("gerado: true", "gerado: true\nprioridade: alta"))
    assert any("'prioridade' fora da lista" in v for v in violacoes(amb, p))


@pytest.mark.parametrize("resíduo", ["%% oculto %%", "<!-- oculto -->", "Destaques - Livro"])
def test_residuos(amb, resíduo):
    p = preparar(amb)
    arq = amb.content / "ideias" / "contexto-importa.md"
    arq.write_text(arq.read_text() + f"\n{resíduo}\n")
    assert any("contém" in v for v in violacoes(amb, p))


def test_imagem_sem_referencia(amb):
    p = preparar(amb)
    (amb.content / "assets" / "deadbeef-solta.png").write_bytes(b"x")
    assert any("imagem sem referência" in v and "solta" in v for v in violacoes(amb, p))


def test_embed_para_arquivo_inexistente(amb):
    p = preparar(amb)
    arq = amb.content / "ideias" / "contexto-importa.md"
    arq.write_text(arq.read_text() + "\n![[assets/fantasma.png]]\n")
    assert any("arquivo inexistente" in v for v in violacoes(amb, p))


def test_bloco_lendo_agora_com_link_inexistente(amb):
    p = preparar(amb)
    arq = amb.content / "clube" / "index.md"
    arq.write_text(arq.read_text().replace(exportar.MARCA_FIM, "[[clube/fantasma|x]]\n" + exportar.MARCA_FIM))
    assert any("lendo agora" in v for v in violacoes(amb, p))


def test_auditoria_falha_nao_escreve_nada(amb, monkeypatch):
    monkeypatch.setattr(exportar, "auditar", lambda *a, **k: ["falha simulada"])
    res = amb.exportar()
    assert res.violacoes == ["falha simulada"] and not res.aplicado
    assert amb.gerados() == set() and not amb.manifesto.exists()
    assert "gerado:lendo-agora -->\n<!--" in amb.ler("clube/index.md")  # página fixa intacta
