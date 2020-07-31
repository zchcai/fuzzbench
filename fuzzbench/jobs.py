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
"""Defines all required jobs for one experiment."""

import os
import subprocess

BASE_TAG = 'gcr.io/fuzzbench'


def build_image(job_obj):
    """Builds a Docker image and returns whether it succeeds."""
    image_tag = os.path.join(BASE_TAG, job_obj['tag'])
    subprocess.run(['docker', 'pull', image_tag], check=True)
    command = ['docker', 'build', '--tag', image_tag, job_obj['context']]
    cpu_options = ['--cpu-period', '100000', '--cpu-quota', '100000']
    command.extend(cpu_options)
    dockerfile = job_obj.get('dockerfile', None)
    if dockerfile:
        command.extend(['--file', dockerfile])
    buildargs = job_obj.get('build_arg', None)
    if buildargs:
        for arg in buildargs:
            command.extend(['--build-arg', arg])
    subprocess.run(command, check=True)
    return True


def run_trial():
    """Runs a trial."""
    return True


def measure_corpus_snapshot():
    """Measures a corpus snapshot."""
    return True
