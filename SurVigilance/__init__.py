from importlib import import_module

__version__ = "0.1.0"


submodules = [
    "ui",
]

__all__ = [
    *submodules,
]


def __dir__():
    return __all__


# taken from scipy
def __getattr__(name):
    if name in submodules:
        return import_module(f"SurVigilance.{name}")
    else:
        try:
            return globals()[name]
        except KeyError as err:
            raise AttributeError(
                f"Module 'SurVigilance' has no attribute '{name}'"
            ) from err
