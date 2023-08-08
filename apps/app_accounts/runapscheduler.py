import logging
import pytz
from apps.app_accounts.models import Accountbyplanet
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from datetime import datetime, timedelta, time
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)

# 비활성화 유저 및 오랫동안 행성 컨펌 받지 못한 유저 삭제
def delete_inactive_users():
    User = get_user_model()
    
    # 현재 시간
    current_datetime = datetime.now()
    
    # 30분전 시간
    time_threshold = current_datetime - timedelta(minutes=30)
    
    # 30분전 시간을 create_at 형식으로 변환
    time_threshold_str = time_threshold.strftime('%Y-%m-%d %H:%M:%S')
    
    # 30분 이상 계정활성화 하지 않은 유저 가져오기
    users_to_delete = User.objects.filter(is_active=False, created_at__lt=time_threshold_str)
    
    # 유저 삭제
    for user in users_to_delete:
        print(f"삭제할 유저: {user}")
        user.delete()

    # Accountbyplanet 삭제
    # 현재 시간
    current_datetime = datetime.now()

    # 삭제할 기준 시간 (7일 이전)
    threshold_datetime     = current_datetime - timedelta(days=7)
    threshold_datetime_str = threshold_datetime.strftime('%Y-%m-%d %H:%M:%S')

    # 기준 시간과 is_confirmed=False인 객체 필터링
    accountbyplanet_to_delete = Accountbyplanet.objects.filter(
        created_at__lt=threshold_datetime,
        is_confirmed=False
    )

    # 객체 삭제
    for accountbyplanet in accountbyplanet_to_delete:
        print(f"삭제할 Accountbyplanet: {accountbyplanet.nickname}")
        accountbyplanet.delete()

# 백그라운드 스케쥴 
def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default") 

    # 설정할 특정 시간 (한국 시간대로 설정)
    target_time = time(0, 0, 0)  # 밤 12시

    # 현재 시간 (한국 시간대로 설정)
    current_datetime = datetime.now(pytz.timezone("Asia/Seoul"))

    # 현재 시간의 시간 구성요소만 추출(날짜 x)
    current_time = current_datetime.time()

    if current_time < target_time:
        today = datetime.now(pytz.timezone("Asia/Seoul")) # 오늘
        run_datetime = datetime.combine(today.date(), target_time) # 오늘 날짜 + 몇시,몇분
        run_datetime = pytz.timezone("Asia/Seoul").localize(run_datetime)  

        if current_datetime > run_datetime:
            run_datetime += timedelta(days=1)  # 현재 시간이 목표 시간보다 늦으면 다음 날 실행

        scheduler.add_job(
            delete_inactive_users,
            trigger="date",
            run_date=run_datetime,
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        

    try:
        # scheduler.start() #[주의] 마이그레이트, 마이그레이션 시 주석처리하고 진행해야함!
        pass
    except KeyboardInterrupt:
        scheduler.shutdown()
