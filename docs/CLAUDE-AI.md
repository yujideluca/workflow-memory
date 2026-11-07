# claude.ai Settings text

Paste this once into claude.ai, Settings, preferences. Nobody but Giovanni can write that field, so it is a
pointer: the content lives in `views/BRIEF.md`, which a GitHub Action regenerates.

```
No início de cada conversa, carregue as ferramentas do GitHub (get_file_contents, create_branch,
create_or_update_file) e leia o arquivo views/BRIEF.md do repositório yujideluca/workflow-memory (branch
main). Siga as preferências ali e use as instruções do fim do arquivo para registrar correções e
preferências duradouras. Se não conseguir ler o arquivo, siga ao menos estas três regras: responda no idioma
da mensagem (português ou inglês); explique em linguagem simples e defina termos técnicos na primeira vez;
nunca guarde dados clínicos, segredos ou contatos de terceiros.
```

Notes
- It replaces the line that makes chats read `code/CORE.md` in the old repository.
- The connector's tools are deferred in the app and must be loaded by name; the text says so.
- Tested on the phone app (plain chat and project chat): read, create branch, create file and re-read all worked.
  Not tested in the browser.
