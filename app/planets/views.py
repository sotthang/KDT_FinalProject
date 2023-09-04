import json
import secrets
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q, Sum, Case, When, IntegerField
from .models import (
    Planet,
    TermsOfService,
    Post,
    Comment,
    Recomment,
    Emote,
    Report,
    Vote,
    VoteTopic,
)
from .forms import PlanetForm, PostForm, CommentForm, RecommentForm, VoteTopicForm
from app.accounts.models import Accountbyplanet, User, Memobyplanet
from app.accounts.forms import AccountbyplanetForm, MemobyplanetForm
from datetime import timedelta
from taggit.models import Tag


def planet_list(request):
    """
    행성 리스트
    """

    planets = Planet.objects.filter(is_public="Public")
    user = request.user
    if user.is_authenticated:
        joined_planet_list = [
            joined_planet.name
            for joined_planet in [
                user_planet.planet
                for user_planet in Accountbyplanet.objects.filter(
                    user=user, planet__in=planets
                )
            ]
        ]
    else:
        joined_planet_list = None

    for planet in planets:
        planet.current_capacity = Accountbyplanet.objects.filter(planet=planet).count()

    return render(
        request,
        "planets/planet_list.html",
        {
            "planets": planets,
            "joined_planet_list": joined_planet_list,
        },
    )


def filter(request, category):
    """
    행성 카테고리 필터
    """

    planets = Planet.objects.filter(category=category, is_public="Public").order_by(
        "-created_at"
    )
    user = request.user
    if user.is_authenticated:
        joined_planet_list = [
            joined_planet.name
            for joined_planet in [
                user_planet.planet
                for user_planet in Accountbyplanet.objects.filter(
                    user=user, planet__in=planets
                )
            ]
        ]
    else:
        joined_planet_list = None

    for planet in planets:
        planet.current_capacity = Accountbyplanet.objects.filter(planet=planet).count()

    return render(
        request,
        "planets/planet_list.html",
        {
            "planets": planets,
            "joined_planet_list": joined_planet_list,
        },
    )


def my_planet_filter(request):
    """
    내가 가입한 행성
    """

    user = request.user
    if user.is_authenticated:
        planets = Planet.objects.filter(is_public="Public")
        user_planets = Accountbyplanet.objects.filter(user=user, planet__in=planets)
        joined_planets = [user_planet.planet for user_planet in user_planets]
        joined_planet_list = [joined_planet.name for joined_planet in joined_planets]
        for planet in joined_planets:
            planet.current_capacity = Accountbyplanet.objects.filter(
                planet=planet
            ).count()
    else:
        return redirect("accounts:login")

    return render(
        request,
        "planets/planet_list.html",
        {"planets": joined_planets, "joined_planet_list": joined_planet_list},
    )


class PlanetCreateView(View):
    """
    행성 생성
    """

    template_name = "planets/planet_create.html"

    def get(self, request):
        """
        행성 생성 페이지 렌더링
        """

        return render(
            request,
            self.template_name,
            {
                "form": PlanetForm(),
            },
        )

    def post(self, request):
        """
        행성 생성 후 조인 페이지로 redirect
        행성 생성 실패하면 회원가입 페이지에서 실패 문구 출력
        """

        form = PlanetForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "양식을 확인해주세요.")
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                },
            )
        planet = form.save(commit=False)
        planet.created_by = request.user
        planet.save()

        if planet.is_public == "Private":
            invite_code = secrets.token_urlsafe(8)
            expiration_date = timezone.now() + timedelta(days=7)
            planet.invite_code = invite_code
            planet.expiration_date = expiration_date
            planet.save()

        for i in range(1, int(request.POST.get("termsofservice_count", 0)) + 1):
            TermsOfService.objects.create(
                Planet=planet,
                order=i,
                content=request.POST.get(f"term_content_{i}", ""),
            )

        return redirect("planets:planet_join", planet.name)


def search(request):
    """
    행성 검색
    """

    query = request.POST.get("q")
    planets = Planet.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query), is_public="Public"
    )  # 제목 또는 설명에 검색어가 포함되는 행성 필터
    user = request.user
    if user.is_authenticated:
        joined_planet_list = [
            joined_planet.name
            for joined_planet in [
                user_planet.planet
                for user_planet in Accountbyplanet.objects.filter(
                    user=user, planet__in=planets
                )
            ]
        ]
    else:
        joined_planet_list = None

    for planet in planets:
        planet.current_capacity = Accountbyplanet.objects.filter(planet=planet).count()

    return render(
        request,
        "planets/planet_list.html",
        {
            "planets": planets,
            "joined_planet_list": joined_planet_list,
        },
    )


@login_required
def planet_contract(request, planet_name):
    """
    행성 이용약관
    """

    planet = Planet.objects.get(name=planet_name)

    # 이미 행성에 계정이 있는 경우
    if Accountbyplanet.objects.filter(planet=planet, user=request.user).exists():
        return redirect("planets:index", planet_name)

    # 행성 최대 인원 초과하는 경우
    if Accountbyplanet.objects.filter(planet=planet).count() >= planet.maximum_capacity:
        messages.warning(request, "행성 최대 인원을 초과하여 가입을 진행할 수 없습니다.")
        return redirect("planets:main")

    termsofservice = TermsOfService.objects.filter(Planet_id=planet.pk)

    return render(
        request,
        "planets/planet_contract.html",
        {
            "termsofservice": termsofservice,
            "planet": planet,
        },
    )


