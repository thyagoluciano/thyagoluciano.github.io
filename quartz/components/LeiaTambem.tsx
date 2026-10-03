import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { resolveRelative } from "../util/path"
import { QuartzPluginData } from "../plugins/vfile"
import { Date, getDate } from "./Date"
import { exportada, maisRecentesPrimeiro } from "./ListaDeCards"

const itensEmComum = (a: QuartzPluginData, b: QuartzPluginData) => {
  const em = (f: QuartzPluginData) =>
    new Set<string>(((f.frontmatter?.tags ?? []) as string[]).map((t) => `tag:${t}`))
  const B = em(b)
  return [...em(a)].filter((x) => B.has(x)).length
}

// "Leia também": até 3 notas exportadas do mesmo tipo, com mais tags em comum.
// Sem nada em comum, entram as mais recentes. Nunca inclui a própria página.
export default (() => {
  const LeiaTambem: QuartzComponent = ({ allFiles, fileData, cfg }: QuartzComponentProps) => {
    const tipo = fileData.frontmatter?.tipo
    const candidatas = allFiles
      .filter((f) => exportada(f) && f.slug !== fileData.slug && f.frontmatter?.tipo === tipo)
      .map((f) => ({ f, pontos: itensEmComum(fileData, f) }))
      .sort((a, b) => b.pontos - a.pontos || maisRecentesPrimeiro(cfg)(a.f, b.f))
      .slice(0, 3)
    if (candidatas.length === 0) return null
    return (
      <section class="leia-tambem">
        <h2>Leia também</h2>
        <ul>
          {candidatas.map(({ f }) => {
            const data = getDate(cfg, f)
            return (
              <li>
                <h3>
                  <a class="internal" href={resolveRelative(fileData.slug!, f.slug!)}>
                    {f.frontmatter?.title}
                  </a>
                </h3>
                {f.description && <p>{f.description}</p>}
                {data && (
                  <span class="leia-data">
                    <Date date={data} locale={cfg.locale} />
                  </span>
                )}
              </li>
            )
          })}
        </ul>
      </section>
    )
  }

  LeiaTambem.css = `
.leia-tambem h2 {
  font-size: 1.25rem;
  margin: 2rem 0 0.75rem;
}
.leia-tambem ul {
  display: grid;
  gap: 1rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
@media (min-width: 850px) {
  .leia-tambem ul {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.leia-tambem li {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--lightgray);
  border-radius: 10px;
  background: var(--superficie);
}
.leia-tambem h3 {
  margin: 0;
  font-size: 1rem;
  line-height: 1.3;
}
.leia-tambem h3 a.internal {
  background: none;
  padding: 0;
  color: var(--dark);
}
.leia-tambem p {
  margin: 0;
  color: var(--darkgray);
  font-size: 0.85rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.leia-data {
  margin-top: auto;
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.75rem;
}
`
  return LeiaTambem
}) satisfies QuartzComponentConstructor
