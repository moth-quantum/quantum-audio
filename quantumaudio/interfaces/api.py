import quantumaudio
from quantumaudio import load_scheme
from quantumaudio.utils import pick_key
from quantumaudio.tools import stream_data

# ------------------- Core Functions ---------------------------

def encode(data, scheme="qpam", **kwargs):
    """Encodes data using a specified quantum scheme.

    Args:
        data (any): The data to encode.
        scheme (str): Name of the encoding scheme to use. Defaults to "qpam".
        **kwargs: Additional keyword arguments passed to the encoding method.

    Returns:
        Encoded data according to the provided scheme.
    """
    scheme_kwargs, kwargs = _split_kwargs(kwargs)
    return _load_scheme(scheme, **scheme_kwargs).encode(data, **kwargs)


def decode(circuit, **kwargs):
    """Decodes a quantum circuit using the scheme it was encoded with.

    Args:
        circuit (object): Qiskit circuit object to decode.
        **kwargs: Additional keyword arguments passed to the decoding method.

    Returns:
        Decoded data from the quantum circuit.
    """
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(circuit, kwargs)
    return _load_scheme(scheme, **scheme_kwargs).decode(circuit, **kwargs)

# ------------------- Tool Function ---------------------------

def stream(data, scheme="qpam", **kwargs):
    """Streams data through a quantum encoding scheme for longer arrays.

    Args:
        data (any): Data to be streamed.
        scheme (str): Name of the quantum scheme to use for streaming.
        **kwargs: Additional keyword arguments passed to the streaming method.

    Returns:
        Processed stream data based on the quantum scheme.
    """
    scheme_kwargs, kwargs = _split_kwargs(kwargs)
    scheme = _load_scheme(scheme, **scheme_kwargs)
    return stream_data(data=data, scheme=scheme, **kwargs)


# ------------------- Additional Functions ---------------------------

def calculate(data, scheme="qpam", **kwargs):
    """Estimates and Prints the resources required (number of qubits) according to a scheme.

    Args:
        data (any): The data to encode.
        scheme (str): Name of the encoding scheme to use. Defaults to "qpam".
        **kwargs: Additional keyword arguments passed to the scheme class.
    """
    _load_scheme(scheme, **kwargs).calculate(data)

def decode_result(result, **kwargs):
    """Decodes a quantum result object.

    Args:
        result (object): Qiskit result object to decode.
        **kwargs: Additional keyword arguments passed to the decoding method.

    Returns:
        Decoded data from the result object.
    """
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(result, kwargs)
    return _load_scheme(scheme, **scheme_kwargs).decode_result(result, **kwargs)


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
    return _load_scheme(scheme, **scheme_kwargs).decode_counts(counts, **kwargs)


# ------------------- API Helpers ---------------------------

_cache = {}

def _load_scheme(scheme, **scheme_kwargs):
    """Load a scheme with specified keyword arguments, caching the result to 
    avoid repeated loading for the same parameters.

    Args:
        scheme (str): Name of the quantum scheme to use for streaming.
        scheme_kwargs (dict): Dictionary containing keyword arguments.

    Returns:
        The loaded or cached scheme object.
    """
    if isinstance(scheme, quantumaudio.schemes.Scheme):
        return scheme
    
    cache_key = (scheme, frozenset(scheme_kwargs.items()))
    if cache_key not in _cache:
        _cache[cache_key] = load_scheme(scheme, **scheme_kwargs)
    return _cache[cache_key]

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
    scheme = kwargs.pop('scheme', None)
    if scheme and isinstance(scheme, quantumaudio.schemes.Scheme):
        return scheme, {}, kwargs
    
    scheme = pick_key(kwargs, instance, key="scheme")
    scheme_kwargs = {}
    num_channels = pick_key(kwargs, instance, key="num_channels")
    if num_channels:
        scheme_kwargs["num_channels"] = num_channels
    qubit_shape = pick_key(kwargs, instance, key="qubit_shape")
    if qubit_shape and "qsm" in scheme:
        scheme_kwargs["qubit_depth"] = qubit_shape[-1]
    return scheme, scheme_kwargs, kwargs
