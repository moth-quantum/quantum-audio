import importlib
from . import schemes
  
def load_scheme(name, *args, **kwargs):
    try:
        scheme = importlib.import_module(f'quantumaudio.schemes.{name.lower()}')
        return getattr(scheme, name.upper())(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not load class '{name}' from schemes. Error: {e}.")