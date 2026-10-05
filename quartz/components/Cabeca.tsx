import { i18n } from "../i18n"
import { FullSlug, getFileExtension, joinSegments, pathToRoot, simplifySlug } from "../util/path"
import { CSSResourceToStyleElement, JSResourceToScriptElement } from "../util/resources"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { unescapeHTML } from "../util/escape"
import { dadosEstruturados, serializar } from "./dadosEstruturados"
const LATIN =
  "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"

const FONTES: [string, string, string][] = [
  // [família, estilo, arquivo]
  ["Inter", "normal", "inter-latin-wght-normal"],
  ["Source Serif 4", "normal", "source-serif-4-latin-wght-normal"],
  ["Source Serif 4", "italic", "source-serif-4-latin-wght-italic"],
  ["JetBrains Mono", "normal", "jetbrains-mono-latin-wght-normal"],
]

const fontFaces = (baseDir: string) =>
  FONTES.map(
    ([familia, estilo, arquivo]) =>
      `@font-face{font-family:"${familia}";font-style:${estilo};font-weight:100 900;font-display:optional;` +
      `src:url(${joinSegments(baseDir, `static/fonts/${arquivo}.woff2`)}) format("woff2");unicode-range:${LATIN}}`,
  ).join("")

export default (() => {
  const Cabeca: QuartzComponent = ({ cfg, fileData, externalResources }: QuartzComponentProps) => {
    const titleSuffix = cfg.pageTitleSuffix ?? ""
    // `tituloSeo` (frontmatter) substitui o título e o sufixo no <title> e nos cartões sociais
    const title =
      (fileData.frontmatter?.tituloSeo as string | undefined) ??
      (fileData.frontmatter?.title ?? i18n(cfg.locale).propertyDefaults.title) + titleSuffix
    const description =
      fileData.frontmatter?.socialDescription ??
      fileData.frontmatter?.description ??
      unescapeHTML(fileData.description?.trim() ?? i18n(cfg.locale).propertyDefaults.description)

    const { css, js, additionalHead } = externalResources

    const url = new URL(`https://${cfg.baseUrl ?? "example.com"}`)
    const path = url.pathname as FullSlug
    const baseDir = fileData.slug === "404" ? path : pathToRoot(fileData.slug!)
    const iconPath = joinSegments(baseDir, "static/icon.png")

    // Url canônica da página (pastas terminam em "/", como no sitemap)
    const simples = fileData.slug === "404" ? "/" : simplifySlug(fileData.slug!)
    const socialUrl = `https://${cfg.baseUrl}/${simples === "/" ? "" : simples}`

    // Imagem de compartilhamento: capa da nota; sem capa, a imagem padrão (PNG 1200×630).
    // Não usamos o CustomOgImages porque ele gera WebP, que o LinkedIn não exibe.
    const capa = typeof fileData.frontmatter?.capa === "string" ? fileData.frontmatter.capa : ""
    const imagem = capa
      ? `https://${cfg.baseUrl}/${capa}`
      : `https://${cfg.baseUrl}/static/og-padrao.png`
    const extensao = (getFileExtension(imagem) ?? ".png").replace(".", "").toLowerCase()
    const tipoImagem = `image/${extensao === "jpg" ? "jpeg" : extensao === "svg" ? "svg+xml" : extensao}`

    const dados = dadosEstruturados({ cfg, fileData, url: socialUrl, imagem, descricao: description })

    return (
      <head>
        <title>{title}</title>
        <meta charSet="utf-8" />
        {/* Fontes hospedadas no próprio site (quartz/static/fonts): sem requisições a terceiros */}
        <link
          rel="preload"
          href={joinSegments(baseDir, "static/fonts/inter-latin-wght-normal.woff2")}
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <link
          rel="preload"
          href={joinSegments(baseDir, "static/fonts/source-serif-4-latin-wght-normal.woff2")}
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <style dangerouslySetInnerHTML={{ __html: fontFaces(baseDir) }} />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <meta name="og:site_name" content={cfg.pageTitle}></meta>
        <meta property="og:title" content={title} />
        <meta
          property="og:type"
          content={fileData.frontmatter?.tipo === "post" ? "article" : "website"}
        />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta property="og:description" content={description} />
        <meta property="og:image:alt" content={description} />

        <meta property="og:image" content={imagem} />
        <meta property="og:image:url" content={imagem} />
        <meta name="twitter:image" content={imagem} />
        <meta property="og:image:type" content={tipoImagem} />
        {!capa && (
          <>
            <meta property="og:image:width" content="1200" />
            <meta property="og:image:height" content="630" />
          </>
        )}

        {cfg.baseUrl && (
          <>
            <meta property="twitter:domain" content={cfg.baseUrl}></meta>
            <meta property="og:url" content={socialUrl}></meta>
            <meta property="twitter:url" content={socialUrl}></meta>
          </>
        )}

        <link rel="icon" href={iconPath} />
        {fileData.slug !== "404" && <link rel="canonical" href={socialUrl} />}
        <meta name="description" content={description} />
        <meta name="generator" content="Quartz" />
        {dados && (
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: serializar(dados) }}
          />
        )}

        {css.map((resource) => CSSResourceToStyleElement(resource, true))}
        {js
          .filter((resource) => resource.loadTime === "beforeDOMReady")
          .map((res) => JSResourceToScriptElement(res, true))}
        {additionalHead.map((resource) => {
          if (typeof resource === "function") {
            return resource(fileData)
          } else {
            return resource
          }
        })}
      </head>
    )
  }

  return Cabeca
}) satisfies QuartzComponentConstructor
