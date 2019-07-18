# (c) 2012-2016 Anaconda, Inc. / https://anaconda.com
# All Rights Reserved
#
# conda is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.
'''
We use the following conventions in this module:

    dist:        canonical package name, e.g. 'numpy-1.6.2-py26_0'

    ROOT_PREFIX: the prefix to the root environment, e.g. /opt/anaconda

    PKGS_DIR:    the "package cache directory", e.g. '/opt/anaconda/pkgs'
                 this is always equal to ROOT_PREFIX/pkgs

    prefix:      the prefix of a particular environment, which may also
                 be the root environment

Also, this module is directly invoked by the (self extracting) tarball
installer to create the initial environment, therefore it needs to be
standalone, i.e. not import any other parts of `conda` (only depend on
the standard library).
'''
import os
import re
import sys
import json
import shutil
import stat
from os.path import abspath, dirname, exists, isdir, isfile, islink, join
from optparse import OptionParser


on_win = bool(sys.platform == 'win32')
try:
    FORCE = bool(int(os.getenv('FORCE', 0)))
except ValueError:
    FORCE = False

LINK_HARD = 1
LINK_SOFT = 2  # never used during the install process
LINK_COPY = 3
link_name_map = {
    LINK_HARD: 'hard-link',
    LINK_SOFT: 'soft-link',
    LINK_COPY: 'copy',
}
SPECIAL_ASCII = '$!&\%^|{}[]<>~`"\':;?@*#'

