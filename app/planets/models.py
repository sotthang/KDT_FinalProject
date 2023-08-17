import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.text import slugify
from datetime import timedelta, datetime
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from taggit.managers import TaggableManager
from app.accounts.models import Accountbyplanet
import secrets


# 시간 표시
def get_time_difference(created_at):
    time = datetime.now(tz=timezone.utc) - make_aware(created_at)

    if time < timedelta(minutes=1):
        return "방금 전"
    elif time < timedelta(hours=1):
        return str(int(time.seconds / 60)) + "분 전"
    elif time < timedelta(days=1):
        return str(int(time.seconds / 3600)) + "시간 전"
    elif time < timedelta(days=7):
        time = datetime.now(tz=timezone.utc).date() - created_at.date()
        return str(time.days) + "일 전"
    else:
        return created_at.strftime("%Y-%m-%d")


# 행성
class Planet(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    category_choices = (
        ("Tech", "Tech"),
        ("Game", "Game"),
        ("Music", "Music"),
        ("Sports", "Sports"),
        ("Food", "Food"),
        ("Hobby", "Hobby"),
    )
    category = models.CharField(max_length=20, choices=category_choices)
    image = ProcessedImageField(
        upload_to="planets/",
        processors=[ResizeToFill(256, 128)],
        format="JPEG",
        options={"quality": 100},
        blank=True,
        null=True,
    )
    plan_category = (("Free", "Free"), ("Premium", "Primium"))
    plan = models.CharField(max_length=10, choices=plan_category, default="Free")
    is_public_category = (("Private", "Private"), ("Public", "Public"))
    is_public = models.CharField(
        max_length=10, choices=is_public_category, default="Private"
    )
    # 가입 요청 확인 필요
    need_confirm_category = ((True, "Approval"), (False, "Direct"))
    need_confirm = models.BooleanField(choices=need_confirm_category, default=False)
    maximum_capacity = models.DecimalField(
        default=50, max_digits=1000, decimal_places=0
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invite_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

    # 초대코드 기간 확인
    def is_invite_code_valid(self):
        return self.expiration_date >= timezone.now()

    # 초대코드 생성
    def generate_invite_code(self):
        if self.invite_code and self.is_invite_code_valid():
            return self.invite_code

        # 유효한 초대 코드가 없는 경우 새로 생성
        invite_code = secrets.token_urlsafe(8)
        expiration_date = timezone.now() + timezone.timedelta(weeks=1)

        self.invite_code = invite_code
        self.expiration_date = expiration_date
        self.save()

        return invite_code

    # planets 삭제시 image file 삭제
    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


# 행성별 이용약관
class TermsOfService(models.Model):
    Planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    order = models.IntegerField()
    content = models.CharField(max_length=100, null=False, blank=False)


# 행성 내 게시글
class Post(models.Model):
    content = models.TextField()
    emotion = models.ManyToManyField(
        Accountbyplanet, related_name="emotion_post", through="Emote"
    )

    # 이미지 저장 위치 지정
    def upload_to_directory(instance, filename):
        planet_name_slug = slugify(instance.planet.name)
        return "planets/posts/{}/{}".format(planet_name_slug, filename)

    image = ProcessedImageField(
        upload_to=upload_to_directory,
        # processors = [ResizeToFill(800,400)],
        format="JPEG",
        options={"quality": 100},
        blank=True,
        null=True,
    )
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    accountbyplanet = models.ForeignKey(Accountbyplanet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    # post 시간 표시
    @property
    def created_time(self):
        return get_time_difference(self.created_at)

    # post 삭제시 image file 삭제
    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


# 행성 내 게시글의 댓글
class Comment(models.Model):
    content = models.TextField()
    emotion = models.ManyToManyField(
        Accountbyplanet, related_name="emotion_comment", through="Emote"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    accountbyplanet = models.ForeignKey(Accountbyplanet, on_delete=models.CASCADE)

    # comment 시간 표시
    @property
    def created_time(self):
        return get_time_difference(self.created_at)


# 행성 내 게시글의 대댓글
class Recomment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="recomments"
    )
    accountbyplanet = models.ForeignKey(Accountbyplanet, on_delete=models.CASCADE)

    # recomment 시간 표시
    @property
    def created_time(self):
        return get_time_difference(self.created_at)


# 게시글, 댓글 포함 감정표현
class Emote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    accountbyplanet = models.ForeignKey(Accountbyplanet, on_delete=models.CASCADE)
    emotion = models.CharField(max_length=10)


# 게시글 신고
class Report(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    recomment = models.ForeignKey(Recomment, on_delete=models.CASCADE, null=True)
    # 신고자
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 신고 내용 추가
    content = models.TextField()


# 부적절 단어 DB
class InappropriateWord(models.Model):
    word = models.CharField(max_length=30)

    def __str__(self):
        return self.word


# 투표주제
class VoteTopic(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True)


# 투표
class Vote(models.Model):
    votetopic = models.ForeignKey(VoteTopic, on_delete=models.CASCADE)
    voter = models.ForeignKey(Accountbyplanet, on_delete=models.CASCADE)
