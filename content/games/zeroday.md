---
title: ZeroDay
description: Jogo cooperativo no navegador em que o time de tecnologia defende a produção contra vulnerabilidades. Por que criei, a stack, as IAs e como criar sua head.
date: '2026-11-16'
published: '2026-11-16'
modified: '2026-11-16'
tags:
- games
- gamedev
- ia
- seguranca
- multiplayer
publish: true
gerado: true
tipo: game
capa: assets/ad6ba811-zeroday-capa.jpg
genero: Ação cooperativa
plataformas: Web (PC e celular)
---

![[assets/ad6ba811-zeroday-capa.jpg|Partida de ZeroDay: o time enfrenta o chefão Zero Day em volta do Core]]

O ZeroDay é um jogo cooperativo que roda no navegador. De 1 a 6 pessoas entram na mesma sala, pelo computador ou pelo celular, escolhem uma classe e defendem a produção contra ondas de vulnerabilidades. No fim da partida aparece o chefão, o Zero Day. Cada partida dura cerca de 3 minutos.

<p><a class="external" href="https://zeroday.thyagoluciano.com.br"><strong>Jogar o ZeroDay</strong></a></p>

É um MVP, feito para experimentar IAs novas e ver até onde dava para ir. Este texto conta por que criei o jogo, como ele funciona, quais ferramentas e IAs usei e como você pode colocar a sua própria cabeça nele. Eu também [apresentei o jogo no LinkedIn](https://lnkd.in/p/dXEibdNT), onde o vídeo mostra uma partida.

## Por que criei

Passei os últimos meses lidando com correção de vulnerabilidade e atualização de dependência. Todo dia chega um alerta novo, e a IA está acelerando tanto a descoberta das falhas quanto a correção. Em algum momento pensei em transformar essa rotina em jogo.

A ideia também era reforçar a colaboração entre os papéis de um time de tecnologia, com quatro classes que dependem umas das outras. Depois dos jogos de puzzle que publiquei nas lojas, não consegui parar, e desta vez o formato é outro: multiplayer no navegador, sem instalar nada.

## Como se joga

O time defende o Core, que representa a produção. Se a integridade do Core chega a zero, a partida acaba. Se o time sobrevive às ondas e derrota o chefão, vence.

| | PC | Celular |
|---|---|---|
| Andar | WASD ou setas | joystick esquerdo |
| Mirar | mouse | joystick direito |
| Atirar | segurar o botão do mouse | arrastar o joystick direito |
| Super | Espaço | botão da super |

### As classes

| Classe | Ataque | Super |
|---|---|---|
| Dev Back-end | rajada curta de alto dano | **Hotfix**: explosão em área |
| Dev Front-end | tiro longo que atravessa um inimigo | **Validação**: escudo que bloqueia projéteis |
| QA | tiro que marca o inimigo, e o time causa mais dano nele | **Suíte de testes**: revela inimigos invisíveis |
| SRE | posiciona torretas que atiram e curam aliados | **Rollback**: restaura o Core e revive aliados |

A super carrega quando você causa dano ou cura alguém. O ranking do fim da partida também pontua assistência, cura e defesa do Core, para que QA e SRE disputem o MVP em pé de igualdade com quem mais abate.

### As vulnerabilidades

| Vilão | Comportamento | Fraco a |
|---|---|---|
| SQL Injection | rápido, vai direto ao Core | Dev Back-end |
| XSS | atira e se divide em dois ao morrer | Dev Front-end |
| Secret vazado | invisível até ser revelado | QA |
| Dependência desatualizada | lento, resistente, anda em grupo | Dev Back-end |
| DDoS | enxame de unidades fracas | SRE |
| Zero Day (chefão) | a fraqueza muda durante a luta | rotativa |

Cada vilão recebe o dobro de dano da classe a que é fraco. Isso é um bônus, não uma trava: nenhuma partida exige uma classe específica, então qualquer composição de sala consegue vencer.

![[assets/a7226316-zeroday-xss.jpg|O XSS aparece com o aviso de que é fraco a Dev Front-end]]

## Como criar a sua head

No ZeroDay cada personagem tem corpo e cabeça. O corpo vem da classe. A cabeça pode ser uma das 20 da biblioteca ou uma caricatura sua. O jogo tem um guia em passos para criar a sua:

1. **Imagem base de estilo.** O guia oferece uma imagem de referência que mostra o traço do jogo e como o pescoço é cortado.
2. **Prompt.** Você abre o ChatGPT ou o Gemini pelo próprio guia, com o prompt pronto, e anexa duas imagens, nesta ordem: uma foto sua de rosto e a imagem base.
3. **Resultado.** A ferramenta devolve a cabeça sobre um fundo rosa-choque liso (`#FF00FF`). Se vier com corpo, ombros, cabelo caindo abaixo do pescoço ou outro fundo, é só pedir de novo.
4. **Envio e ajuste.** Você envia a imagem, o servidor remove o fundo e mede onde fica o pescoço. Um passo de ajuste mostra a cabeça sobre o corpo das quatro classes, e você acerta encaixe e tamanho.
5. **Termo de consentimento.** Você aceita um termo e assina com seu nome. Se a foto for de outra pessoa, ela precisa ter autorizado.
6. **Códigos.** O jogo mostra dois códigos: o de uso, que libera a cabeça para você e para quem você quiser, e o de gerenciamento, que só você tem e serve para apagar a caricatura. Guarde os dois.

![[assets/38584b00-zeroday-guia-cabecas.jpg|Primeiro passo do guia Criar minha caricatura, com o prompt pronto para copiar]]

![[assets/4bfe6ca2-zeroday-estilo-base.jpg|Imagem base de estilo do guia, com fundo rosa-choque]]

Algumas decisões de privacidade valem ser ditas:

- A foto vai para a ferramenta de imagem que você escolher, sob os termos dela. O ZeroDay nunca recebe a foto, só a caricatura.
- O código de uso abre a imagem. Na sala, quem joga com a cabeça a mostra aos colegas, e o servidor guarda apenas o hash dos códigos.
- O login com Google é opcional. Com ele, suas caricaturas ficam vinculadas à conta e aparecem em qualquer aparelho.
- A medição de uso (Google Analytics) só liga depois que você aceita o aviso.

## Stack e arquitetura

O projeto é um monorepo TypeScript com três pacotes:

- **shared:** tipos, balanceamento e regras puras (colisão, dano, pontuação e ondas). Todo o balanceamento fica em um arquivo de dados, o que facilita ajustar vida, dano e composição das ondas.
- **server:** a sala do Colyseus, com simulação autoritativa a 20 atualizações por segundo. O servidor decide o que acontece e manda o estado completo da partida aos jogadores.
- **client:** Three.js para a arena, com câmera fixa inclinada, e React para lobby, HUD e tela de resultado.

Resumo das tecnologias:

- **Linguagem e build:** TypeScript, Node.js 22, pnpm e Vite.
- **Jogo:** Three.js, React e uma colisão 2D própria.
- **Multiplayer:** Colyseus. O próprio jogador tem predição local e os outros são interpolados.
- **Testes:** Vitest para regras, simulação e sala em rede, scripts de ponta a ponta no navegador (incluindo os joysticks do celular) e um simulador de partidas com bots para ajustar o balanceamento.
- **Contas e medição:** Firebase, para o login com Google, a medição de uso e, opcionalmente, o armazenamento das caricaturas.
- **Hospedagem:** Docker em uma VPS, com Caddy cuidando do certificado e do WebSocket, e GitHub Actions para o deploy.

## As IAs que usei

O ZeroDay foi feito com IA de ponta a ponta:

- **Código:** Claude Code. Antes de escrever, defini a proposta, as decisões de design e as especificações do jogo com o OpenSpec, e depois pedi a implementação em tarefas. O repositório guarda esses documentos junto com o código.
- **Imagens:** Nano Banana, para as cabeças, os corpos das classes e os vilões. Há um guia de estilo único e uma imagem âncora que vão junto em todo prompt, para o traço ficar consistente.
- **Áudio:** Stable Audio 3, rodando no ComfyUI, para os efeitos sonoros e a música.

Todos os assets ficam registrados em um manifesto, com o prompt e a referência de cada um. São 52 itens: 18 efeitos sonoros, 3 músicas, 7 vilões, 4 corpos, 5 imagens de referência e 15 cabeças. Se eu quiser refazer um som ou uma imagem, edito o prompt no manifesto e rodo o script de novo. Um script de pós-processamento remove o fundo magenta, recorta e padroniza o tamanho de cada imagem.

A geração das imagens é manual de propósito. Os prompts ficam versionados e eu mesmo os executo, porque assim as fotos de pessoas só saem do computador com alguém decidindo enviá-las.

## O que apareceu no caminho

Alguns problemas só surgiram jogando de verdade, e boa parte do histórico do projeto vem deles:

- O encaixe da cabeça no corpo. O servidor passou a medir o pescoço pelo corte reto mais baixo da imagem, para que cabelo caindo não engane a medição, e o guia ganhou o passo de ajuste.
- O celular. Ganhou um botão de ataque dedicado, com mira automática.
- O link de convite. A cópia não funcionava em endereços HTTP sem certificado, e foi preciso um método de reserva.
- As caricaturas protegidas por código, para que as imagens enviadas por jogadores não entrem no bundle nem na imagem do Docker.

## O que falta

É um MVP, e ainda tem muita coisa para melhorar. Os valores de balanceamento começaram como chutes e foram ajustados com o simulador de bots, e ainda dá para refinar. No vídeo do LinkedIn, os 6 jogadores são bots, e o único com rosto de verdade sou eu. Não consegui juntar cinco pessoas com tempo livre para gravar.

![[assets/3d2c88b1-zeroday-onda.jpg|Uma onda de vulnerabilidades chegando ao Core]]

Se você jogar, me conta o que achou. O jogo está em [zeroday.thyagoluciano.com.br](https://zeroday.thyagoluciano.com.br).
