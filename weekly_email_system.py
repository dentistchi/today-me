#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Email System - 28일 가이드 주간 이메일 시스템
사용자별 6개 이메일 생성 및 발송을 위한 간편 인터페이스
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email_scheduler import EmailScheduler
from daily_practice_guide_v1 import DailyPracticeGuide


class WeeklyEmailSystem:
    """
    28일 가이드 주간 이메일 시스템
    
    사용자별로 6개의 이메일을 생성하고 발송 준비:
    1. 진단 완료 (즉시)
    2. Week 1 시작 (Day 1)
    3. Week 2 시작 (Day 8)
    4. Week 3 시작 (Day 15)
    5. Week 4 시작 (Day 22)
    6. 완료 & 재검사 (Day 28)
    """
    
    def __init__(
        self,
        user_email: str,
        user_name: str,
        start_date: datetime,
        analysis_results: Optional[Dict] = None,
        retest_link: str = "https://example.com/retest",
        pdf_report_path: Optional[str] = None
    ):
        """
        Args:
            user_email: 사용자 이메일
            user_name: 사용자 이름
            start_date: 시작 날짜 (첫 이메일 발송 시각)
            analysis_results: 분석 결과 데이터 (None이면 기본값 사용)
            retest_link: 재검사 링크
            pdf_report_path: PDF 보고서 경로 (선택사항)
        """
        self.user_email = user_email
        self.user_name = user_name
        self.start_date = start_date
        self.retest_link = retest_link
        self.pdf_report_path = pdf_report_path
        
        # 분석 결과 기본값 설정
        if analysis_results is None:
            self.analysis_results = {
                "scores": {"rosenberg": 22},
                "profile_type": "developing_critic",
                "detected_patterns": [
                    {"type": "SELF_CRITICISM", "strength": 0.85}
                ],
                "hidden_strengths": [
                    {"name": "회복탄력성", "description": "어려움 속에서도 다시 일어서는 힘"}
                ]
            }
        else:
            self.analysis_results = analysis_results
        
        # 이메일 스케줄러 초기화
        self.scheduler = EmailScheduler()
        self._schedule = None
        self._emails = None
    
    def generate_all_emails(self) -> List[Dict]:
        """
        6개 이메일 전체 생성
        
        Returns:
            이메일 리스트 (각 이메일은 to, subject, body_html, attachments, send_at 포함)
        """
        if self._emails is not None:
            return self._emails
        
        # 이메일 스케줄 생성
        self._schedule = self.scheduler.create_email_schedule(
            user_email=self.user_email,
            user_name=self.user_name,
            analysis_results=self.analysis_results,
            start_date=self.start_date,
            retest_link=self.retest_link,
            pdf_report_path=self.pdf_report_path
        )
        
        # 이메일 리스트 추출
        self._emails = self._schedule['emails']
        
        return self._emails
    
    def get_email_by_type(self, email_type: str) -> Optional[Dict]:
        """
        특정 타입의 이메일 가져오기
        
        Args:
            email_type: 이메일 타입 ('diagnosis_complete', 'week_1_start', etc.)
            
        Returns:
            해당 이메일 딕셔너리 또는 None
        """
        emails = self.generate_all_emails()
        for email in emails:
            if email['type'] == email_type:
                return email
        return None
    
    def get_emails_by_date_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[Dict]:
        """
        날짜 범위로 이메일 필터링
        
        Args:
            start: 시작 날짜
            end: 종료 날짜
            
        Returns:
            해당 기간의 이메일 리스트
        """
        emails = self.generate_all_emails()
        filtered = []
        
        for email in emails:
            send_at = datetime.fromisoformat(email['send_at'])
            if start <= send_at <= end:
                filtered.append(email)
        
        return filtered
    
    def get_schedule_summary(self) -> Dict:
        """
        이메일 스케줄 요약 정보
        
        Returns:
            스케줄 요약 딕셔너리
        """
        if self._schedule is None:
            self.generate_all_emails()
        
        return {
            "user_email": self._schedule['user_email'],
            "user_name": self._schedule['user_name'],
            "start_date": self._schedule['start_date'],
            "total_emails": self._schedule['total_emails'],
            "daily_guide_pdf": self._schedule['daily_guide_pdf'],
            "emails_summary": [
                {
                    "type": email['type'],
                    "send_at": email['send_at'],
                    "subject": email['subject'][:50] + "..."
                }
                for email in self._schedule['emails']
            ]
        }
    
    def export_to_json(self, output_path: str) -> str:
        """
        이메일 스케줄을 JSON 파일로 내보내기
        
        Args:
            output_path: 출력 파일 경로
            
        Returns:
            저장된 파일 경로
        """
        if self._schedule is None:
            self.generate_all_emails()
        
        return self.scheduler.save_schedule_to_json(self._schedule, output_path)


