# PRD: Site pessoal thyagoluciano.com.br

| | |
|---|---|
| Autor | Thyago Luciano |
| Data | 2026-09-28 |
| Status | Aprovado para implementação |
| Documento técnico | [SPEC.md](./SPEC.md) |
| Relacionado | `second-brain-tools/docs/PRD.md` (busca e relatórios do vault) |

## 1. Contexto

Meu conhecimento vive num vault do Obsidian (`SecondBrain`, no iCloud), em Markdown com frontmatter padronizado. O conteúdo segue o modelo **COPE** (*Create Once, Publish Everywhere*): uma ideia no vault gera uma **peça canônica no site** e dela derivam as versões para Substack, LinkedIn, X, Threads e Instagram, que apontam de volta para o site.

Falta o site: o lugar público, sob meu domínio, onde os textos ficam de forma permanente, conectados entre si e fáceis de encontrar.

## 2. Objetivo

Publicar **thyagoluciano.com.br** como um site estático gerado a partir do vault, em que:

1. Escrevo **só no Obsidian**. Publicar é marcar `publicar: true` e rodar um comando.
2. **Nada privado vaza**: só sai o que foi marcado, e links para notas privadas viram texto.
3. As notas publicadas mantêm os **links entre si** como links comuns. O jardim digital (ideias atômicas, backlinks e grafo) vive no Obsidian; o site mostra só o que foi publicado.
4. O site tem posts, um radar de projetos e ferramentas de outras pessoas, leituras, página sobre e acesso à newsletter.

## 3. Público

| Público | O que busca |
|---|---|
| Profissionais de tecnologia (LinkedIn, X) | Posts aprofundados sobre IA, engenharia e liderança, e boas ferramentas para experimentar |
| Assinantes da newsletter | Textos longos e o arquivo completo |
| Leitores das leituras | Resenhas, comentários e sínteses por livro |
| Eu | Um lugar para apontar em todos os canais |

## 4. Casos de uso

| # | Como… | Quero… | Para… |
|---|---|---|---|
| UC1 | autor | marcar uma nota com `publicar: true` e rodar `publicar` | ver o texto no ar em poucos minutos |
| UC2 | autor | ver uma prévia antes de publicar | revisar o resultado no navegador |
| UC3 | autor | ter a garantia de que destaques e notas privadas não saem | publicar sem medo |
| UC4 | leitor | navegar de um post para outros posts relacionados | aprofundar no assunto |
| UC5 | leitor | buscar no site e filtrar por tag | achar o que interessa |
| UC6 | leitor | assinar por RSS ou pela newsletter | acompanhar novas publicações |
| UC7 | leitor | ver o que estou lendo e as resenhas | acompanhar as leituras |
| UC9 | leitor | ver projetos e ferramentas que o autor quer usar, está testando ou já usa | descobrir boas ferramentas e saber a opinião dele |
| UC8 | autor | compartilhar um link com prévia bonita (título, descrição, imagem) | aumentar cliques vindos das redes |

## 5. Requisitos funcionais

### RF1. Seções do site
| Seção | Conteúdo | Origem no vault |
|---|---|---|
| `/` (início) | Apresentação curta, posts recentes, "lendo agora", link para a newsletter | Página escrita no repositório + dados gerados |
| `/posts/` | Peças canônicas: artigos, ensaios e notas longas | `50-Conteudo/Site/` (`tipo: conteudo`, `canal: site`) |
| `/radar/` | Vitrine de projetos e ferramentas de outras pessoas que quero usar ou experimentar, cada um com estado (quero testar, testando, uso, descartei) | Notas `tipo: ferramenta` (ver RF1.1) |
| `/leituras/` | Livro atual, resenhas e comentários do que estou lendo; encontros, se o projeto virar um clube | `10-Fontes/Livros/*/Livro - *.md`, `60-Clube/` |
| `/sobre` | Quem sou, contatos, redes | Página escrita no repositório |
| `/newsletter` | Assinatura do Substack (link para `thyagoluciano.substack.com/subscribe`) | Página escrita no repositório |
| `/tags/…` | Listagem por tag | Gerado |
| `/arquivo` | Linha do tempo de tudo o que foi publicado, por ano e mês | Gerado |

### RF1.1 Radar (notas `tipo: ferramenta`)
Projetos e ferramentas **de outras pessoas**. Campos do frontmatter no vault (todos saem para o site, exceto o que não consta aqui):

| Campo | Obrigatório | Descrição |
|---|---|---|
| `titulo` | sim | Nome da ferramenta |
| `url` | sim | Endereço do projeto (`http` ou `https`) |
| `autor_projeto` | sim | Pessoa ou organização que criou (crédito) |
| `categoria` | sim | Uma categoria (por exemplo IA, terminal, publicação) |
| `estado` | sim | `quero-testar`, `testando`, `uso` ou `descartei` |
| `por_que` | sim | Uma ou duas frases sobre por que me interessou |
| `repositorio` | não | Endereço do repositório |
| `licenca` | não | Licença (por exemplo MIT) |

Referências de desenho: Technology Radar da Thoughtworks (estados), listas `awesome-*` do GitHub e coleções como Raindrop e Are.na.

