import fcntl
import logging
import os
from contextlib import contextmanager

from theano import config

_logger = logging.getLogger(__name__)
# If the user provided a logging level, we don't want to override it.
if _logger.level == logging.NOTSET:
    # INFO will show the "Refreshing lock" messages
    _logger.setLevel(logging.INFO)


@contextmanager
def lock_ctx(lock_dir=None, keep_lock=False, **kw):
    if lock_dir is None:
        lock_dir = config.compiledir
    with open(os.path.join(lock_dir, '.theano_lock'), 'w') as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        yield
        if not keep_lock:
            fcntl.lockf(f, fcntl.LOCK_UN)


def get_lock(lock_dir=None, **kw):
    if lock_dir is None:
        lock_dir = config.compiledir
    f = open(os.path.join(lock_dir, '.theano_lock'), 'w')
    fcntl.lockf(f, fcntl.LOCK_EX)
    assert not getattr(get_lock, 'f', None)
    get_lock.f = f


def release_lock():
    assert get_lock.f
    f = get_lock.f
    fcntl.lockf(f, fcntl.LOCK_UN)
    f.close()
    del get_lock.f
