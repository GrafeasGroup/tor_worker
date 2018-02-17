import json
import os
import random


from tor_worker import cached_property


class helpers:  # pragma: no cover
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
        return json.load(helpers.load_file(path))

    @staticmethod
    def load_file(path):
        helpers.assert_valid_file(path)
        with open(path) as f:
            return f.read()


class RandomizedData(object):
    pass


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

    def __str__(self):
        if self.name == '[default]':
            return 'Default configuration'
        else:
            return f'/r/{self.name} configuration'

    # These should not change on a per-subreddit basis
    _protected_attributes = []

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


class Templates(DeserializerBase):
    """
    Deserializer for templates
    """

    def content(self, domain: str) -> str:
        post_type = self.url_type(domain)
        path = os.path.join(self._base, 'templates', post_type)

        # Check fro domain-specific instructions
        file_path = os.path.join(path, f'{domain}.md')
        if not helpers.is_valid_file(file_path):
            # Use default if no domain-specific instructions
            file_path = os.path.join(path, 'base.md')

        return helpers.load_file(file_path)

    def url_type(self, domain: str) -> str:
        if domain in self._settings.get('filters', {}).get('domains', {})\
                .get('images', []):
            return 'images'
        elif domain in self._settings.get('filters', {}).get('domains', {})\
                .get('video', []):
            return 'video'
        elif domain in self._settings.get('filters', {}).get('domains', {})\
                .get('audio', []):
            return 'audio'
        else:
            return 'other'


class PostConstraintSet(object):
    """
    Helper for filtering posts. Send it data and ``PostConstraintSet`` will say
    whether it is allowed.

        >>> filters = PostConstraintSet(_settings=data)
        >>> filters.url_allowed('www.example.com')
        True
        >>> filters.score_allowed(post_upvotes)
        False
    """

    def __init__(self, _settings={}):
        self._settings = _settings

    def url_allowed(self, domain: str) -> bool:
        """
        Checks if the url is on the whitelisted set of domains

            >>> constraints = PostConstraintSet(_settings=data)
            >>> constraints.url_allowed('www.example.com')
            True
            >>> constraints.url_allowed('www.example.net')
            False
        """
        if self._settings.get('bypass_domain_filter', False):
            return True

        images = self._settings.get('filters', {}).get('domains', {})\
            .get('images', [])
        video = self._settings.get('filters', {}).get('domains', {})\
            .get('video', [])
        audio = self._settings.get('filters', {}).get('domains', {})\
            .get('audio', [])

        allowed_domains = images + video + audio

        if len(allowed_domains) == 0:
            # Allow everything if there is no whitelist
            return True

        return bool(domain in allowed_domains)

    def score_allowed(self, score):
        """
        Checks if the post's score meets our pre-configured threshold
        """
        return score >= self._settings.get('upvote_filter', 0)


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
    _protected_attributes = ['environment']

    @cached_property
    def templates(self) -> Templates:
        return Templates(self._base, _settings=self._default)

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
    def gifs(self) -> RandomizedData:
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
        out = RandomizedData()
        for name, urls in self._settings['gifs'].items():
            setattr(out, name, random.choice(urls))
        return out

    @cached_property
    def filters(self):
        return PostConstraintSet(_settings=self._settings)

    @property
    def subreddits(self):
        path = os.path.join(self._base, 'bots', 'subreddits.json')
        data = helpers.load_json(path)
        return data.keys()

    @cached_property
    def _settings(self) -> dict:
        """
        Helper property to read bot settings scoped to the current subreddit
        """
        # Set the default using ``self._default``, but can be overridden when
        # object is initialized with the ``_settings`` param.
        return self._default

    @cached_property
    def _default(self) -> dict:
        """
        Helper property to read on-the-fly from the bot settings.json file
        """
        path = os.path.join(self._base, 'bots', 'settings.json')
        return helpers.load_json(path)