from django import forms
from django.test import TestCase
from .models import User, Accountbyplanet
from .forms import AccountbyplanetForm
from apps.app_planets.forms import validate_inappropriate_words
from apps.app_planets.models import Planet, InappropriateWord

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


class AccountbyplanetFormTest(TestCase):
    # 테스트 DB 생성
    def setUp(self):
        InappropriateWord.objects.create(word="존나")

    # validate_inappropriate_words 적절 단어 테스트
    def test_clean_nickname_valid(self):
        form = AccountbyplanetForm(data={"nickname": "초코"})
        self.assertTrue(form.is_valid())

    # validate_inappropriate_words 부적절 단어 테스트
    def test_clean_nickname_with_inappropriate_word(self):
        form = AccountbyplanetForm(data={"nickname": "존나1"})
        self.assertFalse(form.is_valid())
        self.assertIn("nickname", form.errors)

    # validate_inappropriate_words 부적절 단어 validation 테스트
    def test_validate_inappropriate_words(self):
        with self.assertRaises(forms.ValidationError) as context:
            validate_inappropriate_words("존나1")
        expected_error_message = "부적절한 단어 (존나) 이/가 포함되어 있습니다. 다시 작성해주세요."
        self.assertEqual(str(context.exception.messages[0]), expected_error_message)
