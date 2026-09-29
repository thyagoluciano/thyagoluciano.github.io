import { QuartzComponent, QuartzComponentConstructor } from "./types"
import Icone from "./Icone"

export default (() => {
  const VoltarAoTopo: QuartzComponent = () => (
    <button type="button" class="voltar-ao-topo" aria-label="Voltar ao topo" hidden>
      <Icone nome="topo" tamanho={20} />
    </button>
  )

  VoltarAoTopo.css = `
.voltar-ao-topo {
  position: fixed;
  right: 1.25rem;
  bottom: 1.25rem;
  z-index: 8;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  padding: 0;
  border: 1px solid var(--lightgray);
  border-radius: 50%;
  background: var(--superficie);
  color: var(--darkgray);
  box-shadow: var(--sombra);
  cursor: pointer;
}
.voltar-ao-topo[hidden] {
  display: none;
}
.voltar-ao-topo:hover {
  color: var(--tertiary);
}
`

  VoltarAoTopo.afterDOMLoaded = `
if (!window.__topoLigado) {
  window.__topoLigado = true
  const atualizar = () => {
    const b = document.querySelector(".voltar-ao-topo")
    if (b) b.hidden = window.scrollY < 300
  }
  window.addEventListener("scroll", atualizar, { passive: true })
  document.addEventListener("nav", atualizar)
  document.addEventListener("click", (e) => {
    if (e.target.closest(".voltar-ao-topo")) window.scrollTo({ top: 0, behavior: "smooth" })
  })
}
`
  return VoltarAoTopo
}) satisfies QuartzComponentConstructor
