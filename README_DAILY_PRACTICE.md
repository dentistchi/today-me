# 28일 매일 실천 가이드 시스템 - 완성 ✅

## 📋 프로젝트 개요

**완성일**: 2026-02-06  
**버전**: v1.0  
**상태**: 100% 완료

## 🎯 시스템 구성

### 1. 핵심 모듈 (3개)

#### ① `daily_practice_guide_v1.py` (929 lines)
- **기능**: 28일 매일 실천 가이드 데이터 생성
- **구조**:
  - Week 1 (Day 1-7): 자기자비 기초
  - Week 2 (Day 8-14): 완벽주의 내려놓기
  - Week 3 (Day 15-21): 공통 인간성 인식
  - Week 4 (Day 22-28): 안정적 자기가치

- **각 Day 데이터 구조**:
  ```python
  {
    "day": 1,
    "week": 1,
    "title": "제목",
    "morning_ritual": "아침 의식",
    "core_practice": {
      "name": "실천명",
      "duration": "시간",
      "steps": ["단계1", "단계2", ...],
      "why_it_works": "효과 설명",
      "psychology_background": "심리학 배경"
    },
    "expected_resistance": "예상 저항",
    "breakthrough_strategy": "돌파 전략",
    "evening_reflection": "저녁 성찰",
    "micro_win": "작은 승리",
    "celebration": "축하 (Week 마무리)"
  }
  ```

