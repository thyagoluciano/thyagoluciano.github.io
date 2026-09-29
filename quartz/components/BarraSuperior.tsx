import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { pathToRoot } from "../util/path"
import { i18n } from "../i18n"
import Icone from "./Icone"

// Parte da barra superior que só existe no mobile: botão do menu e título do site.
// O breadcrumb e a busca são componentes do Quartz, dispostos ao lado dela no `header`.
export default (() => {
  const BarraSuperior: QuartzComponent = ({ fileData, cfg }: QuartzComponentProps) => {
    const titulo = cfg.pageTitle ?? i18n(cfg.locale).propertyDefaults.title
    return (
      <>
        <button
          type="button"
          class="menu-botao"
          aria-controls="barra-lateral"
          aria-expanded="false"
          aria-label="Abrir menu"
        >
          <Icone nome="menu" tamanho={22} />
        </button>
        <a class="topo-titulo" href={pathToRoot(fileData.slug!)}>
          {titulo}
        </a>
      </>
    )
  }

  BarraSuperior.css = `
.menu-botao {
  display: none;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--darkgray);
  cursor: pointer;
}
.topo-titulo {
  display: none;
  font-family: var(--titleFont);
  font-weight: 700;
  color: var(--dark);
  text-decoration: none;
}
@media (max-width: 849px) {
  .menu-botao {
    display: flex;
  }
  .topo-titulo {
    display: block;
  }
}
`
  return BarraSuperior
}) satisfies QuartzComponentConstructor
