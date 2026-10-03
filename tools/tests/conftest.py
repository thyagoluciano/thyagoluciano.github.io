import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import exportar  # noqa: E402

FIXTURE_VAULT = Path(__file__).resolve().parent / "fixtures" / "vault"
HOJE = date(2026, 9, 28)


@pytest.fixture(autouse=True)
def sem_espera(monkeypatch):
    monkeypatch.setattr(exportar, "ESPERA_DOWNLOAD", 0)
    monkeypatch.setattr(exportar, "_baixar", lambda caminho: None)


class Ambiente:
    """Vault, content e manifesto temporários (cópias do vault de exemplo)."""

    def __init__(self, base: Path):
        self.vault = base / "vault"
        self.content = base / "content"
        self.manifesto = base / "manifesto.json"
        shutil.copytree(FIXTURE_VAULT, self.vault)
        for pasta in ("posts", "radar", "leituras"):
            (self.content / pasta).mkdir(parents=True)
            (self.content / pasta / "index.md").write_text(
                f"---\ntitle: {pasta}\npublish: true\n---\n\nTODO: {pasta}\n", encoding="utf-8"
            )
        (self.content / "leituras" / "index.md").write_text(
            "---\ntitle: Leituras\npublish: true\n---\n\nTODO: leituras\n\n"
            f"{exportar.MARCA_INICIO}\n{exportar.MARCA_FIM}\n",
            encoding="utf-8",
        )
        (self.content / "index.md").write_text("---\ntitle: Início\npublish: true\n---\n", encoding="utf-8")

    def exportar(self, **kw):
        kw.setdefault("hoje", HOJE)
        return exportar.exportar(self.vault, self.content, self.manifesto, **kw)

    def ler(self, rel: str) -> str:
        return (self.content / rel).read_text(encoding="utf-8")

    def gerados(self) -> set[str]:
        return {
            p.relative_to(self.content).as_posix()
            for pasta in exportar.PASTAS_GERADAS
            for p in (self.content / pasta).rglob("*")
            if p.is_file() and p.name != "index.md"
        }


@pytest.fixture
def amb(tmp_path):
    return Ambiente(tmp_path)


def hashes(raiz: Path) -> dict[str, str]:
    import hashlib

    return {
        p.relative_to(raiz).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(raiz.rglob("*"))
        if p.is_file()
    }
