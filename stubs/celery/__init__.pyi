from typing import Any

class Task: ...

class Celery(object):
  conf = None  # type: Any

  def __init__(self, *args, **kwargs): ...

class App:
  task = None  # type: Any

def signature(*args, **kwargs) -> Any: ...

current_app = App()
signals = None  # type: Any
