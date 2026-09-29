import pytest

import exportar
from conftest import HOJE

EXPORTADAS = {
    "artigos/agendado-passado.md",
    "artigos/como-uso-ia.md",
    "clube/a-arte-da-guerra.md",
    "clube/encontros/encontro-setembro-2026.md",
    "ideias/contexto-importa.md",
    "temas/inteligencia-artificial.md",
}


def motivos(res):
    return {e["nota"]: e["motivo"] for e in res.erros}


def test_exporta_somente_notas_elegiveis(amb):
    res = amb.exportar()
    assert {n["caminho"] for n in res.novas} == EXPORTADAS
    assert {n for n in amb.gerados() if n.endswith(".md")} == EXPORTADAS


def test_destinos_por_tipo(amb):
    amb.exportar()
    assert 'tipo: artigo' in amb.ler("artigos/como-uso-ia.md")
    assert 'tipo: ideia' in amb.ler("ideias/contexto-importa.md")
    assert 'tipo: resenha' in amb.ler("clube/a-arte-da-guerra.md")
    assert 'tipo: encontro' in amb.ler("clube/encontros/encontro-setembro-2026.md")
    assert 'tipo: tema' in amb.ler("temas/inteligencia-artificial.md")


@pytest.mark.parametrize(
    "nota, trecho",
    [
        ("00-Inbox/Rascunho.md", "nunca é exportada"),
        ("90-Templates/Template - Artigo.md", "nunca é exportada"),
        ("10-Fontes/Livros/A Arte da Guerra/Destaques - A Arte da Guerra.md", "destaques"),
        ("50-Conteudo/Site/Site - Agendado futuro.md", "futuro"),
        ("50-Conteudo/Site/Site - Sem descricao.md", "sem descricao"),
        ("50-Conteudo/Site/Site - Canal errado.md", "canal"),
        ("50-Conteudo/Site/Site - Duplicado A.md", "duplicado"),
        ("50-Conteudo/Site/Site - Duplicado B.md", "duplicado"),
        ("30-Pessoas/Pessoa - Fulano.md", "não é exportável"),
    ],
)
def test_notas_bloqueadas_geram_erro(amb, nota, trecho):
    res = amb.exportar()
    assert trecho in motivos(res)[nota]


def test_notas_privadas_sem_erro_e_sem_saida(amb):
    res = amb.exportar()
    assert not any("Segredo" in e["nota"] or "Nota privada" in e["nota"] for e in res.erros)
    assert not (amb.content / "ideias" / "segredo.md").exists()


def test_estrito_aborta_sem_escrever(amb):
    res = amb.exportar(estrito=True)
    assert res.abortado and res.erros
    assert amb.gerados() == set()
    assert not amb.manifesto.exists()


def test_estrito_passa_sem_erros(amb):
    for nota in list(amb.vault.rglob("*.md")):
        if any(e["nota"] == nota.relative_to(amb.vault).as_posix() for e in amb.exportar(simular=True).erros):
            nota.unlink()
    res = amb.exportar(estrito=True)
    assert not res.abortado and not res.erros and res.aplicado


def test_agendado_futuro_vira_elegivel_quando_a_data_chega(amb):
    from datetime import date

    res = amb.exportar(hoje=date(2099, 1, 2))
    assert "artigos/agendado-futuro.md" in {n["caminho"] for n in res.novas}


def test_slug_invalido(amb):
    nota = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    nota.write_text(nota.read_text().replace("slug: contexto-importa", "slug: Contexto Importa"))
    assert "inválido" in motivos(amb.exportar())["20-Ideias/Ideia - Contexto importa.md"]


def test_descricao_longa(amb):
    nota = amb.vault / "20-Ideias" / "Ideia - Contexto importa.md"
    nota.write_text(nota.read_text().replace("descricao: M", "descricao: " + "x" * 170 + " M"))
    assert "máximo 160" in motivos(amb.exportar())["20-Ideias/Ideia - Contexto importa.md"]


def test_publicar_texto_e_erro(amb):
    nota = amb.vault / "20-Ideias" / "Ideia - Segredo.md"
    nota.write_text(nota.read_text().replace("publicar: false", 'publicar: "true"'))
    assert "booleano" in motivos(amb.exportar())["20-Ideias/Ideia - Segredo.md"]


def test_yaml_quebrado_com_publicar_e_erro(amb):
    (amb.vault / "20-Ideias" / "Quebrada.md").write_text("---\npublicar: true\ntitulo: [aberto\n---\ncorpo\n")
    assert "frontmatter inválido" in motivos(amb.exportar())["20-Ideias/Quebrada.md"]


def test_nao_sobrescreve_arquivo_fixo(amb):
    (amb.content / "ideias" / "contexto-importa.md").write_text("---\ntitle: Manual\npublish: true\n---\n")
    res = amb.exportar()
    assert "não é arquivo gerado" in motivos(res)["20-Ideias/Ideia - Contexto importa.md"]
    assert "Manual" in amb.ler("ideias/contexto-importa.md")
