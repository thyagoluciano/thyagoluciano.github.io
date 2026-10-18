"""llms.txt: índice do site para modelos de IA, gerado junto com a exportação."""

import json

from conftest import hashes


def test_llms_txt_lista_so_o_que_foi_exportado(amb):
    amb.exportar()
    llms = amb.ler("llms.txt")
    assert llms.startswith("# Thyago Luciano\n\n> ")
    assert "## Posts" in llms and "https://thyagoluciano.com.br/posts/como-uso-ia" in llms
    assert "https://thyagoluciano.com.br/radar/quartz" in llms
    assert "/index)" not in llms  # índices das pastas não entram
    for proibido in ("SEGREDO", "Rascunho", "Agendado futuro", "Duplicado", "Inteligência Artificial"):
        assert proibido not in llms


def test_llms_txt_mais_recente_primeiro_e_idempotente(amb):
    amb.exportar()
    posts = [l for l in amb.ler("llms.txt").split("## Posts")[1].split("##")[0].splitlines() if l.startswith("- ")]
    assert len(posts) >= 2
    antes = hashes(amb.content)
    res = amb.exportar()
    assert hashes(amb.content) == antes and not (res.novas or res.alteradas or res.removidas)


def test_simulacao_nao_escreve_llms_txt(amb):
    amb.exportar(simular=True)
    assert not (amb.content / "llms.txt").exists()


def test_llms_txt_acompanha_remocao_de_post(amb):
    amb.exportar()
    assert "como-uso-ia" in amb.ler("llms.txt")
    nota = amb.vault / "50-Conteudo/Site/Site - Como uso IA no dia a dia.md"
    nota.write_text(nota.read_text().replace("publicar: true", "publicar: false"))
    amb.exportar()
    assert "como-uso-ia" not in amb.ler("llms.txt")
