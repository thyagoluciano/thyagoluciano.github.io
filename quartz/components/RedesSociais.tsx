import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { joinSegments, pathToRoot } from "../util/path"
import Icone from "./Icone"

interface Options {
  /** nome -> endereço. Endereços que começam com "/" são internos (ex.: "/index.xml"). */
  links: Record<string, string>
}

const ICONES: Record<string, string> = {
  LinkedIn: "linkedin",
  X: "x",
  Threads: "threads",
  Instagram: "instagram",
  Substack: "substack",
  RSS: "rss",
  GitHub: "github",
}

export default ((opts?: Options) => {
  const links = opts?.links ?? {}

  const RedesSociais: QuartzComponent = ({ fileData }: QuartzComponentProps) => {
    const href = (link: string) =>
      link.startsWith("/") ? joinSegments(pathToRoot(fileData.slug!), link.slice(1)) : link
    return (
      <ul class="redes" aria-label="Redes e contato">
        {Object.entries(links).map(([nome, link]) => (
          <li>
            <a href={href(link)} aria-label={nome} title={nome} rel="me noopener">
              <Icone nome={ICONES[nome] ?? "sobre"} tamanho={18} />
            </a>
          </li>
        ))}
      </ul>
    )
  }

  RedesSociais.css = `
.redes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.1rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.redes a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  color: var(--darkgray);
  background: transparent;
}
.redes a:hover {
  color: var(--tertiary);
}
`
  return RedesSociais
}) satisfies QuartzComponentConstructor
