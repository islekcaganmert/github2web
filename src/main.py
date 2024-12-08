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
        aft = body.split('class="heading-element"')[1]
        aft = aft.removeprefix(aft.split('>')[0] + '>')
        if aft.startswith('<a'):
            title = aft.split('alt="')[1].split('"')[0]
        else:
            title = aft.split('<')[0]
    except IndexError as e:
        title = path.split('/')[-1]
    description = head_wo_title.split('<meta property="og:description" content="')[1].split('">')[0]
    description = description.removesuffix(description.split(' - ')[-1])
    for i in [
        '<meta name="description" content="',
        '<meta property="og',
        '<meta name="twitter',
        '<meta name="fb',
        '<meta name="hostname',
        '<meta name="expected-hostname',
        '<link rel="icon" '
        '<link rel="alternate icon'
    ]:
        while len(head_wo_title.split(i)) > 1:
            to_clean = head_wo_title.split(i)[1].split('>')[0]
            head_wo_title = head_wo_title.replace(f"{i}{to_clean}>", '')
    return f"""
<!DOCTYPE html>
<html {html_args}>
    <head>
        {head_wo_title}
        <title>{title}</title>
        <meta name="description" content="{description}">
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        <meta property="og:site_name" content="{title}">
        <link rel="icon" class="js-site-favicon" type="image/svg+xml" href="{os.environ.get('ICON')}">
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
