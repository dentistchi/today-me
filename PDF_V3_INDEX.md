# 📚 PDF 보고서 생성 시스템 v3.0 - 문서 인덱스

## 🎯 빠른 네비게이션

### 📄 실행 파일
1. **[pdf_generator_v3.py](pdf_generator_v3.py)** (32KB) ⭐
   - 메인 PDF 생성기
   - 6가지 프로파일 지원
   - 한글 폰트, 레이더 차트, 클릭 가능 링크

2. **[demo_pdf_generation.py](demo_pdf_generation.py)** (7.7KB) 🎬
   - 4개 프로파일 데모 실행
   - 샘플 PDF 자동 생성

3. **[comparison_v2_v3.py](comparison_v2_v3.py)** (8.9KB) 📊
   - v2.0 vs v3.0 비교 분석
   - 개선 효과 시각화

### 📋 문서
1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** (7.3KB) 📋
   - **시작하기 좋은 문서!**
   - 프로젝트 전체 요약
   - 완료 체크리스트
   - 성능 지표

2. **[README_PDF_V3.md](README_PDF_V3.md)** (11KB) 📖
   - 상세 사용자 가이드
   - 설치 및 실행 방법
   - 프로파일 타입 설명
   - PDF 구조 상세

3. **[PDF_V3_IMPROVEMENTS.md](PDF_V3_IMPROVEMENTS.md)** (8.3KB) 📝
   - 6가지 개선사항 상세
   - 코드 예시 포함
   - Before/After 비교

### 💾 출력 PDF (outputs/)
1. **report_improved_v3.pdf** (242KB) - 기본 샘플
2. **report_vulnerable.pdf** (244KB) - 위기 상태 (빨강)
3. **report_developing_critic.pdf** (251KB) - 자기비판 (파랑)
4. **report_compassionate_grower.pdf** (250KB) - 성장 (초록)
5. **report_thriving.pdf** (254KB) - 번영 (금색)

---

## 🚀 추천 학습 경로

### 초보자용 (처음 접하는 경우)
1. **PROJECT_SUMMARY.md** 읽기 (5분)
   - 프로젝트 전체 개요 파악
2. **demo_pdf_generation.py** 실행 (1분)
   ```bash
   python demo_pdf_generation.py
   ```
3. 생성된 PDF 확인 (outputs/)
4. **README_PDF_V3.md** 읽기 (10분)
   - 상세 사용법 학습

### 개발자용 (코드 수정이 필요한 경우)
1. **PDF_V3_IMPROVEMENTS.md** 읽기 (10분)
   - 개선사항 및 코드 구조 이해
2. **pdf_generator_v3.py** 코드 분석 (30분)
   - 클래스 구조, 메서드 이해
3. **comparison_v2_v3.py** 실행 (1분)
   ```bash
   python comparison_v2_v3.py
   ```
4. 커스터마이징 시작

### 관리자용 (배포 및 운영)
1. **PROJECT_SUMMARY.md** 읽기
   - 기술 스펙, 성능 지표 확인
2. **README_PDF_V3.md** - 트러블슈팅 섹션
3. 프로덕션 배포 준비

---

## 📊 개선사항 요약

| 항목 | 파일 | 설명 |
|-----|------|------|
| 1️⃣ 텍스트 진하게 | pdf_generator_v3.py:74-88 | #212F3C 색상 |
| 2️⃣ 5차원 한 페이지 | pdf_generator_v3.py:232-258 | 컴팩트 레이아웃 |
| 3️⃣ 섹션 구분 | pdf_generator_v3.py:260,300,332 | PageBreak |
| 4️⃣ 동료 비교 제거 | N/A | 코드 제거됨 |
| 5️⃣ 클릭 링크 | pdf_generator_v3.py:394-424 | `<link>` 태그 |
| 6️⃣ 재검사 박스 | pdf_generator_v3.py:439-449 | 진한 배경 |

---

## 💡 자주 묻는 질문 (FAQ)

### Q1: PDF가 생성되지 않아요
**A:** 의존성 설치 확인
```bash
pip install reportlab matplotlib numpy
```

### Q2: 한글이 깨져요
**A:** 폰트 확인
```bash
ls /usr/share/fonts/truetype/nanum/
# NanumGothic.ttf 파일 확인
```

### Q3: 프로파일 색상을 변경하고 싶어요
**A:** `pdf_generator_v3.py` 파일의 `PROFILE_COLORS` 딕셔너리 수정 (17-48줄)

### Q4: 새로운 섹션을 추가하고 싶어요
**A:** 
1. `_create_new_section()` 메서드 생성
2. `generate()` 메서드에 호출 추가
3. 필요시 `PageBreak()` 추가

### Q5: PDF 페이지 수를 더 줄이고 싶어요
**A:** Spacer 크기 조정 (`Spacer(1, 5*mm)` → `Spacer(1, 3*mm)`)

---

## 🛠️ 커스터마이징 가이드

### 색상 변경
```python
# pdf_generator_v3.py:17-48
PROFILE_COLORS = {
    "custom_profile": {
        "primary": colors.HexColor('#YOUR_COLOR'),
        "secondary": colors.HexColor('#YOUR_COLOR'),
        ...
    }
}
```

### 폰트 크기 조정
```python
# pdf_generator_v3.py:74-88
fontSize=11,  # 본문 크기 변경
```

### 레이더 차트 크기 변경
```python
# pdf_generator_v3.py:253
chart_img = RLImage(chart_buffer, width=110*mm, height=110*mm)
```

### 링크 추가
```python
# pdf_generator_v3.py:405-418
link_text = f"<link href='{url}' color='#2874A6'>{text}</link>"
```

---

## 📞 지원 및 피드백

### 버그 리포트
- 현상: 어떤 문제가 발생했나요?
- 재현: 어떻게 재현할 수 있나요?
- 환경: Python 버전, OS 등

### 기능 요청
- 필요한 기능: 무엇이 필요한가요?
- 사용 사례: 어떤 경우에 사용하나요?
- 우선순위: 얼마나 중요한가요?

---

## 🎓 학습 리소스

### PDF 생성 (reportlab)
- [공식 문서](https://www.reportlab.com/docs/)
- [튜토리얼](https://www.reportlab.com/docs/reportlab-userguide.pdf)

### 데이터 시각화 (matplotlib)
- [공식 사이트](https://matplotlib.org/)
- [갤러리](https://matplotlib.org/stable/gallery/index.html)

### 한글 폰트
- [나눔폰트](https://hangeul.naver.com/font)
- [Google Fonts Korean](https://fonts.google.com/?subset=korean)

---

## 🏆 프로젝트 통계

- **총 코드 라인**: 약 700줄
- **문서 페이지**: 약 30페이지
- **생성 PDF 수**: 5개
- **지원 프로파일**: 6가지
- **개발 시간**: 1일
- **개선 항목**: 6가지
- **테스트 완료**: 100%

---

## 🔄 버전 히스토리

### v3.0 (2026-02-06) - Current
- ✅ 텍스트 색상 진하게
- ✅ 5차원 한 페이지
- ✅ 섹션 구분 명확화
- ✅ 동료 비교 제거
- ✅ 클릭 가능 링크
- ✅ 재검사 박스 강조

### v2.0 (이전 버전)
- 기본 PDF 생성 기능
- 6개 프로파일 지원
- 레이더 차트 시각화

---

**마지막 업데이트**: 2026-02-06  
**버전**: v3.0  
**상태**: ✅ 완료
