from flask import Flask, request
import requests
import os

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path) -> str:
    path = path.removeprefix('/')
    if path.startswith(f"{os.environ['REPO']}/blob/main/"):
        path = path.removeprefix(f"{os.environ['REPO']}/blob/main/")
    resp = requests.get(
        f"https://github.com/{os.environ['REPO']}/blob/main/{path}",
        headers={
            'User-Agent': request.headers.get('User-Agent'),
            'Accept': 'text/html'
        }
    )
    if resp.status_code == 404:
        return resp.text
    elif resp.status_code != 200:
        return f"Error: {resp.status_code}"
    content = resp.text
    html_args = content.split('<html')[1].split('>')[0]
    body = content.split('<body')[1].split('</body>')[0]
    body_args = body.split('>')[0]
    body = body.removeprefix(body_args + '>')
    body = body.replace(f"/{os.environ['REPO']}/blob/main/", '/')
    head = content.split('<head>')[1].split('</head>')[0]
    head += '''
<style>
    body {
        padding: 10px;
    }
</style>
    '''
    head_wo_title = head.split('<title>')[0] + head.split('</title>')[1]
    try:
        title = body.split('class="heading-element"')[1].split('>')[1].split('<')[0]
    except IndexError:
        title = path.split('/')[-1]
    return f"""
<!DOCTYPE html>
<html {html_args}>
    <head>
        {head_wo_title}
        <title>{title}</title>
    </head>
    <body {body_args}>
        {body}
        <script>
            document.body.innerHTML = document.getElementsByClassName('js-snippet-clipboard-copy-unpositioned')[0].innerHTML;
        </script>
    </body>
</html>
    """


if __name__ == '__main__':
    app.run(debug=True)