#### ② `daily_practice_pdf_generator.py` (487 lines)
- **기능**: 28일 가이드 PDF 생성
- **특징**:
  - 한글 폰트 지원 (NanumGothic)
  - 진한 텍스트 색상 (#212F3C)
  - 표지, Day별 페이지, 마무리 페이지
  - 클릭 가능한 재검사 링크 (Day 28)
  - 날짜별 자동 스케줄링
  
- **사용 예시**:
  ```python
  from daily_practice_pdf_generator import DailyPracticePDFGenerator
  
  pdf_gen = DailyPracticePDFGenerator()
  output_path = pdf_gen.generate_daily_practice_pdf(
      user_name="홍길동",
      all_days=all_days_data,
      start_date=datetime(2026, 2, 10),
      retest_link="https://example.com/retest"
  )
  ```

#### ③ `email_scheduler.py` (459 lines)
- **기능**: 28일 가이드 이메일 스케줄링
- **이메일 종류** (총 6개):
  1. 진단 완료 (즉시, PDF 2개 첨부)
  2. Week 1 시작 (Day 1)
  3. Week 2 시작 (Day 8)
  4. Week 3 시작 (Day 15)
  5. Week 4 시작 (Day 22)
  6. 완료 & 재검사 초대 (Day 28)

- **출력 형식**:
  ```json
  {
    "user_email": "user@example.com",
    "user_name": "홍길동",
    "start_date": "2026-02-10T09:00:00",
    "total_emails": 6,
    "daily_guide_pdf": "outputs/daily_practice_guide_홍길동.pdf",
    "emails": [
      {
        "type": "diagnosis_complete",
        "send_at": "2026-02-10T09:00:00",
        "to": "user@example.com",
        "subject": "제목",
        "body_html": "HTML 본문",
        "attachments": [...]
      },
      ...
    ]
  }
  ```

### 2. 기존 시스템 (PDF 보고서 v3.0)

- `pdf_generator_v3.py`: 자존감 분석 보고서 생성
- 6가지 개선사항 완료:
  1. 텍스트 색상 진하게 (#212F3C)
  2. 5차원 설명 한 페이지 표시
  3. 각 섹션 새 페이지 시작
  4. 동료 비교 데이터 제거
  5. 클릭 가능한 온라인 링크
  6. 재검사 박스 진한 배경

## 🚀 통합 워크플로우

```
1. 사용자 진단 완료
   ↓
2. pdf_generator_v3.py → 분석 보고서 PDF 생성
   ↓
3. daily_practice_guide_v1.py → 28일 가이드 데이터 생성
   ↓
4. daily_practice_pdf_generator.py → 28일 가이드 PDF 생성
   ↓
5. email_scheduler.py → 이메일 스케줄 생성 (JSON)
   ↓
6. 이메일 발송 시스템 → JSON 기반 자동 발송
```

## 📊 생성 파일 예시

### outputs/ 디렉토리:
```
outputs/
├── report_example_user.pdf                    # 분석 보고서 (241KB)
├── daily_practice_guide_example_user.pdf     # 28일 가이드 (336KB)
└── email_schedule_example.json               # 이메일 스케줄 (16KB)
```

## 🧪 테스트 방법

### 1. 28일 가이드 데이터 생성 테스트
```bash
cd /home/user/webapp
python daily_practice_guide_v1.py
```

### 2. PDF 생성 테스트
```bash
python daily_practice_pdf_generator.py
```

### 3. 이메일 스케줄링 테스트
```bash
python email_scheduler.py
```

### 4. 통합 시스템 테스트
```bash
python integrated_report_system.py
```

## 📖 사용 가이드

### 빠른 시작 (3단계)

#### 1단계: 분석 결과 준비
```python
analysis_results = {
    "scores": {"rosenberg": 22},
    "profile_type": "developing_critic",
    "detected_patterns": [
        {"type": "SELF_CRITICISM", "strength": 0.85}
    ],
    "hidden_strengths": [
        {"name": "회복탄력성", "description": "..."}
    ]
}
```

#### 2단계: PDF 및 스케줄 생성
```python
from email_scheduler import EmailScheduler
from datetime import datetime

scheduler = EmailScheduler()

schedule = scheduler.create_email_schedule(
    user_email="user@example.com",
    user_name="홍길동",
    analysis_results=analysis_results,
    start_date=datetime(2026, 2, 10, 9, 0, 0),
    retest_link="https://example.com/retest",
    pdf_report_path="outputs/report_user.pdf"  # 선택사항
)

# JSON 저장
scheduler.save_schedule_to_json(schedule, "email_schedule.json")
```

#### 3단계: 이메일 발송
- `email_schedule.json` 파일을 이메일 발송 시스템에 전달
- 시스템이 `send_at` 시각에 맞춰 자동 발송

## 🎨 디자인 특징

### PDF 스타일
- **폰트**: NanumGothic (한글 완벽 지원)
- **텍스트 색상**: #212F3C (진한 검정, 가독성 ↑)
- **강조 색상**:
  - 제목: #3498DB (파랑)
  - 아침 의식: #F39C12 (주황, 배경 #FEF5E7)
  - 작은 승리: #27AE60 (녹색, 배경 #E8F8F5)
  - 축하: #8E44AD (보라, 배경 #F4ECF7)
  - 재검사 박스: #2874A6 (진한 파랑, 흰 글씨)

### 이메일 템플릿
- HTML 이메일 (반응형)
- 이모지 사용으로 친근감 ↑
- 명확한 CTA (Call-To-Action)
- 주차별 테마 색상 구분

## 📈 핵심 통계

| 항목 | 수치 | 비고 |
|------|------|------|
| 총 Day 수 | 28일 | Week 1~4 각 7일 |
| 총 이메일 수 | 6개 | 진단+4주+완료 |
| PDF 페이지 수 | 약 60페이지 | 표지+28일+마무리 |
| PDF 파일 크기 | 약 336KB | 한글 폰트 포함 |
| JSON 파일 크기 | 약 16KB | 이메일 스케줄 |
| 코드 라인 수 | 1,875 lines | 3개 모듈 합계 |

## 🧠 심리학 근거

### 주차별 테마
- **Week 1**: 메타인지 (Flavell, 1979), 자기자비 (Neff, 2003)
- **Week 2**: 완벽주의 (Hewitt & Flett, 1991), 인지 재구조화 (Beck, 1979)
- **Week 3**: 공통 인간성 (Neff, 2003), 취약성 (Brown, 2012)
- **Week 4**: 무조건적 긍정적 존중 (Rogers, 1961), 자기 확언 (Steele, 1988)

### 연구 증거
- MSC 8주 프로그램: 자기자비 +43%, 우울 -31%
- 21일 습관 형성 (Lally et al., 2010)
- 자기 확언 → 스트레스 호르몬 감소 (Creswell et al., 2013)

## 🔗 통합 지점

### 기존 시스템과의 통합
1. **진단 API** → `analysis_results` 데이터 제공
2. **PDF 보고서 v3.0** → 분석 보고서 PDF 생성
3. **28일 가이드 시스템** → 실천 가이드 PDF + 이메일 스케줄
4. **이메일 발송 시스템** → JSON 기반 자동 발송
5. **재검사 시스템** → Day 28 링크 연결

### API 연동 예시
```python
# POST /api/diagnosis/complete
{
  "user_id": "...",
  "email": "user@example.com",
  "name": "홍길동",
  "analysis_results": {...},
  "start_date": "2026-02-10T09:00:00",
  "retest_link": "https://example.com/retest"
}

# Response
{
  "status": "success",
  "report_pdf": "outputs/report_user.pdf",
  "guide_pdf": "outputs/daily_practice_guide_user.pdf",
  "email_schedule": "outputs/email_schedule_user.json",
  "total_days": 28,
  "total_emails": 6
}
```

## ✅ 완료 체크리스트

- [x] Week 1 Day 1-7 완성
- [x] Week 2 Day 8-14 완성
- [x] Week 3 Day 15-21 완성
- [x] Week 4 Day 22-28 완성
- [x] PDF 생성기 구현
- [x] 이메일 스케줄러 구현
- [x] 한글 폰트 지원
- [x] 클릭 가능한 링크
- [x] 재검사 박스 강조
- [x] 날짜 자동 계산
- [x] JSON 스케줄 출력
- [x] 통합 테스트 완료
- [x] 문서화 완료

## 🎯 다음 단계

1. **코드 커밋 및 PR 생성**
2. **API 서버 통합**
3. **이메일 발송 시스템 연동**
4. **프로덕션 배포**
5. **사용자 피드백 수집**

## 💚 핵심 가치

1. **읽기 쉽다**: 진한 텍스트, 명확한 구조
2. **이해하기 쉽다**: 심리학 배경 설명, 구체적 단계
3. **사용하기 쉽다**: 클릭 가능한 링크, 자동 날짜
4. **신뢰할 수 있다**: 연구 근거, 전문적 디자인
5. **개인화되어 있다**: 사용자 이름, 맞춤 데이터

## 📞 지원

질문이나 문제가 있으면:
1. 문서 먼저 확인: `README_DAILY_PRACTICE.md`
2. 코드 주석 참고
3. 테스트 코드 실행

---

**작성자**: Claude Code Assistant  
**날짜**: 2026-02-06  
**버전**: v1.0  
**상태**: ✅ 완료
