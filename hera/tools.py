import contextlib
import time

@contextlib.contextmanager
def measure_time(name):
    start = time.time()
    yield
    print('%s took %.2f s' % (name, time.time() - start))
