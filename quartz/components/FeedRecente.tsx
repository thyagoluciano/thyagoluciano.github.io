import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"
import { classNames } from "../util/lang"
import { Cartoes, CSS_CARDS, maisRecentesPrimeiro, publicada } from "./ListaDeCards"

interface Options {
  limite: number
}

/**
 * Página inicial: um único feed de cards (posts, ferramentas, games, radar e leituras),
 * sem separar por seção, com a publicação mais recente primeiro. O tipo de cada item
 * aparece no próprio card (Post, Ferramenta, Game...).
 */
export default ((opts?: Partial<Options>) => {
  const limite = opts?.limite ?? 12

  const FeedRecente: QuartzComponent = ({
    allFiles,
    fileData,
    cfg,
    displayClass,
  }: QuartzComponentProps) => {
    const paginas = allFiles.filter(publicada).sort(maisRecentesPrimeiro(cfg))
    return (
      <section class={classNames(displayClass, "feed-recente")}>
        <header class="feed-cabeca">
          <h2>Publicações recentes</h2>
          <a class="internal" href={resolveRelative(fileData.slug!, "arquivo" as FullSlug)}>
            Ver arquivo →
          </a>
        </header>
        {paginas.length === 0 ? (
          <p class="cards-vazio">As primeiras publicações chegam em breve.</p>
        ) : (
          <Cartoes paginas={paginas.slice(0, limite)} fileData={fileData} cfg={cfg} />
        )}
      </section>
    )
  }

  FeedRecente.css =
    CSS_CARDS +
    `
.feed-cabeca {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--lightgray);
}
.feed-cabeca h2 {
  margin: 0;
  font-size: 1.4rem;
}
.feed-cabeca a {
  font-family: var(--headerFont);
  font-size: 0.9rem;
}
.feed-recente .cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr));
  gap: 1rem;
}
@media (min-width: 850px) {
  .feed-recente .card.com-capa {
    flex-direction: column;
  }
  .feed-recente .card.com-capa .card-capa-caixa {
    width: auto;
    aspect-ratio: 16 / 9;
    min-height: 0;
  }
}
`
  return FeedRecente
}) satisfies QuartzComponentConstructor
