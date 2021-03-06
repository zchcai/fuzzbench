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
BENCHMARKS := $(notdir $(shell find benchmarks -type f -name benchmark.yaml | xargs dirname))

BASE_TAG ?= gcr.io/fuzzbench

# If we're running on a CI service, cache-from a remote image. Otherwise just
# use the local cache.
cache_from = $(if ${RUNNING_ON_CI},--cache-from $(1),)

# For base-* images (and those that depend on it), use a remote cache by
# default, unless the developer sets DISABLE_REMOTE_CACHE_FOR_BASE.
cache_from_base = $(if ${DISABLE_REMOTE_CACHE_FOR_BASE},,--cache-from $(1))

base-image:
	docker build \
    --tag $(BASE_TAG)/base-image \
    $(call cache_from_base,${BASE_TAG}/base-image) \
    docker/base-image

pull-base-image:
	docker pull $(BASE_TAG)/base-image

dispatcher-image: base-image
	docker build \
    --tag $(BASE_TAG)/dispatcher-image \
    $(call cache_from,${BASE_TAG}/dispatcher-image) \
    docker/dispatcher-image

define benchmark_template
$(1)-fuzz-target  := $(shell cat benchmarks/$(1)/benchmark.yaml | \
                             grep fuzz_target | cut -d ':' -f2 | tr -d ' ')

# TODO: It would be better to call this benchmark builder. But that would be
# confusing because this doesn't involve benchmark-builder/Dockerfile. Rename
# that and then rename this.
.$(1)-project-builder:
	docker build \
    --tag $(BASE_TAG)/builders/benchmark/$(1) \
    --file benchmarks/$(1)/Dockerfile \
    $(call cache_from,${BASE_TAG}/builders/benchmarks/$(1)) \
    benchmarks/$(1)

endef
# Instantiate the above template with all OSS-Fuzz benchmarks.
$(foreach benchmark,$(BENCHMARKS), \
  $(eval $(call benchmark_template,$(benchmark))))
