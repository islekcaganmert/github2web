# github2web

Turn docs hosted on a GitHub repo into a website.

### How to Setup?

```bash
python3 -m venv .venv
. ./.venv/bin/activate
pymake restore
export REPO='username/repo'
export ICON='https://example.com/favicon.png'
```

### How to Run?

```bash
pymake serve :8000 --app app
```