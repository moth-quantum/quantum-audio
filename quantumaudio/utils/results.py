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

from typing import Union
import qiskit
from qiskit.primitives import PrimitiveResult, SamplerPubResult

# ======================
# Post-processing
# ======================


def pad_counts(counts: Union[dict, qiskit.result.Counts]) -> dict:
    """Pads the counts to its full length covering all basis states.

    Args:
        counts: Counts dictionary

    Returns:
        counts: Padded counts dictionary
    """
    num_qubits = len(next(iter(counts)))
    all_states = [
        format(i, "0" + str(num_qubits) + "b") for i in range(2**num_qubits)
    ]
    complete_counts = {state: counts.get(state, 0) for state in all_states}
    return complete_counts


def get_counts(results_obj, result_id=0):
    """
    Extract counts from a results object.

    Args:
        results_obj: An instance of `PrimitiveResult` or `Result` object from which to extract counts.
        result_id: The index of the result to extract if the results object contains multiple results.

    Returns:
        counts: The counts of measurements from the results object.
    """
    counts = {}

    if isinstance(results_obj, PrimitiveResult):
        results_obj = results_obj[result_id]

    if isinstance(results_obj, SamplerPubResult):
        counts = results_obj.data.meas.get_counts()

    elif isinstance(results_obj, qiskit.result.Result):
        counts = results_obj.get_counts()

    else:
        raise TypeError("Unsupported result object type.")

    return counts


def get_metadata(results_obj, result_id=0):
    """
    Extract metadata from a results object.

    Args:
        results_obj: An instance of `PrimitiveResult` or `Result` object from which to extract metadata.
        result_id: The index of the result to extract if the results object contains multiple results.

    Returns:
        metadata: The metadata associated with the result.
    """
    metadata = {}

    if isinstance(results_obj, PrimitiveResult):
        results_obj = results_obj[result_id]

    if isinstance(results_obj, SamplerPubResult):
        metadata = results_obj.metadata.get("circuit_metadata", {})
        if "shots" in results_obj.metadata:
            metadata["shots"] = results_obj.metadata["shots"]

    elif isinstance(results_obj, qiskit.result.Result):
        metadata = results_obj.results[result_id].header.metadata
        metadata["shots"] = results_obj.results[result_id].shots

    else:
        raise TypeError("Unsupported result object type.")

    if not metadata:
        print(f"No metadata found in Results. Try accessing from encoded circuit's `.metadata` attribute")
    
    return metadata


def get_counts_and_metadata(results_obj, result_id=0):
    """
    Extract counts and metadata from a results object.

    Args:
        results_obj: An instance of `PrimitiveResult` or `Result` object from which to extract counts and metadata.
        result_id: The index of the result to extract if the results object if it contains multiple results.

    Returns:
        counts: The counts of measurements from the results object.
        metadata: The metadata associated with the result.
    """
    counts = get_counts(results_obj, result_id)
    metadata = get_metadata(results_obj, result_id)
    return counts, metadata

# ======================
# Retrieve Metadata 
# ======================

def pick_key_from_instance(instance, key):
    """Search for given key in an instance used at decoding.

    Args:
        instance: Can be Qiskit Circuit or Result object.
        key: Key to find in the encoded metadata.

    """
    if isinstance(instance, qiskit.circuit.QuantumCircuit):
        if key == "scheme" and instance.name.upper() in [
            "QPAM",
            "SQPAM",
            "QSM",
            "MSQPAM",
            "MQSM",
        ]:
            return instance.name.upper()
        elif key in instance.metadata:
            return instance.metadata[key]

    elif isinstance(
        instance, (qiskit.result.Result, PrimitiveResult, SamplerPubResult)
    ):
        metadata = get_metadata(instance)
        if key in metadata:
            return metadata[key]

    # If the key was not found in the instance
    if key == "scheme":
        raise ValueError(f"{key} is missing")  # Scheme is essential
    return None


def pick_key(kwargs, instance, key):
    """Search for given key in key words dictionary first if user manually specified or
    continue searching for key using instances

    Args:
        kwargs: Keyword arguments dictionary.
        instance: Can be Qiskit Circuit or Result object.
        key: Key to find in the encoded metadata.

    """
    # Check if the key exists in kwargs
    if key in kwargs:
        return kwargs.pop(key)

    # Check if metadata exists in kwargs and the key is inside it
    if "metadata" in kwargs and key in kwargs["metadata"]:
        return kwargs["metadata"][key]

    # Send the search to pick_key_with_instance
    return pick_key_from_instance(instance, key)