# these may be changed in main()
ROOT_PREFIX = sys.prefix
PKGS_DIR = join(ROOT_PREFIX, 'pkgs')
SKIP_SCRIPTS = False
IDISTS = {
  "asn1crypto-0.24.0-py27_0": {
    "md5": "377e642ea2ec6fea824bca05b2f8187f",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/asn1crypto-0.24.0-py27_0.tar.bz2"
  },
  "ca-certificates-2019.1.23-0": {
    "md5": "f51beb89e3b35de34ff33a5e652adce4",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/ca-certificates-2019.1.23-0.tar.bz2"
  },
  "certifi-2019.3.9-py27_0": {
    "md5": "22a56dda65b4b49452cfe7089e4ec6f9",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/certifi-2019.3.9-py27_0.tar.bz2"
  },
  "cffi-1.12.2-py27hcfb25f9_1": {
    "md5": "4b3b0cb9b2f265fafa88ec22900d8164",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/cffi-1.12.2-py27hcfb25f9_1.tar.bz2"
  },
  "chardet-3.0.4-py27_1": {
    "md5": "39426f1e2f168772bb3de166f0178ef9",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/chardet-3.0.4-py27_1.tar.bz2"
  },
  "conda-4.6.14-py27_0": {
    "md5": "6daffd320663cdcc10f1380e4c73d550",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/conda-4.6.14-py27_0.tar.bz2"
  },
  "console_shortcut-0.1.1-3": {
    "md5": "aaad91749d7bb128bd51c0df273285e6",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/console_shortcut-0.1.1-3.tar.bz2"
  },
  "cryptography-2.6.1-py27hcfb25f9_0": {
    "md5": "e39e5e997cb1454e3a80035ff315f655",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/cryptography-2.6.1-py27hcfb25f9_0.tar.bz2"
  },
  "enum34-1.1.6-py27_1": {
    "md5": "6f0510cb8b664ff900cf589bcc6079a1",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/enum34-1.1.6-py27_1.tar.bz2"
  },
  "futures-3.2.0-py27_0": {
    "md5": "5913a3b0b246ef34c7a7b7b2b519d581",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/futures-3.2.0-py27_0.tar.bz2"
  },
  "idna-2.8-py27_0": {
    "md5": "05e810292b8b0daafd7f8285976ef68b",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/idna-2.8-py27_0.tar.bz2"
  },
  "ipaddress-1.0.22-py27_0": {
    "md5": "c82eeed9f805b12a9d94a0f1868b9f5e",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/ipaddress-1.0.22-py27_0.tar.bz2"
  },
  "menuinst-1.4.16-py27h0c8e037_0": {
    "md5": "6c51adce364c8ab388fac474e7c93f7b",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/menuinst-1.4.16-py27h0c8e037_0.tar.bz2"
  },
  "openssl-1.1.1b-h0c8e037_1": {
    "md5": "50541b0ac977628964c53741939191c3",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/openssl-1.1.1b-h0c8e037_1.tar.bz2"
  },
  "pip-19.0.3-py27_0": {
    "md5": "5e1e30ae30c69dccaa23233f5a884448",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/pip-19.0.3-py27_0.tar.bz2"
  },
  "powershell_shortcut-0.0.1-2": {
    "md5": "6f70b49b7c7ce51e3fdce9256f4fd83c",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/powershell_shortcut-0.0.1-2.tar.bz2"
  },
  "pycosat-0.6.3-py27h0c8e037_0": {
    "md5": "833b1ebe08763848155155de9d08c61f",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/pycosat-0.6.3-py27h0c8e037_0.tar.bz2"
  },
  "pycparser-2.19-py27_0": {
    "md5": "5f9f565c98e9fbe742a7c92ef3a5a1e6",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/pycparser-2.19-py27_0.tar.bz2"
  },
  "pyopenssl-19.0.0-py27_0": {
    "md5": "b846137d1aa39ec7ec1b9f336818356b",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/pyopenssl-19.0.0-py27_0.tar.bz2"
  },
  "pysocks-1.6.8-py27_0": {
    "md5": "6f702ee72946052d833e733b6fe766fa",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/pysocks-1.6.8-py27_0.tar.bz2"
  },
  "python-2.7.16-hcb6e200_0": {
    "md5": "3b019e009384b1c729a7254c6b9f21e3",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/python-2.7.16-hcb6e200_0.tar.bz2"
  },
  "pywin32-223-py27h0c8e037_1": {
    "md5": "d7cc278e03a80514e91a65846312058d",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/pywin32-223-py27h0c8e037_1.tar.bz2"
  },
  "requests-2.21.0-py27_0": {
    "md5": "7620882054a91097f9b00800a82bb2cc",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/requests-2.21.0-py27_0.tar.bz2"
  },
  "ruamel_yaml-0.15.46-py27h0c8e037_0": {
    "md5": "c818841c8b7dd7f43f39a7aa2ca4946f",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/ruamel_yaml-0.15.46-py27h0c8e037_0.tar.bz2"
  },
  "setuptools-41.0.0-py27_0": {
    "md5": "29aeedb685a389c9c9f56f5a58cb7ddc",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/setuptools-41.0.0-py27_0.tar.bz2"
  },
  "six-1.12.0-py27_0": {
    "md5": "e15e3ba11c172a6d982b62aef1059bb0",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/six-1.12.0-py27_0.tar.bz2"
  },
  "sqlite-3.27.2-h0c8e037_0": {
    "md5": "e16f51f5c3e9a4de43e85c61c03b69b5",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/sqlite-3.27.2-h0c8e037_0.tar.bz2"
  },
  "urllib3-1.24.1-py27_0": {
    "md5": "3be6c53fc2b68d9bc6cc405f1486a47a",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/urllib3-1.24.1-py27_0.tar.bz2"
  },
  "vc-9-h7299396_1": {
    "md5": "f2d6cc582005c00a970cb9975b894b45",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/vc-9-h7299396_1.tar.bz2"
  },
  "vs2008_runtime-9.00.30729.1-hfaea7d5_1": {
    "md5": "a821778449a95ff43d21bbb7d2f6794b",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/vs2008_runtime-9.00.30729.1-hfaea7d5_1.tar.bz2"
  },
  "wheel-0.33.1-py27_0": {
    "md5": "a81d9659b719d18aad46dbec233ed2cb",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/wheel-0.33.1-py27_0.tar.bz2"
  },
  "win_inet_pton-1.1.0-py27_0": {
    "md5": "0c5b6d9224e84b8c56859f1d7888d095",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/win_inet_pton-1.1.0-py27_0.tar.bz2"
  },
  "wincertstore-0.2-py27hf04cefb_0": {
    "md5": "f9e1c4824d9c34c53ece4f98d772eea1",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/wincertstore-0.2-py27hf04cefb_0.tar.bz2"
  },
  "yaml-0.1.7-h3e6d941_2": {
    "md5": "46a367eb27f7bc241481da1edc407286",
    "url": "https://repo.anaconda.com/pkgs/main/win-64/yaml-0.1.7-h3e6d941_2.tar.bz2"
  }
}
C_ENVS = {
  "root": [
    "python-2.7.16-hcb6e200_0",
    "ca-certificates-2019.1.23-0",
    "vs2008_runtime-9.00.30729.1-hfaea7d5_1",
    "vc-9-h7299396_1",
    "openssl-1.1.1b-h0c8e037_1",
    "sqlite-3.27.2-h0c8e037_0",
    "yaml-0.1.7-h3e6d941_2",
    "pywin32-223-py27h0c8e037_1",
    "menuinst-1.4.16-py27h0c8e037_0",
    "asn1crypto-0.24.0-py27_0",
    "certifi-2019.3.9-py27_0",
    "chardet-3.0.4-py27_1",
    "console_shortcut-0.1.1-3",
    "enum34-1.1.6-py27_1",
    "futures-3.2.0-py27_0",
    "idna-2.8-py27_0",
    "ipaddress-1.0.22-py27_0",
    "powershell_shortcut-0.0.1-2",
    "pycosat-0.6.3-py27h0c8e037_0",
    "pycparser-2.19-py27_0",
    "ruamel_yaml-0.15.46-py27h0c8e037_0",
    "six-1.12.0-py27_0",
    "win_inet_pton-1.1.0-py27_0",
    "wincertstore-0.2-py27hf04cefb_0",
    "cffi-1.12.2-py27hcfb25f9_1",
    "pysocks-1.6.8-py27_0",
    "setuptools-41.0.0-py27_0",
    "cryptography-2.6.1-py27hcfb25f9_0",
    "wheel-0.33.1-py27_0",
    "pip-19.0.3-py27_0",
    "pyopenssl-19.0.0-py27_0",
    "urllib3-1.24.1-py27_0",
    "requests-2.21.0-py27_0",
    "conda-4.6.14-py27_0"
  ]
}



