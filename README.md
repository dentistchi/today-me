# Phase 1 구현: 부주의 응답 감지 + 응답 스타일 보정

**목표**: 2주 안에 정확도 +15% 달성  
**비용**: 0원  
**개발 기간**: 2주

---

## 📦 패키지 내용

### 1. 핵심 모듈
- `careless_response_detector.py` - 부주의 응답 감지기
- `response_style_corrector.py` - 응답 스타일 보정기
- `api.py` - FastAPI REST API

### 2. 테스트
- `tests/test_detector.py` - 감지기 단위 테스트
- `tests/test_corrector.py` - 보정기 단위 테스트
- `tests/test_api.py` - API 통합 테스트

### 3. 문서
- `README.md` - 이 파일
- `DEPLOYMENT.md` - 배포 가이드

---

## 🚀 빠른 시작

### 설치

```bash
# 1. Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 테스트 실행
pytest tests/

# 4. API 서버 시작
python api.py
```

서버 시작 후:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📊 기능 설명

### 1. 부주의 응답 감지 (CarelessResponseDetector)

**4가지 감지 기법:**

#### ① 응답 시간 분석
```python
# 평균 2초 미만 → Speeder 플래그
# 연속 3개 이상 1초 미만 → Speeder 플래그
detector.analyze(responses, response_times)
```

**학술 근거**: Curran (2016), 1701 인용

#### ② Longstring 분석
```python
# 동일 응답 10개 이상 연속 → Longstring 플래그
# 예: [2,2,2,2,2,2,2,2,2,2,...]
```

**학술 근거**: Johnson (2005)

#### ③ 짝수/홀수 일관성
```python
# 짝수 질문 vs 홀수 질문 상관계수 < 0.3 → 불일치 플래그
even = [Q0, Q2, Q4, ...]
odd = [Q1, Q3, Q5, ...]
correlation = corr(even, odd)
```

**학술 근거**: Ward & Meade (2023), 494 인용

#### ④ Mahalanobis Distance
```python
# 통계적 이상치 감지
# D² > χ²(p=0.001) → 이상치 플래그
```

**학술 근거**: Mahalanobis (1936)

### 2. 응답 스타일 보정 (ResponseStyleCorrector)

**3가지 보정 기법:**

#### ① Extreme Responding
```python
# 1번 or 4번이 70% 이상 → 정규화
# Z-score 변환 후 1-4 재매핑
```

#### ② Midpoint Responding
```python
# 2번 or 3번이 70% 이상 → 분산 증가
```

#### ③ Acquiescence Bias
```python
# 역문항 불일치 70% 이상 → 역문항 뒤집기
# 예: 역문항에서 4 → 1로 변환
```

**학술 근거**: Böckenholt & Meiser (2017), 163 인용

---

## 🔧 API 사용법

### 엔드포인트 1: 평가 실행

```bash
POST /api/assess
Content-Type: application/json

{
  "user_id": "user123",
  "responses": [3, 2, 4, 1, ...],  // 50개
  "response_times": [4.5, 3.2, ...],  // 50개
  "reverse_items": [2, 4, 7, 8, 9]  // 선택
}
```

**응답 예시 (성공):**
```json
{
  "user_id": "user123",
  "status": "success",
  "message": "평가가 성공적으로 완료되었습니다.",
  "data_quality": {
    "quality_score": 0.85,
    "flags": [],
    "recommendation": "excellent"
  },
  "corrected_responses": [3, 2, 4, 1, ...],
  "style_corrections": {
    "corrections_applied": [],
    "style_scores": {
      "extreme_responding": 0.24,
      "midpoint_responding": 0.56,
      "acquiescence": 0.15
    }
  }
}
```

**응답 예시 (거부):**
```json
{
  "status": "invalid",
  "message": "응답 품질이 낮습니다:\n⚠️ 너무 빠르게 응답하셨습니다.\n⚠️ 동일한 답변이 너무 많습니다.",
  "data_quality": {
    "quality_score": 0.35,
    "flags": ["speeding", "longstring"],
    "recommendation": "reject"
  }
}
```

### 엔드포인트 2: A/B 테스트

```bash
POST /api/assess-ab
# 동일한 request body

# 응답에 test_group 추가됨
{
  ...,
  "test_group": "treatment"  // or "control"
}
```

### 엔드포인트 3: 통계 조회

```bash
GET /api/ab-stats

# 응답
{
  "control_group": {
    "avg_quality_score": 0.72,
    "flagged_rate": 0.25
  },
  "treatment_group": {
    "avg_quality_score": 0.85,
    "flagged_rate": 0.10
  },
  "improvement": {
    "quality_score": "+18%",
    "flagged_rate": "-60%"
  }
}
```

