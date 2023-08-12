from django.shortcuts import render, redirect
from .forms import CustomUserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Accountbyplanet, User
from apps.app_planets.models import Planet
from .forms import (
    AccountbyplanetForm,
    CustomAuthentication,
    CustomUserCreationForm,
    CustomSetPasswordForm,
)
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.views import View
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.core import signing  # 암호화
from django.utils.crypto import get_random_string  # 토큰
from django.shortcuts import get_object_or_404

# 이메일
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes

# from base64 import urlsafe_base64_decode
from django.urls import reverse

# 비밀번호 리셋
from django.contrib.auth.views import PasswordResetConfirmView


def login(request):
    if request.user.is_authenticated:
        return redirect("planets:main")

    if request.method == "POST":
        form = CustomAuthentication(request, request.POST)
        if not form.is_valid():
            messages.error(request, "아이디 또는 패스워드를 확인해주세요.")
        else:
            auth_login(request, form.get_user())
            return redirect("planets:main")
    else:
        form = CustomAuthentication()

    context = {
        "form": form,
    }
    return render(request, "accounts/login.html", context)


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if not form.is_valid():
            messages.error(request, "패스워드를 확인해주세요.")
        else:
            update_session_auth_hash(request, form.save())
            return redirect("planets:main")
    else:
        form = PasswordChangeForm(request.user)
    context = {
        "form": form,
    }
    return render(request, "accounts/change_password.html", context)


# 회원가입
def signup(request):
    # 이미 로그인한 경우
    if request.user.is_authenticated:
        return redirect("planets:main")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # 회원가입 O, 계정활성화 X
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            temp_token = get_random_string(length=20)  # 임시 토큰 생성
            request.session["temp_token"] = temp_token
            # 이메일 주소 암호화
            signed_email = signing.dumps(user.email)

            # send_verification_email(request, user)
            return redirect(
                "accounts:verification_sent",
                signed_email=signed_email,
                token=temp_token,
            )
    else:
        form = CustomUserCreationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/signup.html", context)


# username 중복 체크
def check_username(request):
    try:
        User.objects.get(username=request.GET.get("username"))
        check = True
    except ObjectDoesNotExist:
        check = False
    response_data = {"check": check}
    return JsonResponse(response_data)


# email 중복 체크
def check_email(request):
    try:
        User.objects.get(email=request.GET.get("email"))
        check = True
    except ObjectDoesNotExist:
        check = False
    response_data = {"check": check}
    return JsonResponse(response_data)


# 최상위 프로필
def profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    user_by_planets_star = Accountbyplanet.objects.filter(user=user, star=1)
    user_by_planets_not_star = Accountbyplanet.objects.filter(user=user, star=0)

    context = {
        "user": user,
        "user_by_planets_star": user_by_planets_star,  # 유저가 속한 행성 중 즐겨찾기 한 행성
        "user_by_planets_not_star": user_by_planets_not_star,  # 유저가 속한 행성 중 즐겨찾기 안 한 행성
    }
    return render(request, "accounts/profile.html", context)


# 최상위 프로필 업데이트
@login_required
def profile_update(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect("accounts:profile", username=request.user)
    else:
        form = CustomUserChangeForm(instance=request.user)

    context = {"form": form}
    return render(request, "accounts/update.html", context)


# 행성별 프로필
def planet_profile(request, planet_name, nickname):
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


# 행성별 프로필 업데이트
@login_required
def planet_profile_update(request, planet_name, nickname):
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


# 아이디 찾기
class find_id(View):
    def get(self, request):
        return render(request, "accounts/find_id.html")

    def post(self, request):
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        try:
            # 입력받은 정보로 유저 검색
            user_found = User.objects.get(
                email=email, first_name=first_name, last_name=last_name
            )
            context = {
                "user_found": user_found,
            }
            # 일치하는 정보의 유저가 있다면 결과 페이지로 이동
            return render(request, "accounts/find_id_result.html", context)

        except:
            # 일치하는 정보의 유저가 없으면 메시지 출력 후 다시 아이디를 찾을 수 있도록 함
            context = {"message": "일치하는 정보가 없습니다. "}
            return render(request, "accounts/find_id.html", context)


# 계정 삭제
@login_required
def delete(request):
    # 계정 정보 삭제 후 로그아웃
    request.user.delete()
    auth_logout(request)
    return redirect("planets:main")


# 로그아웃
@login_required
def logout(request):
    auth_logout(request)
    return redirect("planets:main")


# 메일 주소 인증(회원가입 중)
def send_verification_email(request, user):
    token = default_token_generator.make_token(user)  # 유저 토큰
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # uid는 유저pk를 암호화

    verification_link = reverse(
        "accounts:activate", kwargs={"uidb64": uid, "token": token}
    )
    verification_url = request.build_absolute_uri(verification_link)

    subject = "[캣츠모스] 계정 활성화"

    # 이메일 템플릿에 전달할 컨텍스트 생성
    context = {
        "user": user,
        "verification_url": verification_url,
    }

    # 이메일 내용을 렌더링
    email_text = render_to_string("accounts/verification_email.txt", context)

    # 이메일 전송
    try:
        send_mail(
            subject,
            email_text,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
    except BadHeaderError:
        return HttpResponse("Invalid header.")


# 메일 인증 페이지(메일에 담긴 링크)
def activation_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode("utf-8")  # 유저 pk
        user = User.objects.get(pk=int(uid))

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        # 유효하지 않은 uidb64 값이거나 해당하는 유저가 없는 경우 처리
        return redirect("accounts:activation_failed")

    # 토큰이 유효한 경우
    if default_token_generator.check_token(user, token):
        # 계정 활성화
        user.is_active = True
        user.save()

        return render(request, "accounts/activation.html")
    else:
        # 토큰이 유효하지 않은 경우 처리
        return redirect("accounts:activation_failed")


# 계정활성화 메일 보냈다는 view
def verification_sent(request, signed_email, token):
    try:
        # 이메일 복호화
        user_email = signing.loads(signed_email)
        context = {"user_email": user_email}

        type = request.GET.get("type")

        user = get_user_model()
        user = user.objects.get(email=user_email)

        session_token = request.session.get("temp_token")

        if type == "re":
            send_verification_email(request, user)
            return render(request, "accounts/verification_sent.html", context)
        elif session_token and session_token == token:
            del request.session["temp_token"]  # 세션에서 임시 토큰 삭제
            send_verification_email(request, user)
            return render(request, "accounts/verification_sent.html", context)
        else:
            # return render(request, 'accounts/not_found.html')
            return render(request, "accounts/verification_sent.html", context)

    except signing.BadSignature:
        # 암호화된 이메일 주소가 올바르지 않은 경우 처리
        return render(request, "accounts/not_found.html")


# 비밀번호 초기화 이메일 전송
def password_reset_request(request):
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
                        # local: '127.0.0.1:8000', prod: 'abc.herokuapp.com'
                        "domain": "127.0.0.1:8000",  # settings.HOSTNAME
                        "site_name": "캣츠모스",
                        # MTE4
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        # local: http, prod: https
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

            else:  # 유저가 존재 하지 않음
                messages.error(request, "존재하지 않는 이메일 주소입니다.")

    else:
        password_reset_form = PasswordResetForm()

    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="accounts/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("planets:main")