class PlanetJoinView(View):
    """
    행성 가입
    """

    template_name = "planets/planet_join.html"

    def get(self, request, planet_name):
        """
        행성 가입 페이지 렌더링
        """

        return render(
            request,
            "planets/planet_join.html",
            {
                "form": AccountbyplanetForm(),
                "planet": Planet.objects.get(name=planet_name),
            },
        )

    def post(self, request, planet_name):
        """
        행성 가입 후 행성의 index 페이지로 redirect
        행성 가입 실패하면 행성 가입 페이지에서 실패 문구 출력
        """

        planet = Planet.objects.get(name=planet_name)
        form = AccountbyplanetForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "양식을 확인해주세요.")
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                },
            )
        accountbyplanet = form.save(commit=False)
        accountbyplanet.planet = planet
        accountbyplanet.user = request.user

        if planet.created_by == request.user:  # 행성 주인일 경우
            accountbyplanet.admin_level = 3
            accountbyplanet.is_confirmed = True
        elif not planet.need_confirm:  # 가입 승인이 필요 없는 경우
            accountbyplanet.is_confirmed = True
        elif planet.need_confirm:  # 가입 승인이 필요한 경우
            messages.success(request, "신청이 완료되었습니다")

        accountbyplanet.save()
        return redirect("planets:index", planet_name)


@login_required
def planet_withdraw(request, planet_name):
    """
    행성 탈퇴
    """

    Accountbyplanet.objects.get(
        planet=Planet.objects.get(name=planet_name), user=request.user
    ).delete()
    return redirect("planets:planet_list")


@login_required
def index(request, planet_name):
    """
    행성 index 페이지
    """

    planet = Planet.objects.get(name=planet_name)

    if (
        not request.user.is_authenticated
        or not Accountbyplanet.objects.filter(planet=planet, user=request.user).exists()
        or Accountbyplanet.objects.get(planet=planet, user=request.user).is_confirmed
        == False
    ):  # 행성에 계정이 없는 경우 또는 가입 승인 대기 중인 경우
        return redirect("planets:main")

    try:
        memo = Memobyplanet.objects.get(
            accountbyplanet=Accountbyplanet.objects.get(
                planet=planet, user=request.user
            )
        )
    except ObjectDoesNotExist:
        memo = None

    return render(
        request,
        "planets/index.html",
        {
            "votetopicform": VoteTopicForm(),
            "postform": PostForm(),
            "planet": planet,
            "memo": memo,
            "memoform": MemobyplanetForm(),
            "user": Accountbyplanet.objects.get(planet=planet, user=request.user),
        },
    )


@login_required
def index_list(request, planet_name):
    """
    행성 내 myplanets 페이지
    """

    planet = Planet.objects.get(name=planet_name)
    user_planets = Accountbyplanet.objects.filter(user=request.user)
    user_categories = user_planets.values_list("planet__category", flat=True).distinct()
    planet_recommends = (
        Planet.objects.filter(category__in=user_categories, is_public="Public")
        .exclude(accountbyplanet__in=user_planets)
        .order_by("?")[:5]
    )
    planet_not_recommends = (
        Planet.objects.exclude(category__in=user_categories)
        .exclude(accountbyplanet__in=user_planets)
        .exclude(is_public="Private")
        .order_by("?")[:5]
    )[: max(0, 5 - len(planet_recommends))]

    try:
        memo = Memobyplanet.objects.get(
            accountbyplanet=Accountbyplanet.objects.get(
                planet=planet, user=request.user
            )
        )
    except:
        memo = None

    if (
        not request.user.is_authenticated
        or not Accountbyplanet.objects.filter(planet=planet, user=request.user).exists()
        or not Accountbyplanet.objects.get(
            planet=planet, user=request.user
        ).is_confirmed
    ):  # 행성에 계정이 없는 경우 또는 가입 승인 대기 중인 경우
        return redirect("planets:main")

    return render(
        request,
        "planets/index_list.html",
        {
            "votetopicform": VoteTopicForm(),
            "postform": PostForm(),
            "planet": planet,
            "memo": memo,
            "memoform": MemobyplanetForm(),
            "user_by_planets_star": Accountbyplanet.objects.filter(
                user=request.user, star=1
            ),
            "user_by_planets_not_star": Accountbyplanet.objects.filter(
                user=request.user, star=0
            ),
            "first_post": Post.objects.filter(planet=planet).first(),
            "user": Accountbyplanet.objects.get(planet=planet, user=request.user),
            "planet_recommends": planet_recommends,
            "planet_not_recommends": planet_not_recommends,
        },
    )


@login_required
def planet_introduction(request, planet_name):
    """
    행성 내 소개 페이지
    """

    planet = Planet.objects.get(name=planet_name)
    planet.current_capacity = Accountbyplanet.objects.filter(planet=planet).count()

    try:
        memo = Memobyplanet.objects.get(
            accountbyplanet=Accountbyplanet.objects.get(
                planet=planet, user=request.user
            )
        )
    except:
        memo = None

    return render(
        request,
        "planets/planet_introduction.html",
        {
            "accounts": Accountbyplanet.objects.filter(planet=planet),
            "planet": planet,
            "memo": memo,
            "memoform": MemobyplanetForm(),
            "user": Accountbyplanet.objects.get(planet=planet, user=request.user),
            "postform": PostForm(),
        },
    )


