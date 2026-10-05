import { GlobalConfiguration } from "../cfg"
import { QuartzPluginData } from "../plugins/vfile"
import { getDate } from "./Date"
import { dataDeAtualizacao, ferramentaPropria } from "./ListaDeCards"

interface Contexto {
  cfg: GlobalConfiguration
  fileData: QuartzPluginData
  /** URL canônica da página. */
  url: string
  imagem: string
  descricao: string
}

const AUTOR = {
  nome: "Thyago Luciano",
  // Mesmos perfis do rodapé da barra lateral (quartz.layout.ts) e da página Sobre
  perfis: [
    "https://www.linkedin.com/in/thyagoluciano",
    "https://www.instagram.com/thyagoluciano",
    "https://github.com/thyagoluciano",
    "https://thyagoluciano.substack.com",
  ],
}

const iso = (data?: Date) => (data ? data.toISOString() : undefined)

/** Remove campos vazios para o JSON-LD não carregar `undefined`. */
const limpar = <T extends Record<string, unknown>>(objeto: T): T =>
  Object.fromEntries(
    Object.entries(objeto).filter(
      ([, valor]) => valor !== undefined && !(Array.isArray(valor) && valor.length === 0),
    ),
  ) as T

/**
 * Dados estruturados (schema.org) da página, como JSON-LD:
 * home → WebSite + Person; posts → BlogPosting; resenhas e encontros → Article;
 * ferramentas escritas no repositório → SoftwareApplication. Demais páginas: nenhum.
 */
export function dadosEstruturados({ cfg, fileData, url, imagem, descricao }: Contexto) {
  const origem = `https://${cfg.baseUrl}`
  const idPessoa = `${origem}/#pessoa`
  const idSite = `${origem}/#site`
  const fm = (fileData.frontmatter ?? {}) as Record<string, any>
  const titulo = String(fm.title ?? "")
  const slug = fileData.slug

  const pessoa = limpar({
    "@type": "Person",
    "@id": idPessoa,
    name: AUTOR.nome,
    url: origem,
    image: `${origem}/static/avatar.png`,
    sameAs: AUTOR.perfis,
  })
  // Fora da home cada página é um documento isolado: autor e site vão embutidos, não por @id
  const autor = limpar({ "@type": "Person", name: AUTOR.nome, url: origem, sameAs: AUTOR.perfis })
  const site = { "@type": "WebSite", name: cfg.pageTitle, url: origem }

  if (slug === "index") {
    return {
      "@context": "https://schema.org",
      "@graph": [
        limpar({
          "@type": "WebSite",
          "@id": idSite,
          name: cfg.pageTitle,
          url: origem,
          description: descricao,
          inLanguage: "pt-BR",
          publisher: { "@id": idPessoa },
        }),
        pessoa,
      ],
    }
  }

  const publicada = getDate(cfg, fileData)
  const atualizada = dataDeAtualizacao(cfg, fileData)
  const tags = Array.isArray(fm.tags) ? fm.tags.map(String) : []

  if (fm.gerado === true && ["post", "resenha", "encontro"].includes(String(fm.tipo))) {
    return {
      "@context": "https://schema.org",
      ...limpar({
        "@type": fm.tipo === "post" ? "BlogPosting" : "Article",
        headline: titulo,
        description: descricao,
        image: imagem,
        datePublished: iso(publicada),
        dateModified: iso(atualizada ?? publicada),
        author: autor,
        publisher: autor,
        mainEntityOfPage: url,
        isPartOf: site,
        inLanguage: "pt-BR",
        keywords: tags,
      }),
    }
  }

  if (ferramentaPropria(fileData)) {
    return {
      "@context": "https://schema.org",
      ...limpar({
        "@type": "SoftwareApplication",
        name: titulo,
        description: descricao,
        url,
        image: imagem,
        applicationCategory: fm.categoria,
        operatingSystem: fm.plataformas,
        isAccessibleForFree: true,
        offers: { "@type": "Offer", price: 0, priceCurrency: "BRL" },
        author: autor,
        datePublished: iso(publicada),
        dateModified: iso(atualizada ?? publicada),
        inLanguage: "pt-BR",
        isPartOf: site,
      }),
    }
  }

  return null
}

/** JSON seguro para dentro de <script>: escapa "<" para que o texto não feche a tag. */
export const serializar = (dados: object) => JSON.stringify(dados).replace(/</g, "\\u003c")
