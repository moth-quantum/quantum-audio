import importlib
from .plot import plot

def __getattr__(name):
    try:
        module = importlib.import_module(f".{name.lower()}", package=__name__)
        return module
    except (ImportError, AttributeError) as e:
        raise AttributeError(f"module {__name__} has no attribute {name}") from e

def __dir__():
    return __all__

__all__ = ["audio", "interactive", "plot", "stream"]