def _link(src, dst, linktype=LINK_HARD):
    if linktype == LINK_HARD:
        if on_win:
            from ctypes import windll, wintypes
            CreateHardLink = windll.kernel32.CreateHardLinkW
            CreateHardLink.restype = wintypes.BOOL
            CreateHardLink.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR,
                                       wintypes.LPVOID]
            if not CreateHardLink(dst, src, None):
                raise OSError('win32 hard link failed')
        else:
            os.link(src, dst)
    elif linktype == LINK_COPY:
        # copy relative symlinks as symlinks
        if islink(src) and not os.readlink(src).startswith(os.path.sep):
            os.symlink(os.readlink(src), dst)
        else:
            shutil.copy2(src, dst)
    else:
        raise Exception("Did not expect linktype=%r" % linktype)


def rm_rf(path):
    """
    try to delete path, but never fail
    """
    try:
        if islink(path) or isfile(path):
            # Note that we have to check if the destination is a link because
            # exists('/path/to/dead-link') will return False, although
            # islink('/path/to/dead-link') is True.
            os.unlink(path)
        elif isdir(path):
            shutil.rmtree(path)
    except (OSError, IOError):
        pass


def yield_lines(path):
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        yield line


prefix_placeholder = ('/opt/anaconda1anaconda2'
                      # this is intentionally split into parts,
                      # such that running this program on itself
                      # will leave it unchanged
                      'anaconda3')

def read_has_prefix(path):
    """
    reads `has_prefix` file and return dict mapping filenames to
    tuples(placeholder, mode)
    """
    import shlex

    res = {}
    try:
        for line in yield_lines(path):
            try:
                parts = [x.strip('"\'') for x in shlex.split(line, posix=False)]
                # assumption: placeholder and mode will never have a space
                placeholder, mode, f = parts[0], parts[1], ' '.join(parts[2:])
                res[f] = (placeholder, mode)
            except (ValueError, IndexError):
                res[line] = (prefix_placeholder, 'text')
    except IOError:
        pass
    return res


def exp_backoff_fn(fn, *args):
    """
    for retrying file operations that fail on Windows due to virus scanners
    """
    if not on_win:
        return fn(*args)

    import time
    import errno
    max_tries = 6  # max total time = 6.4 sec
    for n in range(max_tries):
        try:
            result = fn(*args)
        except (OSError, IOError) as e:
            if e.errno in (errno.EPERM, errno.EACCES):
                if n == max_tries - 1:
                    raise Exception("max_tries=%d reached" % max_tries)
                time.sleep(0.1 * (2 ** n))
            else:
                raise e
        else:
            return result


class PaddingError(Exception):
    pass


