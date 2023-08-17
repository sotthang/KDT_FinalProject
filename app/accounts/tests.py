from django import forms
from django.test import TestCase
from django.urls import reverse
from .models import User
from .forms import AccountbyplanetForm
from app.planets.forms import validate_inappropriate_words
from app.planets.models import InappropriateWord

# Create your tests here.

app_name = "accounts"


class AccountbyplanetFormTest(TestCase):
    """
    Accountbyplanet 닉네임에 부적절한 단어가 들어가는지 판단 여부 테스트
    """

    def setUp(self):
        """
        부적절한 단어 DB 생성
        """
        InappropriateWord.objects.create(word="존나")

    def test_clean_nickname_valid(self):
        """
        적절 단어 테스트
        """
        form = AccountbyplanetForm(data={"nickname": "초코"})
        self.assertTrue(form.is_valid())

    def test_clean_nickname_with_inappropriate_word(self):
        """
        부적절 단어 테스트
        """
        form = AccountbyplanetForm(data={"nickname": "존나1"})
        self.assertFalse(form.is_valid())
        self.assertIn("nickname", form.errors)

    def test_validate_inappropriate_words(self):
        """
        부적절 단어 validation 테스트
        """
        with self.assertRaises(forms.ValidationError) as context:
            validate_inappropriate_words("존나1")
        expected_error_message = "부적절한 단어 (존나) 이/가 포함되어 있습니다. 다시 작성해주세요."
        self.assertEqual(str(context.exception.messages[0]), expected_error_message)


class GetUserViewTest(TestCase):
    """
    회원가입 시 DB 에 중복되는 이메일 있는지 처리하는 함수 테스트
    """

    def test_check_existing_email(self):
        """
        존재하는 이메일을 사용하여 테스트
        """

        existing_email = "sotthang@gmail.com"
        User.objects.create(email=existing_email)

        response = self.client.get(
            reverse("accounts:get_user"), {"email": existing_email}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json())

    def test_check_non_existing_email(self):
        """
        존재하지 않는 이메일을 사용하여 테스트
        """

        non_existing_email = "nonexisting@example.com"

        response = self.client.get(
            reverse("accounts:get_user"), {"email": non_existing_email}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json())
