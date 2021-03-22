import cProfile
import functools
import logging
import os
from server.context import Context


profiler = cProfile.Profile()
context = Context()
DUMP_FILE = context.logs_dir + '/' + context.profile_file
profiling_active = bool(context.profile)
if profiling_active:
    logging.info(f"Profile files at '{DUMP_FILE}'")
    if os.path.exists(DUMP_FILE):
        if not os.path.isfile(DUMP_FILE):
            logging.warning(f"Path '{DUMP_FILE}' already exists and is not a file. Disabling profiling")
            profiling_active = False
    else:
        if os.path.exists(context.logs_dir):
            if not os.path.isdir(context.logs_dir):
                logging.warning(f"Path '{context.logs_dir}' already exists and is not a directory. Disabling profiling")
                profiling_active = False
        else:
            os.mkdir(context.logs_dir)
            # Create dump file
            f = open(DUMP_FILE, 'w+')
            f.close()
else:
    logging.info(f"Profiling disabled")


def profile(_func=None, *, on=profiling_active):

    def profile_decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not on:
                return func(*args, **kwargs)
            profiler.enable()
            result = func(*args, **kwargs)
            profiler.disable()
            profiler.dump_stats(DUMP_FILE)
            return result

        return wrapper

    if not _func:
        return profile_decorator
    else:
        return profile_decorator(_func)