@login_required
def planet_delete(request, planet_name):
    """
    행성 삭제
    """

    planet = Planet.objects.get(name=planet_name)
    if planet.created_by == request.user:
        planet.delete()
    return redirect("planets:main")


@login_required
def planet_posts(request, planet_name):
    """
    게시글 read json
    """

    planet = Planet.objects.get(name=planet_name)
    posts = Post.objects.filter(planet=planet).order_by("-pk")
    page_number = request.POST.get("page")
    paginator = Paginator(posts, 5)  # 5개씩

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    post_list = []
    user = Accountbyplanet.objects.get(user=request.user, planet=planet)
    for post in posts:
        vote_topics = VoteTopic.objects.filter(post=post)
        voted_topics = list(
            Vote.objects.filter(
                voter=user, votetopic__in=VoteTopic.objects.filter(post=post)
            ).values_list("votetopic_id", flat=True)
        )

        post_list.append(
            {
                "pk": post.pk,
                "content": post.content,
                "created_time": post.created_time,
                "nickname": post.accountbyplanet.nickname,
                "image_url": post.image.url if post.image else None,
                "tags": list(post.tags.names()),
                "profile_image_url": post.accountbyplanet.profile_image.url
                if post.accountbyplanet.profile_image
                else None,
                "user": post.accountbyplanet.user.username,
                "votetopics": list(post.votetopic_set.values("title")),
                "post_emote_heart": Emote.objects.filter(
                    post=post, emotion="heart"
                ).count(),
                "post_emote_thumbsup": Emote.objects.filter(
                    post=post, emotion="thumbsup"
                ).count(),
                "post_emote_thumbsdown": Emote.objects.filter(
                    post=post, emotion="thumbsdown"
                ).count(),
                "vote_count": [
                    Vote.objects.filter(votetopic=vote_topic).count()
                    for vote_topic in vote_topics
                ],
                "voted": True if voted_topics else False,
            }
        )

    if posts.has_next():
        return JsonResponse(post_list, safe=False)
    else:
        post_list.append(None)
        return JsonResponse(post_list, safe=False)


@require_POST
def post_create(request, planet_name, post_pk=None):
    """
    게시글 생성 및 수정
    """

    planet = Planet.objects.get(name=planet_name)
    form = PostForm(request.POST, request.FILES)
    votetopicform = VoteTopicForm(request.POST)
    accountbyplanet = Accountbyplanet.objects.get(planet=planet, user=request.user)

    if post_pk:  # 기존 게시글 수정 처리
        try:
            post = Post.objects.get(pk=post_pk, planet=planet)
            if form.is_valid():
                form = PostForm(request.POST, request.FILES, instance=post)
                if form.has_changed():  # 폼 데이터가 변경되었는지 확인
                    post = form.save(commit=False)
                    post.save()
                    form.save_m2m()
            else:
                form = PostForm(instance=post)
        except Post.DoesNotExist:
            return JsonResponse({"success": False, "errors": "Post not found"})
    else:  # 새로운 게시글 생성
        if form.is_valid():
            post = form.save(commit=False)
            post.accountbyplanet = accountbyplanet
            post.planet = planet
            post.image = form.cleaned_data["image"]
            post.save()
            form.save_m2m()
        if votetopicform.is_valid():  # 투표
            titles = request.POST.getlist("title")
            for title in titles:
                if title == "":
                    continue
                votetopic = VoteTopic()
                votetopic.title = title
                votetopic.post = post
                votetopic.save()
        else:
            errors = form.errors.as_json()
            return JsonResponse({"success": False, "errors": errors})

    vote_topics = VoteTopic.objects.filter(post=post)

    response_data = {
        "success": True,
        "post_pk": post.pk,
        "content": post.content,
        "created_time": post.created_time,
        "nickname": post.accountbyplanet.nickname,
        "image_url": post.image.url if post.image else None,
        "tags": list(post.tags.names()),
        "profile_image_url": post.accountbyplanet.profile_image.url
        if post.accountbyplanet.profile_image
        else None,
        "user": post.accountbyplanet.user.username,
        "form_html": form.as_p() if form.as_p() else None,
        "votetopics": list(post.votetopic_set.values("title")),
        "vote_count": [
            Vote.objects.filter(votetopic=vote_topic).count()
            for vote_topic in vote_topics
        ],
        "voted": bool(
            list(
                Vote.objects.filter(
                    voter=accountbyplanet, votetopic__in=vote_topics
                ).values_list("votetopic_id", flat=True)
            )
        ),
    }
    try:
        response_data["votetopic"] = titles
    except NameError:
        response_data["votetopic"] = None

    return JsonResponse(response_data)


@require_POST
def post_delete(request, planet_name, post_pk):
    """
    게시글 삭제
    """

    post = Post.objects.get(pk=post_pk)
    accountbyplanet = Accountbyplanet.objects.get(
        user=request.user.pk, planet=Planet.objects.get(name=planet_name)
    )

    if accountbyplanet == post.accountbyplanet or accountbyplanet.admin_level > 1:
        post.delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@login_required
