import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
// Componentes novos (SPEC 9.3 e SPEC-TEMA-CHIRPY): importados direto para não editar o index.ts do Quartz
import Cabeca from "./quartz/components/Cabeca"
import Vitrines from "./quartz/components/Vitrines"
import Arquivo from "./quartz/components/Arquivo"
import Rodape from "./quartz/components/Rodape"
import BarraLateral from "./quartz/components/BarraLateral"
import BarraSuperior from "./quartz/components/BarraSuperior"
import RedesSociais from "./quartz/components/RedesSociais"
import VoltarAoTopo from "./quartz/components/VoltarAoTopo"
import AncoraConteudo from "./quartz/components/AncoraConteudo"
import PainelDireito from "./quartz/components/PainelDireito"
import MetaDoPost from "./quartz/components/MetaDoPost"
import CapaDoPost from "./quartz/components/CapaDoPost"
import Compartilhar from "./quartz/components/Compartilhar"
import LeiaTambem from "./quartz/components/LeiaTambem"
import AnteriorProximo from "./quartz/components/AnteriorProximo"

// Redes e contato. Endereço vazio = o link não aparece.
const SUBSTACK_URL = "https://thyagoluciano.substack.com/subscribe" // vazio: o botão leva para /newsletter
const FRASE = "Desenvolvedor, explorando tecnologias e compartilhando conhecimento."
const REDES: Record<string, string> = {
  LinkedIn: "https://www.linkedin.com/in/thyagoluciano",
  // X: "https://x.com/thyagoluciano",
  // Threads: "https://www.threads.net/@thyagoluciano",
  // Instagram: "https://www.instagram.com/thyagoluciano",
  Substack: SUBSTACK_URL,
  RSS: "/index.xml",
  GitHub: "https://github.com/thyagoluciano",
}
const links = Object.fromEntries(Object.entries(REDES).filter(([, endereco]) => endereco))

const slugDe = (page: { fileData: { slug?: string } }) => page.fileData.slug ?? ""
const geradoPeloExportador = (page: { fileData: { frontmatter?: Record<string, any> } }) =>
  page.fileData.frontmatter?.gerado === true

const tipoDe = (page: { fileData: { frontmatter?: Record<string, any> } }) =>
  String(page.fileData.frontmatter?.tipo ?? "")
// Painel direito (atualizados, tags em alta): fora das páginas fixas Sobre e Newsletter e da 404
const comPainel = (page: { fileData: { slug?: string } }) =>
  !["sobre", "newsletter", "404"].includes(slugDe(page))
const painelDireito = Component.ConditionalRender({
  component: PainelDireito(),
  condition: comPainel,
})

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
      component: Vitrines(),
      condition: (page) => slugDe(page) === "index",
    }),
    Component.ConditionalRender({
      component: Arquivo(),
      condition: (page) => slugDe(page) === "arquivo",
    }),
    // blocos de post (só notas exportadas)
    Component.ConditionalRender({
      component: Component.TagList(),
      condition: geradoPeloExportador,
    }),
    Component.ConditionalRender({
      component: Compartilhar(),
      condition: geradoPeloExportador,
    }),
    Component.ConditionalRender({
      component: LeiaTambem(),
      condition: (page) => ["post", "resenha"].includes(tipoDe(page)),
    }),
    Component.ConditionalRender({
      component: AnteriorProximo(),
      condition: geradoPeloExportador,
    }),
    VoltarAoTopo(),
  ],
  footer: Rodape({ links: {} }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    AncoraConteudo(),
    Component.ConditionalRender({
      component: CapaDoPost(),
      condition: geradoPeloExportador,
    }),
    Component.ConditionalRender({
      component: Component.ArticleTitle(),
      condition: (page) => slugDe(page) !== "index",
    }),
    Component.ConditionalRender({
      component: MetaDoPost(),
      condition: geradoPeloExportador,
    }),
  ],
  left: barraLateral,
  right: [
    painelDireito,
    Component.ConditionalRender({
      component: Component.DesktopOnly(Component.TableOfContents()),
      condition: (page) => geradoPeloExportador(page) && (page.fileData.toc?.length ?? 0) >= 2,
    }),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [AncoraConteudo(), Component.ArticleTitle()],
  left: barraLateral,
  right: [painelDireito],
}
