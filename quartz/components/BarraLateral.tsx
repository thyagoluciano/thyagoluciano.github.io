import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, joinSegments, pathToRoot, resolveRelative } from "../util/path"
import { i18n } from "../i18n"
import Icone from "./Icone"

interface Options {
  /** Frase curta abaixo do título. */
  frase: string
  /** Caminho do avatar dentro de quartz/static/. */
  avatar: string
}

// [texto, ícone, slug de destino]
const ITENS: [string, string, string][] = [
  ["Início", "casa", "index"],
  ["Artigos", "artigos", "artigos/index"],
  ["Ideias", "ideias", "ideias/index"],
  ["Clube", "clube", "clube/index"],
  ["Temas", "temas", "temas/index"],
  ["Tags", "tags", "tags/index"],
  ["Arquivo", "arquivo", "arquivo"],
  ["Sobre", "sobre", "sobre"],
  ["Newsletter", "newsletter", "newsletter"],
]

export default ((opts?: Partial<Options>) => {
  const frase = opts?.frase ?? ""
  const avatar = opts?.avatar ?? "avatar.png"

  const BarraLateral: QuartzComponent = ({ fileData, cfg }: QuartzComponentProps) => {
    const slug = fileData.slug!
    const raiz = pathToRoot(slug)
    const titulo = cfg.pageTitle ?? i18n(cfg.locale).propertyDefaults.title
    return (
      <>
        <a class="pular" href="#conteudo">
          Pular para o conteúdo
        </a>
        <aside id="barra-lateral" class="barra-lateral" aria-label="Barra lateral">
          <a class="avatar" href={raiz} aria-label="Ir para o início">
            <img
              src={joinSegments(raiz, `static/${avatar}`)}
              width="96"
              height="96"
              alt=""
              decoding="async"
            />
          </a>
          <a class="marca" href={raiz}>
            {titulo}
          </a>
          {frase && <p class="frase">{frase}</p>}
          <nav aria-label="Principal">
            <ul>
              {ITENS.map(([texto, icone, destino]) => {
                const secao = destino.replace(/\/index$/, "")
                const atual =
                  destino === "index"
                    ? slug === "index"
                    : slug === destino || slug.startsWith(`${secao}/`)
                return (
                  <li>
                    <a
                      class="internal"
                      href={resolveRelative(slug, destino as FullSlug)}
                      aria-current={atual ? "page" : undefined}
                    >
                      <Icone nome={icone} />
                      <span>{texto}</span>
                    </a>
                  </li>
                )
              })}
            </ul>
          </nav>
        </aside>
      </>
    )
  }

  BarraLateral.css = `
.pular {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}
.pular:focus {
  width: auto;
  height: auto;
  overflow: visible;
  clip-path: none;
  left: 0.5rem;
  top: 0.5rem;
  z-index: 100;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  background: var(--secondary);
  color: var(--light);
  font-family: var(--headerFont);
  text-decoration: none;
}
.barra-lateral {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.barra-lateral .avatar {
  display: block;
  box-sizing: border-box;
  flex-shrink: 0;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid var(--superficie);
  box-shadow: var(--sombra);
}
.barra-lateral .avatar img {
  display: block;
  width: 100%;
  height: 100%;
  max-width: none;
  margin: 0;
  border-radius: 0;
  object-fit: cover;
}
.barra-lateral .marca {
  font-family: var(--titleFont);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--dark);
  text-decoration: none;
  text-align: center;
}
.barra-lateral .frase {
  margin: 0;
  color: var(--gray);
  font-size: 0.9rem;
  text-align: center;
}
.barra-lateral nav {
  align-self: stretch;
  margin-top: 1.25rem;
}
.barra-lateral ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.barra-lateral nav a {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.6rem 0.9rem;
  border-radius: 8px;
  font-family: var(--headerFont);
  font-size: 0.95rem;
  color: var(--darkgray);
  text-decoration: none;
  background: transparent;
}
.barra-lateral nav a:hover {
  color: var(--tertiary);
}
.barra-lateral nav a[aria-current="page"] {
  color: var(--dark);
  font-weight: 600;
  background: var(--highlight);
}
`

  // Gaveta mobile: abre/fecha o menu, fecha ao navegar, com Esc ou tocando fora; o foco fica preso enquanto aberta.
  BarraLateral.afterDOMLoaded = `
if (!window.__gavetaLigada) {
  window.__gavetaLigada = true
  const aberta = () => document.body.dataset.gaveta === "aberta"
  const botao = () => document.querySelector(".menu-botao")
  const fechar = (devolverFoco) => {
    if (!aberta()) return
    delete document.body.dataset.gaveta
    const b = botao()
    if (b) { b.setAttribute("aria-expanded", "false"); if (devolverFoco) b.focus() }
  }
  document.addEventListener("click", (e) => {
    // "Pular para o conteúdo": o SPA do Quartz não move o foco sozinho; sem isso o próximo Tab volta ao início
    if (e.target.closest(".pular")) {
      setTimeout(() => document.getElementById("conteudo")?.focus({ preventScroll: true }), 0)
      return
    }
    const b = e.target.closest(".menu-botao")
    if (b) {
      if (aberta()) return fechar(true)
      document.body.dataset.gaveta = "aberta"
      b.setAttribute("aria-expanded", "true")
      const primeiro = document.querySelector(".barra-lateral nav a")
      if (primeiro) primeiro.focus()
      return
    }
    if (e.target === document.body || e.target.closest(".left.sidebar a")) fechar(false)
  })
  document.addEventListener("keydown", (e) => {
    if (!aberta()) return
    if (e.key === "Escape") return fechar(true)
    if (e.key !== "Tab") return
    const itens = [...document.querySelectorAll(".left.sidebar a[href]:not(.pular), .left.sidebar button")]
    if (itens.length === 0) return
    const primeiro = itens[0], ultimo = itens[itens.length - 1]
    if (e.shiftKey && document.activeElement === primeiro) { e.preventDefault(); ultimo.focus() }
    else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primeiro.focus() }
  })
  document.addEventListener("nav", () => fechar(false))
}
`
  return BarraLateral
}) satisfies QuartzComponentConstructor
