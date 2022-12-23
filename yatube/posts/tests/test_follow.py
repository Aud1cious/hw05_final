import shutil
import tempfile


from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

file = b"\x01\x02\x03"
test_image = SimpleUploadedFile(
    name="file.png", content=file, content_type="image/png"
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.author = User.objects.create_user(username="author")
        cls.authorized_client = Client()
        cls.user = User.objects.create_user(username="user")
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="test_group",
            slug="test_slug",
            description="test_description",
        )
        cls.post = Post.objects.create(
            text="test_post",
            group=cls.group,
            author=cls.author,
            image=test_image,
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_follow(self):
        URL = reverse("posts:profile_follow", args=[self.author.username])
        followers_before = Follow.objects.count()
        self.assertFalse(
            Follow.objects.filter(
                user=self.user, author=self.author
            ).exists()
        )
        self.authorized_client.get(URL, follow=True)
        self.assertEqual(Follow.objects.count(), followers_before + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user, author=self.author
            ).exists()
        )

    def test_unfollow(self):
        URL = reverse("posts:profile_unfollow", args=[self.author.username])
        Follow.objects.create(user=self.user, author=self.author)
        followers_before = Follow.objects.count()
        self.authorized_client.get(URL, follow=True)
        self.assertEqual(Follow.objects.count(), followers_before - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user, author=self.author
            ).exists()
        )