def post_detail(request, planet_name, post_pk):
    """
    게시글 상세
    """

    post = Post.objects.get(pk=post_pk)
    planet = Planet.objects.get(name=planet_name)
    accountbyplanet = Accountbyplanet.objects.get(planet=planet, user=request.user)
    vote_topics = VoteTopic.objects.filter(post=post)
    vote_count = [
        Vote.objects.filter(votetopic=vote_topic).count() for vote_topic in vote_topics
    ]

    try:
        memo = Memobyplanet.objects.get(accountbyplanet=accountbyplanet)
    except:
        memo = None

    return render(
        request,
        "planets/planet_detail.html",
        {
            "votetopicform": VoteTopicForm(),
            "postform": PostForm(),
            "post": post,
            "comments": Comment.objects.filter(post=post),
            "planet": planet,
            "commentform": CommentForm(),
            "recommentform": RecommentForm(),
            "memo": memo,
            "memoform": MemobyplanetForm(),
            "post_emotion_heart": Emote.objects.filter(post=post, emotion="heart"),
            "post_emotion_thumbsup": Emote.objects.filter(
                post=post, emotion="thumbsup"
            ),
            "post_emotion_thumbsdown": Emote.objects.filter(
                post=post, emotion="thumbsdown"
            ),
            "user": Accountbyplanet.objects.get(user=request.user.pk, planet=planet),
            "votetopics_count": zip(vote_topics, vote_count),
            "total_vote_count": sum(vote_count),
            "voted": True
            if list(
                Vote.objects.filter(
                    voter=accountbyplanet, votetopic__in=vote_topics
                ).values_list("votetopic_id", flat=True)
            )
            else False,
            "vote_topics": vote_topics,
        },
    )


@login_required
def detail_comments(request, planet_name, post_pk):
    """
    댓글 read json
    """

    comments = []
    for comment in Comment.objects.filter(post_id=post_pk):
        recomments = []
        for recomment in Recomment.objects.filter(comment=comment.pk):
            recomments.append(
                {
                    "pk": recomment.pk,
                    "content": recomment.content,
                    "created_time": recomment.created_time,
                    "nickname": recomment.accountbyplanet.nickname,
                    "profile_image_url": recomment.accountbyplanet.profile_image.url
                    if recomment.accountbyplanet.profile_image
                    else None,
                }
            )
        comments.append(
            {
                "pk": comment.pk,
                "content": comment.content,
                "created_time": comment.created_time,
                "nickname": comment.accountbyplanet.nickname,
                "profile_image_url": comment.accountbyplanet.profile_image.url
                if comment.accountbyplanet.profile_image
                else None,
                "user": comment.accountbyplanet.user.username,
                "recomments": recomments,
                "comment_emote_heart": Emote.objects.filter(
                    comment=comment, emotion="heart"
                ).count(),
                "comment_emote_thumbsup": Emote.objects.filter(
                    comment=comment, emotion="thumbsup"
                ).count(),
                "comment_emote_thumbsdown": Emote.objects.filter(
                    comment=comment, emotion="thumbsdown"
                ).count(),
            }
        )
    return JsonResponse(comments, safe=False)


@require_POST
def comment_create(request, planet_name, post_pk, comment_pk=None):
    """
    댓글 생성 및 수정
    """
    planet = Planet.objects.get(name=planet_name)
    post = Post.objects.get(pk=post_pk, planet=planet)
    form = CommentForm(request.POST)

    if comment_pk:  # 기존 댓글 수정 처리
        try:
            comment = Comment.objects.get(pk=comment_pk)
            if form.is_valid():
                form = CommentForm(request.POST, instance=comment)
                if form.has_changed():  # 폼 데이터가 변경되었는지 확인
                    comment = form.save(commit=False)
                    comment.save()
            else:
                form = CommentForm(instance=comment)
        except Comment.DoesNotExist:
            return JsonResponse({"success": False, "errors": "Comment not found"})
    else:  # 새로운 댓글 생성
        if form.is_valid():
            comment = form.save(commit=False)
            comment.accountbyplanet = Accountbyplanet.objects.get(
                planet=planet, user=request.user
            )
            comment.planet = planet
            comment.content = form.cleaned_data["content"]
            comment.post = post
            comment.save()
        else:
            errors = form.errors.as_json()
            return JsonResponse({"success": False, "errors": errors})

    return JsonResponse(
        {
            "success": True,
            "comment_pk": comment.pk,
            "content": comment.content,
            "created_time": comment.created_time,
            "nickname": comment.accountbyplanet.nickname,
            "profile_image_url": comment.accountbyplanet.profile_image.url
            if comment.accountbyplanet.profile_image
            else None,
            "user": comment.accountbyplanet.user.username,
            "form_html": form.as_p() if form.as_p() else None,
        }
    )


@require_POST
def comment_delete(request, planet_name, comment_pk):
    """
    # 댓글 삭제
    """

    comment = Comment.objects.get(pk=comment_pk)
    accountbyplanet = Accountbyplanet.objects.get(
        user=request.user.pk, planet=Planet.objects.get(name=planet_name)
    )

    if accountbyplanet == comment.accountbyplanet or accountbyplanet.admin_level > 1:
        if Recomment.objects.filter(comment=comment).exists():  # 대댓글이 있는 상태에서 댓글 삭제
            comment.content = "이미 삭제된 댓글입니다."
            comment.save()
            return JsonResponse(
                {"success": "Change", "comment_content": comment.content}
            )
        else:  # 대댓글 없는 경우
            comment.delete()
            return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@require_POST
