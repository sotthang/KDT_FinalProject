from django.shortcuts import render, redirect, get_object_or_404
from .models import Accountbyplanet, User
from app.planets.models import Planet
from .forms import (
    AccountbyplanetForm,
    CustomAuthenticationForm,
    CustomUserCreationForm,
    CustomSetPasswordForm,
    CustomUserChangeForm,
)
from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView  # 비밀번호 리셋
from django.contrib.auth.tokens import default_token_generator
from django.views import View
from django.views.generic.detail import DetailView
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.core import signing  # 암호화
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from http import HTTPStatus


class LoginView(View):
    """
    로그인 처리
    """

    template_name = "accounts/login.html"

    def get(self, request):
        """
        이미 로그인 되어 있으면 main 으로 redirect
        안되어 있으면 로그인 페이지 렌더링
        """

        if request.user.is_authenticated:
            return redirect("planets:main")
        return render(
            request,
            self.template_name,
            {
                "form": CustomAuthenticationForm(),
            },
        )

    def post(self, request):
        """
        이미 로그인 되어 있으면 main 으로 redirect
        안되어 있으면 로그인 진행 후 main 으로 redirect
        로그인 실패하면 로그인 페이지에서 실패 문구 출력
        """

        if request.user.is_authenticated:
            return redirect("planets:main")
        form = CustomAuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            messages.error(request, "아이디 또는 패스워드를 확인해주세요.")
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                },
            )

        login(request, form.get_user())
        return redirect("planets:main")


class SignupView(View):
    """
    회원가입
    """

    template_name = "accounts/signup.html"

    def get(self, request):
        """
        이미 로그인 되어 있으면 main 으로 redirect
        안되어 있으면 회원가입 페이지 렌더링
        """

        if request.user.is_authenticated:
            return redirect("planets:main")
        return render(
            request,
            self.template_name,
            {
                "form": CustomUserCreationForm(),
            },
        )

    def post(self, request):
        """
        이미 로그인 되어 있으면 main 으로 redirect
        안되어 있으면 회원가입 진행 후 main 으로 redirect
        회원가입 실패하면 회원가입 페이지에서 실패 문구 출력
        """

        if request.user.is_authenticated:
            return redirect("planets:main")
        form = CustomUserCreationForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "양식을 확인해주세요.")
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                },
            )
        user = form.save(commit=False)
        user.save()
        request.session["temp_token"] = user.temp_token
        send_verification_email(request, user)

        return redirect(
            "accounts:verification_sent",
            signed_email=user.signed_email,
            token=user.temp_token,
        )


def get_user(request):
    """
    username, email 중복 체크
    """

    data = {}
    if "username" in request.GET:
        data["username"] = request.GET["username"]
    elif "email" in request.GET:
        data["email"] = request.GET["email"]

    try:
        users = User.objects.filter(**data)
        context = []
        for user in users:
            context = {
                "username": user.username,
                "email": user.email,
            }
        return JsonResponse(data=context, status=HTTPStatus.OK, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(data=[], status=HTTPStatus.NOT_FOUND)


class PasswordView(LoginRequiredMixin, View):
    """
    비밀번호 변경
    """

    template_name = "accounts/change_password.html"

    def get(self, request):
        """
        로그인 안되어 있으면 login 으로 redirect
        로그인 되어 있으면 비밀번호 변경 페이지 렌더링
        """

        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return render(
            request,
            self.template_name,
            {
                "form": PasswordChangeForm(request.user),
            },
        )

    def post(self, request):
        """
        로그인 안되어 있으면 login 으로 redirect
        로그인 되어 있으면 비밀번호 변경 진행 후 main 으로 redirect
        비밀번호 변경 실패하면 비밀번호 변경 페이지에서 실패 문구 출력
        """

        if not request.user.is_authenticated:
            return redirect("accounts:login")

        form = PasswordChangeForm(request.user, request.POST)
        if not form.is_valid():
            messages.error(request, "양식을 확인해주세요.")
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                },
            )
        update_session_auth_hash(request, form.save())
        return redirect("planets:main")


class ProfileUpdateView(LoginRequiredMixin, View):
    """
    메인 프로필
    """

    template_name = "accounts/update.html"

    def get(self, request):
        """
        로그인 안되어 있으면 login 으로 redirect
        로그인 되어 있으면 메인 프로필 수정 페이지 렌더링
        """

        if not request.user.is_authenticated:
            return redirect("accounts:login")

        return render(
            request,
            self.template_name,
            {"form": CustomUserChangeForm(instance=request.user)},
        )

    def post(self, request):
        """
        로그인 안되어 있으면 login 으로 redirect
        로그인 되어 있으면 프로필 정보 수정 진행 후 main 으로 redirect
        프로필 정보 수정 실패하면 프로필 정보 수정 페이지에서 실패 문구 출력
        """

        if not request.user.is_authenticated:
            return redirect("accounts:login")

        form = CustomUserChangeForm(request.POST, instance=request.user)
        if not form.is_valid():
            messages.error(request, "양식을 확인해주세요.")
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                },
            )
        form.save()
        return redirect("accounts:profile", username=request.user)


