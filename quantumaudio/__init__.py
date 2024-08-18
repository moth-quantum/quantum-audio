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

"""A Python package for building Quantum Representations of Digital Audio.
Developed by Moth Quantum. https://mothquantum.com/
"""

__version__ = "0.1.0"

import importlib


def load_scheme(name, *args, **kwargs):
    """Dynamically load and instantiate a class from a scheme string."""
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
