import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/footer.scss"
import { joinSegments, pathToRoot } from "../util/path"

interface Options {
  /** texto -> endereço. Endereços que começam com "/" são internos (ex.: "/index.xml"). */
  links: Record<string, string>
}

export default ((opts?: Options) => {
  const Rodape: QuartzComponent = ({ displayClass, fileData }: QuartzComponentProps) => {
    const ano = new Date().getFullYear()
    const links = opts?.links ?? {}
    const href = (link: string) =>
      link.startsWith("/") ? joinSegments(pathToRoot(fileData.slug!), link.slice(1)) : link
    return (
      <footer class={`${displayClass ?? ""}`}>
        <p>
          © {ano} Thyago Luciano. Feito com <a href="https://quartz.jzhao.xyz/">Quartz</a>.
        </p>
        <ul>
          {Object.entries(links).map(([texto, link]) => (
            <li>
              <a href={href(link)}>{texto}</a>
            </li>
          ))}
        </ul>
      </footer>
    )
  }

  Rodape.css = style
  return Rodape
}) satisfies QuartzComponentConstructor