def binary_replace(data, a, b):
    """
    Perform a binary replacement of `data`, where the placeholder `a` is
    replaced with `b` and the remaining string is padded with null characters.
    All input arguments are expected to be bytes objects.
    """
    def replace(match):
        occurances = match.group().count(a)
        padding = (len(a) - len(b)) * occurances
        if padding < 0:
            raise PaddingError(a, b, padding)
        return match.group().replace(a, b) + b'\0' * padding

    pat = re.compile(re.escape(a) + b'([^\0]*?)\0')
    res = pat.sub(replace, data)
    assert len(res) == len(data)
    return res


def update_prefix(path, new_prefix, placeholder, mode):
    if on_win:
        # force all prefix replacements to forward slashes to simplify need
        # to escape backslashes - replace with unix-style path separators
        new_prefix = new_prefix.replace('\\', '/')

    path = os.path.realpath(path)
    with open(path, 'rb') as fi:
        data = fi.read()
    if mode == 'text':
        new_data = data.replace(placeholder.encode('utf-8'),
                                new_prefix.encode('utf-8'))
    elif mode == 'binary':
        if on_win:
            # anaconda-verify will not allow binary placeholder on Windows.
            # However, since some packages might be created wrong (and a
            # binary placeholder would break the package, we just skip here.
            return
        new_data = binary_replace(data, placeholder.encode('utf-8'),
                                  new_prefix.encode('utf-8'))
    else:
        sys.exit("Invalid mode:" % mode)

    if new_data == data:
        return
    st = os.lstat(path)
    # unlink in case the file is memory mapped
    exp_backoff_fn(os.unlink, path)
    with open(path, 'wb') as fo:
        fo.write(new_data)
    os.chmod(path, stat.S_IMODE(st.st_mode))


def name_dist(dist):
    if hasattr(dist, 'name'):
        return dist.name
    else:
        return dist.rsplit('-', 2)[0]


def create_meta(prefix, dist, info_dir, extra_info):
    """
    Create the conda metadata, in a given prefix, for a given package.
    """
    # read info/repodata_record.json first
    with open(join(info_dir, 'repodata_record.json')) as fi:
        meta = json.load(fi)
    # add extra info
    meta.update(extra_info)
    # write into <prefix>/conda-meta/<dist>.json
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        os.makedirs(meta_dir)
    with open(join(meta_dir, dist + '.json'), 'w') as fo:
        json.dump(meta, fo, indent=2, sort_keys=True)


def run_script(prefix, dist, action='post-link'):
    """
    call the post-link (or pre-unlink) script, and return True on success,
    False on failure
    """
    path = join(prefix, 'Scripts' if on_win else 'bin', '.%s-%s.%s' % (
            name_dist(dist),
            action,
            'bat' if on_win else 'sh'))
    if not isfile(path):
        return True
    if SKIP_SCRIPTS:
        print("WARNING: skipping %s script by user request" % action)
        return True

    if on_win:
        cmd_exe = os.path.join(os.environ['SystemRoot'], 'System32', 'cmd.exe')
        if not os.path.isfile(cmd_exe):
            cmd_exe = os.path.join(os.environ['windir'], 'System32', 'cmd.exe')
        if not os.path.isfile(cmd_exe):
            print("Error: running %s failed.  cmd.exe could not be found.  "
                "Looked in SystemRoot and windir env vars.\n" % path)
            return False
        args = [cmd_exe, '/d', '/c', path]
    else:
        shell_path = '/bin/sh' if 'bsd' in sys.platform else '/bin/bash'
        args = [shell_path, path]

    env = os.environ
    env['PREFIX'] = prefix

    import subprocess
    try:
        subprocess.check_call(args, env=env)
    except subprocess.CalledProcessError:
        return False
    return True


url_pat = re.compile(r'''
(?P<baseurl>\S+/)                 # base URL
(?P<fn>[^\s#/]+)                  # filename
([#](?P<md5>[0-9a-f]{32}))?       # optional MD5
$                                 # EOL
''', re.VERBOSE)

def read_urls(dist):
    try:
        data = open(join(PKGS_DIR, 'urls')).read()
        for line in data.split()[::-1]:
            m = url_pat.match(line)
            if m is None:
                continue
            if m.group('fn') == '%s.tar.bz2' % dist:
                return {'url': m.group('baseurl') + m.group('fn'),
                        'md5': m.group('md5')}
    except IOError:
        pass
    return {}


def read_no_link(info_dir):
    res = set()
    for fn in 'no_link', 'no_softlink':
        try:
            res.update(set(yield_lines(join(info_dir, fn))))
        except IOError:
            pass
    return res


