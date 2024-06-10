import importlib
  
def load(name,module_name='quantumaudio.schemes'):
    try:
        scheme = importlib.import_module(f'{module_name}.{name.lower()}')
        return getattr(scheme, name.upper())
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not load class '{name}' from module '{module_name}'. Error: {e}")