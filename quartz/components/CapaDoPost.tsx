import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"

// Capa da nota no topo do post (decorativa: o título já descreve o conteúdo).
export default (() => {
  const CapaDoPost: QuartzComponent = ({ fileData }: QuartzComponentProps) => {
    const capa = fileData.frontmatter?.capa
    if (typeof capa !== "string" || !capa) return null
    return (
      <figure class="capa-post">
        <img
          src={resolveRelative(fileData.slug!, capa as FullSlug)}
          width="1200"
          height="675"
          alt=""
          decoding="async"
        />
      </figure>
    )
  }

  CapaDoPost.css = `
.capa-post {
  margin: 0 0 1.5rem;
}
.capa-post img {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  margin: 0;
  border-radius: 10px;
}
`
  return CapaDoPost
}) satisfies QuartzComponentConstructor
