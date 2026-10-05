---
title: OmniDesk
description: Sincroniza a área de transferência e envia arquivos entre seus computadores e o celular pela rede local, sem nuvem e sem conta.
capa: static/ferramentas/capas/omnidesk.jpg
date: '2026-10-05'
tags:
- ferramentas
- produtividade
- open-source
publish: true
---

<p><img src="/static/ferramentas/capas/omnidesk.jpg" width="1200" height="630" alt="OmniDesk: painel no computador e aplicativo no celular" style="height:auto" /></p>

O OmniDesk leva texto e arquivos de um aparelho para outro sem passar pela internet. Você copia um texto em um aparelho e cola no outro, ou arrasta um arquivo para o dispositivo de destino. Tudo fica na sua rede Wi-Fi, direto de um aparelho para o outro.

A solução tem duas partes: o **OmniDesk**, para Linux, macOS e Windows, e o **OmniDesk Mobile**, para iOS e Android. As duas são de código aberto, com licença MIT.

<p><a class="external" href="https://github.com/thyagoluciano/OmniDesk"><strong>OmniDesk no GitHub</strong></a> · <a class="external" href="https://github.com/thyagoluciano/OmniDeskMobile"><strong>OmniDesk Mobile no GitHub</strong></a></p>

Como o Course2Brain, ele não roda no navegador: você instala no computador e no celular.

## O que ele faz

- **Clipboard sincronizado:** o texto, link ou trecho de código copiado em um aparelho pareado vai para os outros. Há proteção contra loop de cópia entre os aparelhos, e dá para ligar e desligar a sincronização a qualquer momento.
- **Envio de arquivos:** arraste e solte no painel, use o botão de envio ou o terminal. Do celular, dá para mandar fotos da galeria e documentos. Os arquivos recebidos no computador ficam em `Downloads/OmniDesk`.
- **Descoberta automática:** os aparelhos se encontram na rede por mDNS (Bonjour), sem digitar endereço IP.
- **Pareamento único:** entre computadores, com um PIN de 6 dígitos. Com o celular, lendo um QR Code que o painel mostra na tela.
- **Painel web e bandeja:** o painel abre em `http://127.0.0.1:24850/ui/` ou pelo ícone na bandeja do sistema, e há notificações nativas.
- **Linha de comando:** `omnidesk status`, `devices`, `pair` e `send` cobrem o uso sem interface gráfica.
- **Inicialização com o sistema:** sobe em segundo plano no login, sem precisar de administrador.

## No computador

O painel lista os dispositivos pareados e os que foram descobertos na rede, e tem uma página para a área de transferência, com o histórico de cópias, e outra para envio de arquivos.

![Dispositivos pareados e descobertos na rede](/static/ferramentas/omnidesk/desktop-dispositivos.png)

![Histórico da área de transferência](/static/ferramentas/omnidesk/desktop-area-de-transferencia.png)

![Envio de arquivos por arrastar e soltar](/static/ferramentas/omnidesk/desktop-arquivos.png)

## No celular

O aplicativo faz o pareamento pela câmera e, depois, envia clipboard, fotos e arquivos para o computador. A aba de transferências guarda o histórico do que foi enviado e recebido.

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;align-items:start">
<img src="/static/ferramentas/omnidesk/mobile-sem-pareamento.png" width="462" height="1000" alt="Tela inicial do aplicativo sem computador pareado, com o botão Escanear QR Code" loading="lazy" style="height:auto" />
<img src="/static/ferramentas/omnidesk/mobile-pareado.png" width="462" height="1000" alt="Aplicativo com um computador pareado e online, com os botões Enviar Clipboard, Fotos e Arquivos" loading="lazy" style="height:auto" />
<img src="/static/ferramentas/omnidesk/mobile-historico-textos.png" width="462" height="1000" alt="Histórico de transferências filtrado por textos enviados ao computador" loading="lazy" style="height:auto" />
<img src="/static/ferramentas/omnidesk/mobile-historico-fotos.png" width="462" height="1000" alt="Histórico de transferências filtrado por fotos enviadas ao computador, com o tamanho de cada uma" loading="lazy" style="height:auto" />
</div>

## Como instalar

**No computador**, baixe o instalador na [página de releases](https://github.com/thyagoluciano/OmniDesk/releases):

- **macOS:** `OmniDesk.dmg`, arrastando o app para Aplicativos.
- **Linux:** pacote `.deb`, ou `./omnidesk install` para instalar no seu usuário com serviço systemd.
- **Windows 10 e 11:** instalador `.exe`.

Para compilar do código-fonte, é preciso Go 1.22 ou mais novo.

**No celular**, o README do OmniDesk Mobile documenta a instalação compilando o código-fonte com Flutter, para iOS 15 ou mais novo e Android API 21 ou mais novo. Os passos estão no [README do projeto](https://github.com/thyagoluciano/OmniDeskMobile).

## Como parear

1. Deixe o computador e o celular na mesma rede Wi-Fi.
2. No painel do computador, clique em **Parear Celular (QR Code)**.
3. No aplicativo, toque em **Escanear QR Code** e aponte a câmera para a tela.
4. Pronto: clipboard e envio de arquivos funcionam nos dois sentidos.

Entre dois computadores, clique em **Parear** no primeiro e, no segundo, em **Aprovar PIN**, digitando o código de 6 dígitos que apareceu.

## Privacidade

Nada passa por servidor externo. Não há conta, rastreamento nem telemetria. O pareamento troca tokens criptográficos entre os aparelhos, e o aplicativo guarda as credenciais no Keychain do iOS ou no armazenamento criptografado do Android.

O OmniDesk Mobile pede só três permissões: câmera, para ler o QR Code; rede local, para encontrar o computador; e fotos, para escolher o que enviar.

## Código aberto

Licença MIT. Contribuições, issues e ideias são bem-vindas nos dois repositórios.
