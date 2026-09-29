# SPEC: Tema visual inspirado no Chirpy

Complemento da [SPEC.md](./SPEC.md). **Substitui a seção 9 (layout e tema)** e as partes de layout do M4. Status: implementado (marcos T0 a T4). O restante da SPEC (exportador, deploy, domínio, SEO, testes de privacidade) não muda.

Referência de design: [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) (Jekyll, licença MIT). Usamos o desenho de layout e a hierarquia de informação. Não copiamos código nem imagens, e o tema de cores e as fontes continuam os nossos.

## 1. Objetivo

Trocar o layout de coluna única do M4 por um layout de blog técnico com barra lateral fixa, lista de cards, painel lateral direito e navegação entre posts, sem perder:

- o Lighthouse mobile ≥ 95 em Performance, Boas práticas e SEO, e ≥ 95 em Acessibilidade (RNF3);
- os dois temas (claro e escuro) com contraste ≥ 4,5:1 (RNF4);
- a compatibilidade com `npx quartz update` (RNF8): só mexemos nos arquivos da SPEC seção 3, item 4;
- a privacidade: o tema só lê campos que o exportador já entrega (seção 9 deste documento). O exportador não muda.

## 2. Restrições

| Regra | Como se aplica |
|---|---|
| Arquivos permitidos | `quartz.config.ts`, `quartz.layout.ts`, `quartz/styles/custom.scss`, `quartz/components/` (só arquivos novos), `quartz/static/`, `content/`, `tools/` |
| Emissores | Os emissores `FolderPage` e `TagPage` aceitam um `pageBody` próprio, passado em `quartz.config.ts`. Nenhum plugin do Quartz é editado. |
| Sem JavaScript pesado | Tudo que puder ser feito na build é feito na build (componentes renderizados no servidor a partir de `allFiles`). O JS do cliente se limita a gaveta mobile, botão de voltar ao topo e copiar link. |
| Teto de JS | `postscript.js` abaixo de 250 KB (teste automático, já existente) |
| Sem fontes de ícones | Ícones em SVG embutido, sem Font Awesome e sem CDN |
| Sem recursos externos | Continua valendo o M4: fontes locais, nenhuma requisição a terceiros |
| Sem comentários, PWA ou analytics | Fora de escopo (PRD seção 7) |

## 3. Estrutura da página

### 3.1 Pontos de quebra

| Faixa | Layout |
|---|---|
| < 850 px (mobile) | Barra superior com menu, título e busca. A barra lateral vira gaveta. Coluna única. |
| 850 a 1199 px (tablet) | Barra lateral fixa à esquerda + conteúdo. Sem painel direito. |
| ≥ 1200 px (desktop) | Barra lateral + conteúdo + painel direito |

Os pontos de quebra ficam em `custom.scss`. As variáveis do Quartz (800 e 1200 px) não são alteradas.

### 3.2 Grade (desktop)

```
┌────────────┬───────────────────────────────┬──────────────┐
│  Barra     │ Barra superior (breadcrumb    │              │
│  lateral   │ + busca)                      │   Painel     │
│  260 px    ├───────────────────────────────┤   direito    │
│  (fixa)    │ Conteúdo (máx. 60 rem; o      │   280 px     │
│            │ texto ocupa a coluna toda)    │   (sticky)   │
│            ├───────────────────────────────┤              │
│            │ Rodapé                        │              │
└────────────┴───────────────────────────────┴──────────────┘
```

- A barra lateral usa a área `left` do Quartz (hoje oculta). O painel direito usa a área `right`.
- Painel direito colado à direita (margem fixa de 1,5 rem) e coluna central centralizada entre a barra lateral e o painel (folgas iguais dos dois lados). A coluna central chega a 60 rem (960 px) e o texto do artigo ocupa a coluna toda, com corpo em 18 px no desktop (decisão do autor, no lugar dos 65 a 72 caracteres por linha).

## 4. Componentes novos (`quartz/components/`)

