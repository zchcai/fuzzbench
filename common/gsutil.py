# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper functions for using the gsutil tool."""

from common import logs
from common import new_process

logger = logs.Logger('gsutil')


def command(arguments, *args, parallel=False, **kwargs):
    """Executes a gsutil command with |arguments| and returns the result."""
    command_list = ['gsutil']
    if parallel:
        command_list.append('-m')
    return new_process.execute(command_list + arguments, *args, **kwargs)


def cp(*cp_arguments, **kwargs):  # pylint: disable=invalid-name
    """Executes gsutil's "cp" command with |cp_arguments| and returns the
    returncode and the output."""
    command_list = ['cp']
    command_list.extend(cp_arguments)
    return command(command_list, **kwargs)


def ls(*ls_arguments, must_exist=True, **kwargs):  # pylint: disable=invalid-name
    """Executes gsutil's "ls" command with |ls_arguments| and returns the result
    and the returncode. Does not except on nonzero return code if not
    |must_exist|."""
    command_list = ['ls'] + list(ls_arguments)
    # Don't use parallel as it probably doesn't help at all.
    result = command(command_list, expect_zero=must_exist, **kwargs)
    retcode = result.retcode  # pytype: disable=attribute-error
    output = result.output.splitlines()  # pytype: disable=attribute-error
    return retcode, output


def rm(*rm_arguments, recursive=True, force=False, **kwargs):  # pylint: disable=invalid-name
    """Executes gsutil's rm command with |rm_arguments| and returns the result.
    Uses -r if |recursive|. If |force|, then uses -f and will not except if
    return code is nonzero."""
    command_list = ['rm'] + list(rm_arguments)[:]
    if recursive:
        command_list.insert(1, '-r')
    if force:
        command_list.insert(1, '-f')
    return command(command_list, expect_zero=(not force), **kwargs)


def rsync(  # pylint: disable=too-many-arguments
        source,
        destination,
        delete=True,
        recursive=True,
        gsutil_options=None,
        options=None,
        **kwargs):
    """Does gsutil rsync from |source| to |destination| using sane defaults that
    can be overriden. Prepends any |gsutil_options| before the rsync subcommand
    if provided."""
    command_list = [] if gsutil_options is None else gsutil_options
    command_list.append('rsync')
    if delete:
        command_list.append('-d')
    if recursive:
        command_list.append('-r')
    if options is not None:
        command_list.extend(options)
    command_list.extend([source, destination])
    return command(command_list, **kwargs)
