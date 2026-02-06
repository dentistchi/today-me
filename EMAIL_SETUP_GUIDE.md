# 실제 이메일 발송 설정 가이드

## 🚨 현재 문제: 사용자에게 이메일이 오지 않음

**원인**: 실제 이메일 발송 시스템이 설정되지 않음  
**해결**: SMTP 서버 설정 후 이메일 발송 기능 활성화

---

## ✅ 해결 방법 (3단계)

### 1단계: SMTP 서버 설정 (Gmail 추천)

#### Gmail 사용 시

1. **Google 계정 보안 설정**
   - https://myaccount.google.com/security 접속
   - "2단계 인증" 활성화 (필수)

2. **앱 비밀번호 생성**
   - https://myaccount.google.com/apppasswords 접속
   - 앱 선택: **메일**
   - 기기 선택: **기타** (사용자 지정 이름 입력)
   - 생성된 **16자리 비밀번호** 복사 (예: `abcd efgh ijkl mnop`)

3. **환경 변수 설정**

```bash
# Linux/Mac
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=abcdefghijklmnop  # 공백 제거한 앱 비밀번호
export FROM_EMAIL=your-email@gmail.com

# 또는 .env 파일 생성 (권장)
cat > .env << EOF
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
FROM_EMAIL=your-email@gmail.com
EOF
```

### 2단계: 테스트 발송

```bash
cd /home/user/webapp

# SMTP 설정 가이드 보기
python send_user_emails.py setup

# 환경 변수 로드 (.env 파일 사용 시)
export $(cat .env | xargs)

# 테스트 이메일 발송
python send_user_emails.py test
```

테스트가 성공하면 다음과 같이 표시됩니다:
```
✅ 이메일 발송 성공: test@example.com
🎉 테스트 성공! test@example.com로 이메일이 발송되었습니다.
```

### 3단계: 실제 사용자에게 발송

#### 방법 1: 명령줄에서 발송

```bash
python send_user_emails.py send user@example.com "홍길동"
```

#### 방법 2: Python 코드에서 발송

```python
from send_user_emails import send_user_emails
from datetime import datetime

# 사용자 이메일 발송
success = send_user_emails(
    user_email='user@example.com',
    user_name='홍길동',
    start_date=datetime(2026, 3, 1, 9, 0),
    analysis_results={
        "scores": {"rosenberg": 22},
        "profile_type": "developing_critic",
        "detected_patterns": [
            {"type": "SELF_CRITICISM", "strength": 0.85}
        ],
        "hidden_strengths": [
            {"name": "회복탄력성", "description": "어려움 속에서도 다시 일어서는 힘"}
        ]
    },
    retest_link='https://yourapp.com/retest',
    pdf_report_path='outputs/report_user.pdf'
)

if success:
    print("✅ 모든 이메일 발송 완료!")
else:
    print("❌ 일부 발송 실패")
```

---

## 📧 발송되는 이메일

총 **6개** 이메일이 발송됩니다:

| # | 타입 | 발송 시점 | 내용 |
|---|------|-----------|------|
| 1 | 진단 완료 | 즉시 | 분석 보고서 PDF + 28일 가이드 PDF 첨부 |
| 2 | Week 1 시작 | Day 1 | 자기자비 기초 - Week 1 리마인더 |
| 3 | Week 2 시작 | Day 8 | 완벽주의 내려놓기 - Week 2 리마인더 |
| 4 | Week 3 시작 | Day 15 | 공통 인간성 인식 - Week 3 리마인더 |
| 5 | Week 4 시작 | Day 22 | 안정적 자기가치 - Week 4 리마인더 |
| 6 | 완료 & 재검사 | Day 28 | 28일 완주 축하 + 재검사 초대 |

---

## 🔧 다른 이메일 서비스 사용

### Naver Mail (네이버 메일)

```bash
export SMTP_HOST=smtp.naver.com
export SMTP_PORT=587
export SMTP_USER=your-id@naver.com
export SMTP_PASSWORD=your-password
export FROM_EMAIL=your-id@naver.com
```

### Daum Mail (다음 메일)

```bash
export SMTP_HOST=smtp.daum.net
export SMTP_PORT=465
export SMTP_USER=your-id@daum.net
export SMTP_PASSWORD=your-password
export FROM_EMAIL=your-id@daum.net
```

### Outlook / Office 365

```bash
export SMTP_HOST=smtp.office365.com
export SMTP_PORT=587
export SMTP_USER=your-email@outlook.com
export SMTP_PASSWORD=your-password
export FROM_EMAIL=your-email@outlook.com
```

---

## 🐛 문제 해결

### 문제 1: "Authentication failed" 오류

**원인**: SMTP 비밀번호가 잘못됨  
**해결**:
- Gmail: 일반 비밀번호가 아닌 **앱 비밀번호** 사용
- 2단계 인증이 활성화되어 있는지 확인
- 앱 비밀번호를 다시 생성

### 문제 2: "Connection refused" 오류

**원인**: SMTP 서버 주소 또는 포트가 잘못됨  
**해결**:
- `SMTP_HOST`와 `SMTP_PORT` 확인
- 방화벽에서 SMTP 포트 허용 확인

### 문제 3: 이메일이 스팸함으로 감

**원인**: 발신자 인증 부족  
**해결**:
- SPF, DKIM, DMARC 설정 (도메인 사용 시)
- "스팸 아님"으로 표시 요청
- 발신자를 주소록에 추가 안내

### 문제 4: 환경 변수가 로드되지 않음

**해결**:
```bash
# .env 파일 로드
export $(cat .env | xargs)

# 또는 python-dotenv 사용
pip install python-dotenv
```

Python 코드에 추가:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 📊 발송 로그 확인

모든 발송 기록은 `email_send_log.txt`에 저장됩니다:

```bash
# 로그 확인
cat email_send_log.txt

# 성공한 발송만 보기
grep '"success": true' email_send_log.txt

# 실패한 발송만 보기
grep '"success": false' email_send_log.txt
```

---

## 🚀 프로덕션 배포 시 권장사항

1. **환경 변수 관리**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Kubernetes Secrets

2. **이메일 서비스 업그레이드**
   - SendGrid (추천)
   - AWS SES
   - Mailgun
   - Postmark

3. **모니터링**
   - 발송 성공률 추적
   - 오류 알림 설정
   - 반송 이메일 처리

4. **규정 준수**
   - 수신 동의 확인
   - 수신 거부 링크 포함
   - 개인정보 보호 정책 명시

---

## 💡 빠른 시작 체크리스트

- [ ] Gmail 2단계 인증 활성화
- [ ] Gmail 앱 비밀번호 생성
- [ ] 환경 변수 설정 (`.env` 파일)
- [ ] 테스트 이메일 발송 (`python send_user_emails.py test`)
- [ ] 받은 편지함 확인
- [ ] 실제 사용자에게 발송

---

**도움이 필요하면**:
```bash
python send_user_emails.py setup  # 설정 가이드 보기
python real_email_sender.py setup # 상세 Gmail 가이드
```

