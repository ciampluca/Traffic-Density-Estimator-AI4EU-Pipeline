import logging
import os
import yaml
from itertools import starmap

_CONFIG_FILE = 'config/config.yaml'

_LOG_FORMAT = '[ %(levelname)s ] %(asctime)s (%(module)s) %(message)s'
_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
_AVAILABLE_LOG_LEVELS = [
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
    logging.NOTSET
]

class Context:
    """
    Singleton class to setup the configs for the server
    Configs priorities are as follows: Environment variables, Config files
    meaning an environment variable has precedence over the same variable
    in a config file
    """

    class __Config:

        def __init__(self):

            self.__environment = {
                k.lower(): v for (k, v) in os.environ.items()
            }

            with open(_CONFIG_FILE, 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)

            environment = starmap(lambda k, v: (k.lower(), v), config['environment'].items())
            for key, value in environment:
                if key not in self.__environment:
                    self.__environment[key] = value
            self.__config = config['server_variables']

        def __getattr__(self, name: str):
            if name in self.__environment:
                return self.__environment[name]
            if name in self.__config:
                return self.__config[name]
            raise AttributeError(f'''context variable not found: \'{name}\'''')

    __instance = __Config()
    __set_up = False

    def __new__(cls):
        if not Context.__set_up:
            cls.__setup_log_level()
            Context.__set_up = True
        return Context.__instance

    @staticmethod
    def __setup_log_level():
        level = logging.INFO
        if hasattr(Context.__instance, 'log_level'):
            context_level = Context.__instance.log_level
            for log_level in _AVAILABLE_LOG_LEVELS:
                if context_level == logging.getLevelName(log_level):
                    level = log_level
                    break

        logging.basicConfig(level=level,
                            format=_LOG_FORMAT,
                            datefmt=_LOG_DATE_FORMAT)

        logging.info(f'Log level set to {logging.getLevelName(level)}')