def linked(prefix):
    """
    Return the (set of canonical names) of linked packages in prefix.
    """
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        return set()
    return set(fn[:-5] for fn in os.listdir(meta_dir) if fn.endswith('.json'))


def link(prefix, dist, linktype=LINK_HARD, info_dir=None):
    '''
    Link a package in a specified prefix.  We assume that the packacge has
    been extra_info in either
      - <PKGS_DIR>/dist
      - <ROOT_PREFIX>/ (when the linktype is None)
    '''
    if linktype:
        source_dir = join(PKGS_DIR, dist)
        info_dir = join(source_dir, 'info')
        no_link = read_no_link(info_dir)
    else:
        info_dir = info_dir or join(prefix, 'info')

    files = list(yield_lines(join(info_dir, 'files')))
    # TODO: Use paths.json, if available or fall back to this method
    has_prefix_files = read_has_prefix(join(info_dir, 'has_prefix'))

    if linktype:
        for f in files:
            src = join(source_dir, f)
            dst = join(prefix, f)
            dst_dir = dirname(dst)
            if not isdir(dst_dir):
                os.makedirs(dst_dir)
            if exists(dst):
                if FORCE:
                    rm_rf(dst)
                else:
                    raise Exception("dst exists: %r" % dst)
            lt = linktype
            if f in has_prefix_files or f in no_link or islink(src):
                lt = LINK_COPY
            try:
                _link(src, dst, lt)
            except OSError:
                pass

    for f in sorted(has_prefix_files):
        placeholder, mode = has_prefix_files[f]
        try:
            update_prefix(join(prefix, f), prefix, placeholder, mode)
        except PaddingError:
            sys.exit("ERROR: placeholder '%s' too short in: %s\n" %
                     (placeholder, dist))

    if not run_script(prefix, dist, 'post-link'):
        sys.exit("Error: post-link failed for: %s" % dist)

    meta = {
        'files': files,
        'link': ({'source': source_dir,
                  'type': link_name_map.get(linktype)}
                 if linktype else None),
    }
    try:    # add URL and MD5
        meta.update(IDISTS[dist])
    except KeyError:
        meta.update(read_urls(dist))
    meta['installed_by'] = 'Miniconda2-4.6.14-Windows-x86_64.exe'
    create_meta(prefix, dist, info_dir, meta)


def duplicates_to_remove(linked_dists, keep_dists):
    """
    Returns the (sorted) list of distributions to be removed, such that
    only one distribution (for each name) remains.  `keep_dists` is an
    interable of distributions (which are not allowed to be removed).
    """
    from collections import defaultdict

    keep_dists = set(keep_dists)
    ldists = defaultdict(set) # map names to set of distributions
    for dist in linked_dists:
        name = name_dist(dist)
        ldists[name].add(dist)

    res = set()
    for dists in ldists.values():
        # `dists` is the group of packages with the same name
        if len(dists) == 1:
            # if there is only one package, nothing has to be removed
            continue
        if dists & keep_dists:
            # if the group has packages which are have to be kept, we just
            # take the set of packages which are in group but not in the
            # ones which have to be kept
            res.update(dists - keep_dists)
        else:
            # otherwise, we take lowest (n-1) (sorted) packages
            res.update(sorted(dists)[:-1])
    return sorted(res)


def yield_idists():
    for line in open(join(PKGS_DIR, 'urls')):
        m = url_pat.match(line)
        if m:
            fn = m.group('fn')
            yield fn[:-8]


def remove_duplicates():
    idists = list(yield_idists())
    keep_files = set()
    for dist in idists:
        with open(join(ROOT_PREFIX, 'conda-meta', dist + '.json')) as fi:
            meta = json.load(fi)
        keep_files.update(meta['files'])

    for dist in duplicates_to_remove(linked(ROOT_PREFIX), idists):
        print("unlinking: %s" % dist)
        meta_path = join(ROOT_PREFIX, 'conda-meta', dist + '.json')
        with open(meta_path) as fi:
            meta = json.load(fi)
        for f in meta['files']:
            if f not in keep_files:
                rm_rf(join(ROOT_PREFIX, f))
        rm_rf(meta_path)


