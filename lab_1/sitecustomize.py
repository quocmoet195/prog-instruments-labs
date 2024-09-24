import os
import sys


def trySetupCoverage():  # pragma: no cover - can hardly measure coverage here :)
    """
    Attempts to set up code coverage using the `coverage` module.
    """
    try:
        import coverage
        coverage.process_startup()  # doesn't do anything unless COVERAGE_PROCESS_START is set
    except Exception: 
        pass


def loadTestCustomize():
    """
    Attempts to load a `testcustomize` module to customize Python's behavior during tests.
    """
    try:
        # Generic file name to customize the behaviour of Python per test
        import testcustomize
    except ImportError:
        pass


def trySetupCaptureMock():
    """
    Attempts to set up `capturemock` for mocking during testing.
    """
    try:
        import capturemock
        capturemock.process_startup()  # doesn't do anything unless CAPTUREMOCK_PROCESS_START is set
    except Exception:
        pass


def loadRealSiteCustomize(fileName): # pragma: no cover - coverage not set up yet
    """
    Loads the real `sitecustomize` module from the system's Python path.
    Args:
        fileName: The name of the current file, used to find the directory
                        and position in the Python path.
    """
    # must do this before setting up coverage as real sitecustomize might
    # manipulate PYTHONPATH in such a way that coverage can be found
    import imp
    myDir = os.path.dirname(fileName)
    pos = sys.path.index(myDir)
    try:
        file, pathname, description = imp.find_module("sitecustomize", sys.path[pos + 1:])
        if os.path.basename(os.path.dirname(pathname)) == "traffic_intercepts":
            # For the self-tests: don't load another copy ourselves recursively
            loadRealSiteCustomize(pathname)
        else:
            imp.load_module("sitecustomize", file, pathname, description)
    except ImportError:
        pass


loadRealSiteCustomize(__file__)  # pragma: no cover - coverage not set up yet
trySetupCoverage()  # pragma: no cover - coverage not set up yet
loadTestCustomize()  # pragma: no cover - coverage not set up yet
trySetupCaptureMock()  # pragma: no cover - coverage not set up yet