def recomment_create(request, planet_name, post_pk, comment_pk, recomment_pk=None):
    """
    대댓글 생성
    """

    planet = Planet.objects.get(name=planet_name)
    post = Post.objects.get(pk=post_pk, planet=planet)
    comment = Comment.objects.get(pk=comment_pk, post=post)
    form = RecommentForm(request.POST)

    if recomment_pk:  # 기존 대댓글 수정 처리
        try:
            recomment = Recomment.objects.get(pk=recomment_pk)
            if form.is_valid():
                form = RecommentForm(request.POST, instance=recomment)
                if form.has_changed():  # 폼 데이터가 변경되었는지 확인
                    recomment = form.save(commit=False)
                    recomment.save()
            else:
                form = RecommentForm(instance=recomment)
        except Recomment.DoesNotExist:
            return JsonResponse({"success": False, "errors": "Recomment not found"})
    else:  # 새로운 대댓글 생성
        if form.is_valid():
            recomment = form.save(commit=False)
            recomment.accountbyplanet = Accountbyplanet.objects.get(
                planet=planet, user=request.user
            )
            recomment.planet = planet
            recomment.content = form.cleaned_data["content"]
            recomment.post = post
            recomment.comment = comment
            recomment.save()
        else:
            errors = form.errors.as_json()
            return JsonResponse({"success": False, "errors": errors})

    return JsonResponse(
        {
            "success": True,
            "recomment_pk": recomment.pk,
            "content": recomment.content,
            "created_time": recomment.created_time,
            "nickname": recomment.accountbyplanet.nickname,
            "profile_image_url": recomment.accountbyplanet.profile_image.url
            if recomment.accountbyplanet.profile_image
            else None,
            "user": recomment.accountbyplanet.user.username,
            "form_html": form.as_p() if form.as_p() else None,
        }
    )


@require_POST
def recomment_delete(request, planet_name, recomment_pk):
    """
    대댓글 삭제
    """

    recomment = Recomment.objects.get(pk=recomment_pk)
    accountbyplanet = Accountbyplanet.objects.get(
        user=request.user.pk, planet=Planet.objects.get(name=planet_name)
    )

    if accountbyplanet == recomment.accountbyplanet or accountbyplanet.admin_level > 1:
        recomment.delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@login_required
def planet_admin(request, planet_name):
    """
    행성 관리 페이지
    """

    planet = Planet.objects.get(name=planet_name)
    # 관리자인 경우 관리 페이지 접근 가능
    is_staff = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level
        == 2
        else False
    )
    is_manager = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level
        == 3
        else False
    )

    if is_staff or is_manager:
        if request.method == "POST":
            form_planet = PlanetForm(request.POST, request.FILES, instance=planet)
            if form_planet.is_valid():
                form_planet.save()
                return redirect("planets:index", planet.name)
        else:
            form_planet = PlanetForm(instance=planet)

        planet.generate_invite_code()  # 초대코드 갱신

        return render(
            request,
            "planets/planet_admin.html",
            {
                "form_planet": form_planet,
                "planet": planet,
                "is_manager": is_manager,
            },
        )
    else:
        messages.warning(request, "관리자만 접근 가능합니다. ")
        return redirect("planets:main")


@login_required
def planet_tos_admin(request, planet_name):
    """
    행성 약관 관리 페이지
    """

    planet = Planet.objects.get(name=planet_name)
    is_staff = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level > 1
        else False
    )
    if is_staff:
        TOSs = TermsOfService.objects.filter(Planet_id=planet.pk)
        length = TOSs.count()
        if request.method == "POST":
            termsofservice_count = int(request.POST.get("termsofservice_count", 0))
            # 기존 약관 DB 삭제
            old_term = TermsOfService.objects.filter(Planet=planet)
            old_term.delete()
            # 이용 약관 저장
            for i in range(1, termsofservice_count + 1):
                term_content = request.POST.get(f"term_content_{i}", "")
                TermsOfService.objects.create(
                    Planet=planet, order=i, content=term_content
                )

            return redirect("planets:planet_admin", planet_name)
        else:
            return render(
                request,
                "planets/planet_tos_admin.html",
                {
                    "planet": planet,
                    "TOSs": TOSs,
                    "length": length,
                },
            )
    else:
        messages.warning(request, "관리자만 접근 가능합니다. ")
        return redirect("planets:main")


@login_required
def planet_join_admin(request, planet_name):
    """
    행성 가입 관리
    """

    planet = Planet.objects.get(name=planet_name)
    is_staff = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level > 1
        else False
    )
    if is_staff:
        confirms = Accountbyplanet.objects.filter(planet=planet, is_confirmed=False)
        return render(
            request,
            "planets/planet_join_admin.html",
            {
                "planet": planet,
                "confirms": confirms,
            },
        )
    else:
        messages.warning(request, "관리자만 접근 가능합니다. ")
        return redirect("planets:main")


