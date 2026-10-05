# SPEC: Site pessoal thyagoluciano.com.br

Especificação técnica do [PRD.md](./PRD.md). Implementar na ordem dos marcos (seção 13).

## 1. Arquitetura

```
Vault (iCloud, privado)                Repositório do site (GitHub, público)          Internet
SecondBrain/                           thyagoluciano.com.br/
  notas com publicar: true  ──exportar──▶  content/ (gerado + páginas fixas)
                                           quartz.config.ts, quartz.layout.ts
                                           └── git push ──▶ GitHub Actions ──▶ GitHub Pages ──▶ thyagoluciano.com.br
```

- **Gerador:** Quartz v4 (feito para vaults do Obsidian: wikilinks, backlinks, grafo, busca).
- **Exportador:** script Python no repositório do site (`tools/exportar.py`). Lê o vault, escreve em `content/`. Não depende do `second-brain-tools`.
- **Hospedagem:** GitHub Pages via GitHub Actions. Domínio no Registro.br.

## 2. Caminhos

| Item | Mac |
|---|---|
| Vault | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain` |
| Repositório do site | `~/Claude/Projects/Thyago Luciano/thyagoluciano.com.br` (esta pasta) |
| Repositório no GitHub | `github.com/thyagoluciano/thyagoluciano.com.br` (público) |

- As especificações ficam em `specs/`, porque o Quartz já usa a pasta `docs/` para a documentação dele.
- O caminho do vault vem da variável `SB_VAULT` ou de `tools/config.toml` (fora do Git, com `tools/config.example.toml` versionado).

## 3. Instalação do Quartz

1. Node.js na versão exigida pelo `package.json` do Quartz (Node 22 LTS ou superior).
2. Nesta pasta (que já contém `specs/` e `CLAUDE.md`): clonar o Quartz v4 preservando os arquivos existentes, `npm ci`, e `npx quartz create` escolhendo conteúdo vazio e resolução de links **absoluta**.
3. Remotes: `origin` = repositório do site; `upstream` = `jackyzha0/quartz`. Atualizações com `npx quartz update`.
4. Personalizações ficam **somente** em: `quartz.config.ts`, `quartz.layout.ts`, `quartz/styles/custom.scss`, `quartz/components/` (componentes novos, sem editar os originais quando possível), `quartz/static/`, `content/` e `tools/`.

## 4. Configuração do Quartz (`quartz.config.ts`)

```ts
configuration: {
  pageTitle: "Thyago Luciano",
  pageTitleSuffix: " · Thyago Luciano",
  enableSPA: true,
  enablePopovers: false,                // sem prévia ao passar o mouse (decisão do autor)
  analytics: null,                     // decisão pendente (PRD §10)
  locale: "pt-BR",
  baseUrl: "thyagoluciano.com.br",
  ignorePatterns: ["private", "templates", ".obsidian"],
  defaultDateType: "published",
  theme: { /* seção 9 */ },
},
plugins: {
  transformers: [
    Plugin.FrontMatter(),
    Plugin.CreatedModifiedDate({ priority: ["frontmatter", "git", "filesystem"] }),
    Plugin.SyntaxHighlighting(),
    Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
    Plugin.GitHubFlavoredMarkdown(),
    Plugin.TableOfContents(),
    Plugin.CrawlLinks({ markdownLinkResolution: "absolute" }),
    Plugin.Description(),
  ],
  filters: [Plugin.ExplicitPublish()],   // 2ª barreira: só páginas com publish: true
  emitters: [
    Plugin.AliasRedirects(),
    Plugin.ComponentResources(),
    Plugin.ContentPage(),
    Plugin.FolderPage(),
    Plugin.TagPage(),
    Plugin.ContentIndex({ enableSiteMap: true, enableRSS: true, rssLimit: 20 }),
    Plugin.Assets(),
    Plugin.Static(),
    Plugin.NotFoundPage(),
    Plugin.CNAME(),
    // CustomOgImages não é usado: gera WebP, que o LinkedIn não exibe (seção 10)
  ],
}
```

- Os nomes exatos de plugins e opções devem ser conferidos na versão instalada do Quartz. Em caso de divergência, vale a intenção desta seção.
- `ExplicitPublish` exige `publish: true` em **toda** página, inclusive as fixas (`index.md`, `sobre.md` etc.).

## 5. Estrutura de `content/`

```
content/
├── index.md              # fixo (escrito no repositório)
├── sobre.md              # fixo
├── newsletter.md         # fixo
├── posts/                # GERADO
│   └── index.md          # fixo: introdução da seção
├── radar/                # GERADO (projetos e ferramentas de outras pessoas)
│   └── index.md          # fixo
├── ferramentas/          # ESCRITO NO REPOSITÓRIO (ferramentas minhas, não vêm do vault)
│   ├── index.md          # fixo: introdução da seção
│   └── <ferramenta>.md   # página de apresentação; o HTML fica em quartz/static/ferramentas/<ferramenta>/index.html
├── leituras/             # GERADO (resenhas e encontros)
│   └── index.md          # fixo + bloco "lendo agora" gerado (seção 6.8)
└── assets/               # GERADO (imagens usadas)
```

- `ferramentas/` não é gerada: o exportador não a toca. Cada ferramenta é um HTML único, sem backend e sem CDN (fontes de `quartz/static/fonts/`), servido em `/static/ferramentas/<ferramenta>/` com `noindex`; a página de apresentação em `content/ferramentas/` é a que fica indexada. As páginas de ferramentas entram na página Tags e no Arquivo (rótulo "Ferramenta") por `publicada` em `ListaDeCards.tsx`; painéis, vitrines da home e "Leia também" continuam só com notas exportadas.
- O exportador **só escreve** em `posts/`, `radar/`, `leituras/` e `assets/`, e nunca apaga ou sobrescreve arquivos `index.md` dessas pastas.
- Arquivos gerados levam no frontmatter `gerado: true`. O exportador só remove arquivos com essa marca.

## 6. Exportador (`tools/exportar.py`)

Python 3.12, dependências: `PyYAML`. Rodar com `uv run tools/exportar.py` (script com metadados PEP 723).

```
exportar.py [--vault PATH] [--simular] [--estrito] [--json]
```

### 6.1 Seleção
Nota elegível se **todas** forem verdadeiras:
- `publicar: true` (booleano YAML).
- Não está em `00-Inbox/`, `90-Templates/`, `_sistema/`, `.obsidian/`, `.smart-env/`.
- `subtipo` não é `destaques`.
- Tem `slug` (minúsculas, `a-z0-9-`, único entre as elegíveis) e `descricao` (até 160 caracteres).
- Se `tipo: conteudo`: `canal: site` e `status` em `publicado` ou `agendado`; se `agendado`, `data_publicacao` ≤ hoje.

Nota com `publicar: true` que falhe em qualquer regra: **erro** listado; com `--estrito` (padrão no comando `publicar`), aborta a exportação inteira.

### 6.2 Destino
| Nota no vault | Destino |
|---|---|
| `tipo: conteudo`, `canal: site` | `content/posts/<slug>.md` |
| `tipo: ferramenta` | `content/radar/<slug>.md` |
| `tipo: fonte`, `subtipo: livro` | `content/leituras/<slug>.md` (resenha) |
| `tipo: encontro` | `content/leituras/encontros/<slug>.md` |
| `tipo: ideia`, `tipo: mapa` | Ficam só no Obsidian: nunca exportados (erro se `publicar: true`) |
| Outros tipos | Não exportados (erro se `publicar: true`) |

Links de notas publicadas para ideias e mapas viram texto simples (regra da seção 6.4).

### 6.3 Frontmatter de saída (lista de permissão)
Somente estes campos saem; todo o resto é descartado.

| Saída | Origem |
|---|---|
| `title` | `titulo` (sem prefixos como `Site - `, `Livro - `, `Mapa - `) |
| `description` | `descricao` |
| `date` / `published` | `data_publicacao` (senão `criado`) |
| `modified` | `atualizado` |
| `tags` | `tags` |
| `aliases` | slugs anteriores (manifesto, seção 6.7) |
| `publish` | `true` (sempre) |
| `gerado` | `true` (sempre) |
| `tipo` | `post`, `ferramenta`, `resenha` ou `encontro` |
| `capa` | caminho da imagem copiada, se `capa` existir |
| `autor_livro`, `nota` | só para resenhas: nome do autor (texto) e nota 1–5 |
| `url`, `autor_projeto`, `categoria`, `estado`, `por_que` | só para `tipo: ferramenta` (obrigatórios) |
| `repositorio`, `licenca` | só para `tipo: ferramenta` (opcionais) |

**Radar (`tipo: ferramenta`).** Além das regras gerais, o exportador reporta erro se faltar `url`, `autor_projeto`, `categoria`, `estado` ou `por_que`, se `estado` não for `quero-testar`, `testando`, `uso` ou `descartei`, ou se `url` ou `repositorio` não começarem com `http://` ou `https://`. O slug `encontros` é reservado em `leituras/`.

