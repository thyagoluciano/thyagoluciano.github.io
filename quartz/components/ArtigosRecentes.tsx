import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"
import { byDateAndAlphabetical } from "./PageList"
import { Date, getDate } from "./Date"
import { classNames } from "../util/lang"

interface Options {
  limite: number
}

export default ((opts?: Partial<Options>) => {
  const limite = opts?.limite ?? 5

  const ArtigosRecentes: QuartzComponent = ({
    allFiles,
    fileData,
    cfg,
    displayClass,
  }: QuartzComponentProps) => {
    const artigos = allFiles
      .filter((f) => f.slug!.startsWith("artigos/") && f.slug !== "artigos/index")
      .sort(byDateAndAlphabetical(cfg))
    return (
      <section class={classNames(displayClass, "artigos-recentes")}>
        <h2>Artigos recentes</h2>
        {artigos.length === 0 ? (
          <p>Os primeiros artigos chegam em breve.</p>
        ) : (
          <ul>
            {artigos.slice(0, limite).map((pagina) => (
              <li>
                <h3>
                  <a href={resolveRelative(fileData.slug!, pagina.slug!)} class="internal">
                    {pagina.frontmatter?.title}
                  </a>
                </h3>
                {pagina.dates && (
                  <p class="meta">
                    <Date date={getDate(cfg, pagina)!} locale={cfg.locale} />
                  </p>
                )}
                {pagina.description && <p>{pagina.description}</p>}
              </li>
            ))}
          </ul>
        )}
        <p>
          <a href={resolveRelative(fileData.slug!, "artigos/index" as FullSlug)} class="internal">
            Ver todos os artigos →
          </a>
        </p>
      </section>
    )
  }

  ArtigosRecentes.css = `
.artigos-recentes ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.artigos-recentes li {
  margin: 0 0 1.25rem;
}
.artigos-recentes h3 {
  margin: 0;
  font-size: 1.15rem;
}
.artigos-recentes p {
  margin: 0.15rem 0 0;
}
.artigos-recentes .meta {
  color: var(--gray);
  font-size: 0.9rem;
}
`
  return ArtigosRecentes
}) satisfies QuartzComponentConstructor
