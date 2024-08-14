"""This package provides Quantum Audio Representations of Digital Audio and
necessary utilities.
"""

__version__ = "0.1.0"

import importlib

def __getattr__(name):
    try:
        if name in _all_modules:
            module = importlib.import_module(f".{name.lower()}", package=__name__)
            return module
        else:
            module = importlib.import_module(f".schemes.{name.lower()}", package=__name__)
            return getattr(module, name.upper())
    except (ImportError, AttributeError) as e:
        raise AttributeError(f"module {__name__} has no attribute {name}") from e

def __dir__():
    return __all__

_all_modules = ["schemes", "utils"]
_all_schemes = ["QPAM", "SQPAM", "QSM", "MSQPAM", "MQSM"]

__all__ = _all_modules + _all_schemes