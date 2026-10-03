import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"
import { classNames } from "../util/lang"

interface Options {
  /** Página de assinatura do Substack (`/subscribe`). Sem ela, o botão leva para /newsletter. */
  substackUrl?: string
}

export default ((opts?: Options) => {
  const Newsletter: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
    const externo = Boolean(opts?.substackUrl)
    const destino = opts?.substackUrl || resolveRelative(fileData.slug!, "newsletter" as FullSlug)
    return (
      <aside class={classNames(displayClass, "newsletter")} aria-labelledby="newsletter-titulo">
        <h2 id="newsletter-titulo">Receba a newsletter</h2>
        <p>Uma seleção dos textos e ideias, enviada periodicamente por e-mail.</p>
        <a
          class="newsletter-botao"
          href={destino}
          target={externo ? "_blank" : undefined}
          rel={externo ? "noopener noreferrer" : undefined}
        >
          Assinar a newsletter
        </a>
        <p class="newsletter-aviso">O cadastro é feito no Substack.</p>
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
.newsletter .newsletter-aviso {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
  color: var(--darkgray);
}
`
  return Newsletter
}) satisfies QuartzComponentConstructor
