from unittest.mock import MagicMock
import importlib

import celery


signature_mocks = {}


def is_valid_import_path(*args, **kwargs):
    # @see https://stackoverflow.com/a/14050282
    return importlib.util.find_spec(*args, **kwargs) is not None


def signature(pypath, *args, **kwargs):
    """Mock of the ``celery.signature`` method"""
    key = hash((pypath, tuple(args), tuple(kwargs)))

    try:
        out = signature_mocks[key]
    except KeyError:
        # Only run this as we're creating new mocks
        if not is_valid_import_path(pypath):
            raise NotImplementedError(f'{pypath} is not a registered task')

        out = MagicMock(name=pypath, spec=celery.Signature)
        signature_mocks[key] = out

    return out
