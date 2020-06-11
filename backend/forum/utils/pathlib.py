from __future__ import annotations

from os import chown
from os import name as os_name
from os import umask
from pathlib import Path as PathBase
from pathlib import PosixPath as PosixPathBase
from pathlib import WindowsPath as WindowsPathBase
from threading import RLock
from typing import Optional, Union

_LOCK = RLock()


class Path(PathBase):
    'Extending the built-in `Path`.'

    def __new__(cls, *args, **kwargs):
        if cls is Path:
            cls = WindowsPath if os_name == 'nt' else PosixPath
        self = cls._from_parts(args, init=False)
        if not self._flavour.is_supported:
            raise NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        return self

    def _ensure_dirs_inner(
            self, relative_path: Path, mode: Optional[int] = None,
            uid: Optional[int] = None, gid: Optional[int] = None) -> Path:
        'Do the work for `ensure_dirs` while threadlocked or not.'
        new_path = self
        for part in relative_path.parts[:-1]:
            new_path = new_path.joinpath(part)
            if new_path.exists():
                continue
            new_path.mkdir()
            if uid is None and gid is None:
                continue
            chown(
                path=new_path, uid=-1 if uid is None else uid,
                gid=-1 if gid is None else gid)
        return new_path.joinpath(relative_path.parts[-1])

    def ensure_dirs(
            self, relative_path: Union[Path, str], mode: Optional[int] = None,
            uid: Optional[int] = None, gid: Optional[int] = None) -> Path:
        """
        Ensure the directories up until the last part (the file) in
        self, starting from `self`. If `mode`, `uid` and `gid` is
        passed, the ownership and modes will be set on the
        *newly created* directories. If you pass `mode`, `uid` and
        `gid`, make sure you can set the appropriate umask for `mode`
        and you can set the ownership for the passed `uid`/`gid`.

        Return the ensured `self`+`relative_path` for when done.
        """
        if type(relative_path) is str:
            relative_path = Path(relative_path)
        if not self.is_dir():
            raise ValueError(f'{self!r} must be a directory.')
        if mode is None:
            return self._ensure_dirs_inner(
                relative_path=relative_path, mode=mode, uid=uid, gid=gid)
        try:
            _LOCK.acquire()
            old_umask = umask(0o777 - mode)
            return self._ensure_dirs_inner(
                relative_path=relative_path, mode=mode, uid=uid, gid=gid)
        finally:
            umask(old_umask)
            _LOCK.release()

    def get_relative(self, to: Path) -> Path:
        """
        Calculate and return a relative path between `self` and `to`
        paths. Both paths must be absolute!
        """
        if not self.is_absolute() or not to.is_absolute():
            raise ValueError(f'{self!r} or {to!r} is not absolute.')
        items_from = self.parts
        items_to = to.parts
        # Remove identical path prefix parts
        while items_from[0] == items_to[0]:
            items_from = items_from[1:]
            items_to = items_to[1:]
        return Path(*('..' for x in range(1, len(items_from))), *items_to)


class WindowsPath(Path, WindowsPathBase):
    'Extending `WindowsPath`.'


class PosixPath(Path, PosixPathBase):
    'Extending `PosixPath`.'