Todos são arquivos novos, importados direto em `quartz.layout.ts` (sem editar o `index.ts` do Quartz). CSS embutido no componente, exceto o que for global (vai em `custom.scss`).

| Componente | Onde | Conteúdo e comportamento |
|---|---|---|
| `BarraLateral.tsx` | `left` | Avatar redondo (`quartz/static/avatar.png`), título do site, frase curta, menu com ícones (Início, Artigos, Ideias, Clube, Temas, Tags, Arquivo, Sobre, Newsletter), item da página atual destacado (`aria-current`). No rodapé da barra: ícones das redes (a lista `REDES` do layout) e o botão claro/escuro (`Darkmode` do Quartz). |
| `BarraSuperior.tsx` | `header` | Breadcrumb à esquerda, busca (`Search` do Quartz) à direita. No mobile: botão de menu (abre a gaveta), título do site e ícone de busca. |
| `GavetaMobile` (script dentro de `BarraLateral`) | mobile | Botão com `aria-expanded`, fecha ao navegar (evento `nav`) e com Esc, foco preso enquanto aberta. Fundo escurecido clicável. |
| `ListaDeCards.tsx` | corpo de pastas e tags (`pageBody`) e home | Lista de cards (seção 5.1). |
| `PaginaDeTag.tsx` | `pageBody` do `TagPage` | Em `/tags/`: lista de tags com contagem. Em `/tags/<tag>/`: `ListaDeCards` filtrada. |
| `Arquivo.tsx` | página `/arquivo` | Linha do tempo agrupada por ano e mês (seção 6.5). |
| `PainelDireito.tsx` | `right` (desktop) | Blocos "Atualizados recentemente" e "Tags em alta" (seção 5.2), seguidos do sumário da página (`TableOfContents` do Quartz) fixo ao rolar. |
| `MetaDoPost.tsx` | `beforeBody` | Linha de metadados do post (seção 6.2). |
| `CapaDoPost.tsx` | `beforeBody` | Imagem da capa no topo do post, se a nota tiver `capa`. |
| `Compartilhar.tsx` | `afterBody` | Botões LinkedIn, X e copiar link (seção 6.2). |
| `LeiaTambem.tsx` | `afterBody` | Até 3 posts relacionados (seção 6.2). |
| `AnteriorProximo.tsx` | `afterBody` | Navegação entre posts da mesma seção (seção 6.2). |
| `NotasDoTema.tsx` | páginas de tema | Lista as notas que citam o tema (seção 6.4). |
| `VoltarAoTopo.tsx` | shell | Botão que aparece após rolar 300 px. |
| `Icone.tsx` | uso interno | Conjunto de ícones SVG (menu, casa, livro, lâmpada, mapa, tag, arquivo, usuário, e-mail, busca, calendário, relógio, pasta, redes, RSS, copiar). Sem dependências. |

Componentes do M4 que continuam: `Cabeca` (head/SEO), `Newsletter`, `MencionadoEm`, `Grafo`, `Rodape`. Saem de uso ao fim do T4: `Cabecalho` (substituído pela barra lateral e superior) e `ArtigosRecentes` (substituído pelos cards da home). Os arquivos são removidos junto com o T4.

## 5. Blocos compartilhados

### 5.1 Card

Estrutura de cada card (`<article>` dentro de uma lista):

| Elemento | Origem |
|---|---|
| Miniatura (opcional, 16:9 no topo do card) | `frontmatter.capa`; sem capa, o card não mostra imagem |
| Título (link) | `frontmatter.title` |
| Resumo (até 3 linhas, com reticências) | `frontmatter.description` |
| Rodapé: data, tipo (Artigo, Ideia, Resenha, Encontro, Tema), tempo de leitura | `dates.published`, `frontmatter.tipo`, `text` (velocidade de leitura como no `ContentMeta`) |
| Tags | `frontmatter.tags`, até 3, cada uma linka para `/tags/<tag>` |

