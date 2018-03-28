import sys
import importlib.util

def importModuleFromFile(module, filename):
    spec = importlib.util.spec_from_file_location(module, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
