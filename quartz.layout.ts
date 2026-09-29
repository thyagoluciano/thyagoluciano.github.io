import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
// Componentes novos (SPEC 9.3): importados direto para não editar o index.ts do Quartz
import Cabeca from "./quartz/components/Cabeca"
import Cabecalho from "./quartz/components/Cabecalho"
import Newsletter from "./quartz/components/Newsletter"
import MencionadoEm from "./quartz/components/MencionadoEm"
import ArtigosRecentes from "./quartz/components/ArtigosRecentes"
import Rodape from "./quartz/components/Rodape"
import Grafo from "./quartz/components/Grafo"

// TODO: confirmar os endereços das redes. Endereço vazio = o link não aparece no rodapé.
const SUBSTACK_URL = "" // decisão pendente (PRD §10): sem endereço, o botão leva para /newsletter
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

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Cabeca(),
  header: [Cabecalho(), Component.Search(), Component.Darkmode()],
  afterBody: [
    Component.ConditionalRender({
      component: ArtigosRecentes({ limite: 5 }),
      condition: (page) => slugDe(page) === "index",
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
  ],
  footer: Rodape({ links }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs({ rootName: "Início" }),
      condition: (page) => slugDe(page) !== "index",
    }),
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
  left: [],
  right: [
    Component.ConditionalRender({
      component: Component.DesktopOnly(Component.TableOfContents()),
      condition: geradoPeloExportador,
    }),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs({ rootName: "Início" }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
  ],
  left: [],
  right: [],
}
