# WeeklyEmailSystem 사용 가이드

## 📧 간편한 이메일 발송 시스템

`WeeklyEmailSystem`은 28일 실천 가이드의 6개 이메일을 쉽게 생성하고 발송할 수 있는 간편 인터페이스입니다.

## 🚀 빠른 시작

### 1. 기본 사용법

```python
from weekly_email_system import WeeklyEmailSystem
from datetime import datetime

# 사용자별 이메일 시스템 생성
email_system = WeeklyEmailSystem(
    user_email='user@example.com',
    user_name='김철수',
    start_date=datetime(2026, 3, 1, 9, 0)
)

# 6개 이메일 전체 생성
emails = email_system.generate_all_emails()

# 각 이메일 발송
for email in emails:
    send_email(
        to=email['to'],
        subject=email['subject'],
        html=email['body_html'],
        attachments=email['attachments'],
        scheduled_time=email['send_at']
    )
```

### 2. 분석 결과와 함께 사용

```python
from weekly_email_system import WeeklyEmailSystem
from datetime import datetime

# 분석 결과 데이터
analysis_results = {
    "scores": {"rosenberg": 18},
    "profile_type": "vulnerable",
    "detected_patterns": [
        {"type": "SELF_CRITICISM", "strength": 0.92},
        {"type": "SOCIAL_COMPARISON", "strength": 0.78}
    ],
    "hidden_strengths": [
        {"name": "공감 능력", "description": "타인의 감정을 잘 이해합니다"}
    ]
}

# 시스템 생성 (분석 결과 포함)
email_system = WeeklyEmailSystem(
    user_email='user@example.com',
    user_name='김철수',
    start_date=datetime(2026, 3, 1, 9, 0),
    analysis_results=analysis_results,
    retest_link='https://yourapp.com/retest',
    pdf_report_path='outputs/report_user.pdf'
)

# 이메일 생성 및 발송
emails = email_system.generate_all_emails()
for email in emails:
    send_email(**email)
```

## 📦 생성되는 6개 이메일

| # | 타입 | 발송 시점 | 설명 |
|---|------|-----------|------|
| 1 | `diagnosis_complete` | 즉시 (Day 1) | 진단 완료 + PDF 2개 첨부 |
| 2 | `week_1_start` | Day 1 | Week 1 시작 리마인더 |
| 3 | `week_2_start` | Day 8 (+7일) | Week 2 시작 리마인더 |
| 4 | `week_3_start` | Day 15 (+14일) | Week 3 시작 리마인더 |
| 5 | `week_4_start` | Day 22 (+21일) | Week 4 시작 리마인더 |
| 6 | `completion_and_retest` | Day 28 (+27일) | 완료 축하 + 재검사 초대 |

## 🔧 고급 기능

### 1. 특정 이메일만 가져오기

```python
# 완료 이메일만 가져오기
completion_email = email_system.get_email_by_type('completion_and_retest')

if completion_email:
    send_email(**completion_email)
```

### 2. 날짜 범위로 필터링

```python
from datetime import datetime

# Week 1 이메일만 가져오기
week1_start = datetime(2026, 3, 1, 0, 0)
week1_end = datetime(2026, 3, 7, 23, 59)

week1_emails = email_system.get_emails_by_date_range(week1_start, week1_end)

for email in week1_emails:
    send_email(**email)
```

### 3. 스케줄 요약 확인

```python
summary = email_system.get_schedule_summary()

print(f"사용자: {summary['user_name']}")
print(f"총 이메일: {summary['total_emails']}개")
print(f"PDF: {summary['daily_guide_pdf']}")

for email_info in summary['emails_summary']:
    print(f"- {email_info['type']} @ {email_info['send_at']}")
```

### 4. JSON으로 내보내기

```python
# 이메일 스케줄을 JSON 파일로 저장
json_path = email_system.export_to_json("schedule.json")
print(f"저장 완료: {json_path}")
```

## 📨 이메일 발송 구현

### SendGrid 사용 예제

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType
import base64
import os

def send_email_with_sendgrid(
    to: str,
    subject: str,
    html: str,
    attachments: list,
    scheduled_time: str = None
):
    """SendGrid를 사용한 이메일 발송"""
    
    message = Mail(
        from_email='noreply@yourapp.com',
        to_emails=to,
        subject=subject,
        html_content=html
    )
    
    # 첨부 파일 추가
    for att in attachments:
        with open(att['path'], 'rb') as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        
        attachment = Attachment(
            FileContent(encoded),
            FileName(att['filename']),
            FileType('application/pdf')
        )
        message.add_attachment(attachment)
    
    # 예약 발송
    if scheduled_time:
        from datetime import datetime
        send_at = int(datetime.fromisoformat(scheduled_time).timestamp())
        message.send_at = send_at
    
    # 발송
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    
    return response.status_code == 202


# 사용
email_system = WeeklyEmailSystem(
    user_email='user@example.com',
    user_name='김철수',
    start_date=datetime(2026, 3, 1, 9, 0)
)

emails = email_system.generate_all_emails()

for email in emails:
    success = send_email_with_sendgrid(
        to=email['to'],
        subject=email['subject'],
        html=email['body_html'],
        attachments=email['attachments'],
        scheduled_time=email['send_at']
    )
    print(f"{'✅' if success else '❌'} {email['type']}")
