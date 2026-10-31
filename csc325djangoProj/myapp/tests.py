from importlib import import_module

from django.apps import apps
from django.test import SimpleTestCase
from django.urls import URLPattern, URLResolver


class ModelTests(SimpleTestCase):
	def test_app_models_have_primary_keys(self):
		app_config = apps.get_containing_app_config(__name__)
		self.assertIsNotNone(app_config, "myapp must be installed")

		models = list(app_config.get_models())
		self.assertTrue(models, "myapp should define at least one model")
		for model in models:
			with self.subTest(model=model.__name__):
				self.assertIsNotNone(model._meta.pk)


class ViewTests(SimpleTestCase):
	def test_app_url_patterns_have_callable_views(self):
		app_config = apps.get_containing_app_config(__name__)
		self.assertIsNotNone(app_config, "myapp must be installed")
		urls_module = import_module(f"{app_config.name}.urls")

		def patterns_have_callable_views(patterns):
			for pattern in patterns:
				if isinstance(pattern, URLResolver):
					if not patterns_have_callable_views(pattern.url_patterns):
						return False
				elif isinstance(pattern, URLPattern) and not callable(pattern.callback):
					return False
			return True

		self.assertTrue(urls_module.urlpatterns)
		self.assertTrue(patterns_have_callable_views(urls_module.urlpatterns))
