import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

// A home não mostra título (as vitrines abrem a página), mas precisa de um <h1> para leitores de tela
// e buscadores. O texto vem do campo `h1` do frontmatter; sem ele, o nome do site.
export default (() => {
  const TituloDaHome: QuartzComponent = ({ fileData, cfg }: QuartzComponentProps) => {
    const texto = String(fileData.frontmatter?.h1 ?? cfg.pageTitle)
    return <h1 class="titulo-home">{texto}</h1>
  }

  TituloDaHome.css = `
.titulo-home {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
`
  return TituloDaHome
}) satisfies QuartzComponentConstructor
