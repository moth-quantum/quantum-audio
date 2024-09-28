from quantumaudio import load_scheme
from quantumaudio.utils import pick_key
from quantumaudio.tools import stream_data


# ------------------- Main Functions ---------------------------


def encode(data, scheme="qpam", **kwargs):
    """Encodes data using a specified quantum scheme.

    Args:
        data (any): The data to encode.
        scheme (str): Name of the encoding scheme to use.
        **kwargs: Additional keyword arguments passed to the encoding method.

    Returns:
        Encoded data according to the provided scheme.
    """
    scheme_kwargs, kwargs = _split_kwargs(kwargs)
    return load_scheme(scheme, **scheme_kwargs).encode(data, **kwargs)


def decode(circuit, **kwargs):
    """Decodes a quantum circuit using a specified scheme.

    Args:
        circuit (object): Qiskit circuit object to decode.
        **kwargs: Additional keyword arguments passed to the decoding method.

    Returns:
        Decoded data from the quantum circuit.
    """
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(circuit, kwargs)
    return load_scheme(scheme, **scheme_kwargs).decode(circuit, **kwargs)


def stream(data, scheme, **kwargs):
    """Streams data through a quantum encoding scheme for longer arrays.

    Args:
        data (any): Data to be streamed.
        scheme (str): Name of the quantum scheme to use for streaming.
        **kwargs: Additional keyword arguments passed to the streaming method.

    Returns:
        Processed stream data based on the quantum scheme.
    """
    scheme_kwargs, kwargs = _split_kwargs(kwargs)
    scheme = load_scheme(scheme, **scheme_kwargs)
    return stream_data(data=data, scheme=scheme, **kwargs)


# ------------------- Additional Decode Options ---------------------------


def decode_result(result, **kwargs):
    """Decodes a quantum result object.

    Args:
        result (object): Qiskit result object to decode.
        **kwargs: Additional keyword arguments passed to the decoding method.

    Returns:
        Decoded data from the result object.
    """
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(result, kwargs)
    return load_scheme(scheme, **scheme_kwargs).decode_result(result, **kwargs)


def decode_counts(counts, metadata, **kwargs):
    """Decodes quantum counts using metadata.

    Args:
        counts (dict): Quantum counts to decode.
        metadata (dict): Metadata associated with the circuit that was executed.
        **kwargs: Additional keyword arguments passed to the decoding method.

    Returns:
        Decoded data from the counts.
    """
    kwargs["metadata"] = metadata
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(counts, kwargs)
    return load_scheme(scheme, **scheme_kwargs).decode_counts(counts, **kwargs)


# ------------------- Helper Functions ---------------------------

def _split_kwargs(kwargs):
    """Splits keyword arguments between scheme loading and encoding operations.

    Args:
        kwargs (dict): Dictionary containing keyword arguments.

    Returns:
        Two dictionaries for scheme-related keyword arguments, and remaining keyword arguments.
    """
    scheme_args = ("qubit_depth", "num_channels")
    return {
        arg: kwargs.pop(arg) for arg in scheme_args if arg in kwargs
    }, kwargs


def _fetch_kwargs(instance, kwargs):
    """Fetches scheme at decoding and splits keyword arguments accordingly.

    Args:
        instance (object): Qiskit circuit or Results object.
        kwargs (dict): Dictionary containing keyword arguments.

    Returns:
        Tuple of Scheme name, scheme-related keyword arguments, and remaining keyword arguments.
    """
    scheme = pick_key(kwargs, instance, key="scheme")
    scheme_kwargs = {}
    num_channels = pick_key(kwargs, instance, key="num_channels")
    if num_channels:
        scheme_kwargs["num_channels"] = num_channels
    num_qubits = pick_key(kwargs, instance, key="num_qubits")
    if num_qubits and "qsm" in scheme:
        scheme_kwargs["qubit_depth"] = num_qubits[-1]
    return scheme, scheme_kwargs, kwargs