---

## 🧪 테스트

### 단위 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 개별 모듈
pytest tests/test_detector.py -v
pytest tests/test_corrector.py -v

# 커버리지 확인
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

### 수동 테스트

```python
# 감지기 테스트
python careless_response_detector.py

# 보정기 테스트
python response_style_corrector.py

# API 테스트
python api.py
# 브라우저에서 http://localhost:8000/docs
```

---

## 📈 성능 지표

### 목표 vs. 실제 (2주 후 측정)

| 지표 | 현재 | 목표 | 측정 방법 |
|------|------|------|-----------|
| Test-Retest 상관 | 0.70 | 0.80+ | 4주 후 재검사 |
| 부주의 응답률 | 25% | 10% | 플래그 발생률 |
| 완료율 | 65% | 75%+ | 제출/시작 비율 |
| 품질 점수 평균 | 0.72 | 0.85+ | quality_score |

---

## 🔄 프론트엔드 통합

### React 예시

```javascript
import { useState } from 'react';

export default function AssessmentForm() {
  const [responses, setResponses] = useState(Array(50).fill(null));
  const [startTimes, setStartTimes] = useState({});
  
  const handleQuestionFocus = (qId) => {
    setStartTimes(prev => ({ ...prev, [qId]: Date.now() }));
  };
  
  const handleQuestionBlur = (qId, response) => {
    const duration = (Date.now() - startTimes[qId]) / 1000;
    
    setResponses(prev => {
      const newResp = [...prev];
      newResp[qId] = response;
      return newResp;
    });
    
    setResponseTimes(prev => {
      const newTimes = [...prev];
      newTimes[qId] = duration;
      return newTimes;
    });
  };
  
  const handleSubmit = async () => {
    const res = await fetch('/api/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: getUserId(),
        responses,
        response_times: responseTimes
      })
    });
    
    const result = await res.json();
    
    if (result.status === 'invalid') {
      alert(result.message);  // 품질 경고 표시
      // 재검사 권유
    } else {
      navigateToResults(result);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* 질문들 */}
    </form>
  );
}
```

---

## 📚 참고 논문

1. **Ward, M. K., & Meade, A. W. (2023)**. Dealing with careless responding in survey data. *Annual Review of Psychology*, 74, 1-26. [494 citations]

2. **Curran, P. G. (2016)**. Methods for the detection of carelessly invalid responses. *Journal of Experimental Social Psychology*, 66, 4-19. [1701 citations]

3. **Böckenholt, U., & Meiser, T. (2017)**. Response style analysis with threshold and multi-process IRT models. *British Journal of Mathematical and Statistical Psychology*, 70(1), 159-176. [163 citations]

4. **Johnson, J. A. (2005)**. Ascertaining the validity of individual protocols. *Journal of Research in Personality*, 39, 103-129.

---

## 🐛 트러블슈팅

### 문제 1: ImportError
```bash
# 해결: 모듈을 같은 디렉토리에 배치
phase1_implementation/
  ├── careless_response_detector.py
  ├── response_style_corrector.py
  └── api.py
```

### 문제 2: CORS 에러
```python
# api.py에서 origins 수정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 주소
)
```

### 문제 3: 느린 Mahalanobis 계산
```python
# reference_data 없이 실행 (처음 500명 수집 전)
detector.analyze(responses, times, reference_data=None)
```

---

## 🚀 배포

### Docker (권장)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api.py"]
```

```bash
# 빌드 및 실행
docker build -t phase1-api .
docker run -p 8000:8000 phase1-api
```

### 직접 배포 (Ubuntu)

```bash
# 1. 서버 준비
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 2. 코드 배포
cd /var/www
git clone <repo-url> phase1
cd phase1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Systemd 서비스 등록
sudo nano /etc/systemd/system/phase1.service

[Unit]
Description=Phase 1 API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/phase1
ExecStart=/var/www/phase1/venv/bin/python api.py
Restart=always

[Install]
WantedBy=multi-user.target

# 4. 서비스 시작
sudo systemctl enable phase1
sudo systemctl start phase1

# 5. Nginx 리버스 프록시 설정
sudo nano /etc/nginx/sites-available/phase1

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

sudo ln -s /etc/nginx/sites-available/phase1 /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

---

## 📞 지원

문의사항:
- 이메일: support@example.com
- GitHub Issues: <repo-url>/issues

---

## 📄 라이선스

MIT License

Copyright (c) 2026 자존감 평가 시스템 개발팀
