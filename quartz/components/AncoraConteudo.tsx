import { QuartzComponent, QuartzComponentConstructor } from "./types"

// Destino do link "Pular para o conteúdo" (fica logo antes do título da página).
export default (() => {
  const AncoraConteudo: QuartzComponent = () => <span id="conteudo" tabIndex={-1}></span>
  return AncoraConteudo
}) satisfies QuartzComponentConstructor