# ==========================================
# 이메일 발송 함수 예제
# ==========================================

def send_email(
    to: str,
    subject: str,
    html: str,
    attachments: List[Dict],
    scheduled_time: str = None
) -> bool:
    """
    이메일 발송 함수 (예제 - 실제 구현 필요)
    
    실제 환경에서는 SendGrid, AWS SES, SMTP 등을 사용하여 구현
    
    Args:
        to: 수신자 이메일
        subject: 제목
        html: HTML 본문
        attachments: 첨부 파일 리스트
        scheduled_time: 예약 발송 시각 (ISO format)
        
    Returns:
        발송 성공 여부
    """
    print(f"📧 이메일 발송 (또는 예약)")
    print(f"   수신자: {to}")
    print(f"   제목: {subject[:50]}...")
    print(f"   첨부 파일: {len(attachments)}개")
    if scheduled_time:
        print(f"   예약 시각: {scheduled_time}")
    print()
    
    # 실제 구현 예시:
    # if scheduled_time:
    #     # 예약 발송
    #     schedule_email_with_sendgrid(to, subject, html, attachments, scheduled_time)
    # else:
    #     # 즉시 발송
    #     send_email_with_sendgrid(to, subject, html, attachments)
    
    return True


def send_email_with_sendgrid(
    to: str,
    subject: str,
    html: str,
    attachments: List[Dict],
    scheduled_time: str = None
) -> bool:
    """
    SendGrid를 사용한 이메일 발송 (예제)
    
    실제 사용 시 SendGrid API 키 필요
    """
    try:
        # SendGrid 예제 (실제 사용 시 주석 해제)
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
        # import base64
        # 
        # message = Mail(
        #     from_email='noreply@yourapp.com',
        #     to_emails=to,
        #     subject=subject,
        #     html_content=html
        # )
        # 
        # # 첨부 파일 추가
        # for att in attachments:
        #     with open(att['path'], 'rb') as f:
        #         data = f.read()
        #     encoded = base64.b64encode(data).decode()
        #     
        #     attachment = Attachment(
        #         FileContent(encoded),
        #         FileName(att['filename']),
        #         FileType('application/pdf'),
        #         Disposition('attachment')
        #     )
        #     message.add_attachment(attachment)
        # 
        # # 예약 발송
        # if scheduled_time:
        #     send_at = int(datetime.fromisoformat(scheduled_time).timestamp())
        #     message.send_at = send_at
        # 
        # # 발송
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        # response = sg.send(message)
        # 
        # return response.status_code == 202
        
        print(f"✅ SendGrid 이메일 발송 성공 (시뮬레이션)")
        return True
        
    except Exception as e:
        print(f"❌ SendGrid 이메일 발송 실패: {str(e)}")
        return False


def send_email_with_aws_ses(
    to: str,
    subject: str,
    html: str,
    attachments: List[Dict]
) -> bool:
    """
    AWS SES를 사용한 이메일 발송 (예제)
    
    실제 사용 시 AWS 자격 증명 필요
    """
    try:
        # AWS SES 예제 (실제 사용 시 주석 해제)
        # import boto3
        # from email.mime.multipart import MIMEMultipart
        # from email.mime.text import MIMEText
        # from email.mime.application import MIMEApplication
        # 
        # ses_client = boto3.client('ses', region_name='us-east-1')
        # 
        # msg = MIMEMultipart()
        # msg['Subject'] = subject
        # msg['From'] = 'noreply@yourapp.com'
        # msg['To'] = to
        # 
        # # HTML 본문
        # msg.attach(MIMEText(html, 'html'))
        # 
        # # 첨부 파일
        # for att in attachments:
        #     with open(att['path'], 'rb') as f:
        #         attachment = MIMEApplication(f.read())
        #         attachment.add_header('Content-Disposition', 'attachment', filename=att['filename'])
        #         msg.attach(attachment)
        # 
        # # 발송
        # response = ses_client.send_raw_email(
        #     Source='noreply@yourapp.com',
        #     Destinations=[to],
        #     RawMessage={'Data': msg.as_string()}
        # )
        # 
        # return 'MessageId' in response
        
        print(f"✅ AWS SES 이메일 발송 성공 (시뮬레이션)")
        return True
        
    except Exception as e:
        print(f"❌ AWS SES 이메일 발송 실패: {str(e)}")
        return False


