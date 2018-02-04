import json
import os
import random

from tor_worker import cached_property


class helpers:
    """
    Helper methods that are pulled out for an easier time with unit testing
    """

    @staticmethod
    def is_valid_directory(path):
        return os.path.isdir(path)

    @staticmethod
    def assert_valid_directory(path):
        if not helpers.is_valid_directory(path):
            raise NotADirectoryError(f'{repr(path)} is not '
                                     f'a valid directory')

    @staticmethod
    def is_valid_file(path):
        return os.path.isfile(path)

    @staticmethod
    def assert_valid_file(path):
        if not helpers.is_valid_file(path):
            raise FileNotFoundError(f'{repr(path)} is not '
                                    f'a valid file path')

    @staticmethod
    def load_json(path):
        helpers.assert_valid_file(path)
        with open(path) as f:
            return json.load(f.read())


class DeserializerBase(object):
    _base = os.environ.get('TOR_CONFIG_PATH', '.')

    def __init__(self, base_path=None, _settings=None, _name=None):
        # Default value is set as a class variable for easier stubbing
        # We offer an option to update it on instantiating a new class
        if base_path:
            self._base = base_path

        # Set the subreddit name here, if it's a specific one
        self.name = _name if _name else '[default]'

        # Allow for inserting the settings as a factory pattern
        if _settings:
            self._settings = _settings
        else:
            helpers.assert_valid_directory(self._base)


class Templates(DeserializerBase):
    """
    Deserializer for templates
    """


class Config(DeserializerBase):
    """
    Deserializer base for configuration file contents

    This is the main entry point for the whole of the configuration set.

    EXAMPLE::
        >>> config = Config.subreddit('TranscribersOfReddit')
        >>> config.gifs.no
        'https://gfycat.com/HeavenlyElderlyHornet'
        >>> config.gifs.no
        'https://gfycat.com/PowerlessLikableHarvestmouse'
        >>> config.env
        'development'
    """

    # These should not change on a per-subreddit basis
    _protected_attributes = ['environment']

    @classmethod
    def subreddit(cls, name: str) -> 'Config':
        """
        A factory method for overlaying subreddit-specific configurations onto
        the default ones.

        :param name: the target subreddit (case-sensitive)
        :return: subreddit-specific configurations flattened
        """
        defaults = helpers.load_json(os.path.join(cls._base, 'bots',
                                                  'settings.json'))
        subreddit = helpers.load_json(os.path.join(cls._base, 'bots',
                                                   'subreddits.json'))
        # non-mutating way of combining these 2 dicts
        data = {**defaults,
                **subreddit.get(name, {})}
        # Revert protected attributes to global defaults
        for attr in cls._protected_attributes:
            data[attr] = defaults[attr]

        return cls(_settings=data, _name=name)

    @cached_property
    def templates(self) -> Templates:
        return Templates(self.base)

    @property
    def env(self) -> str:
        """
        The current operating environment, used as a basis for
        environment-specific safeguards. Possible options are:
            - 'development'
            - 'testing'
            - 'production'
        """
        return self._settings.get('environment', 'development')

    @property
    def gifs(self) -> object:
        """
        A property for accessing random GIFs for every occasion, randomized
        every time this property is accessed.

        EXAMPLE:
            >>> config = Config()
            >>> config.gifs.no
            'https://gfycat.com/HeavenlyElderlyHornet'
            >>> config.gifs.thumbs_up
            'http://i.imgur.com/QMPRHW9.gif'

        Note that the GIF urls above are randomized every time ``config.gifs``
        is accessed.
        """
        out = object()
        for name, urls in self._settings['gifs'].items():
            setattr(out, name, random.choice(urls))
        return out

    @cached_property
    def _settings(self) -> dict:
        """
        Helper property to read on-the-fly from the bot settings.json file
        """
        path = os.path.join(self._base, 'bots', 'settings.json')
        return helpers.load_json(path)
