'''from . import schemes

__all__ = [
    "set_scheme",
    "schemes"
]

schemes_dict = {
        "qpam": schemes.QPAM,
        "sqpam": schemes.SQPAM,
        "qsm": schemes.QSM,
        "mqsm": schemes.MQSM
}'''

def load_scheme(name, *args, **kwargs):
    try:
        # Dynamically import the scheme class based on the name
        module = __import__(f"quantumaudio.schemes.{name.lower()}", fromlist=[name])
        scheme_class = getattr(module, name.upper())
        return scheme_class(*args, **kwargs)
    except ImportError:
        raise ValueError(f"Scheme {name} is not recognized.")

'''def set_scheme(name, *args, **kwargs):
    try:
        scheme_class = schemes_dict[name]
        return scheme_class(*args, **kwargs)
    except KeyError:
        available_schemes = "\n".join(schemes_dict.keys())
        raise ValueError(f"Scheme {name} is not recognized.\nAvailable schemes: \n{available_schemes}")'''