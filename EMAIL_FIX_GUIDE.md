# 이메일 발송 문제 해결 가이드

## 문제: 사용자에게 이메일이 발송되지 않음

이메일이 발송되지 않는 원인과 해결 방법을 안내합니다.

---

## ✅ 해결 방법

### 1단계: .env 파일 생성

```bash
cd /home/user/webapp
cp .env.example .env
```

### 2단계: Gmail 앱 비밀번호 생성

#### A. Google 계정 2단계 인증 활성화
1. https://myaccount.google.com/security 접속
2. "2단계 인증" 활성화 (필수!)

#### B. 앱 비밀번호 생성
1. https://myaccount.google.com/apppasswords 접속
2. "앱 선택" → **메일** 선택
3. "기기 선택" → **기타 (사용자 지정)** 선택
4. 이름 입력 (예: "자존감 평가 시스템")
5. **생성** 버튼 클릭
6. 표시되는 **16자리 비밀번호 복사** (예: `abcd efgh ijkl mnop`)

### 3단계: .env 파일 수정

`.env` 파일을 열고 다음 값들을 **실제 값으로 변경**하세요:

```env
# SMTP 서버 설정 (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Gmail 계정 정보
SMTP_USER=your-email@gmail.com          # ← 실제 Gmail 주소로 변경
SMTP_PASSWORD=abcd efgh ijkl mnop        # ← 생성한 앱 비밀번호로 변경

# 발신자 정보
FROM_EMAIL=your-email@gmail.com          # ← 실제 Gmail 주소로 변경
FROM_NAME=자기자비 여정

# 이메일 발송 활성화
ENABLE_EMAIL=true                        # ← true로 설정 (실제 발송)
```

**예시:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=myemail@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=myemail@gmail.com
FROM_NAME=자기자비 여정
ENABLE_EMAIL=true
```

### 4단계: 이메일 발송 테스트

```bash
# 방법 1: 직접 테스트
python real_email_sender.py test

# 방법 2: 대화형 테스트
python send_user_emails.py test
```

테스트 시 본인의 이메일 주소를 입력하여 이메일이 정상적으로 수신되는지 확인하세요.

### 5단계: API 서버 재시작

```bash
# 서버 재시작 (변경사항 적용)
python api.py
```

서버가 시작될 때 다음과 같은 메시지가 표시되어야 합니다:
```
✅ .env 파일 로드: /home/user/webapp/.env
```

---

## 🧪 테스트 방법

### 1. SMTP 설정 테스트

```bash
python real_email_sender.py test
```

본인의 이메일 주소를 입력하면 테스트 이메일이 발송됩니다.

### 2. API 테스트

서버 시작 후 `/api/assess` 엔드포인트로 POST 요청을 보내세요:

```bash
curl -X POST http://localhost:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test@example.com",
    "responses": [3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2],
    "response_times": [4.5,3.2,5.1,3.8,4.2,3.9,4.7,3.5,4.1,3.6,4.8,3.3,4.4,3.7,4.6,3.4,4.3,3.8,4.9,3.2,4.1,3.9,4.5,3.6,4.2,3.7,4.8,3.3,4.4,3.5,4.6,3.8,4.3,3.4,4.7,3.9,4.1,3.6,4.9,3.2,4.5,3.8,4.2,3.7,4.6,3.3,4.4,3.9,4.8,3.5]
  }'
```

서버 로그에서 다음과 같은 메시지를 확인하세요:
```
[이메일 1/X] 발송 중...
   ✅ 성공
```

---

## 🔧 트러블슈팅

### 문제 1: "Authentication failed" 오류

**원인:** SMTP 인증 실패

**해결:**
- Gmail 앱 비밀번호를 정확히 입력했는지 확인
- 2단계 인증이 활성화되어 있는지 확인
- 공백을 포함하여 비밀번호 입력 (또는 공백 제거)

### 문제 2: 이메일이 발송되지 않음

**원인:** ENABLE_EMAIL=false 또는 SMTP 미설정

**해결:**
- `.env` 파일에서 `ENABLE_EMAIL=true` 설정 확인
- SMTP 설정이 모두 입력되었는지 확인
- 서버 재시작

### 문제 3: 이메일이 스팸함으로 감

**해결:**
- FROM_EMAIL을 실제 도메인 이메일로 설정
- 신뢰할 수 있는 이메일 서비스 사용 (Gmail, SendGrid, Mailgun 등)

### 문제 4: "Connection refused" 오류

**원인:** 방화벽 또는 네트워크 제한

**해결:**
- 포트 587 (또는 465) 아웃바운드 허용 확인
- 프록시 환경인 경우 프록시 설정 추가

---

## 📝 주요 변경사항

### 1. `email_scheduler.py`
- `RealEmailSender` 통합
- `send_email_now()` 메서드 추가
- `schedule_three_stage_emails()` 메서드 추가
- 테스트 모드와 실제 발송 모드 지원

### 2. `api.py`
- `.env` 파일 자동 로딩 기능 추가
- 환경 변수 확인 로그 추가

### 3. `.env.example`
- 더 명확한 설정 가이드 추가
- `ENABLE_EMAIL` 옵션 추가

---

## 📧 Gmail 외 다른 이메일 서비스 사용

### Naver Mail
```env
SMTP_HOST=smtp.naver.com
SMTP_PORT=587
SMTP_USER=your-id@naver.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-id@naver.com
```

### Outlook / Hotmail
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-email@outlook.com
```

---

## 🔐 보안 주의사항

1. **절대 .env 파일을 Git에 커밋하지 마세요**
   - `.gitignore`에 `.env`가 포함되어 있는지 확인

2. **앱 비밀번호 주기적 변경**
   - 3개월마다 새로운 앱 비밀번호 생성 권장

3. **운영 환경에서는 환경 변수 사용**
   - AWS Secrets Manager, Azure Key Vault 등 사용 권장

---

## ✅ 확인 체크리스트

- [ ] `.env` 파일 생성
- [ ] Gmail 2단계 인증 활성화
- [ ] Gmail 앱 비밀번호 생성
- [ ] `.env` 파일에 SMTP 설정 입력
- [ ] `ENABLE_EMAIL=true` 설정
- [ ] `python real_email_sender.py test` 실행 및 테스트 이메일 수신 확인
- [ ] API 서버 재시작
- [ ] API 테스트 요청 후 이메일 수신 확인

---

## 📞 추가 지원

문제가 계속되면 다음을 확인하세요:
- 서버 로그에서 오류 메시지 확인
- `email_send_log.txt` 파일 확인
- SMTP 서버 연결 가능 여부 확인