- Layout: coluna única, cards empilhados com espaçamento de 1,25 rem. Com capa, a imagem ocupa a altura do card em telas ≥ 850 px (miniatura à esquerda, 240 px) e vai para cima no mobile.
- Ordem: `dates.published` decrescente, depois título.
- Tamanho da página: sem paginação. A home mostra os 10 primeiros e um link "Ver todos" para `/arquivo`. Listas de pasta e de tag mostram todos.

### 5.2 Painel direito

| Bloco | Regra |
|---|---|
| Atualizados recentemente | Até 5 notas exportadas (`gerado: true`) ordenadas por `dates.modified` decrescente. Cada item: título e data. |
| Tags em alta | Até 10 tags mais usadas em notas exportadas, com contagem, ordenadas por contagem e depois por nome. |
| Sumário | Só em páginas exportadas com pelo menos 2 títulos. Fica fixo abaixo dos blocos e destaca a seção visível. |

Os blocos não aparecem quando não há itens.

## 6. Páginas

### 6.1 Início (`/`)

1. Introdução (texto de `content/index.md`, hoje com `TODO:`).
2. "Lendo agora" (transclusão do bloco do clube, como no M4).
3. Cards das 10 publicações mais recentes de tipo artigo (seção 13, decisão 2).
4. Bloco de newsletter.

### 6.2 Post (artigo, ideia, resenha, encontro)

Ordem: breadcrumb (barra superior) → capa → título → metadados → texto → tags → compartilhar → leia também → anterior/próximo → newsletter → "Mencionado em" → grafo (ideias e temas, como no M4).

| Bloco | Regra |
|---|---|
| Metadados | Data de publicação, "Atualizado em" (só se `modified` ≠ `published`), tempo de leitura, tipo. Ícones de calendário e relógio. |
| Compartilhar | Links para LinkedIn e X com o endereço canônico da página, e "Copiar link" (único uso de JS aqui, com `aria-live` para confirmar). |
| Leia também | Até 3 notas exportadas do mesmo tipo de conteúdo (artigo, ideia), pontuadas por tags e temas em comum; empate desempata por data. Sem candidatas com ao menos 1 item em comum, mostra as 3 mais recentes. Nunca inclui a própria página. |
| Anterior e próximo | Dentro da mesma seção (`artigos/`, `ideias/`...), pela ordem de `dates.published`. Só aparece quando existe pelo menos um vizinho. |

### 6.3 Listas de pasta (`/artigos/`, `/ideias/`, `/clube/`, `/temas/`)

- Texto de introdução do `index.md` da pasta, seguido de `ListaDeCards` com todas as notas exportadas da pasta (o `pageBody` customizado substitui a lista padrão do Quartz).
- `/clube/`: o bloco "Lendo agora" fica antes dos cards. Os encontros (`clube/encontros/`) aparecem na mesma lista, com o tipo "Encontro".
- `/temas/`: mantém o grafo global do M4 acima dos cards.

### 6.4 Página de tema (`/temas/<slug>`)

Texto do mapa + `NotasDoTema`: cards das notas cujo campo `temas` cita o título do tema (mesma regra de "temas publicados" do exportador).

### 6.5 Arquivo (`/arquivo`)

Página fixa `content/arquivo.md` (`publish: true`, texto curto com `TODO:`). O componente `Arquivo` lista todas as notas exportadas de artigos, ideias, resenhas e encontros, agrupadas por ano e mês (mais recente primeiro): dia, título (link) e tipo. Substitui a "categorias" e o "arquivo" do Chirpy.

### 6.6 Tags (`/tags/`, `/tags/<tag>/`)

Índice com a lista de tags e contagem. Página de tag com os cards. Sem página de categorias: os temas fazem esse papel.

### 6.7 Sobre, Newsletter e 404

Sem cards e sem painel direito na Sobre e na Newsletter. A Sobre mostra a foto (`quartz/static/foto.jpg`, ainda espaço reservado). A 404 mantém a mensagem em português e o menu da barra lateral.

## 7. Tema visual

Os tokens de cor do M4 continuam. A identidade visual própria segue pendente (PRD seção 10); os tokens abaixo só acrescentam superfícies.

