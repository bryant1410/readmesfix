#!/usr/bin/env python
import argparse
import csv
import fileinput
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import traceback

import git
import requests
import tqdm

import util

ENV_VAR_NAME = 'GITHUB_ACCESS_TOKEN'
if ENV_VAR_NAME not in os.environ:
    sys.exit(f"Error: you need to setup {ENV_VAR_NAME} env var to run this script.")
AUTH_PARAMS = {'access_token': os.environ[ENV_VAR_NAME]}

HEADING_WITHOUT_SPACE_RE = re.compile(r'^(#+)([^\s#])(.*?)(#+)?$')

CODE_BLOCK_FENCE = re.compile(r'^```')

inside_code_block = False


def detect_code_block_fence(match):
    global inside_code_block
    inside_code_block = not inside_code_block
    return match.group(0)


def heading_fix(match):
    global inside_code_block
    if inside_code_block:
        return match.group(0)
    elif match.group(4):
        return f'{match.group(1)} {match.group(2)}{match.group(3)} {match.group(4)}'
    else:
        return f'{match.group(1)} {match.group(2)}{match.group(3)}'


def crlf_paths(paths):
    paths_with_crlf = set()
    for path in paths:
        if 'CRLF' in subprocess.run(['file', path], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8'):
            paths_with_crlf.add(path)
    return paths_with_crlf


def insensitive_glob(pattern, *, recursive=False):
    """From: http://stackoverflow.com/a/10886685/1165181"""
    def either(char):
        return f'[{char.lower()}{char.upper()}]' if char.isalpha() else char
    return glob.glob(''.join(either(char) for char in pattern), recursive=recursive)


def create_pr(repo_name, base_branch, branch_name):
    params = {
        'title': f"Fix broken headings in Markdown files",
        'head': branch_name,
        'base': base_branch,
        'body': textwrap.dedent("""\
            GitHub changed the way Markdown headings are parsed, so this change fixes it.
            
            See [bryant1410/readmesfix](https://github.com/bryant1410/readmesfix) for more information.
            
            Tackles bryant1410/readmesfix#1
            """),
    }

    pull_request_endpoint = f"https://api.github.com/repos/{repo_name}/pulls"
    response = requests.post(pull_request_endpoint, json=params, params=AUTH_PARAMS)
    response_dict = json.loads(response.text)
    if response.status_code != 201:
        print(f"There was an error creating the PR of {repo_name}: {response_dict}")


def main(dataset_path):
    global inside_code_block

    with open(dataset_path) as file:
        number_of_lines = sum(1 for _ in file)
        file.seek(0)

        for (repo_name,) in tqdm.tqdm(csv.reader(file), total=number_of_lines):
            with tempfile.TemporaryDirectory() as temp_dir, util.pushd(temp_dir):
                # noinspection PyBroadException
                try:
                    repo = git.Repo.clone_from(f'git@github.com:{repo_name}.git', '.', depth=1, origin='upstream')
                    markdown_paths = set(insensitive_glob('**/*.md', recursive=True)) \
                        | set(insensitive_glob('**/*.mkdn?', recursive=True)) \
                        | set(insensitive_glob('**/*.mdown', recursive=True)) \
                        | set(insensitive_glob('**/*.markdown', recursive=True))
                    markdown_paths = {path for path in markdown_paths if os.path.isfile(path)}
                    if markdown_paths:  # Gets stuck otherwise
                        paths_with_crlf = crlf_paths(markdown_paths)
                        with fileinput.input(markdown_paths, inplace=True) as markdown_file:
                            use_crlf = False
                            for line in markdown_file:
                                if fileinput.isfirstline():
                                    inside_code_block = False
                                    use_crlf = markdown_file.filename() in paths_with_crlf
                                if use_crlf:
                                    line = line[:-1] + '\r\n'
                                CODE_BLOCK_FENCE.sub(detect_code_block_fence, line)
                                print(HEADING_WITHOUT_SPACE_RE.sub(heading_fix, line), end='')

                        if repo.index.diff(None):
                            repo.git.add('.')
                            repo.git.commit(m="Fix broken Markdown headings")

                            response = requests.post(f'https://api.github.com/repos/{repo_name}/forks',
                                                     params=AUTH_PARAMS)
                            response_dict = json.loads(response.text)
                            if response.status_code == 202:
                                repo.create_remote('origin', response_dict['ssh_url']).push()
                                create_pr(repo_name, response_dict["default_branch"],
                                          f'{response_dict["owner"]["login"]}:{response_dict["default_branch"]}')
                            else:
                                print(f"There was an error forking {repo_name}: {response_dict}")
                except Exception:
                    print(traceback.format_exc())

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--dataset', default='top_broken.tsv')
    args = arg_parser.parse_args()

    main(args.dataset)