### 6.4 Corpo
Na ordem:
1. Remover `%% ... %%` (inclusive multilinha) e `<!-- ... -->`.
2. Remover linhas de marcador vazio (`-`, `1.`, `>`) e cabeçalhos cuja seção ficou vazia.
3. Remover o primeiro `# Título` se for igual ao `title` (o Quartz já exibe o título).
4. **Wikilinks** `[[alvo#secao|apelido]]`:
   - alvo elegível → `[[<pasta-destino>/<slug>#secao|texto]]`, em que `texto` = apelido, ou o título sem prefixo;
   - alvo não elegível ou inexistente → `texto` simples, sem link.
5. **Embeds** `![[arquivo]]`:
   - imagem (`png`, `jpg`, `jpeg`, `gif`, `webp`, `svg`) → copiar para `content/assets/<hash8>-<nome>` e reescrever o embed;
   - nota → remover o embed (não transcluir conteúdo de notas no site na v1).
6. Links Markdown externos (`[texto](https://…)`) ficam como estão.

### 6.5 Leitura do vault (iCloud)
- Mesma regra do `second-brain-tools`: detectar arquivo não baixado (`SF_DATALESS` ou `EDEADLK`), rodar `brctl download` e tentar de novo 3 vezes; persistindo, **abortar** com a lista de arquivos (não publicar parcialmente).

