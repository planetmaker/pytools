__license__ = """
NML is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

NML is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with NML; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

# The following version determination code is a greatly simplified version
# of the mercurial repo code. The version is stored in nml/__version__.py
# get_numeric_version is used only for the purpose of packet creation,
# in all other cases use get_nml_version()

import subprocess, os

def get_child_output(cmd):
    """
    Run a child process, and collect the generated output.

    @param cmd: Command to execute.
    @type  cmd: C{list} of C{str}

    @return: Generated output of the command, split on whitespace.
    @rtype:  C{list} of C{str}
    """
    return subprocess.check_output(cmd, universal_newlines = True).split()


def get_hg_version(path = None):
    if path is None:
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    version = ''
    modified = False
    if os.path.isdir(os.path.join(path,'.hg')):
        # we want to return to where we were. So save the old path
        try:
            version_list = get_child_output(['hg', '-R', path, 'id', '-n', '-t', '-i'])
        except OSError as e:
            print("Mercurial checkout found but cannot determine its version. Error({0}): {1}".format(e.errno, e.strerror))
            return version

        if version_list[1].endswith('+'):
            modified = True
        else:
            modified = False

        # Test whether we have a tag (=release version) and add it, if found
        if len(version_list) > 2 and version_list[2] != 'tip' and modified == '':
            # Tagged release
            version = version_list[2]
        else:
            # Branch or modified version
            hash = version_list[0].rstrip('+')


            # Combine the version string
            version = "v{}-{}".format(version_list[1], hash)

    print("Version logged from '{}': {}".format(path, version))

    return version, modified
