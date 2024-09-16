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

"""This package provides Quantum Audio Representations of Digital Audio and
necessary utilities.
"""

__version__ = "0.1.0b"

import importlib

# --------------------------- Lazy Loader ---------------------------


def load_scheme(name, *args, **kwargs):
    """
    Load and instantiate a quantum audio representation (or scheme) class from a string.

    Args:
        name (str): The name of the scheme to load. It can be one of the following:
            `qpam`, `sqpam`, `qsm`, `msqpam`, or `mqsm`.
        *args: Optional positional arguments to pass to the scheme class.
        **kwargs: Optional keyword arguments to pass to the scheme class such as:

            - ``qubit_depth`` (int): For `qsm` and `mqsm` to manually set the number of qubits 
              to represent the amplitude of audio.
            - ``num_channels`` (int): For `msqpam` and `mqsm` to manually set the number 
              of channels to represent.

    Returns:
        quantumaudio.schemes.Scheme:
            An instance of the Quantum Audio Scheme.
    """
    try:
        scheme = importlib.import_module(
            f"quantumaudio.schemes.{name.lower()}"
        )
        scheme_class = getattr(scheme, name.upper())
        return scheme_class(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Could not load class '{name}' from schemes. Error: {e}."
        ) from e


def __getattr__(name):
    """Dynamically load and instantiate a class from a scheme attribute."""
    try:
        if name.upper() not in _all_schemes:
            module = importlib.import_module(
                f".{name.lower()}", package=__name__
            )
            return module
        else:
            module = importlib.import_module(
                f".schemes.{name.lower()}", package=__name__
            )
            return getattr(module, name.upper())
    except (ImportError, AttributeError) as e:
        raise AttributeError(
            f"module {__name__} has no attribute {name}"
        ) from e


def __dir__():
    """Set the available attributes."""
    return __all__


_all_schemes = ["QPAM", "SQPAM", "QSM", "MSQPAM", "MQSM"]

__all__ = [
    "load_scheme",
    "schemes",
    "utils",
    "QPAM",
    "SQPAM",
    "QSM",
    "MSQPAM",
    "MQSM",
]