def determine_link_type_capability():
    src = join(PKGS_DIR, 'urls')
    dst = join(ROOT_PREFIX, '.hard-link')
    assert isfile(src), src
    assert not isfile(dst), dst
    try:
        _link(src, dst, LINK_HARD)
        linktype = LINK_HARD
    except OSError:
        linktype = LINK_COPY
    finally:
        rm_rf(dst)
    return linktype


def link_dist(dist, linktype=None):
    if not linktype:
        linktype = determine_link_type_capability()
    prefix = prefix_env('root')
    link(prefix, dist, linktype)


def link_idists():
    linktype = determine_link_type_capability()
    for env_name in sorted(C_ENVS):
        dists = C_ENVS[env_name]
        assert isinstance(dists, list)
        if len(dists) == 0:
            continue

        prefix = prefix_env(env_name)
        for dist in dists:
            assert dist in IDISTS
            link_dist(dist, linktype)

        for dist in duplicates_to_remove(linked(prefix), dists):
            meta_path = join(prefix, 'conda-meta', dist + '.json')
            print("WARNING: unlinking: %s" % meta_path)
            try:
                os.rename(meta_path, meta_path + '.bak')
            except OSError:
                rm_rf(meta_path)


def prefix_env(env_name):
    if env_name == 'root':
        return ROOT_PREFIX
    else:
        return join(ROOT_PREFIX, 'envs', env_name)


def post_extract(env_name='root'):
    """
    assuming that the package is extracted in the environment `env_name`,
    this function does everything link() does except the actual linking,
    i.e. update prefix files, run 'post-link', creates the conda metadata,
    and removed the info/ directory afterwards.
    """
    prefix = prefix_env(env_name)
    info_dir = join(prefix, 'info')
    with open(join(info_dir, 'index.json')) as fi:
        meta = json.load(fi)
    dist = '%(name)s-%(version)s-%(build)s' % meta
    if FORCE:
        run_script(prefix, dist, 'pre-unlink')
    link(prefix, dist, linktype=None)
    shutil.rmtree(info_dir)


def multi_post_extract():
    # This function is called when using the --multi option, when building
    # .pkg packages on OSX.  I tried avoiding this extra option by running
    # the post extract step on each individual package (like it is done for
    # the .sh and .exe installers), by adding a postinstall script to each
    # conda .pkg file, but this did not work as expected.  Running all the
    # post extracts at end is also faster and could be considered for the
    # other installer types as well.
    for dist in yield_idists():
        info_dir = join(ROOT_PREFIX, 'info', dist)
        with open(join(info_dir, 'index.json')) as fi:
            meta = json.load(fi)
        dist = '%(name)s-%(version)s-%(build)s' % meta
        link(ROOT_PREFIX, dist, linktype=None, info_dir=info_dir)


def main():
    global SKIP_SCRIPTS, ROOT_PREFIX, PKGS_DIR

    p = OptionParser(description="conda post extract tool used by installers")

    p.add_option('--skip-scripts',
                 action="store_true",
                 help="skip running pre/post-link scripts")

    p.add_option('--rm-dup',
                 action="store_true",
                 help="remove duplicates")

    p.add_option('--multi',
                 action="store_true",
                 help="multi post extract usecase")

    p.add_option('--link-dist',
                 action="store",
                 default=None,
                 help="link dist")

    p.add_option('--root-prefix',
                 action="store",
                 default=abspath(join(__file__, '..', '..')),
                 help="root prefix (defaults to %default)")

    p.add_option('--post',
                 action="store",
                 help="perform post extract (on a single package), "
                      "in environment NAME",
                 metavar='NAME')

    opts, args = p.parse_args()
    ROOT_PREFIX = opts.root_prefix.replace('//', '/')
    PKGS_DIR = join(ROOT_PREFIX, 'pkgs')

    if args:
        p.error('no arguments expected')

    if FORCE:
        print("using -f (force) option")

    if opts.post:
        post_extract(opts.post)
        return

    if opts.skip_scripts:
        SKIP_SCRIPTS = True

    if opts.rm_dup:
        remove_duplicates()
        return

    if opts.multi:
        multi_post_extract()
        return

    if opts.link_dist:
        link_dist(opts.link_dist)
        return

    if IDISTS:
        link_idists()
    else:
        post_extract()


def warn_on_special_chrs():
    if on_win:
        return
    for c in SPECIAL_ASCII:
        if c in ROOT_PREFIX:
            print("WARNING: found '%s' in install prefix." % c)


if __name__ == '__main__':
    main()
    warn_on_special_chrs()
