# 이메일 발송 시스템 설정 가이드

## 🎯 개요

이 시스템은 테스트 완료 후 3단계로 이메일을 자동 발송합니다:

1. **즉시 발송**: 테스트 완료 알림
2. **2시간 후**: 중간 분석 보고서
3. **24시간 후**: 상세 분석 보고서 (PDF 첨부)

## 📧 SMTP 설정

### Gmail 사용하기 (추천)

1. **Google 계정에서 2단계 인증 활성화**
   - https://myaccount.google.com/security 접속
   - "2단계 인증" 활성화

2. **앱 비밀번호 생성**
   - https://myaccount.google.com/apppasswords 접속
   - "앱 선택" > "기타(맞춤 이름)" 선택
   - 이름 입력 (예: "자존감 평가 시스템")
   - 생성된 16자리 비밀번호 복사

3. **환경변수 설정**
   ```bash
   cp .env.example .env
   ```

4. **.env 파일 편집**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # 생성된 앱 비밀번호
   FROM_EMAIL=noreply@selfesteem.com
   FROM_NAME=자존감 연구팀
   
   # 개발자 이메일 (중요!)
   ADMIN_EMAIL=developer@example.com  # 알림을 받을 개발자 이메일
   
   ENABLE_EMAIL=true  # 실제 발송 활성화
   ```

## 📧 개발자 알림 기능 (NEW!)

사용자가 테스트를 완료하면 **개발자에게 즉시 알림 이메일**이 발송됩니다.

### 알림 이메일에 포함되는 내용:

1. **사용자 정보**
   - 이메일
   - 이름
   - 프로파일 유형 (취약형, 번영형 등)
   - Rosenberg 점수

2. **5차원 점수**
   - 자존감 안정성, 자기자비, 성장 마인드셋 등
   - 각 차원별 10점 만점 점수

3. **스케줄 정보**
   - 24시간 후 발송 예정 시간
   - PDF 첨부 여부

4. **이메일 미리보기**
   - 사용자가 받을 최종 리포트 내용
   - 첨부될 PDF (있는 경우)

### 활용 방법:

```bash
# .env 파일에서 개발자 이메일 설정
ADMIN_EMAIL=your-email@gmail.com
```

개발자는:
- ✅ 사용자가 받을 이메일을 미리 확인 가능
- ✅ 내용에 문제가 있으면 발송 전 수정 가능
- ✅ PDF 파일을 미리 다운로드하여 검토 가능
- ✅ 필요시 스케줄 취소 가능

### 예시 알림 이메일:

```
제목: [알림] 새 사용자 리포트 생성: user@example.com (취약형)

사용자 정보:
- 이메일: user@example.com
- 프로파일: 취약형 (Vulnerable)
- Rosenberg 점수: 18/40

5차원 점수:
- 자존감 안정성: 5.5/10
- 자기자비: 4.2/10
- 성장 마인드셋: 7.8/10
...

발송 예정: 2026-02-07 10:30:00
PDF 첨부: ✅ Yes

[사용자가 받을 이메일 미리보기]
...
```

### 다른 SMTP 서비스 사용하기

#### SendGrid
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

#### AWS SES
```env
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-aws-smtp-username
SMTP_PASSWORD=your-aws-smtp-password
```

#### Mailgun
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

## 🧪 테스트 모드

개발 및 테스트 중에는 실제로 이메일을 발송하지 않고 로그만 출력하도록 설정할 수 있습니다:

```env
ENABLE_EMAIL=false
```

이 경우 이메일 발송 대신 콘솔에 로그가 출력됩니다:

```
📧 [TEST MODE] Email to user@example.com
   Subject: 🌟 테스트 완료! 당신에 대한 특별한 이야기를 준비하고 있습니다
   Body length: 1234 chars
```

## 🚀 사용 방법

### API를 통한 자동 발송

테스트 완료 API를 호출하면 자동으로 이메일이 예약됩니다:

```bash
curl -X POST http://localhost:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user@example.com",
    "responses": [3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2,4,1,3,2],
    "response_times": [4.5,3.2,5.1,3.8,4.2,3.9,4.7,3.5,4.1,3.6,4.8,3.3,4.4,3.7,4.6,3.4,4.3,3.8,4.9,3.2,4.1,3.9,4.5,3.6,4.2,3.7,4.8,3.3,4.4,3.5,4.6,3.8,4.3,3.4,4.7,3.9,4.1,3.6,4.9,3.2,4.5,3.8,4.2,3.7,4.6,3.3,4.4,3.9,4.8,3.5]
  }'
```

### 예약된 이메일 확인

```bash
# 예약된 이메일 목록
curl http://localhost:8000/api/scheduled-emails

# 특정 이메일 취소 (관리자)
curl -X POST http://localhost:8000/api/cancel-email/{job_id}
```

## 🔧 트러블슈팅

### 문제 1: "Authentication failed" 오류

**원인**: SMTP 인증 실패

**해결**:
- Gmail 앱 비밀번호를 정확히 입력했는지 확인
- 2단계 인증이 활성화되어 있는지 확인
- 공백 없이 비밀번호 입력

### 문제 2: 이메일이 발송되지 않음

**원인**: ENABLE_EMAIL=false 또는 SMTP 미설정

**해결**:
- `.env` 파일에서 `ENABLE_EMAIL=true` 설정
- SMTP 설정이 모두 입력되었는지 확인

### 문제 3: 이메일이 스팸함으로 감

**해결**:
- FROM_EMAIL을 실제 도메인 이메일로 설정
- SPF, DKIM, DMARC 레코드 설정 (도메인 관리자)
- SendGrid, Mailgun 등 전문 서비스 사용 권장

### 문제 4: "Connection refused" 오류

**원인**: 방화벽 또는 네트워크 제한

**해결**:
- 포트 587 (또는 465) 아웃바운드 허용 확인
- 프록시 환경인 경우 프록시 설정 추가

## 📊 로그 확인

이메일 발송 로그는 콘솔에 출력됩니다:

```
✅ Email Scheduler started
📧 [Stage 1/3] Basic email sent to user@example.com
📅 [Stage 2/3] Intermediate email scheduled for 2026-02-06 12:30:00
📅 [Stage 3/3] Detailed email scheduled for 2026-02-07 10:30:00
✅ Email sent to user@example.com
```

## 🔐 보안 주의사항

1. **.env 파일을 절대 Git에 커밋하지 마세요**
   - `.gitignore`에 이미 포함되어 있습니다

2. **운영 환경에서는 환경변수 사용**
   ```bash
   export SMTP_USERNAME=your-email@gmail.com
   export SMTP_PASSWORD=your-app-password
   ```

3. **앱 비밀번호 주기적 변경**
   - 3개월마다 새로운 앱 비밀번호 생성 권장

## 📚 참고 자료

- [Gmail SMTP 설정](https://support.google.com/mail/answer/7126229)
- [SendGrid 문서](https://docs.sendgrid.com/)
- [AWS SES 가이드](https://docs.aws.amazon.com/ses/)
- [APScheduler 문서](https://apscheduler.readthedocs.io/)
