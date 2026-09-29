import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, getAllSegmentPrefixes, resolveRelative } from "../util/path"
import { Date } from "./Date"
import { dataDeAtualizacao, exportada } from "./ListaDeCards"

interface Options {
  atualizados: number
  tags: number
}

// Painel do lado direito (desktop): "Atualizados recentemente" e "Tags em alta".
// Só considera notas exportadas; páginas fixas nunca entram.
export default ((opts?: Partial<Options>) => {
  const opcoes: Options = { atualizados: 5, tags: 10, ...opts }

  const PainelDireito: QuartzComponent = ({ allFiles, fileData, cfg }: QuartzComponentProps) => {
    const notas = allFiles.filter(exportada)
    const atualizados = notas
      .map((nota) => ({ nota, data: dataDeAtualizacao(cfg, nota) }))
      .filter((item) => item.data)
      .sort(
        (a, b) =>
          b.data!.getTime() - a.data!.getTime() ||
          (a.nota.frontmatter?.title ?? "").localeCompare(b.nota.frontmatter?.title ?? ""),
      )
      .slice(0, opcoes.atualizados)

    const contagem = new Map<string, number>()
    for (const nota of notas) {
      for (const tag of new Set((nota.frontmatter?.tags ?? []).flatMap(getAllSegmentPrefixes))) {
        contagem.set(tag, (contagem.get(tag) ?? 0) + 1)
      }
    }
    const tags = [...contagem.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .slice(0, opcoes.tags)

    if (atualizados.length === 0 && tags.length === 0) return null
    return (
      <aside class="painel" aria-label="Painel lateral">
        {atualizados.length > 0 && (
          <section class="painel-bloco">
            <h2>Atualizados recentemente</h2>
            <ul class="painel-lista">
              {atualizados.map(({ nota, data }) => (
                <li>
                  <a class="internal" href={resolveRelative(fileData.slug!, nota.slug!)}>
                    {nota.frontmatter?.title}
                  </a>
                  <span class="painel-data">
                    <Date date={data!} locale={cfg.locale} />
                  </span>
                </li>
              ))}
            </ul>
          </section>
        )}
        {tags.length > 0 && (
          <section class="painel-bloco">
            <h2>Tags em alta</h2>
            <ul class="painel-tags">
              {tags.map(([tag, n]) => (
                <li>
                  <a
                    class="internal tag-link"
                    href={resolveRelative(fileData.slug!, `tags/${tag}` as FullSlug)}
                  >
                    {tag}
                  </a>
                  <span class="painel-contagem">{n}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </aside>
    )
  }

  PainelDireito.css = `
.painel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  margin-bottom: 1rem;
}
.painel-bloco {
  padding: 1rem 1.1rem;
  border: 1px solid var(--lightgray);
  border-radius: 10px;
  background: var(--superficie);
}
.painel-bloco h2 {
  margin: 0 0 0.6rem;
  font-size: 0.85rem;
  font-family: var(--headerFont);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--gray);
}
.painel-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.painel-lista li {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
.painel .painel-lista a.internal {
  background: none;
  padding: 0;
  color: var(--darkgray);
  font-family: var(--headerFont);
  font-size: 0.9rem;
  line-height: 1.35;
}
.painel-lista a:hover {
  color: var(--tertiary);
}
.painel-data {
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.75rem;
}
.painel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.painel-tags li {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.painel-contagem {
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.75rem;
}
`
  return PainelDireito
}) satisfies QuartzComponentConstructor
