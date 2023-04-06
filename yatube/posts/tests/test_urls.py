from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.user2 = User.objects.create_user(username='tester2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.urls_data = [
            ('/', HTTPStatus.OK, HTTPStatus.OK,),
            (f'/group/{cls.group.slug}/', HTTPStatus.OK, HTTPStatus.OK),
            (f'/posts/{cls.post.pk}/', HTTPStatus.OK, HTTPStatus.OK),
            (f'/posts/{cls.post.pk}/edit/', HTTPStatus.FOUND, HTTPStatus.OK),
            (f'/profile/{cls.user.username}/', HTTPStatus.OK, HTTPStatus.OK),
            ('/create/', HTTPStatus.FOUND, HTTPStatus.OK),
            ('/unexiting_page/', HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND),
            ('/follow/', HTTPStatus.FOUND, HTTPStatus.OK),
            (f'/profile/{cls.user2}/follow/',
                HTTPStatus.FOUND, HTTPStatus.FOUND),
            (f'/profile/{cls.user2}/unfollow/',
                HTTPStatus.FOUND, HTTPStatus.FOUND),
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(URLTests.user)
        cache.clear()

    def test_urls_are_available_for_guest(self):
        """ Проверка доступа к страницам без авторизации """
        for url, guest_status, _ in self.urls_data:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    guest_status,
                    f'Ошибка доступа к "{url}" без авторизации'
                )

    def test_urls_are_available_for_authorized(self):
        """ Проверка доступа с авторизацией """
        for url, _, user_status in self.urls_data:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    user_status,
                    f'Ошибка доступа к "{url}" с авторизацией'
                )

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = [
            ('posts/index.html', '/'),
            ('posts/group_list.html', f'/group/{self.group.slug}/'),
            ('posts/create_post.html', '/create/'),
            ('posts/post_detail.html', f'/posts/{self.post.pk}/'),
            ('posts/create_post.html', f'/posts/{self.post.pk}/edit/'),
            ('posts/profile.html', f'/profile/{self.user.username}/'),
            ('posts/follow.html', '/follow/'),
        ]
        for template, url in templates_url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Ошибка использования шаблона для адреса "{url}"'
                )

    def test_redirections_for_guest(self):
        """Переадресация гостя на недоступных страницах"""
        urls_for_authenticated = (
            f'/posts/{self.post.pk}/edit/',
            '/create/',
            '/follow/',
            f'/profile/{self.user}/follow/',
            f'/profile/{self.user}/unfollow/',
        )
        for url in urls_for_authenticated:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}'
                )

    def test_redirects_nonauthor_editing_post(self):
        """ Проверка переадресации неавтора при редактировании поста """
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_guest_cant_push_comments_and_posts(self):
        """Гость не может запушить посты и комментарий методом post"""
        form_data = {'text': 'test', }
        urls_for_posting = [
            f'/posts/{self.post.pk}/comment/',
            '/create/',
        ]
        for url in urls_for_posting:
            with self.subTest(url=url):
                response = self.guest_client.post(
                    url,
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}'
                )
