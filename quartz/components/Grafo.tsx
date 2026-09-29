import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { pathToRoot } from "../util/path"
import { classNames } from "../util/lang"

interface Options {
  /** false: vizinhança direta da página (grafo local). true: todas as páginas conectadas (grafo global). */
  global?: boolean
}

/**
 * Grafo de conexões leve (SVG, sem dependências). Substitui o Graph do Quartz, cujo script
 * (d3 + pixi.js) pesa ~200 KB e derruba o Lighthouse mobile abaixo de 95 (RNF3).
 * Usa o índice de conteúdo (`fetchData`) e só considera artigos, ideias, clube e temas.
 */
export default ((opts?: Options) => {
  const global = opts?.global ?? false

  const Grafo: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => (
    <div class={classNames(displayClass, "grafo")}>
      <h2>{global ? "Mapa de conexões" : "Conexões"}</h2>
      <div
        class="grafo-container"
        data-global={global ? "1" : "0"}
        data-slug={fileData.slug}
        data-raiz={pathToRoot(fileData.slug!)}
        role="img"
        aria-label="Grafo de conexões entre as páginas do site"
      ></div>
    </div>
  )

  Grafo.css = `
.grafo h2 {
  font-size: 1.25rem;
  margin: 0 0 0.5rem;
}
.grafo-container {
  position: relative;
  border: 1px solid var(--lightgray);
  border-radius: 8px;
  height: 260px;
  overflow: hidden;
}
.grafo-container[data-global="1"] {
  height: 420px;
}
.grafo-container svg {
  display: block;
  width: 100%;
  height: 100%;
}
.grafo-container .grafo-vazio {
  margin: 0;
  padding: 1rem;
  color: var(--gray);
}
.grafo-container line {
  stroke: var(--lightgray);
  stroke-width: 1.25;
}
.grafo-container .no {
  cursor: pointer;
}
.grafo-container .no circle {
  fill: var(--gray);
  transition: fill 0.15s;
}
.grafo-container .no.atual circle {
  fill: var(--secondary);
}
.grafo-container .no:hover circle {
  fill: var(--tertiary);
}
.grafo-container .no text {
  fill: var(--darkgray);
  font-family: var(--bodyFont);
  font-size: 11px;
  text-anchor: middle;
  pointer-events: none;
}
.grafo-container .no.oculto text {
  opacity: 0;
}
.grafo-container .no.oculto:hover text {
  opacity: 1;
}
`

  Grafo.afterDOMLoaded = `
document.addEventListener("nav", async () => {
  const el = document.querySelector(".grafo-container")
  if (!el) return
  const global = el.dataset.global === "1"
  const simples = (s) => s.replace(/\\/?index$/, "") || "/"
  const dados = await fetchData
  const secao = /^(artigos|ideias|clube|temas)\\//
  const info = new Map()
  for (const [chave, d] of Object.entries(dados)) {
    const id = simples(chave)
    if (secao.test(chave) && !/(^|\\/)index$/.test(chave)) info.set(id, { id, titulo: d.title, links: d.links || [] })
  }
  const arestas = []
  for (const n of info.values()) for (const alvo of n.links) if (info.has(alvo) && alvo !== n.id) arestas.push([n.id, alvo])
  const atual = simples(el.dataset.slug)
  let ids
  if (global) {
    ids = new Set(arestas.flat())
  } else {
    ids = new Set([atual])
    for (const [a, b] of arestas) { if (a === atual) ids.add(b); if (b === atual) ids.add(a) }
  }
  const nos = [...ids].filter((id) => info.has(id)).map((id) => ({ ...info.get(id), grau: 0 }))
  const porId = new Map(nos.map((n) => [n.id, n]))
  const ligacoes = arestas.filter(([a, b]) => porId.has(a) && porId.has(b) && (global || a === atual || b === atual))
  for (const [a, b] of ligacoes) { porId.get(a).grau++; porId.get(b).grau++ }
  el.replaceChildren()
  if (nos.length < 2) {
    const p = document.createElement("p")
    p.className = "grafo-vazio"
    p.textContent = "Ainda sem conexões com outras páginas."
    el.appendChild(p)
    return
  }
  const w = el.clientWidth || 600
  const h = el.clientHeight || 260
  const n = nos.length
  const raio = Math.min(w, h) / 3
  nos.forEach((no, i) => {
    const ang = (2 * Math.PI * i) / n
    no.x = w / 2 + Math.cos(ang) * raio
    no.y = h / 2 + Math.sin(ang) * raio
    no.vx = 0
    no.vy = 0
  })
  const distancia = n > 25 ? 45 : 110
  for (let t = 0; t < 300; t++) {
    const alfa = 1 - t / 300
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      const a = nos[i], b = nos[j]
      let dx = b.x - a.x, dy = b.y - a.y
      const d = Math.max(Math.hypot(dx, dy), 1)
      const f = (1800 / d) * alfa
      dx /= d; dy /= d
      a.vx -= dx * f; a.vy -= dy * f; b.vx += dx * f; b.vy += dy * f
    }
    for (const [ia, ib] of ligacoes) {
      const a = porId.get(ia), b = porId.get(ib)
      let dx = b.x - a.x, dy = b.y - a.y
      const d = Math.max(Math.hypot(dx, dy), 1)
      const f = 0.08 * (d - distancia)
      dx /= d; dy /= d
      a.vx += dx * f; a.vy += dy * f; b.vx -= dx * f; b.vy -= dy * f
    }
    for (const no of nos) {
      no.vx += (w / 2 - no.x) * 0.02
      no.vy += (h / 2 - no.y) * 0.02
      no.vx *= 0.8; no.vy *= 0.8
      no.x = Math.min(w - 40, Math.max(40, no.x + no.vx))
      no.y = Math.min(h - 18, Math.max(18, no.y + no.vy))
    }
  }
  const ns = "http://www.w3.org/2000/svg"
  const mk = (tag, attrs) => { const e = document.createElementNS(ns, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e }
  const svg = mk("svg", { viewBox: "0 0 " + w + " " + h, "aria-hidden": "true" })
  for (const [ia, ib] of ligacoes) {
    const a = porId.get(ia), b = porId.get(ib)
    svg.appendChild(mk("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y }))
  }
  const rotular = n <= 25
  for (const no of nos) {
    const g = mk("g", { class: "no" + (no.id === atual ? " atual" : "") + (rotular || no.id === atual ? "" : " oculto") })
    g.appendChild(mk("circle", { cx: no.x, cy: no.y, r: 4 + 2 * Math.sqrt(no.grau) }))
    const texto = mk("text", { x: no.x, y: no.y - 10 - 2 * Math.sqrt(no.grau) })
    texto.textContent = no.titulo.length > 26 ? no.titulo.slice(0, 25) + "…" : no.titulo
    g.appendChild(texto)
    if (no.id !== atual) g.addEventListener("click", () => window.spaNavigate(new URL(el.dataset.raiz + "/" + no.id, location.href)))
    svg.appendChild(g)
  }
  el.appendChild(svg)
})
`
  return Grafo
}) satisfies QuartzComponentConstructor
