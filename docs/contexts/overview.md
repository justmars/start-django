# Overview

I find myself learning various coding subcultures. I don't have a proper word for it so I'll just make one up for now. Consider the following project structure where :simple-django: technically should occupy a single `/src` folder.

```yaml title="github workflow, justfile, docs, env examples, container files" linenums="1" hl_lines="10"
<root>
├── .github/workflows/main.yml # ci
├── .vscode/ # configures mkdocs, ruff, pytest, etc., file associations
├── .venv/ # local virtual environment
├── deploy/ # dockerfiles, fly.toml, env.fly.tpl
    ├── sq/ # config: sqlite
    ├── pg/ # config: postgres
├── docs/ # material for mkdocs
├── etc/ # example env variables
├── src/ # this is django, everything else has its place
├── justfile # shortcut recipes like 'just start'
├── pyproject.toml # poetry-driven
├── tailwind.config.js # sets up locations to watch, theme variables
├── .env
```

Context | Focus
--:|:--
[local](./local.md) | `.venv`, `/src` + `tailwind.config.js`
[ide](./ide.md) | `.vscode/`
[repl](./repl.md) | tooling from `python manage.py shell_plus`, Jupyter extension, etc.
[repo](./repo.md) | see `.github/workflows/main.yml`
[container](./container.md) | see `/deploy`
[site](./site.md) | see `/deploy`
