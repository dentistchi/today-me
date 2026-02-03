# 자존감 분석 시스템 v1.0

## 📋 개요
50개 질문 기반의 다차원 자존감 분석 웹 애플리케이션입니다. 사용자의 응답을 분석하여 6가지 자존감 유형을 도출하고, Google Sheets 및 이메일로 결과를 자동 발송합니다.

## 🎯 주요 기능
*   **5차원 자존감 분석**: 핵심 자존감, 자기 자비, 안정성, 성장 마인드셋, 사회적 자존감
*   **실시간 결과 시각화**: SVG 그래프 및 애니메이션을 통한 즉각적인 피드백
*   **자동 이메일 리포트**: Google Apps Script를 활용한 맞춤형 결과 보고서 발송
*   **데이터 수집**: Google Sheets에 모든 응답 데이터 자동 저장

## 📦 구성 요소
```
self-esteem-system/
├── self_esteem_system.py      # Python 분석 엔진
├── example_integration.js      # Node.js 연동 예시
├── README.md                   # 이 파일
└── requirements.txt            # Python 의존성
```

## 🚀 빠른 시작

### 1. Python 분석 엔진 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 예시 실행
python3 self_esteem_system.py
```

**출력 예시:**
```
============================================================
자존감 분석 시스템 v1.0
============================================================

✅ 분석 완료! 결과가 self_esteem_results_20240202_143022.json에 저장되었습니다.

📊 프로파일 요약:
- Rosenberg 점수: 23/40
- 자존감 유형: developing_balanced

✨ 발견된 강점: 3개
```

### 2. 웹 애플리케이션 통합

#### Node.js/Express 예시

```javascript
const express = require('express');
const app = express();

// 라우터 등록
const testRouter = require('./example_integration');
app.use('/', testRouter);

// 서버 시작
app.listen(3000, () => {
  console.log('서버 시작: http://localhost:3000');
});
```

#### API 호출

```javascript
// 프론트엔드
const submitTest = async (responses) => {
  const res = await fetch('/api/test/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userName: '홍길동',
      userEmail: 'user@example.com',
      responses: responses,  // [1, 2, 3, ...] (50개)
      responseTimes: responseTimes  // 선택사항
    })
  });
  
  return res.json();
};
```

## 📊 응답 데이터 형식

### 질문 구조 (50개)

```javascript
const responses = [
  // Rosenberg Self-Esteem (10개, 인덱스 0-9)
  2, 3, 2, 3, 2, 3, 2, 2, 3, 2,
  
  // Self-Compassion (12개, 인덱스 10-21)
  3, 2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3,
  
  // Growth Mindset (8개, 인덱스 22-29)
  3, 2, 3, 3, 3, 4, 3, 3,
  
  // Relational (10개, 인덱스 30-39)
  3, 2, 3, 2, 3, 3, 3, 3, 2, 3,
  
  // Implicit (10개, 인덱스 40-49)
  3, 3, 2, 3, 3, 3, 2, 3, 3, 3
];

// 응답 척도: 1 (전혀 아니다) ~ 4 (매우 그렇다)
```

### 분석 결과 형식

```json
{
  "profile": {
    "scores": {
      "rosenberg": 23,
      "rosenberg_max": 40,
      "self_compassion": 2.75,
      "mindset": 3.12,
      "relational": 2.9,
      "implicit": 2.8
    },
    "esteem_type": "developing_balanced",
    "dimensions": {
      "자존감_안정성": 5.7,
      "자기_자비": 5.5,
      "성장_마인드셋": 6.2,
      "관계적_독립성": 5.8,
      "암묵적_자존감": 5.6
    }
  },
  "strengths": [
    {
      "name": "회복탄력성 (Resilience)",
      "detail": "어려운 상황에서도 포기하지 않으려는 강한 의지",
      "score": 3.75,
      "evidence_questions": [6, 18, 33]
    }
  ],
  "emails": {
    "basic": { ... },
    "intermediate": { ... },
    "detailed": { ... }
  }
}
```

## 🎯 자존감 유형 분류

| 유형 | Rosenberg | Self-Compassion | 특징 |
|------|-----------|-----------------|------|
| **vulnerable** | < 20 | < 2.5 | 취약형: 자기비판 + 낮은 자존감 |
| **compassionate_grower** | < 20 | ≥ 2.5 | 자비로운 성장형 |
| **developing_critic** | 20-29 | < 3.0 | 발전형 (자기비판) |
| **developing_balanced** | 20-29 | ≥ 3.0 | 발전형 (균형) |
| **stable_rigid** | ≥ 30 | < 3.5 | 안정형이나 경직 |
| **thriving** | ≥ 30 | ≥ 3.5 | 번영형 (가장 건강) |

## 📧 이메일 발송 시스템

### 타이밍 전략

```
테스트 완료
    ↓
