# 🔥 긴급 수정사항 (2024-02-08)

## 문제: 이메일 발송 안됨

### 원인 분석
1. `SpreadsheetApp.getActiveSpreadsheet()` 사용 시 웹앱에서 작동 안함
2. 트리거 데이터 키 형식 불일치
3. 로깅 부족으로 문제 파악 어려움

### 해결 방법

#### 1. Google Apps Script 코드 업데이트
```javascript
// 변경 전 (❌)
var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

// 변경 후 (✅)
var properties = PropertiesService.getScriptProperties();
var spreadsheetId = properties.getProperty('SPREADSHEET_ID');
var spreadsheet = SpreadsheetApp.openById(spreadsheetId);
```

#### 2. Script Properties 설정 필수
Apps Script 에디터 → 프로젝트 설정 → 스크립트 속성 추가:
```
속성: SPREADSHEET_ID
값: {스프레드시트 ID}
```

#### 3. 로깅 강화
- 모든 주요 단계에 `Logger.log()` 추가
- 성공/실패 명확히 표시 (✅/❌)
- 오류 발생 시 스택 트레이스 출력

#### 4. 테스트 시간 단축
실제 운영: 24시간, 7일, 14일...
테스트용: 2분, 3분, 4분, 5분, 6분, 7분

---

## 📝 즉시 해야 할 일

### Step 1: 스프레드시트 ID 설정
1. Google Sheets에서 스프레드시트 열기
2. URL에서 ID 복사: `https://docs.google.com/spreadsheets/d/{ID}/edit`
3. Apps Script → 프로젝트 설정 → 스크립트 속성 추가
   - 속성: `SPREADSHEET_ID`
   - 값: 복사한 ID

### Step 2: 코드 업데이트
1. `google_apps_script.js` 파일의 최신 코드 복사
2. Apps Script 에디터에 붙여넣기
3. 저장 (Ctrl+S)

### Step 3: 재배포
1. 배포 → 배포 관리 → 수정 (또는 새 배포)
2. 웹 앱 URL 확인 (변경되었다면 `index.html`에도 업데이트)

### Step 4: 테스트
1. `test_email.html` 파일로 테스트 이메일 발송
2. 즉시 "진단 완료" 이메일 수신 확인
3. 2-7분 후 후속 이메일 수신 확인
4. Google Sheets에 데이터 저장 확인
5. Apps Script 실행 로그에서 오류 확인

---

## 🔍 디버깅 방법

### Apps Script 로그 확인
1. Apps Script 에디터 열기
2. 왼쪽 메뉴에서 "실행" 클릭
3. 최근 실행 내역 및 로그 확인

### 로그 메시지 예시
```
=== doPost 시작 ===
수신 이메일: test@example.com
답변 파싱 완료: 50개
응답 신뢰도: Normal (variance: 1.234)
✅ 스프레드시트 저장 완료
강점 추출 완료: 3개
📧 이메일 발송 시도: test@example.com
✅ 환영 이메일 발송 완료!
트리거 1 생성: 상세 보고서 (2분 후) - xyz123
✅ 모든 트리거 설정 완료
```

### 트리거 확인
1. Apps Script 에디터 → 트리거 (시계 아이콘)
2. 생성된 트리거 6개 확인
3. 실행 내역 및 오류 확인

---

## ⚠️ 주의사항

### 이메일 할당량
- Gmail 계정: 하루 100통
- Google Workspace: 하루 1,500통
- 테스트 시 할당량 소진 주의

### 스팸 방지
- 짧은 시간에 많은 이메일 발송 시 스팸 처리 가능
- 테스트는 소량으로 진행

### Script Properties 보안
- SPREADSHEET_ID는 노출되어도 큰 문제 없음
- 민감한 API 키 등은 저장하지 말 것

---

## 📚 관련 문서
- [GOOGLE_APPS_SCRIPT_SETUP.md](./GOOGLE_APPS_SCRIPT_SETUP.md) - 전체 설정 가이드
- [EMAIL_SETUP.md](./EMAIL_SETUP.md) - 이메일 시스템 설명
- [test_email.html](./test_email.html) - 테스트 페이지

---

**긴급 수정 완료: 2024-02-08**