@login_required
def planet_join_confirm(request, planet_name, user_pk):
    """
    행성 가입 승인
    """

    planet = Planet.objects.get(name=planet_name)
    is_staff = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level > 1
        else False
    )
    if is_staff:
        account = Accountbyplanet.objects.get(
            planet=planet, user=User.objects.get(pk=user_pk)
        )
        account.is_confirmed = True
        account.save()
        return JsonResponse({"success": True})
    else:
        messages.warning(request, "관리자만 접근 가능합니다.")
        return redirect("planets:main")


@login_required
def planet_join_reject(request, planet_name, user_pk):
    """
    행성 가입 거절
    """

    planet = Planet.objects.get(name=planet_name)
    is_staff = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level > 1
        else False
    )
    if is_staff:
        user = User.objects.get(pk=user_pk)
        account = Accountbyplanet.objects.get(planet=planet, user=user)
        account.delete()
        return JsonResponse({"success": True})
    else:
        messages.warning(request, "관리자만 접근 가능합니다.")
        return redirect("planets:main")


@login_required
def report(request, planet_name, report_category, pk):
    """
    게시글 신고 기능
    """

    planet = Planet.objects.get(name=planet_name)
    user = request.user
    accountbyplanet = Accountbyplanet.objects.get(planet=planet, user=user)
    if request.method == "POST":
        content = request.POST.get("report_content")
        if report_category == "post":
            post = Post.objects.get(pk=pk)
            if not Report.objects.filter(post=post, user=user):
                Report.objects.create(post=post, content=content, user=user)
                messages.info(request, "신고가 완료되었습니다.")
            else:
                messages.warning(request, "이미 신고한 게시글입니다.")
        elif report_category == "comment":
            comment = Comment.objects.get(pk=pk)
            if not Report.objects.filter(comment=comment, user=user):
                Report.objects.create(comment=comment, content=content, user=user)
                messages.info(request, "신고가 완료되었습니다.")
            else:
                messages.warning(request, "이미 신고한 댓글입니다.")
        else:
            recomment = Recomment.objects.get(pk=pk)
            if not Report.objects.filter(recomment=recomment, user=user):
                Report.objects.create(recomment=recomment, content=content, user=user)
                messages.info(request, "신고가 완료되었습니다.")
            else:
                messages.warning(request, "이미 신고한 댓글입니다.")
        return redirect("planets:index", planet.name)
    else:
        if report_category == "post":
            post = Post.objects.get(pk=pk)
            if accountbyplanet == post.accountbyplanet:
                messages.warning(request, "본인의 게시물은 신고할 수 없습니다. ")
                return redirect("planets:index", planet.name)
            else:
                context = {
                    "reported": post,
                }
        elif report_category == "comment":
            comment = Comment.objects.get(pk=pk)
            if accountbyplanet == comment.accountbyplanet:
                messages.warning(request, "본인의 댓글은 신고할 수 없습니다. ")
                return redirect("planets:index", planet.name)
            else:
                context = {
                    "reported": comment,
                }
        else:
            recomment = Recomment.objects.get(pk=pk)
            if accountbyplanet == recomment.accountbyplanet:
                messages.warning(request, "본인의 대댓글은 신고할 수 없습니다. ")
                return redirect("planets:index", planet.name)
            else:
                context = {
                    "reported": recomment,
                }
        context["category"] = report_category
        context["planet"] = planet
        context["pk"] = pk
        context["user"] = Accountbyplanet.objects.get(planet=planet, user=request.user)
        context["user_id"] = request.user
        return render(request, "planets/report.html", context)


def admin_report(request, planet_name):
    """
    신고 관리 페이지
    """

    planet = Planet.objects.get(name=planet_name)
    is_manager = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level
        == 3
        else False
    )
    if is_manager:
        post_reports = Report.objects.exclude(post__isnull=True)
        comment_reports = Report.objects.exclude(comment__isnull=True)
        recomment_reports = Report.objects.exclude(recomment__isnull=True)
        post_reports_count = (
            Report.objects.exclude(post__isnull=True)
            .values("post")
            .annotate(Count("pk"))
        )
        comment_reports_count = (
            Report.objects.exclude(comment__isnull=True)
            .values("comment")
            .annotate(Count("pk"))
        )
        recomment_reports_count = (
            Report.objects.exclude(recomment__isnull=True)
            .values("recomment")
            .annotate(Count("pk"))
        )
        return render(
            request,
            "planets/admin_report.html",
            {
                "planet": planet,
                "post_reports": post_reports,
                "post_reports_count": post_reports_count,
                "comment_reports": comment_reports,
                "comment_reports_count": comment_reports_count,
                "recomment_reports": recomment_reports,
                "recomment_reports_count": recomment_reports_count,
            },
        )
    else:
        messages.warning(request, "매니저만 접근 가능합니다.")
        return redirect("planets:main")


def admin_member(request, planet_name):
    """
    행성 회원 관리
    """

    planet = Planet.objects.get(name=planet_name)
    is_manager = (
        True
        if Accountbyplanet.objects.get(planet=planet, user=request.user).admin_level
        == 3
        else False
    )
    if is_manager:
        if request.method == "POST":
            accounts = request.POST.getlist("account_pk")
            for pk in accounts:
                admin_levels = request.POST.get("admin_level_" + pk)
                temp = Accountbyplanet.objects.get(planet=planet, pk=pk)
                temp.admin_level = admin_levels
                temp.save()
            return redirect("planets:planet_admin", planet_name)
        accounts = Accountbyplanet.objects.filter(planet=planet)
        return render(
            request,
            "planets/admin_member.html",
            {
                "accounts": accounts,
                "planet_name": planet_name,
            },
        )
    else:
        messages.warning(request, "매니저만 접근 가능합니다.")
        return redirect("planets:main")


