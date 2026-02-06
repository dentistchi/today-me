"""
이메일 스케줄링 시스템
=====================
- 즉시 발송 (테스트 완료 알림)
- 2시간 후 발송 (중간 분석 보고서)
- 24시간 후 발송 (상세 분석 보고서 with PDF)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailConfig:
    """이메일 설정 (환경변수 또는 설정 파일에서 로드)"""
    
    def __init__(self):
        # SMTP 서버 설정 (예: Gmail)
        # 실제 운영시에는 환경변수에서 로드해야 함
        self.SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
        self.FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@selfesteem.com")
        self.FROM_NAME = os.getenv("FROM_NAME", "자존감 연구팀")
        
        # 이메일 전송 여부 (테스트 모드)
        self.ENABLE_EMAIL = os.getenv("ENABLE_EMAIL", "false").lower() == "true"
    
    def is_configured(self) -> bool:
        """SMTP 설정이 완료되었는지 확인"""
        return bool(self.SMTP_USERNAME and self.SMTP_PASSWORD)


class EmailScheduler:
    """이메일 예약 발송 시스템"""
    
    def __init__(self, config: EmailConfig = None):
        self.config = config or EmailConfig()
        
        # APScheduler 설정
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=3)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Seoul'
        )
        
        # 스케줄러 시작
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Email Scheduler started")
    
    def send_email(self, 
                   to_email: str, 
                   subject: str, 
                   body_html: str, 
                   body_text: str = None,
                   attachments: List[str] = None) -> bool:
        """
        이메일 발송
        
        Args:
            to_email: 수신자 이메일
            subject: 제목
            body_html: HTML 본문
            body_text: 텍스트 본문 (fallback)
            attachments: 첨부파일 경로 리스트
        
        Returns:
            성공 여부
        """
        try:
            # 테스트 모드이거나 SMTP 미설정시 로그만 출력
            if not self.config.ENABLE_EMAIL or not self.config.is_configured():
                logger.info(f"📧 [TEST MODE] Email to {to_email}")
                logger.info(f"   Subject: {subject}")
                logger.info(f"   Body length: {len(body_html)} chars")
                if attachments:
                    logger.info(f"   Attachments: {len(attachments)} files")
                return True
            
            # 실제 이메일 발송
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 텍스트 본문 추가
            if body_text:
                part_text = MIMEText(body_text, 'plain', 'utf-8')
                msg.attach(part_text)
            
            # HTML 본문 추가
            part_html = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(part_html)
            
            # 첨부파일 추가
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            filename = os.path.basename(file_path)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={filename}'
                            )
                            msg.attach(part)
                    else:
                        logger.warning(f"⚠️  첨부파일 없음: {file_path}")
            
            # SMTP 연결 및 발송
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}")
            return False
    
    def schedule_three_stage_emails(self,
                                   user_email: str,
                                   user_name: str,
                                   emails: Dict,
                                   pdf_path: Optional[str] = None) -> Dict:
        """
        3단계 이메일 예약 발송
        
        Args:
            user_email: 사용자 이메일
            user_name: 사용자 이름
            emails: {
                'basic': {'subject': '', 'body': '', 'send_delay_minutes': 0},
                'intermediate': {'subject': '', 'body': '', 'send_delay_minutes': 120},
                'detailed': {'subject': '', 'body': '', 'send_delay_minutes': 1440}
            }
            pdf_path: PDF 파일 경로 (detailed 이메일에 첨부)
        
        Returns:
            스케줄 정보
        """
        now = datetime.now()
        scheduled_jobs = {}
        
        # 1단계: 즉시 발송 (테스트 완료 알림)
        if 'basic' in emails:
            email_data = emails['basic']
            result = self.send_email(
                to_email=user_email,
                subject=email_data['subject'],
                body_html=email_data['body'],
                body_text=self._strip_html(email_data['body'])
            )
            scheduled_jobs['basic'] = {
                'status': 'sent' if result else 'failed',
                'sent_at': now.isoformat(),
                'scheduled_for': now.isoformat()
            }
            logger.info(f"📧 [Stage 1/3] Basic email sent to {user_email}")
        
        # 2단계: 2시간 후 발송 (중간 분석)
        if 'intermediate' in emails:
            email_data = emails['intermediate']
            send_time = now + timedelta(minutes=email_data['send_delay_minutes'])
            
            job = self.scheduler.add_job(
                func=self.send_email,
                trigger='date',
                run_date=send_time,
                args=[
                    user_email,
                    email_data['subject'],
                    email_data['body'],
                    self._strip_html(email_data['body'])
                ],
                id=f"email_intermediate_{user_email}_{now.timestamp()}",
                name=f"Intermediate email to {user_email}",
                replace_existing=True
            )
            
            scheduled_jobs['intermediate'] = {
                'status': 'scheduled',
                'job_id': job.id,
                'scheduled_for': send_time.isoformat(),
                'delay_minutes': email_data['send_delay_minutes']
            }
            logger.info(f"📅 [Stage 2/3] Intermediate email scheduled for {send_time}")
        
        # 3단계: 24시간 후 발송 (상세 보고서 with PDF)
        if 'detailed' in emails:
            email_data = emails['detailed']
            send_time = now + timedelta(minutes=email_data['send_delay_minutes'])
            
            # PDF 첨부파일 준비
            attachments = [pdf_path] if pdf_path and os.path.exists(pdf_path) else []
            
            job = self.scheduler.add_job(
                func=self.send_email,
                trigger='date',
                run_date=send_time,
                args=[
                    user_email,
                    email_data['subject'],
                    email_data['body'],
                    self._strip_html(email_data['body']),
                    attachments
                ],
                id=f"email_detailed_{user_email}_{now.timestamp()}",
                name=f"Detailed email to {user_email}",
                replace_existing=True
            )
            
            scheduled_jobs['detailed'] = {
                'status': 'scheduled',
                'job_id': job.id,
                'scheduled_for': send_time.isoformat(),
                'delay_minutes': email_data['send_delay_minutes'],
                'has_attachment': bool(attachments)
            }
            logger.info(f"📅 [Stage 3/3] Detailed email scheduled for {send_time}")
        
        return {
            'user_email': user_email,
            'user_name': user_name,
            'scheduled_at': now.isoformat(),
            'jobs': scheduled_jobs
        }
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """예약된 작업 목록 조회"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs
    
    def cancel_job(self, job_id: str) -> bool:
        """작업 취소"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"✅ Job {job_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"❌ Job cancellation failed: {e}")
            return False
    
    def shutdown(self):
        """스케줄러 종료"""
        self.scheduler.shutdown()
        logger.info("🛑 Email Scheduler stopped")
    
    def _strip_html(self, html: str) -> str:
        """HTML 태그 제거 (간단한 텍스트 버전 생성)"""
        import re
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', html)
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 연속된 줄바꿈 제거
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()


# ==================== 사용 예시 ====================

def example_usage():
    """이메일 스케줄러 사용 예시"""
    
    # 설정 초기화
    config = EmailConfig()
    scheduler = EmailScheduler(config)
    
    # 예시 이메일 데이터
    emails = {
        'basic': {
            'subject': '🌟 테스트 완료! 당신에 대한 특별한 이야기를 준비하고 있습니다',
            'body': '<h1>안녕하세요!</h1><p>테스트가 완료되었습니다.</p>',
            'send_delay_minutes': 0
        },
        'intermediate': {
            'subject': '📊 홍길동님의 자존감 프로파일이 완성되었습니다',
            'body': '<h1>중간 분석</h1><p>당신의 프로파일이 준비되었습니다.</p>',
            'send_delay_minutes': 120  # 2시간
        },
        'detailed': {
            'subject': '💎 홍길동님을 위한 완전한 분석 보고서',
            'body': '<h1>상세 보고서</h1><p>첨부된 PDF를 확인해주세요.</p>',
            'send_delay_minutes': 1440  # 24시간
        }
    }
    
    # 3단계 이메일 예약
    schedule_info = scheduler.schedule_three_stage_emails(
        user_email="user@example.com",
        user_name="홍길동",
        emails=emails,
        pdf_path="/path/to/report.pdf"
    )
    
    print("=" * 60)
    print("✅ 이메일 스케줄링 완료")
    print("=" * 60)
    print(json.dumps(schedule_info, indent=2, ensure_ascii=False))
    
    # 예약된 작업 목록
    print("\n📅 예약된 작업:")
    for job in scheduler.get_scheduled_jobs():
        print(f"  - {job['name']} ({job['next_run_time']})")
    
    return scheduler


if __name__ == "__main__":
    scheduler = example_usage()
    
    print("\n💡 스케줄러가 백그라운드에서 실행 중입니다.")
    print("   Ctrl+C를 눌러 종료하세요.")
    
    try:
        # 계속 실행 (실제 운영에서는 서버와 함께 실행)
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 스케줄러 종료 중...")
        scheduler.shutdown()
        print("✅ 종료 완료")
