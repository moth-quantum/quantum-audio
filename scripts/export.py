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

import sys
import os
from params import *
import argparse
sys.path.insert(0, os.path.dirname(os.getcwd()))
import tools
import quantumaudio

def set_output_path(input_path,prefix='qa_',suffix=''):
    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path).split('.')[0]
    output_filename = f"{prefix}{input_filename}{suffix}"
    output_path = os.path.join(input_dir, output_filename + '.wav')
    return output_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process quantum audio and export')

    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input audio file.')
    parser.add_argument('-o', '--output', type=str, help='Path to the output audio file.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode.')

    parser.add_argument('--scheme', choices=all_schemes, default=default_scheme, help='Processing mode (default: quick).')
    parser.add_argument('--shots', type=int, default=default_shots, help='Number of items to process.')

    parser.add_argument('--sr', type=int, default=default_sr, help='Number of items to process.')
    parser.add_argument('--stereo', action='store_true', help='Enable verbose mode.')
    parser.add_argument('--buffer_size', type=int, default=default_chunk_size, help='Number of items to process.')

    # Parse the arguments
    args = parser.parse_args()

    # Access the arguments
    input_path = args.input
    output_path = args.output
    verbose = args.verbose

    scheme = args.scheme
    shots = args.shots

    sr = args.sr
    stereo = args.stereo
    mono = not stereo
    chunk_size = args.buffer_size

    # Adjust arguments
    if not output_path:
        output_path = set_output_path(input_path)

    if stereo:
        scheme = default_multi_channel_scheme

    scheme = quantumaudio.load_scheme(scheme)

    # Export
    tools.audio.save_quantumaudio(file_path=input_path,output_filepath=output_path,sr=sr,mono=mono,scheme=scheme,shots=shots,chunk_size=chunk_size,verbose=verbose)