```

### AWS SES 사용 예제

```python
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_with_aws_ses(
    to: str,
    subject: str,
    html: str,
    attachments: list
):
    """AWS SES를 사용한 이메일 발송"""
    
    ses_client = boto3.client('ses', region_name='us-east-1')
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'noreply@yourapp.com'
    msg['To'] = to
    
    # HTML 본문
    msg.attach(MIMEText(html, 'html'))
    
    # 첨부 파일
    for att in attachments:
        with open(att['path'], 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=att['filename']
            )
            msg.attach(attachment)
    
    # 발송
    response = ses_client.send_raw_email(
        Source='noreply@yourapp.com',
        Destinations=[to],
        RawMessage={'Data': msg.as_string()}
    )
    
    return 'MessageId' in response


# 사용
for email in emails:
    success = send_email_with_aws_ses(
        to=email['to'],
        subject=email['subject'],
        html=email['body_html'],
        attachments=email['attachments']
    )
    print(f"{'✅' if success else '❌'} {email['type']}")
```

## 📊 이메일 데이터 구조

각 이메일은 다음 정보를 포함합니다:

```python
{
    "type": "diagnosis_complete",           # 이메일 타입
    "send_at": "2026-03-01T09:00:00",      # 발송 시각 (ISO format)
    "to": "user@example.com",               # 수신자
    "subject": "제목...",                    # 제목
    "body_html": "<html>...</html>",        # HTML 본문
    "attachments": [                        # 첨부 파일 리스트
        {
            "type": "pdf",
            "path": "outputs/report.pdf",
            "filename": "보고서.pdf"
        }
    ]
}
```

## 🔄 워크플로우

```
1. WeeklyEmailSystem 생성
   ↓
2. generate_all_emails() 호출
   ↓
3. EmailScheduler → 28일 가이드 PDF 생성
   ↓
4. 6개 이메일 데이터 생성
   ↓
5. 각 이메일 발송 (즉시 또는 예약)
   ↓
6. (선택) JSON 내보내기
```

## ⚙️ 초기화 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `user_email` | str | ✅ | - | 사용자 이메일 |
| `user_name` | str | ✅ | - | 사용자 이름 |
| `start_date` | datetime | ✅ | - | 시작 날짜 |
| `analysis_results` | dict | ❌ | 기본값 | 분석 결과 데이터 |
| `retest_link` | str | ❌ | "https://..." | 재검사 링크 |
| `pdf_report_path` | str | ❌ | None | PDF 보고서 경로 |

## 📝 예제: API 엔드포인트 통합

```python
from flask import Flask, request, jsonify
from weekly_email_system import WeeklyEmailSystem
from datetime import datetime

app = Flask(__name__)

@app.route('/api/send-welcome-emails', methods=['POST'])
def send_welcome_emails():
    """진단 완료 후 6개 이메일 발송 API"""
    
    data = request.json
    
    # 이메일 시스템 생성
    email_system = WeeklyEmailSystem(
        user_email=data['email'],
        user_name=data['name'],
        start_date=datetime.fromisoformat(data['start_date']),
        analysis_results=data['analysis_results'],
        retest_link=data['retest_link'],
        pdf_report_path=data.get('pdf_report_path')
    )
    
    # 이메일 생성
    emails = email_system.generate_all_emails()
    
    # 발송
    results = []
    for email in emails:
        success = send_email(**email)  # 실제 발송 함수
        results.append({
            "type": email['type'],
            "success": success,
            "send_at": email['send_at']
        })
    
    # 응답
    return jsonify({
        "status": "success",
        "total_emails": len(emails),
        "results": results,
        "schedule_file": email_system.export_to_json(
            f"schedules/user_{data['email']}.json"
        )
    })
```

## 🎯 모범 사례

1. **에러 처리**: 이메일 발송 실패 시 재시도 로직 구현
2. **로깅**: 모든 발송 기록 저장
3. **모니터링**: 발송 성공률 추적
4. **테스트**: 실제 발송 전 테스트 환경에서 검증
5. **개인정보**: 이메일 주소 암호화 저장

## 🔍 문제 해결

### Q: PDF가 생성되지 않아요
```python
# 출력 디렉토리 확인
import os
os.makedirs("outputs", exist_ok=True)

# 폰트 확인
ls /usr/share/fonts/truetype/nanum/
```

### Q: 이메일이 발송되지 않아요
```python
# SendGrid API 키 확인
import os
print(os.environ.get('SENDGRID_API_KEY'))

# 테스트 이메일 발송
send_test_email()
```

### Q: 날짜가 잘못 계산돼요
```python
from datetime import datetime

# UTC 시간 사용 권장
start_date = datetime(2026, 3, 1, 9, 0, 0)

# 또는 타임존 지정
from datetime import timezone
start_date = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
```

## 📚 추가 문서

- [README_DAILY_PRACTICE.md](README_DAILY_PRACTICE.md) - 전체 시스템 가이드
- [email_scheduler.py](email_scheduler.py) - 하위 레벨 API
- [daily_practice_guide_v1.py](daily_practice_guide_v1.py) - 28일 가이드 데이터

---

**작성**: Claude Code Assistant  
**날짜**: 2026-02-06  
**버전**: v1.0