@login_required
def invite_create(request):
    """
    초대 코드 생성
    """

    invite_code = json.loads(request.body.decode("utf-8"))["user_input"]
    planets = Planet.objects.filter(is_public="Private")
    for planet in planets:
        planet.generate_invite_code()  # 초대코드 갱신
    try:
        planet = Planet.objects.get(invite_code=invite_code)
        return JsonResponse({"result": True, "invite_code": invite_code})
    except ObjectDoesNotExist:
        return JsonResponse({"result": False, "invite_code": "실패"})


@login_required
def invite_check(request, invite_code):
    """
    초대 확인
    """

    return render(
        request,
        "planets/invite_check.html",
        {
            "planet": Planet.objects.get(invite_code=invite_code),
            "invite_code": invite_code,
        },
    )


@login_required
def following(request, planet_name, user_pk):
    """
    팔로우
    """

    planet = Planet.objects.get(name=planet_name)
    to_user = Accountbyplanet.objects.get(planet=planet, pk=user_pk)
    from_user = Accountbyplanet.objects.get(planet=planet, user=request.user)
    if to_user != from_user:
        if to_user.followers.filter(pk=from_user.pk).exists():
            to_user.followers.remove(from_user)
            is_followed = False
        else:
            to_user.followers.add(from_user)
            is_followed = True
        return JsonResponse(
            {
                "is_followed": is_followed,
                "following_count": to_user.followings.count(),
                "follower_count": to_user.followers.count(),
                "from_user_name": from_user.nickname,
                "from_user_pk": from_user.pk,
            }
        )
    return redirect("planets:index", planet_name)


@login_required
def vote(request, post_pk, vote_title):
    """
    투표
    """

    post = Post.objects.get(pk=post_pk)
    user = Accountbyplanet.objects.get(user=request.user, planet=post.planet)
    vote_topic = VoteTopic.objects.get(title=vote_title, post=post)
    if request.method == "POST":
        if Vote.objects.filter(voter=user, votetopic__post=post).exists():
            return redirect("planets:index", post.planet.name)
        vote = Vote(votetopic=vote_topic, voter=user)
        vote.save()
        return JsonResponse(
            {
                "result": "success",
                "planet_name": post.planet.name,
            }
        )


@login_required
def post_emote(request, planet_name, post_pk, emotion):
    """
    비동기 post emote
    """

    planet = Planet.objects.get(name=planet_name)
    post = Post.objects.get(pk=post_pk)
    user = Accountbyplanet.objects.get(planet=planet, user=request.user)
    emote = Emote.objects.filter(post=post, accountbyplanet=user, emotion=emotion)
    if emote.exists():
        emote.delete()
    else:
        Emote.objects.create(post=post, accountbyplanet=user, emotion=emotion)
    return JsonResponse(
        {"emotion_count": Emote.objects.filter(post=post, emotion=emotion).count()}
    )


@login_required
def comment_emote(request, planet_name, post_pk, comment_pk, emotion):
    """
    비동기 comment emote
    """

    planet = Planet.objects.get(name=planet_name)
    comment = Comment.objects.get(pk=comment_pk)
    user = Accountbyplanet.objects.get(planet=planet, user=request.user)
    emote = Emote.objects.filter(comment=comment, accountbyplanet=user, emotion=emotion)
    if emote.exists():
        emote.delete()
    else:
        Emote.objects.create(comment=comment, accountbyplanet=user, emotion=emotion)
    return JsonResponse(
        {
            "emotion_count": Emote.objects.filter(
                comment=comment, emotion=emotion
            ).count()
        }
    )


@login_required
def tags_list(request, planet_name):
    """
    tags 리스트 페이지
    """

    planet = Planet.objects.get(name=planet_name)
    posts = Post.objects.filter(
        planet=planet, created_at__gte=timezone.now() - datetime.timedelta(weeks=2)
    )
    tags = (
        Tag.objects.filter(post__in=posts)
        .annotate(tag_count=Count("post"))
        .order_by("-tag_count")[:5]
    )
    accountbyplanet = Accountbyplanet.objects.get(planet=planet, user=request.user)
    try:
        memo = Memobyplanet.objects.get(accountbyplanet=accountbyplanet)
    except:
        memo = None
    return render(
        request,
        "planets/planet_tags.html",
        {
            "postform": PostForm(),
            "memo": memo,
            "memoform": MemobyplanetForm(),
            "tags": tags,
            "total_posts": sum([tag.tag_count for tag in tags]),
            "planet": planet,
            "user": accountbyplanet,
            "user_id": request.user,
        },
    )


