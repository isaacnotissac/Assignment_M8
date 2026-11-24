from importlib import import_module

from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import URLPattern, URLResolver

from .models import Category, Task


class ModelTests(TestCase):
	def test_app_models_have_primary_keys(self):
		app_config = apps.get_containing_app_config(__name__)
		self.assertIsNotNone(app_config, "myapp must be installed")

		models = list(app_config.get_models())
		self.assertTrue(models, "myapp should define at least one model")
		for model in models:
			with self.subTest(model=model.__name__):
				self.assertIsNotNone(model._meta.pk)

	def test_task_defaults_and_category_relationship(self):
		category = Category.objects.create(name="School")
		task = Task.objects.create(title="Finish assignment", category=category)

		self.assertEqual(task.status, Task.Status.TODO)
		self.assertEqual(task.category, category)
		self.assertEqual(category.tasks.get(), task)
		self.assertEqual(str(task), "Finish assignment")
		self.assertEqual(str(category), "School")

	def test_category_can_be_deleted_without_deleting_tasks(self):
		category = Category.objects.create(name="School")
		task = Task.objects.create(title="Finish assignment", category=category)

		category.delete()
		task.refresh_from_db()

		self.assertIsNone(task.category)


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


class TaskViewTests(TestCase):
	def test_home_links_to_task_list(self):
		response = self.client.get("/")

		self.assertContains(response, 'href="/tasks/"')

	def test_task_list_displays_tasks(self):
		Task.objects.create(title="Review notes")

		response = self.client.get("/tasks/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Review notes")

	def test_task_create_saves_valid_task_and_redirects(self):
		response = self.client.post(
			"/tasks/new/",
			{
				"title": "Submit project",
				"description": "Upload the final files",
				"status": Task.Status.IN_PROGRESS,
				"due_date": "2026-12-01",
			},
		)

		self.assertRedirects(response, "/tasks/")
		self.assertTrue(
			Task.objects.filter(
				title="Submit project",
				status=Task.Status.IN_PROGRESS,
			).exists()
		)

	def test_task_create_shows_errors_for_invalid_data(self):
		response = self.client.post("/tasks/new/", {"title": ""})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "This field is required.")
		self.assertEqual(Task.objects.count(), 0)
