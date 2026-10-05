import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { Root } from "hast"
import { ComponentChildren } from "preact"
import { htmlToJsx } from "../util/jsx"
import { Cartoes, exportada, maisRecentesPrimeiro } from "./ListaDeCards"

// Corpo das páginas de pasta (/posts/, /radar/, /leituras/...): o texto do index.md
// seguido de cards com as notas exportadas da pasta. Substitui o FolderContent do Quartz.
export default (() => {
  const PaginaDePasta: QuartzComponent = ({
    tree,
    fileData,
    allFiles,
    cfg,
  }: QuartzComponentProps) => {
    const pasta = fileData.slug!.replace(/\/?index$/, "")
    // Ferramentas são escritas no repositório (sem `gerado`), então entram na lista pela pasta
    const escritaNoRepositorio = pasta === "ferramentas"
    const paginas = allFiles
      .filter(
        (f) =>
          f.slug!.startsWith(`${pasta}/`) &&
          (exportada(f) || (escritaNoRepositorio && f.slug !== "ferramentas/index")),
      )
      .sort(maisRecentesPrimeiro(cfg))
    const semTexto = (tree as Root).children.length === 0
    const conteudo = (
      semTexto ? fileData.description : htmlToJsx(fileData.filePath!, tree)
    ) as ComponentChildren
    const classes = ((fileData.frontmatter?.cssclasses as string[]) ?? []).join(" ")
    return (
      <div class="popover-hint">
        <article class={classes}>{conteudo}</article>
        {semTexto && <h2 class="cards-titulo">Publicações</h2>}
        <div class="page-listing">
          {paginas.length === 0 ? (
            <p class="cards-vazio">Nada publicado aqui ainda.</p>
          ) : (
            <Cartoes paginas={paginas} fileData={fileData} cfg={cfg} />
          )}
        </div>
      </div>
    )
  }

  return PaginaDePasta
}) satisfies QuartzComponentConstructor
