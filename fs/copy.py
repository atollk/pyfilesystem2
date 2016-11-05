from __future__ import print_function
from __future__ import unicode_literals

from . import walk
from .opener import manage_fs
from .path import abspath
from .path import combine
from .path import frombase
from .path import normpath


def copy_fs(src_fs, dst_fs):
    """
    Copy the contents of one filesystem to another.

    :param src_fs: Source filesystem.
    :type src_fs: :type src_fs: FS URL or instance
    :param src_path: A path to a directory on ``src_fs``.
    :type src_path: str
    :param dst_fs: Destination filesystem.
    :type dst_fs: FS URL or instance

    """
    copy_dir(src_fs, '/', dst_fs, '/')


def copy_file(src_fs, src_path, dst_fs, dst_path):
    """
    Copy a file from one filesystem to another.

    :param src_fs: Source filesystem.
    :type src_fs: FS URL or instance
    :param src_path: Path to a file on ``src_fs``.
    :type src_path: str
    :param dst_fs: Destination filesystem.
    :type dst_fs: FS URL or instance
    :param dst_path: Path to a file on ``dst_fs``.
    :type dst_path: str

    """
    with manage_fs(src_fs, writeable=False) as src_fs:
        with manage_fs(dst_fs, create=True) as dst_fs:
            if src_fs is dst_fs:
                # Same filesystem, so we can do a potentially optimized copy
                src_fs.copy(src_path, dst_path)
            else:
                # Standard copy
                with src_fs.lock(), dst_fs.lock():
                    with src_fs.open(src_path, 'rb') as read_file:
                        # There may be an optimized copy available on dst_fs
                        dst_fs.setbin(dst_path, read_file)


def copy_structure(src_fs, dst_fs):
    """
    Copy directories (but not files) from ``src_fs`` to ``dst_fs``.

    :param src_fs: Source filesystem.
    :type src_fs: FS URL or instance
    :param dst_fs: Destination filesystem.
    :type dst_fs: FS URL or instance

    """
    with manage_fs(src_fs, writeable=False) as src_fs:
        with manage_fs(dst_fs, create=True) as dst_fs:
            with src_fs.lock(), dst_fs.lock():
                for dir_path in walk.walk_dirs(src_fs):
                    dst_fs.makedir(dir_path, recreate=True)


def copy_dir(src_fs, src_path, dst_fs, dst_path):
    """
    Copy a directory from one filesystem to another.

    :param src_fs: Source filesystem.
    :type src_fs: FS URL or instance
    :param src_path: A path to a directory on ``src_fs``.
    :type src_path: str
    :param dst_fs: Destination filesystem.
    :type dst_fs: FS URL or instance
    :param dst_path: A path to a directory on ``dst_fs``.

    """

    _src_path = abspath(normpath(src_path))
    _dst_path = abspath(normpath(dst_path))

    with manage_fs(src_fs, writeable=False) as src_fs:
        with manage_fs(dst_fs, create=True) as dst_fs:
            with src_fs.lock(), dst_fs.lock():
                dst_fs.makedir(_dst_path, recreate=True)
                for dir_path, dirs, files in walk.walk(src_fs, _src_path):
                    copy_path = combine(
                        _dst_path,
                        frombase(_src_path, dir_path)
                    )
                    for info in dirs:
                        dst_fs.makedir(
                            info.make_path(copy_path),
                            recreate=True
                        )
                    for info in files:
                        copy_file(
                            src_fs,
                            info.make_path(dir_path),
                            dst_fs,
                            info.make_path(copy_path)
                        )
