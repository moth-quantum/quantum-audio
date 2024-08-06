"""This package provides Quantum Audio Representations of Digital Audio and
necessary utilities.
"""

__version__ = "0.1.0"

import importlib


def load_scheme(name, *args, **kwargs):
    try:
        scheme = importlib.import_module(
            f"quantumaudio.schemes.{name.lower()}"
        )
        return getattr(scheme, name.upper())(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Could not load class '{name}' from schemes. Error: {e}."
        )
