import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"
import { classNames } from "../util/lang"

interface Options {
  /** Página de assinatura do Substack. Sem ela, o botão leva para /newsletter. */
  substackUrl?: string
}

export default ((opts?: Options) => {
  const Newsletter: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
    const destino = opts?.substackUrl || resolveRelative(fileData.slug!, "newsletter" as FullSlug)
    return (
      <aside class={classNames(displayClass, "newsletter")} aria-labelledby="newsletter-titulo">
        <h2 id="newsletter-titulo">Receba os novos textos</h2>
        <p>Um e-mail quando eu publicar algo novo, com o texto completo.</p>
        <a class="newsletter-botao" href={destino}>
          Assinar a newsletter
        </a>
      </aside>
    )
  }

  Newsletter.css = `
.newsletter {
  margin: 2.5rem 0 1.5rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--lightgray);
  border-radius: 8px;
  background: var(--highlight);
}
.newsletter h2 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
}
.newsletter p {
  margin: 0 0 1rem;
}
.newsletter .newsletter-botao {
  display: inline-block;
  padding: 0.5rem 1.1rem;
  border-radius: 6px;
  background: var(--secondary);
  color: var(--light);
  font-family: var(--headerFont);
  font-weight: 600;
  text-decoration: none;
}
.newsletter .newsletter-botao:hover {
  background: var(--tertiary);
  color: var(--light);
}
`
  return Newsletter
}) satisfies QuartzComponentConstructor
