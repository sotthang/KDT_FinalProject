from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path("login/", views.login, name="login"),
    path("membership/", views.membership, name="membership"),
    path("services/", views.services, name="services"),
    path("signup/", views.signup, name="signup"),
    path('password/', views.change_password, name='change_password'),
    path("contract/", views.contract, name="contract"),
    path('activate/<str:uidb64>/<str:token>/', views.activation_view, name='activate'), # 이메일 인증
    path('activation-failed/', views.activation_failed_view, name='activation_failed'), # 유효하지 않은 접근일떄
    path('verification-sent/<str:signed_email>/<str:token>/', views.verification_sent, name='verification_sent'), # 메일 보내고 나서!
    # 최상위 프로필
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('find_id/', views.find_id.as_view(), name='find_id'),
    path('delete/', views.delete, name='delete'),
    path('logout/', views.logout, name='logout'),
    # 비밀번호 초기화
    path('password_reset/', views.password_reset_request, name="password_reset"), # 이메일 적는 url
    path('password_reset/done/', # 이메일 전송후 url
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', # 비밀번호 초기화 url
    views.CustomPasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
    name='password_reset_confirm'),
]


