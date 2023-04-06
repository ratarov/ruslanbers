import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='tester')
        cls.post = Post.objects.create(
            text='Еще один тестовый пост',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_post_is_saved_in_db_when_created(self):
        """ Создается запись в БД при отправке формы со страницы /create """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'В результате создания поста кол-во постов в БД не изменилось')
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.user,
            ).exists(), 'Поля формы нового поста неверно сохраняются в БД'
        )

    def test_post_is_saved_in_db_when_edited(self):
        """ Результаты изменения поста сохраняются в БД """
        posts_count = Post.objects.count()
        new_data = {
            'text': 'Новыйтекст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=new_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'В результате редактирования изменяется кол-во постов'
        )
        self.assertTrue(
            Post.objects.filter(
                text=new_data['text'],
                group=new_data['group'],
                author=self.user,
            ).exists(),
            'Поля формы неверно сохраняются в БД при редактировании'
        )

    def test_post_page_shows_new_comments(self):
        """Новые комментарии появляются на странице поста"""
        comments_count = Comment.objects.count()
        comment_data = {'text': 'Комментарий', }
        response = self.authorized_client.post(
            f'/posts/{self.post.pk}/comment/',
            data=comment_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            'Новые комментарии не появляются'
        )
        self.assertTrue(
            Comment.objects.filter(
                text=comment_data['text'],
                author=self.user,
            ).exists(),
            'Данные комментария неверно сохраняются в БД'
        )
