import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.core import signing
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class User(AbstractUser):
    """
    Catsmos 서비스 계정
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.CharField(max_length=255, unique=True)


class UnVerifiedUser(User):
    """
    이메일 미인증 유저
    """

    class Meta:
        proxy = True

    @property
    def temp_token(self):
        return get_random_string(length=20)

    @property
    def signed_email(self):
        return signing.dumps(self.email)

    def save(self, *args, **kwargs):
        # Set is_active to False
        self.is_active = False
        # Call the parent class's save method
        super().save(*args, **kwargs)


class Accountbyplanet(models.Model):
    """
    행성 별 별도 계정
    """

    nickname = models.CharField(max_length=15, blank=False, null=False)
    profile_image = ProcessedImageField(
        upload_to="accounts/",
        processors=[ResizeToFill(128, 128)],
        format="JPEG",
        options={"quality": 100},
        blank=True,
        null=True,
    )
    background_image = ProcessedImageField(
        upload_to="accounts/",
        processors=[ResizeToFill(500, 100)],
        format="JPEG",
        options={"quality": 100},
        blank=True,
        null=True,
    )
    followings = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="followers"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accountsbyplanet",
    )
    planet = models.ForeignKey("planets.Planet", on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_category = ((1, "user"), (2, "staff"), (3, "admin"))  # 행성 관리자 권한 설정
    admin_level = models.IntegerField(choices=admin_category, default=1)
    star = models.BooleanField(default=False)  # 즐겨찾기

    @property
    def has_star(self):
        """
        즐겨찾기 여부 판단
        """
        return self.star

    def delete(self, *args, **kwargs):
        """
        ccountbyplanet 삭제시 image file 삭제
        """
        if self.profile_image:
            path = self.profile_image.path
            if os.path.isfile(path):
                os.remove(path)
        if self.background_image:
            path = self.background_image.path
            if os.path.isfile(path):
                os.remove(path)
        super().delete(*args, **kwargs)


class Memobyplanet(models.Model):
    """
    행성 별로 별도 메모를 작성 가능 (optional)
    """

    memo = models.TextField(blank=True, null=True)
    accountbyplanet = models.ForeignKey(
        Accountbyplanet, on_delete=models.CASCADE, related_name="accountbyplanet"
    )
