from math import ceil
from time import sleep
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post, User

POSTS_SAMPLE = 104
POSTS_PER_PAGE = 10
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='tester1')
        cls.user2 = User.objects.create_user(username='tester2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовый пост 1'
        )
        sleep(0.1)
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Тестовый пост 2',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user1)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_page_names = [
            ('posts/index.html', reverse('posts:index')),
            ('posts/group_list.html', reverse(
                'posts:group_list',
                args=(self.group.slug, )
            )),
            ('posts/profile.html', reverse(
                'posts:profile',
                args=(self.user1.username, )
            )),
            ('posts/post_detail.html', reverse(
                'posts:post_detail',
                args=(self.post1.pk, )
            )),
            ('posts/create_post.html', reverse(
                'posts:post_edit',
                args=(self.post1.pk, )
            )),
            ('posts/create_post.html', reverse('posts:post_create'))
        ]
        for template, reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Ошибка шаблона для адреса "{reverse_name}"'
                )

    def object_context_tester(self, context_object, fixture_object):
        post_author = context_object.author.username
        post_text = context_object.text
        post_group = context_object.group.id
        post_image = context_object.image
        self.assertEqual(post_author, fixture_object.author.username)
        self.assertEqual(post_text, fixture_object.text)
        self.assertEqual(post_group, fixture_object.group.id)
        self.assertEqual(post_image, fixture_object.image)

    def test_index_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.object_context_tester(first_object, self.post2)
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_group_list_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug, ))
        )
        first_object = response.context['page_obj'][0]
        self.object_context_tester(first_object, self.post2)
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user2.username, ))
        )
        first_object = response.context['page_obj'][0]
        self.object_context_tester(first_object, self.post2)
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_detail_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post2.id, ))
        )
        object = response.context['post']
        self.object_context_tester(object, self.post2)

    def test_post_edit_shows_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=(self.post1.id, ))
        )
        form_fields = {
            'text': self.post1.text,
            'group': self.post1.group,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].initial[value]
                self.assertEqual(form_field, expected)
        self.assertEqual(response.context.get('form').instance, self.post1)

    def test_post_create_shows_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_comments_for_authorized_only(self):
        """Поле ввода комментария не видно гостю"""
        response = self.guest_client.get(
            reverse('posts:post_detail', args=(self.post1.id, ))
        )
        self.assertNotContains(response, "Добавить комментарий:")

    def test_index_page_cache(self):
        """Проверка хранения и очищения кэша главной страницы"""
        response_1 = self.guest_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user1,
            text='Новый пост'
        )
        response_2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            response_1.content,
            response_2.content,
            'Кэширование на главной не работает')
        cache.clear()
        response_3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response_2.content, response_3.content)


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        objs = [Post(author=cls.user, text='', group=cls.group)] * POSTS_SAMPLE
        Post.objects.bulk_create(objs, ignore_conflicts=True)

    def setUp(self):
        self.guest_client = Client()

    def test_paginator(self):
        """ Работа пагинатора на 1 и последней странице"""
        last_page = ceil(POSTS_SAMPLE / POSTS_PER_PAGE)
        posts_last_page = POSTS_SAMPLE - (last_page - 1) * POSTS_PER_PAGE
        pages_data = [(POSTS_PER_PAGE, 1), (posts_last_page, last_page)]
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug, )),
            reverse('posts:profile', args=(self.user.username, ))
        )
        for posts_on_page, page_number in pages_data:
            for url in urls:
                with self.subTest(url=url):
                    response = self.guest_client.get(
                        url, {'page': page_number}
                    )
                    self.assertEqual(
                        len(response.context['page_obj']),
                        posts_on_page,
                        f'Неверная работа пагинатора на {url}, '
                        f'страница №{page_number}'
                    )


class PostCreateViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост #1',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_post_appearance_at_main_group_profile(self):
        """ Появление поста на главной, в группе и в профайле """
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug, )),
            reverse('posts:profile', args=(self.user, ))
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_doesnt_appear_in_wrong_group(self):
        """ Появление поста не в той группе """
        response = self.guest_client.get(
            reverse('posts:group_list', args=(self.group2.slug, ))
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class FollowerViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='follower')
        cls.user2 = User.objects.create_user(username='author')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowerViewsTests.user1)

    def test_subscription_for_authorized(self):
        """Авторизованный пользователь создает и удаляет подписки"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.user2, ))
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user1, author=self.user2).exists(),
            'Новая подписка не создает верный объект класса Follow'
        )
        self.assertEqual(
            Follow.objects.count(),
            follow_count + 1,
            'Новая подписка не создает новый объект класса Follow'
        )
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.user2, ))
        )
        self.assertEqual(
            Follow.objects.count(),
            follow_count + 1,
            'Проверьте, что на автора нельзя подписаться 2 раза'
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.user2, ))
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user1, author=self.user2).exists(),
            'При отмене подписки в БД остается объект класса Follow'
        )
        self.assertEqual(
            Follow.objects.count(),
            follow_count,
            'При отмене подписки объект класса Follow не удаляется'
        )

    def test_follow_page_behavior(self):
        """Новые посты по подписке появляются только у подписчиков"""
        Follow.objects.create(user=self.user1, author=self.user2)
        post = Post.objects.create(author=self.user2, text='test')
        follower_response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.authorized_client.force_login(self.user2)
        following_response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            post,
            follower_response.context['page_obj'],
            'Новый пост не появился на странице подписчика'
        )
        self.assertNotIn(
            post,
            following_response.context['page_obj'],
            'Новый пост появился на странице неподписчика'
        )

    def test_user_cant_follow_himself(self):
        """Подписка на себя недоступна"""
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.user1, ))
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user1, author=self.user1).exists(),
            'Пользователь подписался сам на себя'
        )
