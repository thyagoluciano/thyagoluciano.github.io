import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"
import { QuartzTransformerPlugin } from "./quartz/plugins/types"
import PaginaDePasta from "./quartz/components/PaginaDePasta"
import PaginaDeTag from "./quartz/components/PaginaDeTag"

const BASE_URL = "thyagoluciano.com.br"

/**
 * `<html lang="pt-BR">` em todas as páginas (o Quartz usaria só "pt").
 * Precisa rodar depois do Plugin.FrontMatter().
 */
const MetadadosDoSite: QuartzTransformerPlugin = () => ({
  name: "MetadadosDoSite",
  markdownPlugins: () => [
    () => (_tree, file) => {
      const fm = file.data.frontmatter
      if (!fm) return
      fm.lang = "pt-BR"
    },
  ],
})

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Thyago Luciano",
    pageTitleSuffix: " · Thyago Luciano",
    enableSPA: true,
    enablePopovers: false, // sem prévia ao passar o mouse (decisão do autor)
    analytics: null, // decisão pendente (PRD §10)
    locale: "pt-BR",
    baseUrl: BASE_URL,
    ignorePatterns: ["private", "templates", ".obsidian"],
    defaultDateType: "published",
    theme: {
      fontOrigin: "local", // fontes em quartz/static/fonts, declaradas em quartz/components/Cabeca.tsx
      cdnCaching: false,
      typography: {
        header: "Inter",
        body: "Source Serif 4",
        code: "JetBrains Mono",
      },
      colors: {
        lightMode: {
          light: "#fbfaf7",
          lightgray: "#e6e3dc",
          gray: "#6f6d66",
          darkgray: "#34332f",
          dark: "#1c1b18",
          secondary: "#2f5d8a",
          tertiary: "#a65d34",
          highlight: "rgba(47, 93, 138, 0.10)",
          textHighlight: "#fff23688",
        },
        darkMode: {
          light: "#16161a",
          lightgray: "#2a2a31",
          gray: "#8b8a95",
          darkgray: "#d8d6d0",
          dark: "#f1efe9",
          secondary: "#8cb4dc",
          tertiary: "#e0a07a",
          highlight: "rgba(140, 180, 220, 0.12)",
          textHighlight: "#b3aa0288",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      MetadadosDoSite(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "absolute" }),
      Plugin.Description(),
    ],
    filters: [Plugin.ExplicitPublish()], // 2ª barreira: só páginas com publish: true,
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage({ pageBody: PaginaDePasta() }),
      Plugin.TagPage({ pageBody: PaginaDeTag() }),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
        rssLimit: 20,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      Plugin.CNAME(),
    ],
  },
}

export default config
