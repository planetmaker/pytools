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
# of the nml code. The version is stored in nml/version_info.py
# get_numeric_version is used only for the purpose of packet creation,
# in all other cases use get_nml_version()

import subprocess, os

try:
    from subprocess import DEVNULL  # Python 3.3+
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


def get_child_output(cmd, env=None, stderr=None):
    """
    Run a child process, and collect the generated output.

    @param cmd: Command to execute.
    @type  cmd: C{list} of C{str}

    @param env: Environment
    @type  env: C{dict}

    @param stderr: Pipe destination for stderr
    @type  stderr: file object

    @return: Generated output of the command, split on whitespace.
    @rtype:  C{list} of C{str}
    """
    return subprocess.check_output(cmd, universal_newlines = True, env=env, stderr=stderr).split()


def get_git_version(detailed = False, path = None):
    if path is None:
        # method adopted shamelessly from OpenTTD's findversion.sh
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    version = ''
    env = dict(os.environ, LC_ALL='C')
    if os.path.isdir(os.path.join(path,'.git')):
        # Refresh the index to make sure file stat info is in sync
        try:
            get_child_output(["git", "-C", path, "update-index", "--refresh"], env=env)
        except:
            pass

        # Look for modifications
        try:
            modified  = (len(get_child_output(["git", "-C", path, "diff-index", "HEAD"], env=env)) > 0)
            changeset = get_child_output(["git", "-C", path, "rev-parse", "--verify", "HEAD"], env=env)[0][:8]
            isodate   = get_child_output(["git", "-C", path, "show", "-s", "--pretty=%ci", "HEAD"], env=env)[0]
        except OSError as e:
            print("Git checkout found but cannot determine its version. Error({0}): {1}".format(e.errno, e.strerror))
            return version
        except subprocess.CalledProcessError as e:
            print("Git checkout found but cannot determine its version. Error: ", e)
            return version
        # A detached head will make the command fail, but it's uncritical
        # Treat it like branch 'master'.
        try:
            branch = get_child_output(["git", "-C", path, "symbolic-ref", "-q", "HEAD"], env=env)[0].split('/')[-1]
        except subprocess.CalledProcessError:
            branch = "master"

        # We may fail to find a tag - but that is fine
        tag = []
        try:
            # pipe stderr to /dev/null or it will show in the console
            tag = get_child_output(["git", "-C", path, "name-rev", "--name-only", "--tags", "--no-undefined", "HEAD"], env=env, stderr=DEVNULL)[0]
        except (OSError, subprocess.CalledProcessError):
            pass

        # Compose the actual version string
        str_tag = ""
        if len(tag) > 0:
            version = tag[0]
            str_tag = tag[0]
        elif branch == "master":
            version = isodate + "-g" + changeset
        else:
            version = isodate + "-" + branch + "-g" + changeset

        if modified:
            version += "M"

        if detailed:
            version = changeset + ";" + branch + ";" + str_tag + ";" + str(modified) + ";" + isodate + ";" + version

    return version, modified


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

if __name__ == '__main__':
    print(get_git_version(detailed=True))
