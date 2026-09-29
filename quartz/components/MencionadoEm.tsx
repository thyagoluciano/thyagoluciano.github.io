import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/backlinks.scss"
import { resolveRelative, simplifySlug } from "../util/path"
import { classNames } from "../util/lang"
import OverflowListFactory from "./OverflowList"

// Backlinks com o título "Mencionado em" (o texto do Quartz em pt-BR é "Backlinks").
export default (() => {
  const { OverflowList, overflowListAfterDOMLoaded } = OverflowListFactory()

  const MencionadoEm: QuartzComponent = ({
    fileData,
    allFiles,
    displayClass,
  }: QuartzComponentProps) => {
    const slug = simplifySlug(fileData.slug!)
    const paginas = allFiles.filter((file) => file.links?.includes(slug))
    if (paginas.length === 0) {
      return null
    }
    return (
      <div class={classNames(displayClass, "backlinks")}>
        <h2>Mencionado em</h2>
        <OverflowList>
          {paginas.map((f) => (
            <li>
              <a href={resolveRelative(fileData.slug!, f.slug!)} class="internal">
                {f.frontmatter?.title}
              </a>
            </li>
          ))}
        </OverflowList>
      </div>
    )
  }

  MencionadoEm.css = style
  MencionadoEm.afterDOMLoaded = overflowListAfterDOMLoaded
  return MencionadoEm
}) satisfies QuartzComponentConstructor