@login_required
def post_tag(request, planet_name, tag_name):
    """
    tag 페이지
    """

    planet = Planet.objects.get(name=planet_name)
    tag = Tag.objects.get(name=tag_name)
    accountbyplanet = Accountbyplanet.objects.get(planet=planet, user=request.user)
    posts = (
        Post.objects.filter(planet=planet, tags=tag)
        .order_by("-pk")
        .annotate(
            heart_count=Count("emote", filter=Q(emote__emotion="heart")),
            thumbsup_count=Count("emote", filter=Q(emote__emotion="thumbsup")),
            thumbsdown_count=Count("emote", filter=Q(emote__emotion="thumbsdown")),
        )
    )
    for post in posts:
        post.vote_topics = VoteTopic.objects.filter(post=post)
        post.vote_counts = []
        for vote_topic in post.vote_topics:
            vote_count = Vote.objects.filter(votetopic=vote_topic).count()
            post.vote_counts.append(
                {"vote_topic": vote_topic, "vote_count": vote_count}
            )
        post.voted = Vote.objects.filter(
            votetopic__in=post.vote_topics, voter=accountbyplanet
        ).exists()
        post.total_vote_count = Vote.objects.filter(
            votetopic__in=post.vote_topics
        ).aggregate(
            total=Sum(
                Case(
                    When(voter__isnull=False, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        )[
            "total"
        ]

    try:
        memo = Memobyplanet.objects.get(accountbyplanet=accountbyplanet)
    except:
        memo = None
    return render(
        request,
        "planets/planet_posts_filter.html",
        {
            "postform": PostForm(),
            "posts": posts,
            "memo": memo,
            "memoform": MemobyplanetForm(),
            "planet": planet,
            "user": accountbyplanet,
            "user_id": request.user,
        },
    )


@login_required
def planet_memo(request, planet_name):
    """
    메모
    """

    planet = Planet.objects.get(name=planet_name)
    accountbyplanet = Accountbyplanet.objects.get(planet=planet, user=request.user)
    memoform = MemobyplanetForm(request.POST)
    try:
        memo = Memobyplanet.objects.get(accountbyplanet=accountbyplanet)
    except:
        memo = None

    if memo:  # 기존 메모 수정 처리
        try:
            if memoform.is_valid() and request.POST:
                memoform = MemobyplanetForm(request.POST, instance=memo)
                if memoform.has_changed():  # 폼 데이터가 변경되었는지 확인
                    memoform = MemobyplanetForm(request.POST, instance=memo)
                    memo = memoform.save(commit=False)
                    memo.save()
                else:
                    memo.delete()
                    memo = None
            else:
                memoform = MemobyplanetForm(instance=memo)
        except Memobyplanet.DoesNotExist:
            return JsonResponse({"success": False, "errors": "Memo not found"})
    else:  # 새로운 메모 생성
        if memoform.is_valid():
            memo = memoform.save(commit=False)
            memo.accountbyplanet = accountbyplanet
            memo.save()
        else:
            errors = memoform.errors.as_json()
            return JsonResponse({"success": False, "errors": errors})
    return JsonResponse(
        {
            "success": True,
            "memo": memo.memo if memo else memo,
            "memoform": memoform.as_p() if memoform.as_p() else None,
        }
    )


@login_required
def planet_star(request, planet_name):
    """
    행성 즐겨찾기
    """

    planet = Planet.objects.get(name=planet_name)
    accountbyplanet = Accountbyplanet.objects.get(planet=planet, user=request.user)
    if accountbyplanet.star == False:
        accountbyplanet.star = True
    else:
        accountbyplanet.star = False
    accountbyplanet.save()
    return JsonResponse(
        {
            "success": True,
            "star": accountbyplanet.star,
        }
    )


def post_search(request, planet_name):
    """
    행성 내 post 검색
    """

    planet = Planet.objects.get(name=planet_name)
    keyword = request.GET.get("keyword", False)
    search_results = Post.objects.filter(
        Q(planet=planet, content__icontains=keyword)
        | Q(planet=planet, tags__name__icontains=keyword)
    ).order_by("-pk")
    user = Accountbyplanet.objects.get(planet=planet, user=request.user)

    for post in search_results:
        post.heart_count = Emote.objects.filter(post=post, emotion="heart").count()
        post.thumbsup_count = Emote.objects.filter(
            post=post, emotion="thumbsup"
        ).count()
        post.thumbsdown_count = Emote.objects.filter(
            post=post, emotion="thumbsdown"
        ).count()
        post.vote_topics = VoteTopic.objects.filter(post=post)
        post.vote_counts = []
        for vote_topic in post.vote_topics:
            vote_count = Vote.objects.filter(votetopic=vote_topic).count()
            post.vote_counts.append(
                {"vote_topic": vote_topic, "vote_count": vote_count}
            )
        post.voted = Vote.objects.filter(
            votetopic__in=post.vote_topics, voter=user
        ).exists()
        post.total_vote_count = Vote.objects.filter(
            votetopic__in=post.vote_topics
        ).aggregate(
            total=Sum(
                Case(
                    When(voter__isnull=False, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        )[
            "total"
        ]

    try:
        memo = Memobyplanet.objects.get(accountbyplanet=user)
    except:
        memo = None
    return render(
        request,
        "planets/planet_posts_filter.html",
        {
            "posts": search_results,
            "planet": planet,
            "user": user,
            "postform": PostForm(),
            "memo": memo,
            "memoform": MemobyplanetForm(),
            "user_id": request.user,
        },
    )
