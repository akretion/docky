#!/usr/bin/env python3

from subprocess import run, PIPE
import shlex
import os
import logging


logging.basicConfig(format='{levelname}:{message}',
                    style='{',
                    level=logging.DEBUG)

DOCUMENT_FOLDER = 'doc'
API_DOCUMENT_FOLDER = '{}/{}'.format(DOCUMENT_FOLDER, 'api')
SOURCE = 'docky'
MASTER_BRANCH = 'master'
HTML_DIR = 'html'


def run_cmd(cmd, quiet=False):
    if not quiet:
        logging.info('command: {}'.format(cmd))

    # use shlex to keep quoted substrings
    result = run(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    stdout = result.stdout.strip().decode()
    stderr = result.stderr.strip().decode()

    if stdout and not quiet:
        logging.debug(stdout)

    if stderr and not quiet:
        logging.warning(stderr)

    return result.stdout.strip()

REPLACE_DOC = [
    ("Subcommands:",
    "============== ==========\nSubcommands:\n============== =========="),
    ("VALUE:str", "VALUE"),
    ("\ndocky build", "============== ==========\ndocky build")
    ]

def generate_cmd_doc():
    run_cmd('echo "{}" > docky.yml')
    data = run_cmd('docky --help-all')
    run_cmd('rm -rf doc/auto')
    run_cmd('mkdir doc/auto')
    cmd = open("doc/auto/cmd.rst", "w")
    cmd.write("Command Line\n=========================\n\n")
    data = data.decode()
    for replace in REPLACE_DOC:
        data = data.replace(*replace)
    for doc in data.split("\ndocky "):
        header, doc = doc.split("\n", 1)
        name = header.rsplit(' ', 1)[0]
        filename = name.replace(' ', '.')
        header = "\n".join([name, len(name) * "-"])
        cmd.write(header + "\n")
        cmd.write(doc + "\n\n")
    cmd.close()


def build_docstring_rst():
    run_cmd('sphinx-apidoc -o {} {}'.format(API_DOCUMENT_FOLDER, SOURCE))


def build_html():
    run_cmd('python setup.py build_sphinx -s {}'.format(DOCUMENT_FOLDER))


def clean_old_build():
    run_cmd('rm -rf build/sphinx/html {} {}'.format(API_DOCUMENT_FOLDER,
                                                    HTML_DIR))


def duplicate_old_html():
    url = get_repo_url().decode()
    run_cmd('git clone -b gh-pages {} {}'.format(url, HTML_DIR))
    run_cmd('rm -rf {html}/.git {html}/{br}'.format(html=HTML_DIR,
                                                    br=MASTER_BRANCH))


def get_git_tags():
    return run_cmd('git tag --contains').split()


def update_html():
    run_cmd('mv build/sphinx/html {}/{}'.format(HTML_DIR, MASTER_BRANCH))

    tags = get_git_tags()
    if tags:
        destination = tags[0].decode()
        run_cmd('rm -rf {}/{}'.format(HTML_DIR, destination))
        run_cmd('cp -r {html}/{br} {html}/{dst}'.format(html=HTML_DIR,
                                                        br=MASTER_BRANCH,
                                                        dst=destination))


def get_commit_message():
    return run_cmd('git log -1 --pretty="%s"')


def get_repo_url():
    result = run_cmd('git remote get-url origin')
    # older version of Git doesn't have 'get-ur' ...
    if not result:
        result = run_cmd('git remote -v').split()[1]
    return result


def commit_to_github():
    run_cmd('pip install -U ghp-import')
    if os.environ.get('TRAVIS', ''):
        run_cmd('git config --global user.name "Travis"')
        run_cmd('git config --global user.email bot+travis@akretion.com')
    msg = get_commit_message().decode()
    cmd = 'ghp-import -n -r origin -b gh-pages -m "{}" {}'.format(msg,
                                                                  HTML_DIR)
    run_cmd(cmd)

    url = get_repo_url().decode().lstrip('https://')
    gh_token = os.environ['GH_TOKEN']
    # Please set your GH_TOKEN as Travis CI
    cmd = 'git push -fq \
            https://{}@{} gh-pages:gh-pages'.format(gh_token,
                                                    url)
    run_cmd(cmd, quiet=True)


def main():
    clean_old_build()
    generate_cmd_doc()
    #build_docstring_rst()
    build_html()
    duplicate_old_html()
    update_html()
    commit_to_github()


if __name__ == '__main__':
    main()
