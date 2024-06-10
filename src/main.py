import importlib
  
def load_scheme(name,module_name='src.schemes'):
    try:
        scheme = importlib.import_module(f'{module_name}.{name.lower()}')
        return getattr(scheme, name.upper())
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not load class '{class_name}' from module '{module_name}'. Error: {e}")