Fora do site: notas `tipo: ideia` e `tipo: mapa` continuam no Obsidian e nunca são exportadas. Marcá-las com `publicar: true` gera erro de exportação.

### RF2. Exportação do vault
- Seleciona só notas com `publicar: true` e campos obrigatórios preenchidos.
- Nunca exporta notas `subtipo: destaques`, nem qualquer arquivo de `00-Inbox`, `90-Templates` ou `_sistema`.
- Transforma links: para nota publicada, vira link interno do site; para nota não publicada, vira texto simples.
- Copia só as imagens usadas pelas notas publicadas.
- Remove comentários (`<!-- -->`, `%% %%`), placeholders de template e campos privados do frontmatter.
- Mantém URLs estáveis: mudar o `slug` gera redirecionamento do endereço antigo.
- Tem modo de simulação (mostra o que entra, sai e muda, sem escrever).

### RF3. Navegação e descoberta
- Links entre notas publicadas, como links comuns. Sem backlinks, sem grafo e sem prévia ao passar o mouse (removidos por decisão do autor).
- Busca no site.
- Índice por tags e linha do tempo (`/arquivo`).
- Posts recentes na página inicial.

### RF4. Distribuição
- RSS, sitemap, metadados Open Graph e Twitter Card em todas as páginas.
- Imagem de prévia por página (capa definida ou gerada automaticamente).
- Acesso à newsletter pelo menu (página `/newsletter`) e pelo ícone do Substack na barra lateral. Sem bloco de chamada no fim dos posts.

### RF5. Publicação
- Um comando: exporta, gera o site localmente para validar, faz commit e push.
- Deploy automático no GitHub Pages a cada push na branch principal.
- Domínio próprio com HTTPS.

## 6. Requisitos não funcionais

| # | Requisito |
|---|---|
| RNF1 | **Privacidade por padrão:** duas barreiras independentes (exportador + filtro do gerador). |
| RNF2 | **Português do Brasil** em toda a interface, datas e metadados (`pt-BR`). |
| RNF3 | **Desempenho:** Lighthouse ≥ 95 em Performance, Acessibilidade, Boas práticas e SEO (mobile). |
| RNF4 | **Acessibilidade:** WCAG 2.1 AA; tema claro e escuro. |
| RNF5 | **Custo zero** de hospedagem (GitHub Pages); só o domínio é pago. |
| RNF6 | **Vault intocado:** o exportador só lê o vault. |
| RNF7 | **Build reproduzível:** mesma entrada gera a mesma saída; build falha em link quebrado ou vazamento detectado. |
| RNF8 | **Atualizável:** permite receber atualizações do Quartz sem conflito com as personalizações. |

## 7. Fora de escopo (v1)

- Comentários no site.
- Publicação automática nas redes sociais e no Substack.
- Escrita automática do campo `url` de volta no vault.
- Área logada, formulários próprios ou back-end.
- Versão em inglês.
- Métricas de engajamento das redes.

## 8. Marcos

| Marco | Entrega | Aceite |
|---|---|---|
| M1 | Quartz configurado em pt-BR, deploy no endereço padrão do GitHub Pages | Site de teste no ar |
| M2 | Exportador com testes (vault de exemplo) | Testes de privacidade e links passam |
| M3 | Domínio thyagoluciano.com.br com HTTPS | Domínio e `www` respondendo com certificado |
| M4 | Layout, tema visual e páginas fixas (início, sobre, newsletter, leituras) | Lighthouse ≥ 95; revisão visual aprovada |
| M5 | Primeiro post real publicado e fluxo documentado no `_guia-ia.md` | Post no ar, com prévia correta ao compartilhar |

## 9. Métricas de sucesso

- Publicar um post leva menos de 5 minutos entre marcar `publicar: true` e estar no ar.
- Zero vazamentos (auditoria do exportador em todo build).
- Pelo menos 1 post por semana nos 3 primeiros meses.
- Todo post nas redes aponta para uma página do site.

## 10. Decisões pendentes

| Decisão | Padrão, se não houver resposta |
|---|---|
| Analytics | Nenhum na v1 (depois: Plausible, Umami ou GoatCounter) |
| Foto, bio curta e links para a página sobre | Espaço reservado |
| Identidade visual (cores, fontes) | Tema neutro definido na SPEC |

## 11. Riscos

| Risco | Mitigação |
|---|---|
| Vazamento de nota privada | Exportador com lista de permissão + filtro `ExplicitPublish` do Quartz + auditoria no build |
| Link quebrado ao mudar título ou slug | Manifesto de exportação e aliases de redirecionamento |
| Arquivos do iCloud não baixados no momento da exportação | Detectar, pedir download (`brctl`), abortar com mensagem clara se persistir |
| Push a partir da VM do Cowork sem credenciais do GitHub | Push feito no Mac (Claude Code ou terminal); o Cowork pode exportar e preparar o commit |
| Atualização do Quartz quebrar personalizações | Personalizações concentradas em `quartz.config.ts`, `quartz.layout.ts` e `quartz/styles/custom.scss` |
