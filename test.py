import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

import git

import readmesfix
import util


TEST_REPO_ABSOLUTE_PATH = f'{os.getcwd()}/test-repo.git'


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    @property
    def text(self):
        return json.dumps(self.json_data)

    def json(self):
        return self.json_data

original_clone_from = git.Repo.clone_from


def mocked_clone(*args, **kwargs):
    if args[0] == "git@github.com:test-repo.git.git":
        new_args = list(args)
        new_args[0] = TEST_REPO_ABSOLUTE_PATH
    else:
        new_args = args
    return original_clone_from(*new_args, **kwargs)


# noinspection PyUnusedLocal
def mocked_post(url, *args, **kwargs):
    if url == 'https://api.github.com/repos/test-repo.git/forks':
        return MockResponse({
            'default_branch': 'master',
            'ssh_url': TEST_REPO_ABSOLUTE_PATH,
            'owner': {
                'login': 'bryant1410',
            },
        }, 202)
    elif url == 'https://api.github.com/repos/test-repo.git/pulls':
        return MockResponse({}, 201)
    else:
        assert False, "It shouldn't reach this point for the given test"


class MainTest(unittest.TestCase):
    @mock.patch('requests.post', side_effect=mocked_post)
    @mock.patch('git.Repo.clone_from', side_effect=mocked_clone)
    def test_main(self, mock_clone, mock_post):
        try:
            readmesfix.main('test.tsv')
            self.assertTrue(mock_clone.called)
            self.assertEqual(2, mock_post.call_count)
            with tempfile.TemporaryDirectory() as temp_dir, util.pushd(temp_dir):
                repo = git.Repo.clone_from(TEST_REPO_ABSOLUTE_PATH, '.')
                diff = subprocess.run(['git', 'diff', 'HEAD~'], check=True, stdout=subprocess.PIPE).stdout
                repo.git.reset('--hard', 'HEAD~')
                repo.remotes['origin'].push(force=True)
            with open('test.diff', 'rb') as gold_diff_file:
                self.assertEqual(gold_diff_file.read(), diff)
        finally:
            with util.pushd('test-repo.git'):
                subprocess.run('git -c gc.reflogExpire=0 -c gc.reflogExpireUnreachable=0 -c gc.rerereresolved=0 '
                               '-c gc.rerereunresolved=0 -c gc.pruneExpire=now gc "$@"', shell=True, check=True,
                               stdout=subprocess.PIPE)
