import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"
import { QuartzPluginData } from "../plugins/vfile"
import { GlobalConfiguration } from "../cfg"
import { classNames } from "../util/lang"
import readingTime from "reading-time"
import { Date, getDate } from "./Date"
import Icone from "./Icone"

export const ROTULO_TIPO: Record<string, string> = {
  artigo: "Artigo",
  ideia: "Ideia",
  resenha: "Resenha",
  encontro: "Encontro",
  tema: "Tema",
}

/** Só notas geradas pelo exportador: páginas fixas nunca entram em cards, painéis ou arquivo. */
export const exportada = (f: QuartzPluginData) => f.frontmatter?.gerado === true

/** Data de publicação decrescente; empate por título. */
export const maisRecentesPrimeiro =
  (cfg: GlobalConfiguration) => (a: QuartzPluginData, b: QuartzPluginData) => {
    const da = getDate(cfg, a)?.getTime() ?? 0
    const db = getDate(cfg, b)?.getTime() ?? 0
    return db - da || (a.frontmatter?.title ?? "").localeCompare(b.frontmatter?.title ?? "")
  }

interface CartoesProps {
  paginas: QuartzPluginData[]
  fileData: QuartzPluginData
  cfg: GlobalConfiguration
}

/** Lista de cards (SPEC-TEMA-CHIRPY 5.1). Já recebe as páginas filtradas e ordenadas. */
export function Cartoes({ paginas, fileData, cfg }: CartoesProps) {
  return (
    <ul class="cards">
      {paginas.map((pagina) => {
        const fm = (pagina.frontmatter ?? {}) as Record<string, any>
        const data = getDate(cfg, pagina)
        const minutos = pagina.text ? Math.max(1, Math.ceil(readingTime(pagina.text).minutes)) : 0
        const capa = typeof fm.capa === "string" && fm.capa ? fm.capa : ""
        const tags: string[] = (fm.tags ?? []).slice(0, 3)
        return (
          <li class={classNames(undefined, "card", capa ? "com-capa" : "")}>
            {capa && (
              <div class="card-capa-caixa">
                <img
                  class="card-capa"
                  src={resolveRelative(fileData.slug!, capa as FullSlug)}
                  width="640"
                  height="360"
                  alt=""
                  loading="lazy"
                  decoding="async"
                />
              </div>
            )}
            <div class="card-corpo">
              <h3>
                <a class="internal" href={resolveRelative(fileData.slug!, pagina.slug!)}>
                  {fm.title}
                </a>
              </h3>
              {pagina.description && <p class="card-resumo">{pagina.description}</p>}
              <div class="card-meta">
                {data && (
                  <span>
                    <Icone nome="calendario" tamanho={14} />{" "}
                    <Date date={data} locale={cfg.locale} />
                  </span>
                )}
                {ROTULO_TIPO[fm.tipo] && <span class="card-tipo">{ROTULO_TIPO[fm.tipo]}</span>}
                {minutos > 0 && (
                  <span>
                    <Icone nome="relogio" tamanho={14} /> {minutos} min
                  </span>
                )}
              </div>
              {tags.length > 0 && (
                <ul class="card-tags">
                  {tags.map((tag) => (
                    <li>
                      <a
                        class="internal tag-link"
                        href={resolveRelative(fileData.slug!, `tags/${tag}` as FullSlug)}
                      >
                        {tag}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </li>
        )
      })}
    </ul>
  )
}

export const CSS_CARDS = `
.cards {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.card {
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--lightgray);
  border-radius: 10px;
  background: var(--superficie);
  box-shadow: var(--sombra);
  transition: box-shadow 0.15s ease;
}
.card:hover {
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}
.card:hover h3 a {
  color: var(--tertiary);
}
.card-capa-caixa {
  position: relative;
  aspect-ratio: 16 / 9;
  background: var(--lightgray);
}
.card-capa {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  margin: 0;
  border-radius: 0;
  max-width: none;
}
.card-corpo {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  min-width: 0;
}
.card h3 {
  margin: 0;
  font-size: 1.2rem;
  line-height: 1.3;
}
.card h3 a {
  background: none;
  color: var(--dark);
  text-decoration: none;
}
.card h3 a::after {
  content: "";
  position: absolute;
  inset: 0;
}
.card-resumo {
  margin: 0;
  color: var(--darkgray);
  font-size: 0.95rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem 1rem;
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.8rem;
}
.card-meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.card-tipo {
  font-weight: 600;
}
.card-tags {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
@media (min-width: 850px) {
  .card.com-capa {
    flex-direction: row;
  }
  .card.com-capa .card-capa-caixa {
    width: 230px;
    flex-shrink: 0;
    aspect-ratio: auto;
    min-height: 9.5rem;
  }
}
.cards-titulo {
  font-size: 1.25rem;
  margin: 2rem 0 1rem;
}
.cards-vazio {
  color: var(--gray);
}
.cards-mais {
  margin-top: 1rem;
}
`

interface Options {
  titulo?: string
  limite: number
  filtro: (f: QuartzPluginData) => boolean
  /** Link "Ver todos" ao fim da lista. */
  verTodos?: { texto: string; slug: FullSlug }
  vazio?: string
}

/** Cards avulsos, usados na página inicial. */
export default ((opts?: Partial<Options>) => {
  const opcoes: Options = { limite: 10, filtro: exportada, ...opts }

  const ListaDeCards: QuartzComponent = ({
    allFiles,
    fileData,
    cfg,
    displayClass,
  }: QuartzComponentProps) => {
    const paginas = allFiles
      .filter((f) => exportada(f) && opcoes.filtro(f))
      .sort(maisRecentesPrimeiro(cfg))
    return (
      <section class={classNames(displayClass, "cards-secao")}>
        {opcoes.titulo && <h2 class="cards-titulo">{opcoes.titulo}</h2>}
        {paginas.length === 0 ? (
          <p class="cards-vazio">{opcoes.vazio ?? "Os primeiros textos chegam em breve."}</p>
        ) : (
          <Cartoes paginas={paginas.slice(0, opcoes.limite)} fileData={fileData} cfg={cfg} />
        )}
        {opcoes.verTodos && (
          <p class="cards-mais">
            <a class="internal" href={resolveRelative(fileData.slug!, opcoes.verTodos.slug)}>
              {opcoes.verTodos.texto} →
            </a>
          </p>
        )}
      </section>
    )
  }

  ListaDeCards.css = CSS_CARDS
  return ListaDeCards
}) satisfies QuartzComponentConstructor
