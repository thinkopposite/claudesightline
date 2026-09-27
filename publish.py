"""Publish this folder to a GitHub repo as one commit and switch on GitHub Pages.

    python publish.py OWNER/REPO "commit message"      (token in the GITHUB_TOKEN environment variable)

Token: a fine-grained personal access token limited to this one repository, with
Contents: read and write, and Pages: read and write. Python standard library only.
"""
import base64, json, os, sys, urllib.request, urllib.error

API = 'https://api.github.com'
SKIP = {'.git', '__pycache__', '.DS_Store'}


def call(method, path, token, body=None, ok=(200, 201)):
    req = urllib.request.Request(API + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                                          'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'sightline-publish'})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b'null')
    except urllib.error.HTTPError as e:
        data = e.read()
        if e.code in ok:
            return e.code, json.loads(data or b'null')
        return e.code, json.loads(data or b'null') if data[:1] in (b'{', b'[') else {'message': data.decode(errors='replace')}


def files(root):
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for n in names:
            if n in SKIP:
                continue
            p = os.path.join(d, n)
            yield os.path.relpath(p, root).replace(os.sep, '/'), p


def publish(repo, message, token, root='.'):
    st, info = call('GET', '/repos/%s' % repo, token)
    if st != 200:
        raise SystemExit('Cannot reach %s (%s): %s' % (repo, st, info.get('message')))
    branch = info.get('default_branch') or 'main'
    st, ref = call('GET', '/repos/%s/git/ref/heads/%s' % (repo, branch), token)
    if st != 200:                                    # empty repo: the Git Data API needs one commit first
        call('PUT', '/repos/%s/contents/.nojekyll' % repo, token, {'message': 'Start', 'content': '', 'branch': branch})
        st, ref = call('GET', '/repos/%s/git/ref/heads/%s' % (repo, branch), token)
        if st != 200:
            raise SystemExit('Could not start the repository: %s' % ref.get('message'))
    parent = ref['object']['sha']
    tree = []
    for rel, p in files(root):
        with open(p, 'rb') as f:
            st, blob = call('POST', '/repos/%s/git/blobs' % repo, token, {'content': base64.b64encode(f.read()).decode(), 'encoding': 'base64'})
        if st != 201:
            raise SystemExit('Upload failed for %s: %s' % (rel, blob.get('message')))
        tree.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    st, t = call('POST', '/repos/%s/git/trees' % repo, token, {'tree': tree})          # full tree: removed files disappear too
    st, c = call('POST', '/repos/%s/git/commits' % repo, token, {'message': message, 'tree': t['sha'], 'parents': [parent]})
    st, r = call('PATCH', '/repos/%s/git/refs/heads/%s' % (repo, branch), token, {'sha': c['sha']})
    if st != 200:
        raise SystemExit('Could not move %s to the new commit: %s' % (branch, r.get('message')))
    st, pg = call('GET', '/repos/%s/pages' % repo, token)
    if st == 404:
        st, pg = call('POST', '/repos/%s/pages' % repo, token, {'source': {'branch': branch, 'path': '/'}})
    url = (pg or {}).get('html_url') or 'https://%s.github.io/%s/' % tuple(repo.split('/'))
    print('Published %d files to %s@%s (%s)' % (len(tree), repo, branch, c['sha'][:7]))
    print('Pages:', url, '' if st in (200, 201) else '(switch on in Settings > Pages if this is the first publish: %s)' % (pg or {}).get('message'))


if __name__ == '__main__':
    if len(sys.argv) < 2 or not os.environ.get('GITHUB_TOKEN'):
        raise SystemExit(__doc__)
    publish(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'Update Sightline', os.environ['GITHUB_TOKEN'],
            os.path.dirname(os.path.abspath(__file__)))
