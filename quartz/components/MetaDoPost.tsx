import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { Date, getDate } from "./Date"
import Icone from "./Icone"
import { ROTULO_TIPO, minutosDeLeitura } from "./ListaDeCards"

const mesmoDia = (a: globalThis.Date, b: globalThis.Date) =>
  a.getFullYear() === b.getFullYear() &&
  a.getMonth() === b.getMonth() &&
  a.getDate() === b.getDate()

// Linha de metadados do post: publicação, atualização (só se diferente), tempo de leitura e tipo.
export default (() => {
  const MetaDoPost: QuartzComponent = ({ fileData, cfg }: QuartzComponentProps) => {
    const publicada = getDate(cfg, fileData)
    const atualizada = fileData.frontmatter?.modified ? fileData.dates?.modified : undefined
    const minutos = minutosDeLeitura(fileData)
    const tipo = ROTULO_TIPO[String(fileData.frontmatter?.tipo)]
    return (
      <p class="post-meta">
        {publicada && (
          <span>
            <Icone nome="calendario" tamanho={15} /> <Date date={publicada} locale={cfg.locale} />
          </span>
        )}
        {atualizada && (!publicada || !mesmoDia(atualizada, publicada)) && (
          <span>
            Atualizado em <Date date={atualizada} locale={cfg.locale} />
          </span>
        )}
        {minutos > 0 && (
          <span>
            <Icone nome="relogio" tamanho={15} /> {minutos} min de leitura
          </span>
        )}
        {tipo && <span class="post-tipo">{tipo}</span>}
      </p>
    )
  }

  MetaDoPost.css = `
.post-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem 1.1rem;
  margin: 0.25rem 0 1rem;
  color: var(--gray);
  font-family: var(--headerFont);
  font-size: 0.85rem;
}
.post-meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}
.post-tipo {
  font-weight: 600;
}
`
  return MetaDoPost
}) satisfies QuartzComponentConstructor
