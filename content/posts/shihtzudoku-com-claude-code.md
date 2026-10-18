---
title: Criei um jogo de puzzle com o Claude Code e publiquei no Google Play
description: 'É um puzzle de lógica para celular, feito com o Claude Code e já no Google Play: como trabalhei com a IA, o que deu errado e o que ainda não provei.'
date: '2026-10-18'
published: '2026-10-18'
modified: '2026-10-18'
tags:
- ia
- engenharia-de-software
publish: true
gerado: true
tipo: post
capa: assets/64cc8859-shihtzudoku-capa.png
---

Em cerca de 50 horas de trabalho, entre 6 e 14 de outubro, construí um jogo de puzzle para celular chamado Shih Tzudoku. Quem escreve a maior parte do código é o Claude Code, uma ferramenta de inteligência artificial para programação, e eu dirijo o trabalho: decido o que o jogo deve fazer, aprovo o plano de cada etapa e testo no celular.

Neste texto eu conto como funciona o jogo, como organizei o trabalho com a IA, o que já está pronto, o que deu errado no caminho, como foi publicar nas lojas e o que ainda falta. Não precisa entender de programação para acompanhar.

Começo pelo estado atual: o jogo já está no [Google Play](https://play.google.com/store/apps/details?id=com.thyagoluciano.shihtzudoku). A versão para iPhone foi enviada à Apple em 14 de outubro e aguarda a revisão. Enquanto a Apple não responde, não sei se ela aprova.

[![[assets/e1ad5e03-shihtzudoku-google-play-badge.png|180]]](https://play.google.com/store/apps/details?id=com.thyagoluciano.shihtzudoku)

**App Store:** em breve

![[assets/42617f1a-shihtzudoku-home.png]]
*A tela inicial do Shih Tzudoku, com a campanha, o desafio diário e o ranking.*

## Como o jogo funciona

O tabuleiro é um quadrado dividido em regiões coloridas. Em cada região vive um Shih Tzu, e o jogador precisa descobrir em qual casa cada cachorro fica. As regras são quatro:

1. Um cachorro por linha.
2. Um cachorro por coluna.
3. Um cachorro por região colorida.
4. Dois cachorros não podem se encostar, nem na diagonal.

Todo nível tem uma única resposta certa e pode ser resolvido só com raciocínio, sem chutar. Essa garantia deu mais trabalho que qualquer outra parte do jogo, e eu explico mais abaixo.

![[assets/ecce0f14-shihtzudoku-tabuleiro-8x8-resolvido.png]]
*Um tabuleiro 8×8 resolvido: um cachorro por linha, por coluna e por região, sem nenhum encostar no outro.*

## Como trabalho com o Claude Code

Antes de pedir qualquer código, escrevi um conjunto de regras para a IA seguir. As principais são estas:

- **Um passo de cada vez.** Existe uma lista de etapas, e a IA só trabalha na próxima.
- **Plano antes do código.** A IA me mostra o que pretende fazer, e eu aprovo ou corrijo. Só depois ela começa. Corrigir uma frase de plano é bem mais barato do que revisar dezenas de arquivos prontos.
- **Diário de bordo.** Durante o trabalho, ela anota o que rodou, os erros que apareceram e as decisões que tomou.
- **Não inventar resultado.** O que não foi testado precisa ser registrado como não testado.

Essa regra me obriga a olhar o que realmente aconteceu, e boa parte do que conto neste texto vem desse diário.

Em números, até 14 de outubro: cerca de 50 horas de trabalho com o Claude Code, somando 25 sessões, 143 registros de alteração, mais de 130 mil linhas de código (testes incluídos) e cerca de 2.300 testes automáticos só nas partes do jogo, fora os do servidor. Os testes são pequenos programas que verificam se o jogo se comporta como deveria.

## O que já está pronto

### O cérebro do jogo

A primeira parte foi a mais invisível: o programa que gera os níveis e confere se cada um tem uma única solução.

O gerador monta o tabuleiro de forma aleatória, mas isso quase sempre produz níveis com mais de uma resposta. Na primeira medição, nenhum dos 500 tabuleiros 8×8 gerados tinha solução única. Por isso o programa procura uma segunda solução, muda uma casa de região para eliminá-la e confere de novo, até sobrar uma só.

Esse reparo nem sempre funciona. Em 2% a 9% dos tabuleiros ambíguos, dependendo do tamanho, não havia nenhuma casa que pudesse ser trocada, e o programa precisa descartar o tabuleiro e começar outro.

Há ainda uma segunda exigência: o nível precisa ser resolvível por raciocínio. Para isso, escrevemos um segundo programa que resolve do jeito que uma pessoa resolveria, usando técnicas como "essa região só cabe nesta linha, então o resto da linha fica livre". Todo nível gerado passa por ele. Se o programa não consegue resolver, o nível é descartado.

O mesmo programa serve para o botão de dica. Ele olha o tabuleiro do jogador, encontra o próximo passo lógico, destaca as casas envolvidas e explica o motivo em texto.

![[assets/da743f07-shihtzudoku-dica.png]]
*Uma dica no jogo: todos os lugares possíveis da região B estão na linha 3, então as outras casas livres dessa linha podem ser descartadas.*

### Dificuldade e campanha

A primeira campanha tinha 100 níveis, com o tamanho do tabuleiro subindo e descendo em ondas. Eu a refiz depois de analisar o que o jogo ensinava e quando. A versão atual tem 400 níveis em 8 mundos, e cada mundo usa um tamanho de tabuleiro, de 4×4 até 11×11. Os mundos têm nomes de uma trilha "do quintal ao palácio": Quintal, Sala, Jardim, Praça, Parque, Fazenda, Montanha e Palácio Imperial.

O tamanho e a técnica de raciocínio viraram dois eixos separados. Uma técnica nova é ensinada antes de aparecer num nível: na primeira vez, o jogo mostra um cartão explicando e a dica funciona em dois tempos, primeiro aponta onde olhar e depois explica. A cada dez níveis a dificuldade sobe e cai, e o décimo é um chefe.

Quem vence os chefes abre o Modo Mestre, que repete os níveis no tabuleiro mais difícil e sem ajudas. São 384 níveis, e não 400, porque tutoriais e reforços só têm um tabuleiro. Há também uma dificuldade adaptativa, que oferece uma variante mais fácil ou mais difícil conforme o desempenho de quem joga.

Os pesos que usei para medir a dificuldade, os limites da adaptação e a ordem dos níveis são palpites meus. Joguei no iPhone, mas ainda não pedi a outras pessoas que jogassem para ver se a ordem faz sentido, e isso está na lista do que falta.

![[assets/8dfc092b-shihtzudoku-trilhas.png]]
*O mapa de trilhas do primeiro mundo, o Quintal, com os níveis, as estrelas e os chefes dos níveis 10 e 20.*

### O jogo em si

Depois do cérebro, vieram as telas e as mecânicas:

- **Gestos.** Um toque marca uma patinha, que significa "aqui não tem cachorro". Dois toques seguidos colocam o cachorro. Arrastar o dedo marca várias casas de uma vez. Esse esquema foi pedido por mim depois de jogar no iPhone.
- **Desfazer, cronômetro e vidas.** Há um modo em que cada cachorro no lugar errado custa um ossinho de três.
- **Desafio diário.** Todos os dias há um tabuleiro novo, igual para todos os jogadores, e o jogo conta quantos dias seguidos a pessoa jogou.
- **Estrelas e presentes.** Cada nível rende estrelas, e dominar um mundo inteiro abre um presente.
- **Tutorial.** Na primeira vez que abre o jogo, um tabuleiro 4×4 mostra os gestos e as regras em oito passos, com uma mãozinha apontando onde tocar.
- **Pontuação.** Cada nível vale até 10 pontos. Acertos seguidos rendem elogios como "Nice", que agora também são falados.
- **Sons.** Os efeitos e as vozes dos elogios são gravações reais, geradas por mim com uma ferramenta de voz do Google. Ouvi todos no jogo e aprovei.
- **Idiomas.** Português, espanhol e inglês.

![[assets/af2e0204-shihtzudoku-tutorial-passo-3.png]]
*O tutorial usa o tabuleiro de verdade, escurecido, com só as casas do passo acesas.*

![[assets/d482a0b4-shihtzudoku-pontuacao-elogios.png]]
*Os elogios "Nice" e "Clear" aparecem sobre o tabuleiro. Esta captura é da primeira versão da pontuação, antes do limite de 10 pontos por nível.*

### Acessibilidade e aparência

O jogo tem três cenários (Aconchego, Noite e Alto contraste), quatro cores de pelagem para o cachorro e um modo para quem tem daltonismo. Nesse modo, cada região ganha um desenho de linhas, além da cor, para que dê para distingui-las sem depender dela.

![[assets/91277a8b-shihtzudoku-cenario-noite.png]]
*O cenário Noite com o modo daltônico ligado. Os cachorros com moldura vermelha estão em conflito.*

### Ranking, conta e prêmios

Cada jogador recebe um identificador anônimo na primeira abertura, sem precisar cadastrar nada. Com ele, o jogo oferece:

- **Ranking diário.** Mostra o pódio, a tabela e a posição de quem joga. Recomeça à meia-noite de Brasília.
- **Evolução guardada na nuvem.** Se a pessoa reinstalar o jogo, o progresso volta.
- **Conta opcional.** Quem quiser pode ligar uma conta Apple ou Google ao identificador, e a evolução acompanha a pessoa ao trocar de aparelho. Também dá para excluir a conta pelo próprio jogo.
- **Prêmios.** Quem completa uma semana seguida ganha um presente sorteado, como uma moldura de avatar ou ajudas extras. Os três primeiros do ranking do dia também ganham um prêmio, entregue por um programa que roda no servidor à meia-noite. No iPhone, ele rodou sozinho e o prêmio chegou.

Tomei uma decisão aqui que tem um custo. Não coloquei um teto de pontos por dia. Isso significa que alguém com conhecimento técnico poderia adulterar o aplicativo e mandar uma pontuação absurda. Registrei essa consequência e deixei aberta a possibilidade de proteger melhor mais adiante. Cheguei a implementar uma proteção do servidor contra apps adulterados, mas não consegui provar que ela funcionava no iPhone, então a removi em vez de deixar uma defesa que eu não sei se existe.

O ranking também tem um filtro de apelidos ofensivos em português, inglês e espanhol. Ele roda só dentro do app, e um app adulterado o contorna. Decidi aceitar isso no lançamento porque o ranking é pequeno e público, e um nome ofensivo eu removo pelo painel do servidor.

![[assets/465b75c9-shihtzudoku-fim-de-nivel-ranking.png]]
*A etapa de ranking ao fim de um nível. Mel, Pipoca e Thor são jogadores de exemplo usados na captura. Não são pessoas reais.*

### Anúncios, compra e notificações

Esta é a parte com mais itens prontos no código e menos itens provados na prática:

- **Anúncios.** Só aparecem depois que o jogador dá consentimento. Há um anúncio a cada três níveis, um banner pequeno no rodapé da partida e dois vídeos opcionais, que o jogador escolhe assistir para restaurar a sequência ou ganhar uma ajuda. Só vi anúncios de teste. Os anúncios reais, que valem para quem baixa o jogo na loja, eu ainda não conferi.
- **Versão paga.** O Premium é uma compra única, sem assinatura, que tira os anúncios e renova as ajudas todo dia, até 10 de cada. Antes eu tinha pensado em ajudas ilimitadas e mudei: o Premium passou a ter um saldo como o dos outros jogadores, e o servidor decide a renovação. O preço é US$ 2,99 nas duas lojas. A compra não exige conta, porque pertence ao Apple ID ou à conta Google, e o botão "Restaurar compras" devolve o Premium depois de uma reinstalação. No iPhone, numa versão de release, a compra de teste da Apple (o chamado Sandbox) funcionou e o Restaurar também. No Android, ainda não fiz nenhuma compra.
- **Notificações.** O jogo pode lembrar do desafio do dia, avisar que a sequência está em risco e que um presente está esperando. Os testes automáticos passam, mas ainda não vi uma notificação de verdade chegando num celular.
- **Dados de uso.** O jogo conta eventos simples, como "nível resolvido", sem nome nem e-mail, e o jogador pode desligar isso nas configurações. Já vi um erro de teste chegando ao painel, mas ainda não conferi os eventos de uso.

## O que deu errado

Alguns erros foram da IA, outros foram meus, e vários só apareceram no celular de verdade. Quatro mostram bem o que aprendi:

**Uma tela branca com a causa errada.** Num celular Android, o jogo abria numa tela totalmente branca. O Claude Code concluiu que o culpado era o motor gráfico e desligou uma função por causa disso. Ele chegou a anotar que era só um palpite, porque não tinha lido o registro de erros. Estava errado. O que estava instalado no telefone era uma versão de teste, que não abre o jogo de verdade. Instalado o jogo certo, tudo funcionou com o motor gráfico ligado. Desfiz a mudança e guardei o registro desse erro. Agora, antes de culpar uma peça complicada, confiro se o que está no aparelho é a versão certa.

**Testes que passam sem testar.** Num dos ajustes, a IA gravou por engano o conteúdo de um arquivo de teste dentro de outro. A contagem de "153 testes passando" daquele momento incluía 13 repetidos e nenhum teste dos temas visuais. Quem percebeu foi uma verificação em que se estraga o código de propósito para ver se algum teste reclama: dez de onze estragos passaram sem ninguém notar. Refizemos o arquivo e depois todos foram detectados. Um teste que passa não prova que ele verifica o que você imagina.

**O ambiente de teste não é o ambiente real.** O simulador do servidor de ranking não confere um tipo de configuração que o servidor de verdade exige. Por isso, a tela de prêmios passou em todos os testes e, no celular, o botão não aparecia. O erro só foi achado com o servidor real. Outras falhas apareceram da mesma forma: um emoji de ossinho que virou um quadrado com interrogação no iPhone, e configurações de quem reinstalava o jogo sobrescritas pelos valores padrão. Por causa disso, mantenho para cada etapa concluída uma lista do que ainda precisa ser visto num aparelho ou numa loja de verdade.

**O app de release que caía ao abrir.** A versão de teste do Android funcionava, mas a versão que vai para a loja fechava antes da primeira tela. O registro de erros mostrou que o processo que compacta o código para a loja renomeava uma peça que o banco de dados interno do app procura pelo nome. Depois que adicionei uma regra para ela não ser renomeada, o app passou a abrir. A lição é que a versão de teste e a versão da loja não são o mesmo programa, e só a segunda chega ao jogador.

## Publicar nas lojas

Esta parte foi diferente das outras. Quase nada era código. Era preencher formulários, criar produtos, gerar imagens no tamanho exato e esperar respostas. Parte dos formulários da App Store eu deixei o Claude Code preencher no meu navegador, e eu conferia o resultado.

![[assets/167aedce-shihtzudoku-icone.png]]
*O ícone que vai para as duas lojas, desenhado em código com o mesmo rosto que o jogo desenha.*

O que deu certo foi a lista de verificação que o jogo mesmo cobra. Escrevi um script de build que se recusa a compilar se encontrar uma chave de compra de teste, um bloco de anúncio de teste ou uma chave ausente. Assim, não corro o risco de publicar uma versão com anúncios falsos ou sem a compra funcionando. Testei as recusas com configurações falsas, e o script as barrou.

O que deu errado foi uma lista de pequenos erros, e vale contar alguns:

- **Preço cem vezes maior.** No Play Console em português, digitei "2.99" e ele entendeu 299, porque o ponto é separador de milhar. Vi a tabela mostrando US$ 358,80 num país e corrigi para "2,99" antes de ativar. Nenhum preço errado chegou a valer.
- **Imagens do tamanho errado.** A Apple recusou as seis imagens de cada idioma porque o painel da minha conta só aceitava 1206×2622. Refiz as 18. No Google Play, as imagens do iPhone também não serviram, por causa da proporção, e tive que tirar novas num Android.
- **Cliques no idioma errado.** Duas vezes o Claude Code clicou num menu de idiomas e adicionou Bengalês sem querer. Removeu na hora, sem salvar. Depois disso, passou a conferir o idioma ativo antes de escrever qualquer campo.
- **Uma extensão do navegador que preenche sozinha.** Ela colocou meu e-mail num campo opcional da Apple e trocou o nome do produto "Premium" no Google por outro texto. Corrigimos os dois antes de salvar, mas só porque conferimos depois de cada campo.
- **Uma versão grátis que não ficou.** Em certo momento, escondi o Premium no código para publicar uma primeira versão sem compra. Decidi manter o Premium, porque eu já tinha preenchido tudo na Apple, e desfiz a mudança. Perdi um tempo com isso.

A lição que fica é que o assistente ajuda a preencher, mas quem decide e quem confere sou eu. Contato de revisão, preço e direitos de conteúdo são campos meus, e eu não delego.

## O que falta

- Esperar a resposta da Apple sobre a versão para iPhone.
- Fazer uma compra de teste de verdade e o login com Google no Android, e ver uma notificação chegando num iPhone e num Android.
- Conferir os anúncios reais e a renovação diária das ajudas, que só dá para provar com o jogo publicado.
- Chamar pessoas para jogar e calibrar a dificuldade dos níveis e a adaptação.
- Trocar as imagens provisórias do catálogo (molduras e avatares) por arte final.
- Aproveitar a base para construir um segundo puzzle, para ver se a arquitetura que montei realmente serve para mais de um jogo. Hoje é só uma aposta.

## O que levo disso até agora

Alguns pontos que valem para quem quiser trabalhar com uma IA de programação:

1. Peça o plano antes do código e leia antes de aprovar.
2. Exija que a IA registre o que fez e o que não conseguiu testar.
3. Desconfie de testes que passam de primeira. Pergunte qual deles falharia se o código estivesse errado.
4. Teste no aparelho e no servidor de verdade. Boa parte dos erros reais só aparece lá, e a versão de teste não é a versão da loja.
5. Anote por que cada decisão foi tomada e o que ela deixou sem resolver.
6. Faça o próprio processo recusar o erro previsível. Um script que não compila com chave de teste vale mais do que lembrar de conferir.

## Onde me encontrar

- Jogo no [Google Play](https://play.google.com/store/apps/details?id=com.thyagoluciano.shihtzudoku). Na App Store, em breve.
- Eu no [LinkedIn](https://www.linkedin.com/in/thyagoluciano/), onde conto o que estou aprendendo ao construir com IA.
