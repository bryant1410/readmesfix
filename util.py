import contextlib
import os


@contextlib.contextmanager
def pushd(new_dir):
    """Runs a pushd in new_dir, always returning to the previous dir after finishing.
    
    From: http://stackoverflow.com/a/13847807/1165181"""
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)