# thyagoluciano.com.br

Site pessoal de Thyago Luciano, gerado com [Quartz v4](https://quartz.jzhao.xyz/) a partir das notas públicas do vault Obsidian `SecondBrain`. Fica no ar em <https://thyagoluciano.github.io> (GitHub Pages).

O conteúdo é escrito **só no Obsidian**. Um exportador copia para `content/` apenas o que foi marcado para publicar, o Quartz gera o site, e o GitHub Actions faz o deploy.

```
Obsidian (vault)            Repositório                      Internet
  nota com           npm run publicar           push na main
  publicar: true ───▶ exporta ─▶ valida ─▶ commit ───────────▶ GitHub Actions ─▶ GitHub Pages
                     (auditoria de privacidade)
```

## Publicar um texto (o dia a dia)

1. **No Obsidian**, escreva a nota e preencha o frontmatter (veja [O que cada tipo de nota precisa](#o-que-cada-tipo-de-nota-precisa)). Marque `publicar: true`.
2. **Veja a prévia** (opcional, recomendado):

   ```bash
   npm run previa
   ```

   Exporta o vault, compila o site e abre em <http://localhost:8080>. Edite a nota e recarregue para ver a mudança.
3. **Publique:**

   ```bash
   npm run publicar
   ```

   O comando roda 5 passos e para no primeiro que falhar:

   | Passo | O que faz |
   |---|---|
   | 1 | Exporta o vault em **modo estrito** (qualquer nota com erro aborta tudo) e roda a auditoria de privacidade |
   | 2 | Compila o site (`npx quartz build`) para validar |
   | 3 | `git add content tools/manifesto.json` |
   | 4 | Commit `Publica: <títulos novos ou alterados>` (se não houver mudança, avisa e sai) |
   | 5 | `git push origin main` |

4. **Acompanhe o deploy** na aba *Actions* do repositório. Em poucos minutos o texto está no ar.

> `npm run publicar` **faz `git push`**. Antes de rodar, confira a prévia.

### Só ver o que aconteceria

```bash
npm run simular
```

Mostra o que entraria, sairia e mudaria, sem escrever nada. Útil depois de mexer em várias notas.

### Despublicar

Tire `publicar: true` da nota (ou mude para `false`) e rode `npm run publicar`. O arquivo sai de `content/` e a remoção aparece no resumo.

## O que cada tipo de nota precisa

Campos comuns a **todos** os tipos:

| Campo | Regra |
|---|---|
| `publicar` | `true` (booleano; `"true"` entre aspas dá erro) |
| `slug` | minúsculas, números e hífens (`meu-post`); único na seção; não pode ser `index` |
| `descricao` | até 160 caracteres (vira a descrição nas redes e no Google) |
| `titulo` | prefixos como `Site - `, `Livro - ` são removidos |
| `criado`, `atualizado` | datas `AAAA-MM-DD` (aparecem no site) |
| `tags` | lista; o `#` é ignorado |
| `capa` | imagem do vault (opcional); vira a capa do card e do post |

### Posts (`/posts/`)

```yaml
tipo: conteudo
canal: site
status: publicado        # ou agendado
publicar: true
slug: meu-post
descricao: Uma frase de até 160 caracteres.
data_publicacao: 2026-10-01
```

- `canal` precisa ser `site`. Outros canais (por exemplo `linkedin`) não são exportados.
- `status: agendado` exige `data_publicacao`. O texto só sai quando a data chegar **e você rodar `npm run publicar` de novo**: o site é estático e não publica sozinho.

### Radar (`/radar/`): projetos e ferramentas de outras pessoas

```yaml
tipo: ferramenta
publicar: true
slug: quartz
descricao: Gerador de sites estáticos a partir de notas em Markdown.
url: https://quartz.jzhao.xyz
autor_projeto: Jacky Zhao
categoria: publicação
estado: testando          # quero-testar | testando | uso | descartei
por_que: Publica um vault do Obsidian como site, que é o que este site faz.
repositorio: https://github.com/jackyzha0/quartz   # opcional
licenca: MIT                                       # opcional
```

Obrigatórios: `url`, `autor_projeto`, `categoria`, `estado` e `por_que`. O `estado` só aceita os quatro valores acima, e `url` e `repositorio` precisam começar com `http://` ou `https://`.

### Leituras (`/leituras/`)

Resenha de livro:

```yaml
tipo: fonte
subtipo: livro
publicar: true
slug: a-arte-da-guerra
descricao: Resenha de A Arte da Guerra, de Sun Tzu.
autor: "[[Autor - Sun Tzu]]"
nota: 5                   # de 1 a 5 (opcional)
status_leitura: lendo     # "lendo" aparece em "Lendo agora"
```

Encontro (se a leitura virar um clube): `tipo: encontro`, com `slug`, `descricao` e `data_publicacao`. O slug `encontros` é reservado.

### O que **nunca** é publicado

- Notas `tipo: ideia` e `tipo: mapa`: ficam só no Obsidian. Se marcar uma com `publicar: true`, a exportação dá erro e pede para remover o marcador.
- Notas em `00-Inbox`, `90-Templates` e `_sistema`.
- Notas com `subtipo: destaques`.
- Qualquer nota sem `publicar: true`.

## O que o exportador faz com o texto

- **Links entre notas:** para nota publicada, vira link do site; para nota não publicada (inclusive ideias e mapas), vira **texto simples**.
- **Comentários** `%% ... %%` e `<!-- ... -->`, seções vazias e placeholders de template são removidos.
- **Imagens:** só as usadas pelas notas publicadas são copiadas para `content/assets/`.
- **Campos do frontmatter:** só uma lista fixa sai. Campos privados (`prioridade`, `notas_internas`…) nunca vão para o site.
- **Trocar o `slug`** de uma nota já publicada mantém o endereço antigo funcionando (redirecionamento automático, registrado em `tools/manifesto.json`).

A **auditoria de privacidade** roda em toda exportação. Se achar qualquer problema (link para página inexistente, resíduo de comentário, imagem sem referência), nada é escrito e o comando termina com erro. Nunca desative a auditoria nem o filtro `publish: true` para "fazer passar".

## Páginas escritas no repositório

Estas páginas **não vêm do vault**. Edite os arquivos direto (o exportador nunca sobrescreve os `index.md`):

| Arquivo | Página |
|---|---|
| `content/index.md` | Início |
| `content/sobre.md` | Sobre |
| `content/newsletter.md` | Newsletter |
| `content/arquivo.md` | Arquivo (a lista é gerada) |
| `content/posts/index.md`, `content/radar/index.md`, `content/leituras/index.md` | Texto de apresentação de cada seção |

Em `content/leituras/index.md`, o bloco entre `<!-- gerado:lendo-agora -->` e `<!-- /gerado:lendo-agora -->` é **preenchido pelo exportador** com o livro em leitura. Não edite o que está entre esses marcadores.

Textos de exemplo ainda estão marcados com `TODO:`. Troque pelos seus.

Depois de editar páginas fixas, veja a prévia com `npx quartz build --serve` (não precisa do vault). Para publicar, rode `npm run publicar`: como essas páginas ficam em `content/`, elas entram no mesmo commit das notas exportadas. Se você só mexeu em páginas fixas, o comando ainda exporta o vault antes, então o vault precisa estar acessível; sem ele, use o fluxo de commit manual da próxima seção.

## Mudar configuração, menu ou visual

| O que mudar | Onde |
|---|---|
| Redes sociais (LinkedIn, X, Threads, Instagram, GitHub) e endereço do Substack | `quartz.layout.ts` (objeto `REDES` e `SUBSTACK_URL`) |
| Frase curta abaixo do título | `quartz.layout.ts` (`FRASE`) |
| Menu lateral | `quartz/components/BarraLateral.tsx` (`ITENS`) |
| Título, domínio, plugins, tema de cores e fontes | `quartz.config.ts` |

Mudanças de código **não** entram no `npm run publicar`. Publique assim:

```bash
npm run check                 # tsc + prettier
npm run testar                # testes do exportador e do build
git add -A
git commit -m "Descreve a mudança"
git push origin main          # dispara o deploy
```

## Newsletter

O envio é **manual**, pelo Substack (<https://thyagoluciano.substack.com>): o site só leva o leitor ao cadastro. Para enviar uma edição, publique os textos no site e depois monte e envie a edição no editor do Substack. De tempos em tempos, exporte a lista de assinantes (CSV) como cópia de segurança.

## Configuração inicial (uma vez por máquina)

Requisitos: Node ≥ 22 (versão em `.node-version`), npm ≥ 10.9 e [uv](https://docs.astral.sh/uv/).

```bash
npm ci
```

Informe onde está o vault em `tools/config.toml` (fora do Git):

```toml
vault = "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain"
```

Alternativas: variável de ambiente `SB_VAULT` ou a opção `--vault` do exportador.

## Comandos

| Comando | O que faz |
|---|---|
| `npm run previa` | Exporta o vault e serve o site em <http://localhost:8080> |
| `npm run simular` | Mostra o que a exportação faria, sem escrever |
| `npm run publicar` | Exporta (estrito), valida, faz commit e `git push` |
| `npm run testar` | Testes do exportador e do build (usam um vault de exemplo, nunca o real) |
| `npm run check` | `tsc --noEmit` e `prettier --check` |
| `npx quartz build --serve` | Só o Quartz, sem exportar (bom para testar páginas fixas e visual) |

## Quando algo dá errado

| Sintoma | O que fazer |
|---|---|
| `Erros (n)` no resumo e `exportação abortada` | Leia a lista: cada linha diz a nota e o motivo (falta `slug`, `descricao` longa, estado inválido…). Corrija no Obsidian e rode de novo |
| `Erro: Arquivos do vault não baixados do iCloud` | Abra o Obsidian ou o Finder para baixar os arquivos listados e tente de novo. Nada foi publicado |
| `Auditoria de privacidade: n ocorrência(s)` | Nada foi escrito. Corrija o que a lista aponta (por exemplo um link para uma página que não existe) |
| `Vault não configurado` | Crie `tools/config.toml` (veja acima) ou use `SB_VAULT` |
| Publicou, mas o site não mudou | Veja a aba *Actions* do repositório: o deploy pode ter falhado ou ainda estar rodando |
| Nota agendada não apareceu | Rode `npm run publicar` de novo depois da `data_publicacao` |

Códigos de saída do exportador: `0` ok, `1` erros de seleção (modo estrito), `2` vault indisponível ou caminho inválido, `3` auditoria de privacidade falhou.

## Mais detalhes

- Requisitos do produto: [`specs/PRD.md`](specs/PRD.md)
- Especificação técnica (fonte da verdade): [`specs/SPEC.md`](specs/SPEC.md)
- Tema visual: [`specs/SPEC-TEMA-CHIRPY.md`](specs/SPEC-TEMA-CHIRPY.md)

Gerado com [Quartz v4](https://quartz.jzhao.xyz/) (licença MIT, em `LICENSE.txt`). Para atualizar o Quartz: `npx quartz update`.