### 6.6 Auditoria de privacidade (sempre roda, falha o comando)
Depois de gerar, varrer os arquivos gerados:
- nenhum arquivo gerado veio de nota não elegível (conferir contra a lista de seleção);
- nenhum `[[` sobra apontando para página inexistente no `content/`;
- nenhum campo fora da lista de permissão no frontmatter;
- nenhum texto com `%%`, `<!--` ou `Destaques - `;
- nenhuma imagem em `content/assets/` sem referência.

### 6.7 Manifesto e URLs estáveis
`tools/manifesto.json` (versionado): `{ "<caminho no vault>": { "slug": "...", "slugs_anteriores": [...], "destino": "...", "sha256": "..." } }`.
- Se o slug de uma nota mudou, o anterior vai para `slugs_anteriores` e vira `aliases` (redirecionamento pelo `AliasRedirects`).
- Nota que deixou de ser elegível: arquivo removido do `content/`, entrada marcada como `removida` com data.
- Renomear ou mover a nota no vault não altera a URL: a identidade é o `slug`. Se a nota não for encontrada pelo caminho, buscar pelo `slug` antes de tratar como removida.

### 6.8 Dados gerados para páginas fixas
- `content/leituras/index.md` recebe um bloco entre os marcadores `<!-- gerado:lendo-agora -->` e `<!-- /gerado:lendo-agora -->` com o livro com `status_leitura: lendo` e `publicar: true` (título, autor, link se houver resenha). Único caso em que o exportador edita arquivo fixo, e só entre os marcadores.

### 6.9 Saída
- Resumo: `novas / alteradas / removidas / erros`, com a URL final de cada nota publicada (`https://thyagoluciano.com.br/<destino>/<slug>`), para eu preencher o campo `url` no vault.
- `--simular`: mostra o mesmo resumo sem escrever nada.
- `--json`: mesmo conteúdo em JSON.

## 7. Comando de publicação

`npm run publicar` (script em `package.json`) → `tools/publicar.sh`:

1. `uv run tools/exportar.py --estrito`
2. `npx quartz build` (falha em erro)
3. `git add content tools/manifesto.json`
4. Commit `Publica: <títulos novos ou alterados>` (se houver mudanças)
5. `git push origin main`

