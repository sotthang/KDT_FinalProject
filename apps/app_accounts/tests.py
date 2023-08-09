from django.test import TestCase
from .models import User, Accountbyplanet
from apps.app_planets.models import Planet

# Create your tests here.


class UserandAccountbyplanetModelTest(TestCase):
    # 테스트 계정 생성
    def setUp(self):
        self.user = User.objects.create(email="test@test.com")
        self.planet = Planet.objects.create(
            name="test",
            description="test description",
            category="Tech",
            plan="Free",
            is_public="Public",
            created_by_id=self.user.id,
        )
        self.accountbyplanet = Accountbyplanet.objects.create(
            nickname="test", user=self.user, planet=self.planet
        )

    # User email 테스트
    def test_email_label(self):
        field_label = self.user._meta.get_field("email").verbose_name
        self.assertEquals(field_label, "email")

    # User email 길이 테스트
    def test_email_max_length(self):
        max_length = self.user._meta.get_field("email").max_length
        self.assertEquals(max_length, 255)

    # User created_at 테스트
    def test_created_at_auto_now_add(self):
        created_at = self.user.created_at
        self.assertIsNotNone(created_at)

    # Accountbyplanet nickname 테스트
    def test_nickname_label(self):
        field_label = self.accountbyplanet._meta.get_field("nickname").verbose_name
        self.assertEquals(field_label, "nickname")
