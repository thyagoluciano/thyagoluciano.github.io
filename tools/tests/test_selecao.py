import pytest

import exportar
from conftest import HOJE

EXPORTADAS = {
    "posts/agendado-passado.md",
    "posts/como-uso-ia.md",
    "posts/contexto-importa.md",
    "leituras/a-arte-da-guerra.md",
    "leituras/encontros/encontro-setembro-2026.md",
    "radar/quartz.md",
}


def motivos(res):
    return {e["nota"]: e["motivo"] for e in res.erros}


def test_exporta_somente_notas_elegiveis(amb):
    res = amb.exportar()
    assert {n["caminho"] for n in res.novas} == EXPORTADAS
    assert {n for n in amb.gerados() if n.endswith(".md")} == EXPORTADAS


def test_destinos_por_tipo(amb):
    amb.exportar()
    assert 'tipo: post' in amb.ler("posts/como-uso-ia.md")
    assert 'tipo: ferramenta' in amb.ler("radar/quartz.md")
    assert 'tipo: resenha' in amb.ler("leituras/a-arte-da-guerra.md")
    assert 'tipo: encontro' in amb.ler("leituras/encontros/encontro-setembro-2026.md")


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
        ("20-Ideias/Ideia - Contexto importa.md", "fica só no Obsidian"),
        ("40-Mapas/Mapa - Inteligência Artificial.md", "fica só no Obsidian"),
    ],
)
def test_notas_bloqueadas_geram_erro(amb, nota, trecho):
    res = amb.exportar()
    assert trecho in motivos(res)[nota]


def test_notas_privadas_sem_erro_e_sem_saida(amb):
    res = amb.exportar()
    assert not any("Segredo" in e["nota"] or "Nota privada" in e["nota"] for e in res.erros)
    assert not (amb.content / "posts" / "segredo.md").exists()


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
    assert "posts/agendado-futuro.md" in {n["caminho"] for n in res.novas}


def test_slug_invalido(amb):
    nota = amb.vault / "50-Conteudo/Site/Site - Contexto importa.md"
    nota.write_text(nota.read_text().replace("slug: contexto-importa", "slug: Contexto Importa"))
    assert "inválido" in motivos(amb.exportar())["50-Conteudo/Site/Site - Contexto importa.md"]


def test_descricao_longa(amb):
    nota = amb.vault / "50-Conteudo/Site/Site - Contexto importa.md"
    nota.write_text(nota.read_text().replace("descricao: M", "descricao: " + "x" * 170 + " M"))
    assert "máximo 160" in motivos(amb.exportar())["50-Conteudo/Site/Site - Contexto importa.md"]


def test_publicar_texto_e_erro(amb):
    nota = amb.vault / "20-Ideias" / "Ideia - Segredo.md"
    nota.write_text(nota.read_text().replace("publicar: false", 'publicar: "true"'))
    assert "booleano" in motivos(amb.exportar())["20-Ideias/Ideia - Segredo.md"]


def test_yaml_quebrado_com_publicar_e_erro(amb):
    (amb.vault / "20-Ideias" / "Quebrada.md").write_text("---\npublicar: true\ntitulo: [aberto\n---\ncorpo\n")
    assert "frontmatter inválido" in motivos(amb.exportar())["20-Ideias/Quebrada.md"]


def test_nao_sobrescreve_arquivo_fixo(amb):
    (amb.content / "posts" / "contexto-importa.md").write_text("---\ntitle: Manual\npublish: true\n---\n")
    res = amb.exportar()
    assert "não é arquivo gerado" in motivos(res)["50-Conteudo/Site/Site - Contexto importa.md"]
    assert "Manual" in amb.ler("posts/contexto-importa.md")


def test_ideia_e_mapa_com_publicar_true_abortam_no_estrito(amb):
    res = amb.exportar(estrito=True)
    assert res.abortado
    assert "remova 'publicar: true'" in motivos(res)["20-Ideias/Ideia - Contexto importa.md"]
    assert amb.gerados() == set()


def test_ideia_e_mapa_nunca_saem_no_content(amb):
    amb.exportar()
    assert not (amb.content / "ideias").exists() and not (amb.content / "temas").exists()
    assert not any("contexto-importa" in n and n.startswith("ideias") for n in amb.gerados())


def ferramenta(amb):
    return amb.vault / "70-Radar" / "Ferramenta - Quartz.md"


def test_ferramenta_sem_campo_obrigatorio_e_erro(amb):
    for campo in ("url", "autor_projeto", "categoria", "estado", "por_que"):
        nota = ferramenta(amb)
        original = nota.read_text()
        linhas = [l for l in original.split("\n") if not l.startswith(f"{campo}:")]
        nota.write_text("\n".join(linhas))
        assert f"ferramenta sem '{campo}'" in motivos(amb.exportar())["70-Radar/Ferramenta - Quartz.md"]
        nota.write_text(original)


def test_ferramenta_estado_invalido(amb):
    nota = ferramenta(amb)
    nota.write_text(nota.read_text().replace("estado: testando", "estado: talvez"))
    motivo = motivos(amb.exportar())["70-Radar/Ferramenta - Quartz.md"]
    assert "estado 'talvez' inválido" in motivo and "quero-testar" in motivo


def test_ferramenta_url_invalida(amb):
    nota = ferramenta(amb)
    nota.write_text(nota.read_text().replace("url: https://quartz.jzhao.xyz", "url: quartz.jzhao.xyz"))
    assert "'url' deve começar com http" in motivos(amb.exportar())["70-Radar/Ferramenta - Quartz.md"]


def test_ferramenta_sem_campos_opcionais_exporta(amb):
    nota = ferramenta(amb)
    linhas = [l for l in nota.read_text().split("\n") if not l.startswith(("repositorio:", "licenca:"))]
    nota.write_text("\n".join(linhas))
    res = amb.exportar()
    assert "radar/quartz.md" in {n["caminho"] for n in res.novas}
    texto = amb.ler("radar/quartz.md")
    assert "repositorio" not in texto and "licenca" not in texto


def test_slug_encontros_reservado_em_leituras(amb):
    nota = amb.vault / "10-Fontes/Livros/A Arte da Guerra/Livro - A Arte da Guerra.md"
    nota.write_text(nota.read_text().replace("slug: a-arte-da-guerra", "slug: encontros"))
    assert "reservado em leituras" in motivos(amb.exportar())["10-Fontes/Livros/A Arte da Guerra/Livro - A Arte da Guerra.md"]