Também:
- `npm run previa` → exportar + `npx quartz build --serve` (http://localhost:8080).
- `npm run simular` → `exportar.py --simular`.

### 7.1 Envio da newsletter (manual)

O Substack guarda a lista de assinantes e faz o envio. Não há integração automática: o site só leva o leitor ao cadastro.

1. Publicar os textos no site (`npm run publicar`).
2. Periodicamente, montar a edição no editor do Substack, com uma seleção dos textos e ideias, e enviar.
3. Exportar a lista de assinantes (CSV) do Substack de tempos em tempos, como cópia de segurança.

## 8. Deploy

- `.github/workflows/deploy.yml`: em `push` na `main`, `actions/checkout` com `fetch-depth: 0` (datas do Git), `actions/setup-node` (versão do Quartz), `npm ci`, `npx quartz build`, `actions/upload-pages-artifact` (pasta `public`), `actions/deploy-pages`. Permissões: `pages: write`, `id-token: write`.
- Settings → Pages → Source: **GitHub Actions**.
- **Domínio** (Registro.br, DNS em modo avançado):

| Tipo | Nome | Valor |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153 |
| CNAME | www | thyagoluciano.github.io |

- Settings → Pages → Custom domain: `thyagoluciano.com.br`; ativar **Enforce HTTPS** depois do certificado emitido.
- Verificar o domínio na conta do GitHub (registro TXT), para evitar que outra conta o reivindique.
- Conferir os IPs na documentação atual do GitHub Pages antes de configurar.

## 9. Layout e tema visual

> **Substituída.** O layout e o tema foram reimplementados a partir do Chirpy e estão em [SPEC-TEMA-CHIRPY.md](./SPEC-TEMA-CHIRPY.md) (marcos T0 a T4, concluídos). Vale o que está lá para layout, componentes, tema e acessibilidade. O texto desta seção fica só como histórico do M4.

### 9.1 Layout (`quartz.layout.ts`)
| Área | Componentes |
|---|---|
| Cabeçalho | Título do site, navegação (Posts, Radar, Leituras, Tags, Arquivo, Sobre, Newsletter), busca, alternância claro/escuro |
| Antes do conteúdo | Breadcrumbs (exceto na home), título, data e tempo de leitura, tags |
| Depois do conteúdo | Tags, compartilhar, "leia também" e anterior/próximo (sem grafo, sem bloco de newsletter e sem backlinks: o grafo, o bloco "Receba a newsletter" e a seção "Mencionado em" foram removidos) |
| Lateral (desktop) | Sumário da página |
| Home | Componente de posts recentes e bloco "lendo agora" |
| Rodapé | Links: LinkedIn, X, Threads, Instagram, Substack, RSS, GitHub |

- Remover o explorador de arquivos (a navegação é pelo menu).
- Sem grafo de conexões: o componente `Grafo.tsx` fica no repositório, sem uso, e pode voltar quando houver volume de posts.

### 9.2 Tema (padrão até haver identidade visual)
| Token | Claro | Escuro |
|---|---|---|
| light (fundo) | `#fbfaf7` | `#16161a` |
| lightgray | `#e6e3dc` | `#2a2a31` |
| gray | `#8a8780` | `#6f6e78` |
| darkgray (texto) | `#34332f` | `#d8d6d0` |
| dark (títulos) | `#1c1b18` | `#f1efe9` |
| secondary (links) | `#2f5d8a` | `#8cb4dc` |
| tertiary (hover) | `#b0643a` | `#e0a07a` |
| highlight | `rgba(47,93,138,0.10)` | `rgba(140,180,220,0.12)` |

- Fontes: títulos `Inter`, corpo `Source Serif 4`, código `JetBrains Mono` (Google Fonts, como o Quartz já suporta).
- Largura de leitura de 65–72 caracteres; corpo com 18px no desktop.
- Contraste mínimo de 4,5:1 nos dois temas (verificar).

### 9.3 Componentes novos (`quartz/components/`)
- `Newsletter.tsx`: bloco "Receba a newsletter" com botão para `https://thyagoluciano.substack.com/subscribe` e o aviso "O cadastro é feito no Substack." **Fora de uso**: o bloco não é mais renderizado em nenhuma página. O acesso à newsletter fica no menu (página `/newsletter`) e no ícone do Substack da barra lateral (`SUBSTACK_URL` em `quartz.layout.ts`). Sem formulário próprio nem embed.
- Links externos abrem em nova aba: `RedesSociais.tsx` e `Rodape.tsx` usam `target="_blank"` com `rel` `noopener noreferrer`; nos textos, `Plugin.CrawlLinks` com `openLinksInNewTab: true`. O RSS e os links internos abrem na mesma aba.
- `LendoAgora.tsx` (opcional): se o bloco da seção 6.8 for insuficiente.

## 10. SEO e compartilhamento

- `<html lang="pt-BR">`, `description` em todas as páginas (do campo `descricao`).
- Open Graph e Twitter Card: título, descrição, URL canônica, imagem (capa da nota; sem capa, a imagem padrão `quartz/static/og-padrao.png`, 1200×630, em PNG; o `CustomOgImages` foi descartado porque gera WebP, que o LinkedIn não exibe).
- `sitemap.xml` e `index.xml` (RSS) gerados pelo `ContentIndex`.
- `robots.txt` permitindo tudo e apontando o sitemap.
- Página 404 em português.

## 11. Páginas fixas (rascunho inicial, textos finais meus)

| Página | Conteúdo mínimo |
|---|---|
| `index.md` | 2–3 frases sobre o site, links para as seções, recentes, lendo agora |
| `sobre.md` | Bio, foto (`quartz/static/foto.jpg`), temas que estudo, contatos |
| `newsletter.md` | O que é a newsletter, frequência (periódica, sem dia fixo), botão de assinatura para o Substack, aviso de que o cadastro é feito lá e link do RSS. Sem arquivo de edições |
| `posts/index.md`, `radar/index.md`, `leituras/index.md` | 1 parágrafo explicando a seção |

Todas com `publish: true`. Textos de exemplo marcados com `TODO:` para eu substituir.

## 12. Testes

- `tools/tests/fixtures/vault/`: vault de exemplo com
  - notas elegíveis de cada tipo;
  - nota com `publicar: true` em `00-Inbox` e outra do tipo destaques (devem ser bloqueadas);
  - links para notas privadas, inexistentes, com `#secao` e com apelido;
  - comentários `%%` e `<!-- -->`, template não preenchido;
  - imagem usada e imagem não usada;
  - conteúdo `agendado` com data futura;
  - dois slugs iguais (erro) e troca de slug (gera alias).
- `pytest` cobrindo seleção, frontmatter de saída, reescrita de links, embeds, auditoria, manifesto e o bloco "lendo agora".
- **Teste de vazamento:** todo texto marcado com `SEGREDO-` no vault de exemplo não pode aparecer em nenhum arquivo de `content/` nem de `public/` depois do build.
- CI (`.github/workflows/testes.yml`): `pytest` do exportador + `npx quartz build` em todo pull request.
- Manual (M4): Lighthouse mobile ≥ 95 nas quatro categorias, na home e num artigo.

## 13. Ordem de implementação

| Marco | Tarefas |
|---|---|
| **M1** | Instalar o Quartz (seção 3), configuração pt-BR (seção 4), páginas fixas com `TODO:` (seção 11), workflow de deploy (seção 8), publicar no endereço padrão `thyagoluciano.github.io/thyagoluciano.com.br` (com `baseUrl` temporário igual a esse endereço) |
| **M2** | Exportador completo (seção 6), manifesto, auditoria, testes (seção 12), scripts `publicar`, `previa`, `simular` (seção 7), CI de testes |
| **M3** | `Plugin.CNAME()`, DNS no Registro.br, domínio customizado e HTTPS (seção 8); ajustar `baseUrl` |
| **M4** | Layout, tema, componentes novos, SEO, imagem padrão de compartilhamento, 404 (seções 9 e 10); Lighthouse. O layout passou a seguir o [SPEC-TEMA-CHIRPY.md](./SPEC-TEMA-CHIRPY.md) |
| **M5** | Primeiro artigo real; README com o fluxo de publicação; seção "Publicação no site" no `_sistema/_guia-ia.md` do vault (com commit no Git do vault) |

## 14. Critérios de pronto

- `pytest` e `npx quartz build` passam.
- Auditoria de privacidade sem ocorrências.
- Nenhuma escrita no vault (teste que compara hashes antes e depois da exportação).
- README com: pré-requisitos, instalação, `previa`, `simular`, `publicar`, configuração de domínio e como atualizar o Quartz.
