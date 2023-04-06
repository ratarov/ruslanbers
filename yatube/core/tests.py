from django.test import Client, TestCase


class CoreErrorTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_are_available_for_guest(self):
        """Страница 404 отдает кастомный шаблон"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertTemplateUsed(
            response,
            'core/404.html',
            'Страница 404 не использует кастомный шаблон'
        )
