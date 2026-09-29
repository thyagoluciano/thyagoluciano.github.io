import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { Cartoes, exportada, maisRecentesPrimeiro } from "./ListaDeCards"

// Em páginas de tema: cards das notas exportadas cujo campo `temas` cita este tema.
export default (() => {
  const NotasDoTema: QuartzComponent = ({ allFiles, fileData, cfg }: QuartzComponentProps) => {
    const titulo = String(fileData.frontmatter?.title ?? "")
    const notas = allFiles
      .filter(
        (f) =>
          exportada(f) &&
          f.slug !== fileData.slug &&
          ((f.frontmatter?.temas ?? []) as string[]).includes(titulo),
      )
      .sort(maisRecentesPrimeiro(cfg))
    if (notas.length === 0) return null
    return (
      <section class="notas-do-tema">
        <h2 class="cards-titulo">Notas neste tema</h2>
        <Cartoes paginas={notas} fileData={fileData} cfg={cfg} />
      </section>
    )
  }
  return NotasDoTema
}) satisfies QuartzComponentConstructor