@login_required
def profile(request, username):
    """
    프로필 페이지
    """

    user = get_object_or_404(get_user_model(), username=username)
    user_by_planets = Accountbyplanet.objects.filter(user=user)

    return render(
        request,
        "accounts/profile.html",
        {
            "user": user,
            "user_by_planets_star": [
                accountbyplanet
                for accountbyplanet in user_by_planets
                if accountbyplanet.has_star
            ],  # 유저가 속한 행성 중 즐겨찾기 한 행성
            "user_by_planets_not_star": [
                accountbyplanet
                for accountbyplanet in user_by_planets
                if not accountbyplanet.has_star
            ],  # 유저가 속한 행성 중 즐겨찾기 안 한 행성
        },
    )


@login_required
def planet_profile(request, planet_name, nickname):
    """
    행성 별 프로필
    """
    planet = get_object_or_404(Planet, name=planet_name)
    user_by_planet = get_object_or_404(
        Accountbyplanet, planet=planet, nickname=nickname
    )
    request_user = Accountbyplanet.objects.get(planet=planet, user=request.user)

    context = {
        "user_by_planet": user_by_planet,
        "request_user": request_user,
    }
    return render(request, "accounts/planet_profile.html", context)


@login_required
def planet_profile_update(request, planet_name, nickname):
    """
    행성 별 프로필 수정
    """
    planet = get_object_or_404(Planet, name=planet_name)
    user_by_planet = get_object_or_404(
        Accountbyplanet, planet=planet, nickname=nickname
    )

    if user_by_planet.user == request.user:
        if request.method == "POST":
            planet_user_update_form = AccountbyplanetForm(
                request.POST, request.FILES, instance=user_by_planet
            )
            if planet_user_update_form.is_valid():
                planet_user_update_form.save()
                to_be_nickname = Accountbyplanet.objects.get(
                    planet=planet, user=request.user.pk
                ).nickname
                return redirect("planets:planet_profile", planet_name, to_be_nickname)
        else:
            planet_user_update_form = AccountbyplanetForm(instance=user_by_planet)

    context = {
        "planet": planet,
        "user_by_planet": user_by_planet,
        "planet_user_update_form": planet_user_update_form,
    }
    return render(request, "accounts/planet_update.html", context)


class find_id(View):
    """
    아이디 찾기
    """

    def get(self, request):
        """
        아이디 찾기 페이지 렌더링
        """

        return render(request, "accounts/find_id.html")

    def post(self, request):
        """
        아이디 찾기 진행
        """

        email = request.DATA.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        try:
            user_found = User.objects.get(
                email=email, first_name=first_name, last_name=last_name
            )
            context = {
                "user_found": user_found,
            }
            return render(request, "accounts/find_id_result.html", context)
        except:
            context = {"message": "일치하는 정보가 없습니다. "}
            return render(request, "accounts/find_id.html", context)


@login_required
def delete(request):
    """
    회원 탈퇴
    """
    request.user.delete()
    auth_logout(request)
    return redirect("planets:main")


@login_required
def logout(request):
    """
    로그아웃
    """
    auth_logout(request)
    return redirect("planets:main")


def send_verification_email(request, user):
    """
    메일 주소 인증
    """

    token = default_token_generator.make_token(user)  # 유저 토큰
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # uid는 유저pk를 암호화
    verification_link = reverse(
        "accounts:activate", kwargs={"uidb64": uid, "token": token}
    )
    verification_url = request.build_absolute_uri(verification_link)
    subject = "[캣츠모스] 계정 활성화"
    context = {
        "user": user,
        "verification_url": verification_url,
    }

    try:
        send_mail(
            subject,
            render_to_string("accounts/verification_email.txt", context),
            settings.EMAIL_HOST_USER,
            [user.email],
        )
    except BadHeaderError:
        return HttpResponse("Invalid header.")


def activation_view(request, uidb64, token):
    """
    메일 인증 페이지
    """

    try:
        uid = urlsafe_base64_decode(uidb64).decode("utf-8")  # 유저 pk
        user = User.objects.get(pk=int(uid))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return redirect("accounts:activation_failed")

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "accounts/activation.html")
    else:
        return redirect("accounts:activation_failed")


def verification_sent(request, signed_email, token):
    """
    메일 발송 후 페이지
    """
    try:
        user_email = signing.loads(signed_email)
        context = {"user_email": user_email}
        user = get_user_model().objects.get(email=user_email)
        session_token = request.session.get("temp_token")
        if request.GET.get("type") == "re":
            send_verification_email(request, user)
            return render(request, "accounts/verification_sent.html", context)
        elif session_token and session_token == token:
            del request.session["temp_token"]  # 세션에서 임시 토큰 삭제
            send_verification_email(request, user)
            return render(request, "accounts/verification_sent.html", context)
        else:
            return render(request, "accounts/verification_sent.html", context)
    except signing.BadSignature:
        return render(request, "accounts/not_found.html")


def password_reset_request(request):
    """
    비밀번호 초기화 이메일 전송
    """

    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]  # 폼에서 이메일 추출
            associated_users = get_user_model().objects.filter(email=data)  # 유저 검색

            # 유재 존재 여부
            if associated_users.exists():
                for user in associated_users:
                    subject = "[캣츠모스] 비밀번호 초기화"  # 이메일 제목
                    email_template_name = "accounts/password_reset_email.txt"  # 이메일 내용
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",  # settings.HOSTNAME
                        "site_name": "캣츠모스",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",  # settings.PROTOCOL,
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email,
                            settings.EMAIL_HOST_USER,
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return redirect("accounts:password_reset_done")
            else:
                messages.error(request, "존재하지 않는 이메일 주소입니다.")

    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="accounts/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    비밀번호 초기화
    """

    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("planets:main")