# ==========================================
# 사용 예제
# ==========================================

def example_usage():
    """WeeklyEmailSystem 사용 예제"""
    
    print("=" * 70)
    print("WeeklyEmailSystem 사용 예제")
    print("=" * 70)
    print()
    
    # 1. 시스템 생성
    email_system = WeeklyEmailSystem(
        user_email='user@example.com',
        user_name='김철수',
        start_date=datetime(2026, 3, 1, 9, 0),
        retest_link='https://example.com/retest'
    )
    
    # 2. 6개 이메일 전체 생성
    emails = email_system.generate_all_emails()
    
    print(f"✅ {len(emails)}개 이메일 생성 완료\n")
    
    # 3. 각 이메일 발송 (또는 예약)
    for i, email in enumerate(emails, 1):
        print(f"[{i}/{len(emails)}] {email['type']}")
        send_email(
            to=email['to'],
            subject=email['subject'],
            html=email['body_html'],
            attachments=email['attachments'],
            scheduled_time=email['send_at']
        )
    
    # 4. 스케줄 요약 출력
    print("=" * 70)
    print("이메일 스케줄 요약")
    print("=" * 70)
    
    summary = email_system.get_schedule_summary()
    print(f"사용자: {summary['user_name']} ({summary['user_email']})")
    print(f"시작일: {summary['start_date']}")
    print(f"총 이메일: {summary['total_emails']}개")
    print(f"28일 가이드 PDF: {summary['daily_guide_pdf']}")
    print()
    
    for i, email_info in enumerate(summary['emails_summary'], 1):
        print(f"{i}. [{email_info['type']}]")
        print(f"   발송: {email_info['send_at']}")
        print(f"   제목: {email_info['subject']}")
        print()
    
    # 5. JSON 내보내기
    json_path = email_system.export_to_json("outputs/email_schedule_example.json")
    print(f"✅ JSON 스케줄 저장: {json_path}")
    print()


def example_filtered_emails():
    """날짜 범위로 이메일 필터링 예제"""
    
    print("=" * 70)
    print("날짜 범위 필터링 예제")
    print("=" * 70)
    print()
    
    email_system = WeeklyEmailSystem(
        user_email='user@example.com',
        user_name='김철수',
        start_date=datetime(2026, 3, 1, 9, 0)
    )
    
    # Week 1 이메일만 가져오기 (Day 1-7)
    week1_start = datetime(2026, 3, 1, 0, 0)
    week1_end = datetime(2026, 3, 7, 23, 59)
    
    week1_emails = email_system.get_emails_by_date_range(week1_start, week1_end)
    
    print(f"Week 1 이메일: {len(week1_emails)}개")
    for email in week1_emails:
        print(f"  - {email['type']} @ {email['send_at']}")
    print()


def example_specific_email():
    """특정 이메일 가져오기 예제"""
    
    print("=" * 70)
    print("특정 이메일 가져오기 예제")
    print("=" * 70)
    print()
    
    email_system = WeeklyEmailSystem(
        user_email='user@example.com',
        user_name='김철수',
        start_date=datetime(2026, 3, 1, 9, 0)
    )
    
    # 완료 이메일만 가져오기
    completion_email = email_system.get_email_by_type('completion_and_retest')
    
    if completion_email:
        print("✅ 완료 & 재검사 이메일:")
        print(f"   발송 시각: {completion_email['send_at']}")
        print(f"   제목: {completion_email['subject']}")
        print(f"   첨부 파일: {len(completion_email['attachments'])}개")
    print()


# ==========================================
# 메인 실행
# ==========================================

if __name__ == "__main__":
    # 기본 사용 예제
    example_usage()
    
    print("\n" + "=" * 70 + "\n")
    
    # 필터링 예제
    example_filtered_emails()
    
    print("\n" + "=" * 70 + "\n")
    
    # 특정 이메일 예제
    example_specific_email()
    
    print("=" * 70)
    print("✅ 모든 예제 완료!")
    print("=" * 70)
