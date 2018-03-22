import sys

def importModuleFromFile(module, filename):
    # py35
    if sys.version_info >= (3,5):
        import importlib.util
        spec = importlib.util.spec_from_file_location(module, filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # py33 & py34
    if sys.version_info >= (3,3):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(module, filename).load_module()

    # py27
    import imp
    return imp.load_source(module, filename)
