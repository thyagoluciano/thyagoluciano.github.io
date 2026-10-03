import errno
import json
import subprocess
import sys

import pytest

import exportar
from conftest import FIXTURE_VAULT, HOJE, TOOLS, hashes


def test_vault_nao_e_alterado(amb):
    antes = hashes(amb.vault)
    amb.exportar()
    amb.exportar(simular=True)
    assert hashes(amb.vault) == antes


def test_simular_nao_escreve_nada(amb):
    antes = hashes(amb.content)
    res = amb.exportar(simular=True)
    assert res.simulacao and len(res.novas) == 6 and not res.aplicado
    assert hashes(amb.content) == antes and not amb.manifesto.exists()


def test_vazamento_no_content(amb):
    amb.exportar()
    for arq in amb.content.rglob("*"):
        if arq.is_file():
            assert b"SEGREDO-" not in arq.read_bytes(), arq
    assert "SEGREDO-" not in amb.manifesto.read_text()


def test_vault_inexistente(amb, tmp_path):
    with pytest.raises(exportar.VaultIndisponivel):
        exportar.exportar(tmp_path / "nada", amb.content, amb.manifesto, hoje=HOJE)


def test_arquivo_do_icloud_nao_baixado_aborta(amb, monkeypatch):
    alvo = amb.vault / "50-Conteudo/Site/Site - Contexto importa.md"
    original = exportar._esta_offline
    monkeypatch.setattr(exportar, "_esta_offline", lambda p: p == alvo or original(p))
    chamadas = []
    monkeypatch.setattr(exportar, "_baixar", lambda p: chamadas.append(p))
    with pytest.raises(exportar.VaultIndisponivel) as e:
        amb.exportar()
    assert e.value.arquivos == ["50-Conteudo/Site/Site - Contexto importa.md"]
    assert len(chamadas) == exportar.TENTATIVAS_DOWNLOAD
    assert amb.gerados() == set() and not amb.manifesto.exists()


def test_download_que_funciona_na_segunda_tentativa(amb, monkeypatch):
    alvo = amb.vault / "50-Conteudo/Site/Site - Contexto importa.md"
    estado = {"baixou": False}
    original = exportar._esta_offline
    monkeypatch.setattr(exportar, "_esta_offline", lambda p: (p == alvo and not estado["baixou"]) or original(p))
    monkeypatch.setattr(exportar, "_baixar", lambda p: estado.update(baixou=True))
    assert "posts/contexto-importa.md" in {n["caminho"] for n in amb.exportar().novas}


def test_edeadlk_tambem_e_tratado(tmp_path, monkeypatch):
    arq = tmp_path / "a.md"
    arq.write_text("x")
    import builtins

    real_open = builtins.open

    def falha(caminho, *a, **k):
        if str(caminho) == str(arq):
            raise OSError(errno.EDEADLK, "Resource deadlock avoided")
        return real_open(caminho, *a, **k)

    monkeypatch.setattr(builtins, "open", falha)
    with pytest.raises(exportar.ArquivoNaoBaixado):
        exportar.ler_bytes(arq)


def test_imagem_nao_baixada_aborta(amb, monkeypatch):
    alvo = amb.vault / "_anexos" / "usada.png"
    original = exportar._esta_offline
    monkeypatch.setattr(exportar, "_esta_offline", lambda p: p == alvo or original(p))
    with pytest.raises(exportar.VaultIndisponivel) as e:
        amb.exportar()
    assert e.value.arquivos == ["_anexos/usada.png"]
    assert amb.gerados() == set()


def cli(*args):
    return subprocess.run([sys.executable, str(TOOLS / "exportar.py"), *args], capture_output=True, text=True)


def test_cli_json_e_codigos_de_saida(amb):
    base = ["--vault", str(amb.vault), "--content", str(amb.content), "--manifesto", str(amb.manifesto), "--hoje", "2026-09-28"]
    r = cli(*base, "--simular", "--json")
    dados = json.loads(r.stdout)
    assert r.returncode == 0 and len(dados["novas"]) == 6 and len(dados["erros"]) == 11
    assert dados["novas"][0]["url"].startswith("https://thyagoluciano.github.io/")
    assert dados["auditoria"]["ok"] is True
    assert cli(*base, "--estrito").returncode == 1
    r = cli("--vault", str(amb.vault / "nada"), "--content", str(amb.content))
    assert r.returncode == 2 and "não encontrado" in r.stderr


def test_cli_sem_vault_configurado(monkeypatch, amb):
    cfg = TOOLS / "config.toml"
    bak = TOOLS / "config.toml.bak"
    tinha_cfg = cfg.exists()
    if tinha_cfg:
        cfg.rename(bak)
    try:
        env_limpo = {"PATH": "/usr/bin:/bin"}
        r = subprocess.run([sys.executable, str(TOOLS / "exportar.py")], capture_output=True, text=True, env=env_limpo)
        assert r.returncode == 2 and "Vault não configurado" in r.stderr
    finally:
        if tinha_cfg and bak.exists():
            bak.rename(cfg)


def test_resumo_em_texto(amb):
    base = ["--vault", str(amb.vault), "--content", str(amb.content), "--manifesto", str(amb.manifesto), "--hoje", "2026-09-28"]
    r = cli(*base, "--simular")
    assert "SIMULAÇÃO" in r.stdout and "6 novas" in r.stdout and "11 erros" in r.stdout
    assert "Auditoria de privacidade: sem ocorrências" in r.stdout
