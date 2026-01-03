import io
from contextlib import contextmanager, redirect_stdout, redirect_stderr

@contextmanager
def _suppress_output():
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        yield