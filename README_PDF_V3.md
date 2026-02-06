# 자존감 심층 분석 PDF 보고서 생성 시스템 v3.0

## 📋 목차
1. [개요](#개요)
2. [v3.0 주요 개선사항](#v30-주요-개선사항)
3. [설치 및 실행](#설치-및-실행)
4. [사용 방법](#사용-방법)
5. [프로파일 타입](#프로파일-타입)
6. [PDF 구조](#pdf-구조)
7. [기술 스택](#기술-스택)
8. [파일 구조](#파일-구조)

---

## 개요

자존감 심층 분석 PDF 보고서 생성 시스템은 사용자의 자존감 측정 데이터를 바탕으로 **전문적이고 개인화된 PDF 리포트**를 자동 생성합니다.

### 주요 특징
- ✅ **6가지 프로파일별 맞춤 색상 테마**
- ✅ **5차원 레이더 차트 시각화**
- ✅ **한글 폰트 지원** (NanumGothic)
- ✅ **클릭 가능한 하이퍼링크**
- ✅ **참고문헌 자동 번호 매기기**
- ✅ **4주 성장 프로그램 포함**

---

## v3.0 주요 개선사항

### 1️⃣ 텍스트 색상 진하게 (가독성 향상)
**이전**: 연한 회색 (#7F8C8D)  
**개선**: 진한 검은색 (#212F3C)  
**효과**: 인쇄 및 화면 가독성 대폭 향상

### 2️⃣ 5차원 설명을 한 페이지에 모두 표시
**이전**: 차원별 설명이 여러 페이지에 분산  
**개선**: 레이더 차트 + 5개 차원 설명을 한 페이지에 컴팩트하게 배치  
**효과**: 정보 파악이 쉽고 한눈에 전체 프로필 이해 가능

### 3️⃣ 각 섹션 제목이 새 페이지에서 시작
**적용 섹션**:
- Part 2: 감지된 패턴
- Part 3: 숨겨진 강점
- Part 4: 4주 성장 프로그램
- 자기자비 명상 가이드
- 온라인 리소스

**효과**: 전문적인 레이아웃, 읽기 편한 구조

### 4️⃣ 동료 비교 데이터 제거
**이유**: 나이 정보가 없어 의미 있는 비교 불가  
**효과**: 불필요한 정보 제거, 개인 성장에 집중

### 5️⃣ 온라인 리소스에 실제 클릭 가능한 링크 추가
**추가된 리소스**:
1. Self-Compassion 공식 사이트 (https://self-compassion.org)
2. Mindful Self-Compassion 프로그램 (https://centerformsc.org)
3. TED 강연 (https://www.ted.com/talks)
4. Headspace 명상 앱 (https://www.headspace.com)

**효과**: PDF에서 바로 외부 리소스 접근 가능

### 6️⃣ 재검사 링크 박스 배경색 변경
**이전**: 연한 배경색  
**개선**: 진한 primary 색상 + 흰색 텍스트  
**효과**: 높은 명암비로 가독성 향상, 중요 정보 강조

---

## 설치 및 실행

### 필수 요구사항
- Python 3.8+
- pip (패키지 관리자)

### 1. 의존성 설치
```bash
cd /home/user/webapp
pip install reportlab matplotlib numpy
```

### 2. 한글 폰트 확인
```bash
ls /usr/share/fonts/truetype/nanum/
# NanumGothic.ttf, NanumGothicBold.ttf 확인
```

### 3. 기본 실행
```bash
python pdf_generator_v3.py
```

### 4. 데모 실행 (4개 프로파일)
```bash
python demo_pdf_generation.py
```

---

## 사용 방법

### 기본 사용법

```python
from pdf_generator_v3 import ProfessionalPDFGenerator

# 보고서 데이터 준비
report_data = {
    'user_email': 'user@example.com',
    'profile_type': 'developing_critic',  # 프로파일 타입
    'scores': {
        'rosenberg': 22,  # Rosenberg 자존감 척도 (0-40)
        'dimensions': {
            '자기수용': 3.2,
            '자기가치': 2.8,
            '자기효능감': 3.5,
            '자기자비': 2.5,
            '사회적 연결': 3.0
        }
    },
    'patterns': [
        {
            'name': '패턴 이름',
            'strength': 0.83,  # 0.0 - 1.0
            'evidence': [11, 18, 23],  # 질문 번호
            'description': '패턴 설명',
            'research': '연구 출처'
        }
    ],
    'strengths': [
        {
            'name': '강점 이름',
            'evidence': '증거',
            'how_to_use': '활용 방법'
        }
    ],
    'retest_link': 'https://example.com/retest'
}

# PDF 생성
generator = ProfessionalPDFGenerator(report_data, 'output.pdf')
generator.generate()
```

### 고급 사용법

```python
# 참고문헌 추가
ref_num = generator.add_reference(
    citation="Author, A. (2020). Title. Journal.",
    url="https://doi.org/xxx"
)

# 레이더 차트만 생성
chart_buffer = generator._create_radar_chart(dimensions)
```

---

## 프로파일 타입

| 프로파일 | 코드 | Rosenberg 범위 | Primary 색상 | 설명 |
|---------|------|---------------|-------------|------|
| 위기 상태 | `vulnerable` | 0-15 | #C0392B (진한 빨강) | 전반적 자기부정, 즉시 개입 필요 |
| 자기비판 경향 | `developing_critic` | 16-25 | #2874A6 (진한 파랑) | 사회적 비교, 완벽주의 |
| 균형 발전 | `developing_balanced` | 16-25 | #117A65 (진한 청록) | 균형 있는 발전 중 |
| 자비로운 성장 | `compassionate_grower` | 26-32 | #1E8449 (진한 초록) | 자기자비 높음, 성장 지향 |
| 안정적/경직 | `stable_rigid` | 26-32 | #5D6D7E (진한 회색) | 안정적이나 변화 어려움 |
| 번영 상태 | `thriving` | 33-40 | #D68910 (진한 금색) | 최적의 자존감 상태 |

---

## PDF 구조

### 1. 표지 (Cover Page)
- 메인 타이틀: "자존감 심층 분석 보고서"
- 사용자 이름 맞춤 인사
- 생성 날짜

### 2. 오프닝 레터 (Opening Letter)
- Rosenberg 점수 소개
- 여정 시작 메시지
- 인용구

### 3. Part 1: 5차원 분석 (1페이지)
- 레이더 차트 시각화
- 5개 차원별 점수 및 설명
  - 자기수용
  - 자기가치
  - 자기효능감
  - 자기자비
  - 사회적 연결
- 참고문헌

### 4. Part 2: 내면 패턴 (새 페이지)
- 📊 패턴 강도 해석 가이드 (표)
  - 0.81-1.0: 매우 강함 (빨강)
  - 0.61-0.80: 강함 (주황)
  - 0.41-0.60: 중간 (노랑)
  - 0.21-0.40: 약함 (초록)
- 감지된 패턴 Top 3
- 증거 질문 & 연구 근거

### 5. Part 3: 숨겨진 강점 (새 페이지)
- 강점 Top 3
- 증거
- 활용 방법

### 6. Part 4: 4주 성장 로드맵 (새 페이지)
- **Week 1**: 자기자비 기초
- **Week 2**: 완벽주의 내려놓기
- **Week 3**: 공통 인간성 인식
- **Week 4**: 안정적 자기가치 (새 페이지 시작)

### 7. 자기자비 명상 가이드 (새 페이지)
- 10분 명상 단계별 안내
- 실천 가능한 구체적 지침

### 8. 온라인 리소스 (새 페이지)
- 클릭 가능한 링크 4개
- 각 리소스 상세 설명

### 9. 마지막 편지 (Closing Letter)
- 격려 메시지
- **재검사 링크 박스** (진한 배경, 흰색 텍스트)

### 10. 참고문헌 (References)
- 자동 번호 매기기
- 클릭 가능한 DOI/URL 링크

---

## 기술 스택

### 핵심 라이브러리
- **reportlab**: PDF 생성 및 레이아웃
- **matplotlib**: 레이더 차트 시각화
- **numpy**: 수치 계산

### 폰트
- **NanumGothic**: 한글 본문
- **NanumGothicBold**: 한글 강조
- **Helvetica**: 영문 폴백

### 색상 시스템
- **HexColor**: 프로파일별 맞춤 색상
- **명암비**: WCAG AA 이상 (4.5:1)

---

## 파일 구조

```
/home/user/webapp/
├── pdf_generator_v3.py          # 메인 PDF 생성기
├── demo_pdf_generation.py       # 데모 스크립트
├── PDF_V3_IMPROVEMENTS.md       # 개선사항 문서
├── README_PDF_V3.md             # 이 파일
├── outputs/                     # 출력 디렉토리
│   ├── report_improved_v3.pdf
│   ├── report_vulnerable.pdf
│   ├── report_developing_critic.pdf
│   ├── report_compassionate_grower.pdf
│   └── report_thriving.pdf
└── requirements.txt
```

---

## 예제 출력

### 생성된 PDF 파일 목록

```bash
$ ls -lh outputs/
-rw-r--r-- 1 user user 250K report_compassionate_grower.pdf
-rw-r--r-- 1 user user 251K report_developing_critic.pdf
-rw-r--r-- 1 user user 242K report_improved_v3.pdf
-rw-r--r-- 1 user user 254K report_thriving.pdf
-rw-r--r-- 1 user user 244K report_vulnerable.pdf
```

### 실행 예시

```bash
$ python demo_pdf_generation.py

============================================================
PDF 보고서 생성 시스템 v3.0 - 데모
============================================================

📄 위기 상태 (vulnerable) 보고서 생성 중...
   ✅ 생성 완료: report_vulnerable.pdf (243.2KB)

📄 자기비판 경향 (developing_critic) 보고서 생성 중...
   ✅ 생성 완료: report_developing_critic.pdf (250.8KB)

📄 자비로운 성장 (compassionate_grower) 보고서 생성 중...
   ✅ 생성 완료: report_compassionate_grower.pdf (249.5KB)

📄 번영 상태 (thriving) 보고서 생성 중...
   ✅ 생성 완료: report_thriving.pdf (253.3KB)

============================================================
✨ 모든 보고서 생성 완료!
============================================================
```

---

## 패턴 강도 해석

| 강도 범위 | 해석 | 권장 조치 |
|----------|------|----------|
| 0.81 - 1.0 | 매우 강함 (빨강) | 즉시 개입 필요, Week 1부터 집중 실천 |
| 0.61 - 0.80 | 강함 (주황) | 핵심 과제, 4주 동안 우선 집중 |
| 0.41 - 0.60 | 중간 (노랑) | 주의 필요, 꾸준한 모니터링 |
| 0.21 - 0.40 | 약함 (초록) | 경미한 패턴, 인식만으로도 개선 가능 |

---

## 참고 자료

### 연구 논문
1. Rosenberg, M. (1965). *Society and the adolescent self-image*. Princeton University Press.
2. Neff, K. D. (2003). *Self-compassion: An alternative conceptualization*. Self and Identity.
3. Neff, K. D., & Germer, C. K. (2013). *Mindful self-compassion program*.

### 온라인 리소스
- [Self-Compassion 공식 사이트](https://self-compassion.org)
- [Mindful Self-Compassion 프로그램](https://centerformsc.org)
- [TED 강연](https://www.ted.com/talks)
- [Headspace 명상 앱](https://www.headspace.com)

---

## 트러블슈팅

### 한글 폰트가 표시되지 않을 때
```bash
# 폰트 설치 (Ubuntu/Debian)
sudo apt-get install fonts-nanum

# 또는 폰트 직접 다운로드
wget https://github.com/naver/nanumfont/releases/download/v2.0/NanumFont_v2.0.zip
```

### PDF 생성 오류
```python
# 디버그 모드 활성화
import logging
logging.basicConfig(level=logging.DEBUG)
```

### matplotlib 폰트 경고
```python
# matplotlib 폰트 캐시 삭제
rm -rf ~/.matplotlib
```

---

## 향후 개선 계획

- [ ] 다국어 지원 (영어, 일본어)
- [ ] PDF 워터마크 추가
- [ ] QR 코드 재검사 링크
- [ ] 인터랙티브 체크리스트 (PDF 양식)
- [ ] 통계 차트 추가 (히스토그램, 박스플롯)
- [ ] 개인화된 명상 음악 QR 코드
- [ ] 진행 추적 캘린더 포함
- [ ] PDF 암호화 옵션

---

## 라이선스

MIT License

---

## 문의

이 프로젝트에 대한 문의사항이나 피드백은 언제든 환영합니다!

**Version**: 3.0  
**Last Updated**: 2026-02-06  
**Generated by**: PDF Report System v3.0
