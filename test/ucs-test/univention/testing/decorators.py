from __future__ import print_function
import time
from typing import Any, Callable, TypeVar  # noqa F401

DEFAULT_TIMEOUT = 90  # seconds

F = TypeVar('F', bound=Callable[..., None])


class WaitForNonzeroResultOrTimeout(object):

	def __init__(self, func, timeout=DEFAULT_TIMEOUT):
		# type: (Callable[..., Any], int) -> None
		self.func = func
		self.timeout = timeout

	def __call__(self, *args, **kwargs):
		# type: (*Any, **Any) -> Any
		for i in range(self.timeout):
			result = self.func(*args, **kwargs)
			if result:
				break
			else:
				time.sleep(1)
		return result


class SetTimeout(object):

	def __init__(self, func, timeout=DEFAULT_TIMEOUT):
		# type: (Callable[..., None], int) -> None
		self.func = func
		self.timeout = timeout

	def __call__(self, *args, **kwargs):
		# type: (*Any, **Any) -> Any
		for i in range(self.timeout):
			try:
				print("** Entering", self.func.__name__)
				self.func(*args, **kwargs)
				print("** Exiting", self.func.__name__)
				break
			except Exception as ex:
				print("(%d)-- Exception cought: %s %s" % (i, type(ex), str(ex)))
				time.sleep(1)
		else:
			self.func(*args, **kwargs)


def setTimeout(func, timeout=DEFAULT_TIMEOUT):
	# type: (F, int) -> F
	def wrapper(*args, **kwargs):
		# type: (*Any, **Any) -> None
		for i in range(timeout):
			try:
				print("** Entering", func.__name__)
				func(*args, **kwargs)
				print("** Exiting", func.__name__)
				break
			except Exception as ex:
				print("(%d)-- Exception cought: %s %s" % (i, type(ex), str(ex)))
				time.sleep(1)
		else:
			func(*args, **kwargs)
	return wrapper

# vim: set ft=python ts=4 sw=4 et ai :
