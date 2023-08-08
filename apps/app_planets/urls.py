from django.urls import path
from . import views
from apps.app_accounts import views as accounts_views
app_name = 'planets'

urlpatterns = [
    path('', views.main, name='main'),
    path('planets/', views.planet_list, name='planet_list'),
    path('planets/create/', views.planet_create, name='planet_create'),
    path('planets/search/', views.search, name='search'),
    path('planets/<str:planet_name>/join/', views.planet_join, name='planet_join'),
    path('planets/<str:planet_name>/withdraw/', views.planet_withdraw, name='planet_withdraw'),
    # 마이 플래닛 필터 기능
    path('planets/my_planet_filter/', views.my_planet_filter, name='my_planet_filter'),

    # private 조인
    path('planets/invite_create/', views.invite_create, name='invite_create'),
    path('planets/invite_check/<str:invite_code>/', views.invite_check, name='invite_check'),
    path('planets/<str:planet_name>/contract/', views.planet_contract, name='planet_contract'),
    path('planets/<str:planet_name>/delete/', views.planet_delete, name='planet_delete'),
    path('planets/<str:planet_name>/', views.index, name='index'),
    path('planets/<str:planet_name>/index_list/', views.index_list, name='index_list'),
    path('planets/<str:planet_name>/planet_introduction/', views.planet_introduction, name='planet_introduction'),
    path('planets/<str:planet_name>/posts/', views.planet_posts, name='planet_posts'),
    path('planets/<str:planet_name>/create/', views.post_create, name='post_create'),
    path('planets/<str:planet_name>/<int:post_pk>/update/', views.post_create, name='post_create'),
    path('planets/<str:planet_name>/<int:post_pk>/', views.post_detail, name='post_detail'),
    path('planets/<str:planet_name>/<int:post_pk>/comments/', views.detail_comments, name='detail_comments'),
    path('planets/<str:planet_name>/post/<int:post_pk>/delete/', views.post_delete, name='post_delete'),
    path('planets/<str:planet_name>/<int:post_pk>/create/', views.comment_create, name='comment_create'),
    path('planets/<str:planet_name>/<int:post_pk>/<int:comment_pk>/update/', views.comment_create, name='comment_create'),
    path('planets/<str:planet_name>/comment/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    path('planets/<str:planet_name>/<int:post_pk>/<int:comment_pk>/create/', views.recomment_create, name='recomment_create'),
    path('planets/<str:planet_name>/<int:post_pk>/<int:comment_pk>/<int:recomment_pk>/update/', views.recomment_create, name='recomment_create'),
    path('planets/<str:planet_name>/recomment/<int:recomment_pk>/delete/', views.recomment_delete, name='recomment_delete'),
    path('planets/<str:planet_name>/tags/', views.tags_list, name='tags_list'),
    path('planets/<str:planet_name>/tags/<str:tag_name>/', views.post_tag, name='post_tag'),

    # 행성 수정 페이지
    path('planets/<str:planet_name>/admin/', views.planet_admin, name='planet_admin'),
    path('planets/<str:planet_name>/admin/tos/', views.planet_tos_admin, name='planet_tos_admin'),
    path('planets/<str:planet_name>/admin/join', views.planet_join_admin, name='planet_join_admin'),
    path('planets/<str:planet_name>/admin/join/<int:user_pk>/confirm/', views.planet_join_confirm, name='planet_join_confirm'),
    path('planets/<str:planet_name>/admin/join/<int:user_pk>/reject/', views.planet_join_reject, name='planet_join_reject'),
    # 게시글 신고 관리
    path('planets/<str:planet_name>/admin/report/', views.admin_report, name='admin_report'),
    # 행성 내 회원 관리
    path('planets/<str:planet_name>/admin/member/', views.admin_member, name='admin_member'),
    # 행성별 프로필
    path('planets/<str:planet_name>/profile/<str:nickname>/', accounts_views.planet_profile, name='planet_profile'),
    path('planets/<str:planet_name>/profile/<str:nickname>/update/', accounts_views.planet_profile_update, name='planet_profile_update'),
    # 게시글, 댓글, 대댓글 신고 기능
    path('planets/<str:planet_name>/report/<str:report_category>/<int:pk>/', views.report, name='report'),
    # 리스트 필터 기능
    path('planets/<str:category>/filter/', views.filter, name='filter'),
    # 팔로잉
    path('planets/<str:planet_name>/follow/<int:user_pk>/', views.following, name='following'),
    # 투표
    path('planets/post/<int:post_pk>/<str:vote_title>/', views.vote, name='vote'),
    # 게시글 감정표현 
    path('planets/<str:planet_name>/posts/<int:post_pk>/emotes/<str:emotion>', views.post_emote, name='post_emote'),
    # 댓글 감정 표현
    path('planets/<str:planet_name>/posts/<int:post_pk>/comments/<int:comment_pk>/emotes/<str:emotion>', views.comment_emote, name='comment_emote'),
    # 행성 별 메모
    path('planets/<str:planet_name>/memo/', views.planet_memo, name='planet_memo'),
    # 행성 즐겨찾기
    path('planets/<str:planet_name>/star/', views.planet_star, name='planet_star'),
    # 행성 내 post 검색
    path('planets/<str:planet_name>/search/', views.post_search, name='post_search'),
]
