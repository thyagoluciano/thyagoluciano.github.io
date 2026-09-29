import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, getAllSegmentPrefixes, resolveRelative, simplifySlug } from "../util/path"
import { Root } from "hast"
import { ComponentChildren } from "preact"
import { htmlToJsx } from "../util/jsx"
import { Cartoes, exportada, maisRecentesPrimeiro } from "./ListaDeCards"

const plural = (n: number, singular: string, pluralTxt: string) =>
  `${n} ${n === 1 ? singular : pluralTxt}`

// Corpo do TagPage: em /tags/ a lista de tags com contagem; em /tags/<tag>/ os cards das notas.
export default (() => {
  const PaginaDeTag: QuartzComponent = ({
    tree,
    fileData,
    allFiles,
    cfg,
  }: QuartzComponentProps) => {
    const slug = fileData.slug
    if (!(slug?.startsWith("tags/") || slug === "tags")) {
      throw new Error(`Component "PaginaDeTag" tried to render a non-tag page: ${slug}`)
    }
    const tag = simplifySlug(slug.slice("tags/".length) as FullSlug)
    const notas = allFiles.filter(exportada)
    const comTag = (t: string) =>
      notas.filter((f) => (f.frontmatter?.tags ?? []).flatMap(getAllSegmentPrefixes).includes(t))
    const semTexto = (tree as Root).children.length === 0
    const conteudo = (
      semTexto ? fileData.description : htmlToJsx(fileData.filePath!, tree)
    ) as ComponentChildren
    const classes = ((fileData.frontmatter?.cssclasses as string[]) ?? []).join(" ")

    if (tag === "/") {
      const contagem = new Map<string, number>()
      for (const nota of notas) {
        for (const t of new Set((nota.frontmatter?.tags ?? []).flatMap(getAllSegmentPrefixes))) {
          contagem.set(t, (contagem.get(t) ?? 0) + 1)
        }
      }
      const tags = [...contagem.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      return (
        <div class="popover-hint">
          <article class={classes}>{conteudo}</article>
          <h2 class="cards-titulo">{plural(tags.length, "tag", "tags")}</h2>
          {tags.length === 0 ? (
            <p class="cards-vazio">Ainda não há tags.</p>
          ) : (
            <ul class="nuvem-tags">
              {tags.map(([t, n]) => (
                <li>
                  <a
                    class="internal tag-link"
                    href={resolveRelative(slug as FullSlug, `tags/${t}` as FullSlug)}
                  >
                    {t}
                  </a>
                  <span class="nuvem-contagem">{n}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )
    }

    const paginas = comTag(tag).sort(maisRecentesPrimeiro(cfg))
    return (
      <div class="popover-hint">
        <article class={classes}>{conteudo}</article>
        <h2 class="cards-titulo">{plural(paginas.length, "publicação", "publicações")}</h2>
        <div class="page-listing">
          {paginas.length > 0 && <Cartoes paginas={paginas} fileData={fileData} cfg={cfg} />}
        </div>
      </div>
    )
  }

  PaginaDeTag.css = `
.nuvem-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem 1rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.nuvem-tags li {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.nuvem-contagem {
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.8rem;
}
`
  return PaginaDeTag
}) satisfies QuartzComponentConstructor
