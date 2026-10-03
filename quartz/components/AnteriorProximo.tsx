import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { resolveRelative } from "../util/path"
import { getDate } from "./Date"
import { exportada, maisRecentesPrimeiro } from "./ListaDeCards"

// Anterior (mais antiga) e próximo (mais recente) dentro da mesma seção (posts, radar, leituras).
export default (() => {
  const AnteriorProximo: QuartzComponent = ({ allFiles, fileData, cfg }: QuartzComponentProps) => {
    const secao = fileData.slug!.split("/")[0]
    const ordem = allFiles
      .filter(
        (f) =>
          exportada(f) &&
          getDate(cfg, f) &&
          f.slug!.split("/")[0] === secao &&
          f.slug !== `${secao}/index`,
      )
      .sort((a, b) => maisRecentesPrimeiro(cfg)(b, a)) // do mais antigo ao mais novo
    const i = ordem.findIndex((f) => f.slug === fileData.slug)
    if (i < 0) return null
    const anterior = ordem[i - 1]
    const proximo = ordem[i + 1]
    if (!anterior && !proximo) return null
    const bloco = (f: typeof anterior, classe: string, rotulo: string, seta: string) => (
      <a class={`internal ${classe}`} href={resolveRelative(fileData.slug!, f.slug!)}>
        <span class="ap-rotulo">
          {classe === "ap-anterior" ? `${seta} ${rotulo}` : `${rotulo} ${seta}`}
        </span>
        <span class="ap-titulo">{f.frontmatter?.title}</span>
      </a>
    )
    return (
      <nav class="anterior-proximo" aria-label="Navegação entre publicações">
        {anterior ? bloco(anterior, "ap-anterior", "Anterior", "←") : <span></span>}
        {proximo ? bloco(proximo, "ap-proximo", "Próximo", "→") : <span></span>}
      </nav>
    )
  }

  AnteriorProximo.css = `
.anterior-proximo {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 1.5rem 0;
}
.anterior-proximo a.internal {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.8rem 1rem;
  border: 1px solid var(--lightgray);
  border-radius: 10px;
  background: var(--superficie);
  text-decoration: none;
  background: var(--superficie);
}
.anterior-proximo a:hover .ap-titulo {
  color: var(--tertiary);
}
.anterior-proximo .ap-proximo {
  text-align: right;
}
.ap-rotulo {
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.8rem;
}
.ap-titulo {
  color: var(--dark);
  font-family: var(--headerFont);
  font-weight: 600;
  line-height: 1.3;
}
@media (max-width: 549px) {
  .anterior-proximo {
    grid-template-columns: 1fr;
  }
}
`
  return AnteriorProximo
}) satisfies QuartzComponentConstructor
