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
"""Fake jobs."""

import subprocess
import time
import typing

from fuzzbench import build_jobs

def build_image(name: str):
    """Build a Docker image."""
    print('Building', name)
    if name.startswith('base'):
        if name in ['base-image', 'base-builder', 'base-runner']:
            build_jobs.build_base_images(name)
    else:
        subprocess.run(['docker', '--version'], check=True)
        time.sleep(3)
    return True


def run_trial():
    """Run a trial."""
    return True


def measure_corpus_snapshot():
    """Measure a corpus snapshot."""
    return True
