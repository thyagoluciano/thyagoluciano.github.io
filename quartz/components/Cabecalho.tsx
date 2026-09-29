import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, pathToRoot, resolveRelative } from "../util/path"
import { classNames } from "../util/lang"
import { i18n } from "../i18n"

// [texto, slug de destino]
const ITENS: [string, string][] = [
  ["Artigos", "artigos/index"],
  ["Ideias", "ideias/index"],
  ["Clube", "clube/index"],
  ["Temas", "temas/index"],
  ["Sobre", "sobre"],
  ["Newsletter", "newsletter"],
]

const Cabecalho: QuartzComponent = ({ fileData, cfg, displayClass }: QuartzComponentProps) => {
  const slug = fileData.slug!
  const titulo = cfg.pageTitle ?? i18n(cfg.locale).propertyDefaults.title
  return (
    <>
      <a class={classNames(displayClass, "site-title")} href={pathToRoot(slug)}>
        {titulo}
      </a>
      <nav class={classNames(displayClass, "site-nav")} aria-label="Principal">
        <ul>
          {ITENS.map(([texto, destino]) => {
            const secao = destino.replace(/\/index$/, "")
            const atual = slug === destino || slug.startsWith(`${secao}/`)
            return (
              <li>
                <a
                  class="internal"
                  href={resolveRelative(slug, destino as FullSlug)}
                  aria-current={atual ? "page" : undefined}
                >
                  {texto}
                </a>
              </li>
            )
          })}
        </ul>
      </nav>
    </>
  )
}

Cabecalho.css = `
.site-title {
  font-family: var(--titleFont);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--dark);
  text-decoration: none;
  white-space: nowrap;
}
.site-nav {
  order: 3;
  width: 100%;
}
.site-nav ul {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1.25rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.site-nav a {
  font-family: var(--headerFont);
  font-size: 0.95rem;
  color: var(--darkgray);
  text-decoration: none;
  padding: 0.25rem 0;
  border-bottom: 2px solid transparent;
}
.site-nav a:hover {
  color: var(--tertiary);
}
.site-nav a[aria-current="page"] {
  color: var(--dark);
  border-bottom-color: var(--secondary);
}
`

export default (() => Cabecalho) satisfies QuartzComponentConstructor
