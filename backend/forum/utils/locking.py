from fcntl import LOCK_EX, LOCK_UN, flock
from os import statvfs
from pathlib import Path

from django.conf import settings

settings.FORUM_LOCKROOT_PATH.mkdir(exist_ok=True)
PATH_TEMPLOCK_CONTEXT = Path(settings.FORUM_LOCKROOT_PATH, 'temp-context-lock')
PATH_TEMPLOCK_CONTEXT.touch(exist_ok=True)
PATH_TEMPLOCK_DIR = Path(settings.FORUM_LOCKROOT_PATH, 'temp-locks')
PATH_TEMPLOCK_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILENAME_SIZE = statvfs(path=PATH_TEMPLOCK_DIR).f_namemax


class ContextLock(object):
    """
    A context-using file locker. HEADS UP: man 2 flock:

    Locks are on files, not file descriptors.  That is, file descriptors
    duplicated through dup(2) or fork(2) do not result in multiple
    instances of a lock, but rather multiple references to a single
    lock. If a process holding a lock on a file forks and the child
    explicitly unlocks the file, the parent will lose its lock.

    Processes blocked awaiting a lock may be awakened by signals.
    """

    def __init__(self, path: Path, mode: str = 'w'):
        self.mode = mode
        if path:
            self.path = path

    def __enter__(self):
        'Enter the lock.'
        # Locks on NFS need a write-opened file
        self.file_descriptor = open(self.path, self.mode)
        flock(self.file_descriptor, LOCK_EX)
        return self.file_descriptor

    def __exit__(self, exc_type, exc_value, traceback):
        'Exit the lock.'
        flock(self.file_descriptor, LOCK_UN)
        self.file_descriptor.close()


class TempLock(object):
    """
    A lock that will create the lock file for itself, in a thread-safe
    manner.
    """
    _is_acquired = False

    def __init__(self, name: str):
        name = Path(name).name
        self.path = PATH_TEMPLOCK_DIR.joinpath(name)

    def __enter__(self):
        'Enter the lock.'
        with ContextLock(path=PATH_TEMPLOCK_CONTEXT):
            self.path.touch(exist_ok=True)
        # Locks on NFS need a write-opened file
        self.file = open(self.path, 'w')
        flock(self.file, LOCK_EX)
        self._is_acquired = True

    def __exit__(self, exc_type, exc_value, traceback):
        'Exit the lock.'
        if not self._is_acquired:
            return
        flock(self.file, LOCK_UN)
        self.file.close()
        self._is_acquired = False

    acquire = __enter__

    def release(self):
        'Release the lock.'
        return self.__exit__(exc_type=None, exc_value=None, traceback=None)
