from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from .models import Accountbyplanet, Memobyplanet
from django.contrib.auth.forms import SetPasswordForm
from apps.app_planets.forms import validate_inappropriate_words


# 새 비밀번호 변경 form
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].widget.attrs.update(
            {"class": "", "style": "border: 2px solid red;"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "", "style": "border: 2px solid red;"}
        )


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta(UserChangeForm):
        model = get_user_model()
        fields = (
            "old_password",
            "new_password1",
            "new_password2",
        )


class AccountbyplanetForm(forms.ModelForm):
    nickname = forms.CharField(
        label="닉네임",
        widget=forms.TextInput(
            attrs={
                "class": "form-input mt-1 rounded-md bg-[#101013]",
                "style": "height: 47px;",
            }
        ),
    )

    class Meta:
        model = Accountbyplanet
        fields = ("nickname", "profile_image", "background_image")

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"]
        validate_inappropriate_words(nickname)
        return nickname


class CustomAuthentication(AuthenticationForm):
    username = forms.CharField(
        label=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control block py-2.5 px-0 w-full text-sm text-white-900 bg-transparent border-0 border-b-2 border-gray-400 appearance-none dark:text-white dark:focus:border-yellow-500 focus:outline-none focus:ring-0 focus:border-yellow-600 peer",
                "placeholder": "아이디",
                "style": "height: 47px;",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control block py-2.5 px-0 w-full text-sm text-white-900 bg-transparent border-0 border-b-2 border-gray-400 appearance-none dark:text-white dark:focus:border-yellow-500 focus:outline-none focus:ring-0 focus:border-yellow-600 peer",
                "placeholder": "비밀번호",
                "style": "height: 47px;",
                "autocomplete": "current-password",
            }
        ),
    )

    class Meta:
        model = get_user_model
        fields = ("username", "password")


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "last_name",
            "first_name",
            "email",
            "password1",
            "password2",
        )


class AdminLevelForm(forms.ModelForm):
    class Meta:
        model = Accountbyplanet
        fields = ("admin_level",)


class MemobyplanetForm(forms.ModelForm):
    class Meta:
        model = Memobyplanet
        fields = ("memo",)

    memo = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-input mt-1 rounded-md border-yellow-100 bg-yellow-100 focus:outline-none focus:ring-0 appearance-none placeholder-gray-600 placeholder:text-sm",
                "style": "width: 100%; height: 80%;",
                "placeholder": "메모 작성",
            }
        ),
        required=False,
    )
