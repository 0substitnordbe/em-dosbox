#!/usr/bin/python
from __future__ import print_function
from subprocess import check_output
from sys import argv
import re

def git_modified(s):
    for line in s.splitlines():
        if len(line) > 3 and not line.startswith('?? '):
            return True

    return False

# Inspired by Rockbox version.sh
def git_rev(path):
    try:
        rev = check_output(['git', 'rev-parse', \
                           '--verify', '--short', 'HEAD'], \
                           universal_newlines=True, cwd=path).splitlines()[0]
        sts = check_output(['git', 'status', '--porcelain'],
                           universal_newlines=True, cwd=path)
        if (git_modified(sts)):
            rev += 'M'

    except:
        rev = 'UNKNOWN'

    return rev

# This tries to construct a compiler version string.
# Ideally having the configure options and compiler flags would be nice.
def compiler_rev(compiler):
    try:
        out = check_output(compiler + ['--version'],
                           universal_newlines=True).splitlines()[0]

        if out.startswith('em'):
            # Assume emscripten
            m = re.match('^[^)]+\) ([^ ]+) \((?:commit )?(.......).*$', out)
            rev = 'Emscripten ' + m.group(1) + ' ' + m.group(2)
        else:
            m = re.match('^([^ ]+) .* ([^ ]+)$', out)
            # Assume something like GCC
            rev = m.group(1) + ' ' + m.group(2)
    except:
        rev = 'UNKNOWN'

    return rev;

def make_version_h(gitpath, compiler):
    return '/* Version info file automatically generated by version.py */\n' + \
           '#define VERSION_TEXT "' + git_rev(gitpath) + \
           ' built with ' + compiler_rev(compiler) + '"\n';

# Program begins here

if len(argv) < 4:
    print("Usage: python", argv[0],
          "VERSION_HEADER GIT_PATH COMPILER_EXECUTABLE [ARGUMENTS...]")
    exit(1)

current_version = make_version_h(argv[2], argv[3:])

# Only update file if version info has changed

try:
    with open(argv[1], 'r') as f:
        old_version = f.read()
except:
    old_version = ''

if old_version != current_version:
    with open(argv[1], 'w') as f:
        f.write(current_version)
