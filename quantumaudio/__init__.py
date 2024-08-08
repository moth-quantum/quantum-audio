"""This package provides Quantum Audio Representations of Digital Audio and
necessary utilities.
"""

__version__ = "0.1.0"

import importlib

def load_scheme(name, *args, **kwargs):
    """Dynamically loads and returns a class from a specified scheme module that can perform encoding and decoding operations of Quantum Audio.

    Args:
        name: The name of the scheme to load i.e. "qpam", "sqpam", "qsm", "mqsm" or "msqpam"
        *args: Positional arguments to pass to the class constructor.
        **kwargs: Keyword arguments to pass to the class constructor.
                  "qubit_depth" for state modulations schemes (qsm and mqsm).
                  "num_channels" for multi-channel schemes (mqsm and msqpam).

    Returns:
        object: An instance of the class from the specified scheme module.

    Raises:
        ImportError: If the module or class cannot be imported.
    """
    try:
        scheme = importlib.import_module(
            f"quantumaudio.schemes.{name.lower()}"
        )
        return getattr(scheme, name.upper())(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Could not load class '{name}' from schemes. Error: {e}."
        )
