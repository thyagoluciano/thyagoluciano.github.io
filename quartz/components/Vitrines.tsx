import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"
import { classNames } from "../util/lang"
import { Cartoes, CSS_CARDS, exportada, maisRecentesPrimeiro } from "./ListaDeCards"

interface Vitrine {
  titulo: string
  /** Pasta das notas (ex.: "posts"); o "Ver todos" leva ao index dela. */
  pasta: string
  vazio: string
}

interface Options {
  vitrines: Vitrine[]
  limite: number
}

const PADRAO: Vitrine[] = [
  { titulo: "Posts", pasta: "posts", vazio: "Os primeiros posts chegam em breve." },
  { titulo: "Leituras", pasta: "leituras", vazio: "As primeiras resenhas chegam em breve." },
  { titulo: "Radar", pasta: "radar", vazio: "Os primeiros itens do radar chegam em breve." },
]

/** Página inicial: uma vitrine de cards por seção (Posts, Leituras e Radar). */
export default ((opts?: Partial<Options>) => {
  const vitrines = opts?.vitrines ?? PADRAO
  const limite = opts?.limite ?? 3

  const Vitrines: QuartzComponent = ({
    allFiles,
    fileData,
    cfg,
    displayClass,
  }: QuartzComponentProps) => (
    <div class={classNames(displayClass, "vitrines")}>
      {vitrines.map((v) => {
        const paginas = allFiles
          .filter(
            (f) =>
              exportada(f) && f.slug!.startsWith(`${v.pasta}/`) && f.slug !== `${v.pasta}/index`,
          )
          .sort(maisRecentesPrimeiro(cfg))
        return (
          <section class="vitrine">
            <header class="vitrine-cabeca">
              <h2>{v.titulo}</h2>
              <a
                class="internal"
                href={resolveRelative(fileData.slug!, `${v.pasta}/index` as FullSlug)}
              >
                Ver todos →
              </a>
            </header>
            {paginas.length === 0 ? (
              <p class="cards-vazio">{v.vazio}</p>
            ) : (
              <Cartoes paginas={paginas.slice(0, limite)} fileData={fileData} cfg={cfg} />
            )}
          </section>
        )
      })}
    </div>
  )

  Vitrines.css =
    CSS_CARDS +
    `
.vitrines {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}
.vitrine-cabeca {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--lightgray);
}
.vitrine-cabeca h2 {
  margin: 0;
  font-size: 1.4rem;
}
.vitrine-cabeca a {
  font-family: var(--headerFont);
  font-size: 0.9rem;
}
.vitrine .cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr));
  gap: 1rem;
}
@media (min-width: 850px) {
  .vitrine .card.com-capa {
    flex-direction: column;
  }
  .vitrine .card.com-capa .card-capa-caixa {
    width: auto;
    aspect-ratio: 16 / 9;
    min-height: 0;
  }
}
`
  return Vitrines
}) satisfies QuartzComponentConstructor