| Novo token | Claro | Escuro | Uso |
|---|---|---|---|
| `--barra` | `#f3f1ec` | `#1b1b20` | Fundo da barra lateral |
| `--superficie` | `#ffffff` | `#1e1e24` | Fundo dos cards e dos blocos do painel |
| `--borda` | `#e6e3dc` | `#2a2a31` | Bordas de card (igual ao `lightgray`) |
| `--sombra` | `0 1px 3px rgba(0,0,0,.08)` | `0 1px 3px rgba(0,0,0,.4)` | Elevação do card e realce ao passar o mouse |

- Fontes: Inter na interface (barra lateral, cards, metadados, painel) e Source Serif 4 no texto dos posts, como no M4. Nenhuma fonte nova.
- Card com raio de 10 px. Ao passar o mouse: sombra maior e título na cor `--tertiary`.
- Contraste mínimo de 4,5:1 nos dois temas, inclusive `gray` sobre `--superficie` e `--barra` (verificar; ajustar os tokens se necessário).
- `prefers-reduced-motion`: sem transições.

## 8. Acessibilidade e desempenho

- Landmarks: barra lateral em `<aside aria-label="Barra lateral">` com `<nav aria-label="Principal">`; painel direito com `aria-label="Painel lateral"`. O Quartz não gera `<main>`; a nota de acessibilidade 98 do M4 continua aceita.
- Link "Pular para o conteúdo" como primeiro item focável, com destino `#conteudo`, âncora inserida antes do título.
- Navegação por teclado completa (gaveta, busca, cards, botões de compartilhar). Foco sempre visível.
- Cards inteiros clicáveis pelo título (sem `<a>` aninhado); a imagem tem `alt=""` (decorativa) e `loading="lazy"`, com `width`/`height` para não gerar CLS.
- Meta de desempenho: Lighthouse mobile ≥ 95 nas quatro categorias em `/`, um artigo, uma ideia, `/artigos/`, `/arquivo` e `/tags/`. CLS < 0,05.
- O `postscript.js` continua abaixo de 250 KB.

## 9. Dados usados (nada novo no exportador)

Só campos que a lista de permissão (SPEC 6.3) já exporta:

| Uso no tema | Campo |
|---|---|
| Título, resumo | `title`, `description` |
| Datas | `date`/`published`, `modified` |
| Tags e tags em alta | `tags` |
| Tipo (Artigo, Ideia...) | `tipo` |
| Temas e "Notas do tema" | `temas` |
| Capa dos cards e do post | `capa` |
| Filtro de "só notas exportadas" | `gerado: true` |
| Autor e nota do livro (resenha) | `autor_livro`, `nota` (opcional no card de resenha) |

Páginas fixas (Início, Sobre, Newsletter, índices) não têm `gerado` e nunca entram em cards, "atualizados recentemente", tags em alta nem arquivo.

## 10. Testes

Estendem `tools/tests/test_build_quartz.py` e usam o vault de exemplo (acrescentar ao vault de exemplo um segundo artigo com tags em comum e uma ideia sem capa, para cobrir relacionados e anterior/próximo):

- Barra lateral presente em todas as páginas, com os 9 itens de menu e o item da página atual marcado.
- Home: até 10 cards, ordenados por data; card com capa mostra imagem, sem capa não mostra.
- Listas de pasta e de tag usam cards (não a lista padrão do Quartz); `/tags/` mostra contagens.
- Painel direito: "Atualizados recentemente" ordenado por `modified`, "Tags em alta" ordenada por contagem; páginas fixas não aparecem.
- Post: metadados (inclui "Atualizado em" só quando difere), compartilhar com URL canônica, "Leia também" sem a própria página, anterior/próximo dentro da seção.
- `/arquivo`: agrupamento por ano e mês, mais recente primeiro.
- Página de tema lista as notas que a citam.
- Vazamento (`SEGREDO-`) continua sem ocorrências em `content/` e `public/`; a nota bloqueada não aparece em nenhum card, painel, arquivo, tag ou "leia também".
- Teto de 250 KB para o `postscript.js`.
- Manual (por marco): Lighthouse mobile nas páginas da seção 8, contraste nos dois temas (verificador no navegador) e revisão visual em 390, 820 e 1440 px.

