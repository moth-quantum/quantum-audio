# Copyright 2024 Moth Quantum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==========================================================================

all_schemes = ["qpam", "spqam", "qsm", "msqpam", "mqsm"]

default_scheme = "qpam"
default_multi_channel_scheme = "mqsm"
default_shots = 8000
default_sr = 22050
default_chunk_size = 256

defaults = {
    "scheme": default_scheme,
    "multi_channel_scheme": default_multi_channel_scheme,
    "shots": default_shots,
    "sr": default_sr,
    "chunk_size": default_chunk_size,
}
