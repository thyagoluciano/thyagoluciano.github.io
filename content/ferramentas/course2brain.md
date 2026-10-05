---
title: Course2Brain
description: Extensão de Chrome e motor local que transformam aulas de cursos online em notas conectadas no Obsidian.
capa: static/ferramentas/capas/course2brain.jpg
date: '2026-10-05'
tags:
- ia
- obsidian
- ferramentas
publish: true
---

Criei o Course2Brain para parar de assistir aula só para esquecer depois. Com um clique no navegador, ele pega o conteúdo da aula, transforma em uma nota de estudo no formato de Segundo Cérebro e liga essa nota às que você já tem no Obsidian. É o que uso no fluxo descrito em [[posts/course2brain-transformando-cursos-online-em-notas-conectadas-no-obsidian|Transformando cursos online em notas conectadas no Obsidian]].

<p><a class="external" href="https://github.com/thyagoluciano/course2brain"><strong>Ver o código no GitHub</strong></a></p>

![[assets/8ea54e6e-Pasted-image-20260930154340.png]]

Diferente das outras ferramentas desta seção, o Course2Brain não roda só no navegador. Ele tem duas partes que você instala no seu computador: uma extensão do Chrome e um motor local em Python.

## O que ele faz

- **Captura a aula:** a extensão detecta a plataforma e extrai título, legendas, anotações e links de referência.
- **Limpa as legendas:** converte WebVTT e SRT em parágrafos legíveis.
- **Gera a nota:** resumo executivo, conceitos centrais com seus trade-offs, checklist prático e perguntas de revisão ativa.
- **Organiza o vault:** salva em `10-Cursos/<Curso>/<Aula>.md` e mantém o índice do curso atualizado.
- **Conecta as notas:** busca por similaridade semântica e validação por IA para inserir links bidirecionais na seção `Conexões Relacionadas`, entre cursos, artigos e conceitos.
- **Cria o vault:** o comando `c2b init-vault` monta pastas, modelos de nota e cores do Graph View.

O popup da extensão mostra a plataforma e a aula detectadas, o estado do servidor local e o botão que dispara a síntese.

![[assets/e2f102aa-Pasted-image-20260930154453.png]]

## Plataformas e modelos

A extensão tem extratores para Circle.so, Udacity e Skilljar. Cada plataforma é um arquivo separado, então adicionar outra é uma contribuição pequena.

A síntese funciona com Google Gemini, OpenRouter (inclusive os modelos gratuitos), OpenAI, Grok ou Ollama rodando local. Dá para usar um modelo para escrever as notas e outro para validar as conexões.

## Como instalar

Você precisa de Python 3.11 ou mais novo, Obsidian, Chrome e a chave de API do provedor de IA que escolher.

1. Clone o repositório e instale com `uv pip install -e ".[dev]"`.
2. Crie o vault com `c2b init-vault ~/Obsidian/SecondBrain`.
3. Copie `c2b.example.toml` para `c2b.toml` e informe provedor, modelo e chave.
4. Em `chrome://extensions`, ative o modo desenvolvedor e carregue a pasta `extension/`.
5. Rode `c2b serve` e use o botão da extensão na página da aula.

O passo a passo completo, com exemplos de configuração, está no [README do projeto](https://github.com/thyagoluciano/course2brain).

## Privacidade

O motor roda na sua máquina e as notas ficam no seu vault. O que sai do computador é o texto da aula, enviado ao provedor de IA que você configurou, e vale a política dele. Com Ollama, nada sai.

O código público não baixa vídeos nem contorna proteção de conteúdo. Automações privadas, como guardar mídia em um disco externo, entram como plugins locais na pasta `plugins/`, que o Git ignora.

## Código aberto

Licença MIT. Se uma plataforma que você usa não está na lista, abra um pull request com um novo extrator.
