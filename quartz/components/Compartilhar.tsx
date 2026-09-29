import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { simplifySlug } from "../util/path"
import Icone from "./Icone"

// Compartilhar: LinkedIn, X e copiar link, sempre com o endereço canônico da página.
export default (() => {
  const Compartilhar: QuartzComponent = ({ fileData, cfg }: QuartzComponentProps) => {
    const simples = simplifySlug(fileData.slug!)
    const url = `https://${cfg.baseUrl}/${simples === "/" ? "" : simples}`
    const titulo = String(fileData.frontmatter?.title ?? "")
    const u = encodeURIComponent(url)
    return (
      <div class="compartilhar">
        <span class="compartilhar-rotulo">Compartilhar</span>
        <a
          href={`https://www.linkedin.com/sharing/share-offsite/?url=${u}`}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Compartilhar no LinkedIn"
        >
          <Icone nome="linkedin" tamanho={18} />
        </a>
        <a
          href={`https://x.com/intent/post?url=${u}&text=${encodeURIComponent(titulo)}`}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Compartilhar no X"
        >
          <Icone nome="x" tamanho={18} />
        </a>
        <button type="button" class="copiar-link" data-url={url} aria-label="Copiar link">
          <Icone nome="copiar" tamanho={18} />
        </button>
        <span class="copiar-status" role="status" aria-live="polite"></span>
      </div>
    )
  }

  Compartilhar.css = `
.compartilhar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 2rem 0 1rem;
  font-family: var(--headerFont);
  font-size: 0.9rem;
  color: var(--gray);
}
.compartilhar a,
.compartilhar button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.1rem;
  height: 2.1rem;
  padding: 0;
  border: 1px solid var(--lightgray);
  border-radius: 50%;
  background: var(--superficie);
  color: var(--darkgray);
  cursor: pointer;
}
.compartilhar a:hover,
.compartilhar button:hover {
  color: var(--tertiary);
}
.copiar-status {
  color: var(--darkgray);
  font-size: 0.85rem;
}
`

  Compartilhar.afterDOMLoaded = `
if (!window.__copiarLigado) {
  window.__copiarLigado = true
  document.addEventListener("click", async (e) => {
    const botao = e.target.closest(".copiar-link")
    if (!botao) return
    const status = botao.parentElement.querySelector(".copiar-status")
    let ok = true
    try {
      await navigator.clipboard.writeText(botao.dataset.url)
    } catch {
      const campo = document.createElement("textarea")
      campo.value = botao.dataset.url
      document.body.appendChild(campo)
      campo.select()
      ok = document.execCommand("copy")
      campo.remove()
    }
    status.textContent = ok ? "Link copiado" : "Não foi possível copiar"
    setTimeout(() => (status.textContent = ""), 2500)
  })
}
`
  return Compartilhar
}) satisfies QuartzComponentConstructor