[즉시] VERSION 1: 감사 + 기대감
    ↓ (2시간 대기)
[2시간 후] VERSION 2: 기본 분석 + 강점
    ↓ (22시간 대기)
[24시간 후] VERSION 3: 완전 보고서 + PDF
```

### SMTP 설정 예시

```javascript
// Gmail 사용
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'your-email@gmail.com',
    pass: 'your-app-password'  // 2단계 인증 후 앱 비밀번호
  }
});

// SendGrid 사용 (추천)
const transporter = nodemailer.createTransport({
  host: 'smtp.sendgrid.net',
  port: 587,
  auth: {
    user: 'apikey',
    pass: process.env.SENDGRID_API_KEY
  }
});
```

## 🛠️ 기술 스택

### Backend
- **Python 3.8+**: 분석 엔진
- **Node.js 16+**: 웹 서버
- **Express**: API 라우팅
- **Bull + Redis**: 작업 큐

### 이메일
- **Nodemailer**: 이메일 발송
- **PDFKit**: PDF 생성

### 데이터베이스
- **MongoDB**: 사용자 데이터 저장
- **Redis**: 큐 관리

## 📝 환경 변수 설정

```bash
# .env 파일 생성
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

MONGODB_URI=mongodb://localhost:27017/selfesteem
REDIS_URL=redis://localhost:6379

NODE_ENV=production
PORT=3000
```

## 🔧 커스터마이징 가이드

### 1. 질문 수정

`self_esteem_system.py`에서 문항 인덱스 수정:

```python
self.rosenberg_items = {
    'positive': [0, 1, 3, 5, 6],  # 원하는 인덱스로 변경
    'negative': [2, 4, 7, 8, 9]
}
```

### 2. 이메일 템플릿 수정

`EmailTemplateGenerator` 클래스의 메서드 편집:

```python
def generate_basic_email(self, user_name, user_email):
    template = f"""
    # 여기에 원하는 내용 작성
    """
    return template
```

### 3. 강점 패턴 추가

```python
self.strength_patterns['creativity'] = {
    'questions': [5, 15, 25, 35],
    'threshold': 3.5,
    'description': '창의성',
    'detail': '새로운 아이디어를 생각하는 능력'
}
```

## 📈 성능 최적화

### 1. 이메일 발송 속도

```javascript
// Bull Queue 동시 처리 설정
emailQueue.process('send-email', 5, async (job) => {
  // 최대 5개 이메일 동시 발송
});
```

### 2. PDF 생성 캐싱

```javascript
// Redis 캐싱
const cachedPDF = await redis.get(`pdf:${testResultId}`);
if (cachedPDF) {
  return cachedPDF;
}
```

## 🐛 트러블슈팅

### 문제: 이메일이 스팸함으로 가는 경우

**해결책:**
1. SPF 레코드 설정
```
v=spf1 include:_spf.google.com ~all
```

2. DKIM 서명 추가
```javascript
const transporter = nodemailer.createTransport({
  // ...
  dkim: {
    domainName: 'yourdomain.com',
    keySelector: 'default',
    privateKey: fs.readFileSync('private-key.pem')
  }
});
```

### 문제: Python 프로세스 실행 오류

**해결책:**
```bash
# Python 경로 확인
which python3

# 의존성 재설치
pip3 install --upgrade -r requirements.txt
```

### 문제: PDF 한글 깨짐

**해결책:**
```bash
# 한글 폰트 설치 (Ubuntu)
sudo apt-get install fonts-nanum

# 폰트 경로 확인
fc-list | grep Nanum
```

## 📚 참고 자료

### 심리학 연구
- Rosenberg Self-Esteem Scale (1965)
- Neff's Self-Compassion Scale (2003)
- Dweck's Growth Mindset Theory (2006)

### 기술 문서
- [Nodemailer 공식 문서](https://nodemailer.com/)
- [Bull Queue 가이드](https://github.com/OptimalBits/bull)
- [PDFKit 문서](https://pdfkit.org/)

## 🤝 기여 가이드

버그 리포트나 기능 제안은 GitHub Issues에 등록해주세요.

## 📄 라이선스

MIT License

## 👥 제작자

자존감 연구팀 (2024)

---

## 🚀 다음 단계

### 단기 (1-2주)
- [ ] 이메일 발송 버그 수정
- [ ] 6가지 프로파일 템플릿 완성
- [ ] 기본 PDF 생성 기능

### 중기 (1개월)
- [ ] 50개 질문지 완성 및 검증
- [ ] 웹 인터페이스 개발
- [ ] 데이터베이스 설계

### 장기 (3개월)
- [ ] 4주 프로그램 자동 이메일
- [ ] 재검사 및 성장 곡선 시각화
- [ ] 커뮤니티 기능

---

**문의**: team@selfesteem.com
