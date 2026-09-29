# Site thyagoluciano.com.br

Site estático (Quartz v4) gerado a partir das notas públicas do vault Obsidian "SecondBrain".

- Requisitos: `specs/PRD.md`. Especificação técnica: `specs/SPEC.md` (fonte da verdade). A pasta `docs/` pertence ao Quartz.
- Tema visual: `specs/SPEC-TEMA-CHIRPY.md` (implementado, marcos T0 a T4). Vale no lugar da seção 9 da SPEC e do layout do M4.
- Implemente um marco por vez (SPEC seção 13) e pare ao final de cada um para revisão.
- **Privacidade acima de tudo:** nada sai do vault sem passar pelo exportador e pela auditoria. Nunca desative o filtro `ExplicitPublish` nem a auditoria para "fazer passar".
- **O vault é somente leitura.** Durante o desenvolvimento, use `tools/tests/fixtures/vault/`. Só exporte do vault real quando eu pedir.
- Personalize o Quartz só nos arquivos listados na SPEC seção 3, item 4, para manter `npx quartz update` funcionando.
- Não faça `git push` nem mude configurações do GitHub ou DNS sem eu confirmar.
- Interface, textos e mensagens em português do Brasil.