## 11. Marcos

Um marco por vez; ao final de cada um, parar para revisão (regra do `CLAUDE.md`).

| Marco | Entrega | Aceite |
|---|---|---|
| **T0** | Commit de base dos marcos M1 a M4 e criação da branch `tema-chirpy` (com a sua autorização; o repositório ainda não tem commits) | Branch criada; layout atual preservado na `main` para comparação |
| **T1** | Estrutura: `BarraLateral`, `BarraSuperior`, gaveta mobile, grade e pontos de quebra, tokens novos, `Icone`, `VoltarAoTopo`, link de pular conteúdo | Três faixas de largura corretas; menu, busca e tema funcionam; Lighthouse ≥ 95 em `/` e num artigo |
| **T2** | Cards e listas: `ListaDeCards`, `pageBody` de pastas e tags, `PaginaDeTag`, home com cards, `Arquivo` e `content/arquivo.md` | Home, pastas, tags e arquivo renderizam com cards; testes de vazamento e ordenação passam |
| **T3** | Painel direito e post: `PainelDireito`, `MetaDoPost`, `CapaDoPost`, `Compartilhar`, `LeiaTambem`, `AnteriorProximo`, `NotasDoTema` | Post completo conforme a seção 6.2; painel só em ≥ 1200 px; testes correspondentes |
| **T4** | Acabamento: contraste nos dois temas, acessibilidade, revisão de desempenho em todas as páginas, remoção de `Cabecalho` e `ArtigosRecentes`, atualização da SPEC seção 9 e do M4 apontando para este documento | Critérios da seção 12 |

## 12. Critérios de pronto

- `pytest` (inclui o build do Quartz) e `tsc` passam.
- Lighthouse mobile ≥ 95 nas quatro categorias nas páginas da seção 8.
- Contraste ≥ 4,5:1 nos dois temas.
- Nenhum arquivo do núcleo do Quartz alterado (`git diff` contra a tag `v4.5.2` só toca os arquivos da seção 2).
- Zero ocorrências no teste de vazamento e na auditoria do exportador.
- Revisão visual aprovada por mim em 390, 820 e 1440 px.

## 13. Decisões pendentes

| # | Decisão | Padrão, se não houver resposta |
|---|---|---|
| 1 | Avatar e frase curta da barra lateral | Monograma "TL" (o ícone atual) e frase com `TODO:` |
| 2 | O que a home lista nos cards | Só artigos (10 mais recentes); ideias e resenhas aparecem no arquivo e nas próprias seções |
| 3 | Miniatura nos cards sem `capa` | Sem imagem (card só de texto) |
| 4 | Tema padrão na primeira visita | Segue o sistema (`prefers-color-scheme`), com alternância manual |
| 5 | Tags em alta e "Atualizados recentemente" também nas páginas fixas | Não (só em páginas de conteúdo e listas) |
| 6 | "Voltar ao topo" | Incluir |
| 7 | Redes no rodapé da barra lateral | As mesmas do `REDES` do layout; endereços ainda a confirmar (pendência do M4) |

## 14. Riscos

| Risco | Mitigação |
|---|---|
| A barra lateral e o painel elevam o peso e o CLS | Renderização na build, imagens com dimensões fixas, teto de JS e medição de Lighthouse em todo marco |
| Divergência do Quartz numa atualização (`npx quartz update`) | Só arquivos novos e os da lista permitida; `pageBody` passa pela configuração, não por edição do núcleo |
| Poucos posts no início deixam a home vazia | Estado vazio com mensagem e a introdução em destaque; o bloco "Lendo agora" continua |
| Diferença entre `dates.modified` do frontmatter e do Git | `modified` vem do exportador (`atualizado`); prioridade `frontmatter` já configurada |
| `text` ausente em algum item de `allFiles` (tempo de leitura) | Verificar no T1; sem `text`, o card omite o tempo de leitura |
