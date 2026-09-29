import { PageLayout, SharedLayout } from "./quartz/cfg"
import { FullSlug } from "./quartz/util/path"
import * as Component from "./quartz/components"
// Componentes novos (SPEC 9.3 e SPEC-TEMA-CHIRPY): importados direto para não editar o index.ts do Quartz
import Cabeca from "./quartz/components/Cabeca"
import Newsletter from "./quartz/components/Newsletter"
import MencionadoEm from "./quartz/components/MencionadoEm"
import ListaDeCards from "./quartz/components/ListaDeCards"
import Arquivo from "./quartz/components/Arquivo"
import Rodape from "./quartz/components/Rodape"
import Grafo from "./quartz/components/Grafo"
import BarraLateral from "./quartz/components/BarraLateral"
import BarraSuperior from "./quartz/components/BarraSuperior"
import RedesSociais from "./quartz/components/RedesSociais"
import VoltarAoTopo from "./quartz/components/VoltarAoTopo"
import AncoraConteudo from "./quartz/components/AncoraConteudo"

// TODO: confirmar os endereços das redes. Endereço vazio = o link não aparece.
const SUBSTACK_URL = "" // decisão pendente (PRD §10): sem endereço, o botão leva para /newsletter
const FRASE = "TODO: frase curta sobre você" // decisão pendente (SPEC-TEMA-CHIRPY §13)
const REDES: Record<string, string> = {
  LinkedIn: "https://www.linkedin.com/in/thyagoluciano",
  X: "https://x.com/thyagoluciano",
  Threads: "https://www.threads.net/@thyagoluciano",
  Instagram: "https://www.instagram.com/thyagoluciano",
  Substack: SUBSTACK_URL,
  RSS: "/index.xml",
  GitHub: "https://github.com/thyagoluciano",
}
const links = Object.fromEntries(Object.entries(REDES).filter(([, endereco]) => endereco))

const slugDe = (page: { fileData: { slug?: string } }) => page.fileData.slug ?? ""
const geradoPeloExportador = (page: { fileData: { frontmatter?: Record<string, any> } }) =>
  page.fileData.frontmatter?.gerado === true

// Barra lateral (avatar, título, menu) + redes e alternância de tema no rodapé dela
const barraLateral = [
  BarraLateral({ frase: FRASE }),
  Component.Flex({
    components: [
      { Component: RedesSociais({ links }), grow: true },
      { Component: Component.Darkmode() },
    ],
  }),
]

// Barra superior: botão e título (mobile), breadcrumb e busca
const barraSuperior = [
  BarraSuperior(),
  Component.ConditionalRender({
    component: Component.Breadcrumbs({ rootName: "Início" }),
    condition: (page) => slugDe(page) !== "index",
  }),
  Component.Search(),
]

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Cabeca(),
  header: barraSuperior,
  afterBody: [
    Component.ConditionalRender({
      component: ListaDeCards({
        titulo: "Artigos recentes",
        limite: 10,
        filtro: (f) => f.slug!.startsWith("artigos/") && f.slug !== "artigos/index",
        verTodos: { texto: "Ver todos", slug: "arquivo" as FullSlug },
        vazio: "Os primeiros artigos chegam em breve.",
      }),
      condition: (page) => slugDe(page) === "index",
    }),
    Component.ConditionalRender({
      component: Arquivo(),
      condition: (page) => slugDe(page) === "arquivo",
    }),
    Component.ConditionalRender({
      component: Newsletter({ substackUrl: SUBSTACK_URL }),
      condition: (page) => !["sobre", "newsletter", "404"].includes(slugDe(page)),
    }),
    MencionadoEm(),
    // grafo local só em ideias e temas
    Component.ConditionalRender({
      component: Grafo(),
      condition: (page) => /^(ideias|temas)\//.test(slugDe(page)) && !/\/index$/.test(slugDe(page)),
    }),
    // grafo global na página /temas/
    Component.ConditionalRender({
      component: Grafo({ global: true }),
      condition: (page) => slugDe(page) === "temas/index",
    }),
    VoltarAoTopo(),
  ],
  footer: Rodape({ links: {} }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    AncoraConteudo(),
    Component.ArticleTitle(),
    Component.ConditionalRender({
      component: Component.ContentMeta(),
      condition: geradoPeloExportador,
    }),
    Component.ConditionalRender({
      component: Component.TagList(),
      condition: geradoPeloExportador,
    }),
  ],
  left: barraLateral,
  right: [
    Component.ConditionalRender({
      component: Component.DesktopOnly(Component.TableOfContents()),
      condition: geradoPeloExportador,
    }),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [AncoraConteudo(), Component.ArticleTitle()],
  left: barraLateral,
  right: [],
}
