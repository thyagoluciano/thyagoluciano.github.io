import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { resolveRelative } from "../util/path"
import { QuartzPluginData } from "../plugins/vfile"
import { getDate } from "./Date"
import { ROTULO_TIPO, ferramentaPropria, maisRecentesPrimeiro, publicada } from "./ListaDeCards"

const MESES = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
]

// Linha do tempo por ano e mês de tudo o que foi publicado (posts, itens do radar, resenhas, encontros e ferramentas).
export default (() => {
  const Arquivo: QuartzComponent = ({ allFiles, fileData, cfg }: QuartzComponentProps) => {
    const paginas = allFiles
      .filter((f) => publicada(f) && getDate(cfg, f))
      .sort(maisRecentesPrimeiro(cfg))
    if (paginas.length === 0) {
      return <p class="cards-vazio">Nenhuma publicação ainda.</p>
    }
    // ano -> mês -> páginas (já em ordem decrescente)
    const anos = new Map<number, Map<number, QuartzPluginData[]>>()
    for (const pagina of paginas) {
      const data = getDate(cfg, pagina)!
      const meses = anos.get(data.getFullYear()) ?? new Map<number, QuartzPluginData[]>()
      meses.set(data.getMonth(), [...(meses.get(data.getMonth()) ?? []), pagina])
      anos.set(data.getFullYear(), meses)
    }
    return (
      <div class="arquivo">
        {[...anos.entries()].map(([ano, meses]) => (
          <section>
            <h2>{ano}</h2>
            {[...meses.entries()].map(([mes, itens]) => (
              <div class="arquivo-mes">
                <h3>{MESES[mes]}</h3>
                <ul>
                  {itens.map((pagina) => (
                    <li>
                      <span class="arquivo-dia">
                        {String(getDate(cfg, pagina)!.getDate()).padStart(2, "0")}
                      </span>
                      <a class="internal" href={resolveRelative(fileData.slug!, pagina.slug!)}>
                        {pagina.frontmatter?.title}
                      </a>
                      <span class="arquivo-tipo">
                        {ferramentaPropria(pagina)
                          ? "Ferramenta"
                          : ROTULO_TIPO[String(pagina.frontmatter?.tipo)]}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </section>
        ))}
      </div>
    )
  }

  Arquivo.css = `
.arquivo h2 {
  margin: 2rem 0 0.5rem;
  font-size: 1.5rem;
}
.arquivo h3 {
  margin: 1rem 0 0.25rem;
  font-size: 1rem;
  color: var(--gray);
  font-family: var(--headerFont);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.arquivo ul {
  list-style: none;
  margin: 0;
  padding: 0 0 0 1rem;
  border-left: 2px solid var(--lightgray);
}
.arquivo li {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0.25rem 0;
}
.arquivo-dia {
  min-width: 1.5rem;
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.85rem;
}
.arquivo-tipo {
  margin-left: auto;
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.8rem;
}
`
  return Arquivo
}) satisfies QuartzComponentConstructor
