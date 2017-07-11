import json
import pathlib
import subprocess

import requests


url = 'https://api.github.com/repos/atom/atom/releases'


def installed(beta=False):
    if beta is False:
        cmd = 'atom'
    else:
        cmd = 'atom-beta'
    out = subprocess.Popen([cmd, '-v'], stdout=subprocess.PIPE).stdout
    lines = out.read().decode('utf-8').split('\n')
    _, ver = lines[0].split(':')
    return ver.strip()


def download_url(item):
    for asset in item['assets']:
        if 'amd64.deb' in asset['browser_download_url']:
            return asset['browser_download_url']


def download_file(url):
    print('Downloading {}'.format(url))
    local_file = pathlib.PurePath(url)
    local_file = "atom-{0}-{1}".format(url.split('/')[-2],
                                       url.split('/')[-1].replace('atom-', ''))
    local_file = pathlib.Path('/tmp', local_file)
    subprocess.run(['wget', url, '-O', local_file.as_posix()])
    print('Done')
    return local_file


def install(latest):
    url = download_url(latest)
    new_file = download_file(url)
    print('Installing')
    subprocess.run(['sudo', 'dpkg', '-i', new_file.as_posix()])
    print('Done')


def latest(installed, beta=False):
    r = requests.get(url)
    js = json.loads(r.text)
    for release in js:
        latest_version = release['name']
        if beta and 'beta' not in latest_version:
            continue
        if not beta and 'beta' in latest_version:
            continue
        if latest_version != installed:
            print(latest_version, '>', installed)
            install(release)
            return
        else:
            print(latest_version, '==', installed)
            return


def update(beta=False):
    latest(installed(beta), beta)


if __name__ == '__main__':
    update()
    update(beta=True)
