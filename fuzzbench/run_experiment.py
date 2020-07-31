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
"""Runs a FuzzBench experiment."""

import time

import redis
import rq

from common import config_utils, environment, yaml_utils
from experiment.build import docker_images
from fuzzbench import jobs

redis_connection = redis.Redis(host="queue-server")  # pylint: disable=invalid-name


def run_experiment(config):
    """Main experiment logic."""
    print('Initializing the job queue.')
    # Create the queue for scheduling build jobs and run jobs.
    queue = rq.Queue('build_n_run_queue')

    images_to_build = docker_images.get_images_to_build(config['fuzzers'],
                                                        config['benchmarks'])
    jobs_list = []
    for name, obj in images_to_build.items():
        if 'depends_on' not in obj:
            jobs_list.append(
                queue.enqueue(jobs.build_image,
                              job_obj=obj,
                              job_timeout=1800,
                              result_ttl=config['max_total_time'],
                              job_id=name))
            continue

        jobs_list.append(
            queue.enqueue(jobs.build_image,
                          job_obj=obj,
                          job_timeout=1800,
                          result_ttl=config['max_total_time'],
                          job_id=name,
                          depends_on=obj['depends_on'][0]))

    while True:
        print('Current status of jobs:')
        print('\tqueued:\t%d' % queue.count)
        print('\tstarted:\t%d' % queue.started_job_registry.count)
        print('\tdeferred:\t%d' % queue.deferred_job_registry.count)
        print('\tfinished:\t%d' % queue.finished_job_registry.count)
        print('\tfailed:\t%d' % queue.failed_job_registry.count)
        for job in jobs_list:
            print('  %s : %s\t(%s)' % (job.func_name, job.get_status(), job.id))

        if all([job.result is not None for job in jobs_list]):
            break
        time.sleep(3)
    print('All done!')


def main():
    """Set up Redis connection and start the experiment."""
    config_path = environment.get('EXPERIMENT_CONFIG', 'config.yaml')
    config = yaml_utils.read(config_path)

    config = config_utils.validate_and_expand(config)

    with rq.Connection(redis_connection):
        return run_experiment(config)


if __name__ == '__main__':
    main()
