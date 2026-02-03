/**
 * [Google Apps Script 설정 방법]
 * 1. Google 스프레드시트 접속 -> 확장 프로그램 -> Apps Script
 * 2. 이 파일의 모든 내용을 복사하여 'Code.gs'에 붙여넣기
 * 3. '배포' -> '새 배포' -> 유형: '웹 앱'
 * 4. 액세스 권한: '모든 사용자' (필수)
 * 5. 생성된 웹 앱 URL을 index.html의 form action에 적용
 */

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var params = e.parameter;
  
  // 1. 헤더가 없으면 추가
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "Timestamp", "Email", "Total Score", "Core", "Compassion", 
      "Stability", "Growth", "Social", "Profile Type", "Answers"
    ]);
  }
  
  // 2. 데이터 시트에 저장
  sheet.appendRow([
    new Date(),
    params.email,
    params.total_score,
    params.core_score,
    params.compassion_score,
    params.stability_score,
    params.growth_score,
    params.social_score,
    params.profile_type,
    params.answers
  ]);
  
  // 3. 이메일 본문(HTML) 생성
  var emailBody = createEmailTemplate(params);
  
  // 4. 사용자에게 이메일 발송
  try {
    MailApp.sendEmail({
      to: params.email,
      subject: "[오늘의 나] " + params.profile_type + " 유형 분석 결과 보고서",
      htmlBody: emailBody,
      name: "오늘의 나 연구팀"
    });
  } catch (error) {
    console.error("사용자 이메일 발송 실패: " + error);
  }

  // 5. 관리자(나)에게 알림 이메일 발송
  try {
    MailApp.sendEmail({
      to: Session.getActiveUser().getEmail(),
      subject: "[Admin] 새로운 자존감 진단 제출: " + params.profile_type,
      htmlBody: "<p>새로운 진단 결과가 제출되었습니다.</p>" +
                "<p><strong>이메일:</strong> " + params.email + "</p>" +
                "<p><strong>총점:</strong> " + params.total_score + "점</p>" +
                "<p><strong>유형:</strong> " + params.profile_type + "</p>" +
                "<p><a href='" + SpreadsheetApp.getActiveSpreadsheet().getUrl() + "'>스프레드시트 확인하기</a></p>"
    });
  } catch (error) {
    console.error("관리자 알림 발송 실패: " + error);
  }
  
  // 성공 응답 반환
  return ContentService.createTextOutput(JSON.stringify({"result":"success"}))
    .setMimeType(ContentService.MimeType.JSON);
}

function createEmailTemplate(data) {
  var score = parseInt(data.total_score);
  var feedback = "";
  
  if (score >= 70) {
    feedback = "당신의 자존감은 매우 건강한 상태입니다. 자신을 사랑하고 타인을 존중하는 균형 잡힌 마음을 가지고 계시네요.";
  } else if (score >= 40) {
    feedback = "당신의 자존감은 보통 수준입니다. 조금 더 자신을 아껴주고 격려해준다면 더 단단한 마음을 가질 수 있습니다.";
  } else {
    feedback = "현재 자존감이 다소 낮아져 있는 상태로 보입니다. 너무 걱정하지 마세요. 자존감은 연습을 통해 충분히 성장할 수 있습니다.";
  }

  return `
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
        <h1 style="margin: 0; font-size: 24px;">오늘의 나 분석 리포트</h1>
        <p style="margin: 10px 0 0; opacity: 0.9;">${data.profile_type}</p>
      </div>
      <div style="padding: 30px; background-color: #ffffff;">
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 0;">안녕하세요, 진단 결과가 도착했습니다.</h2>
        <p style="color: #4a5568; line-height: 1.6;">당신의 자존감 총점은 <strong>${data.total_score}점</strong>입니다.</p>
        <div style="background-color: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <p style="margin: 0; color: #4a5568; font-style: italic;">"${feedback}"</p>
        </div>
        <div style="margin-top: 30px; text-align: center;">
          <a href="https://dentistchi.github.io/today-me/" style="background-color: #667eea; color: white; padding: 12px 25px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">다시 검사하기</a>
        </div>
      </div>
      <div style="background-color: #f7fafc; padding: 20px; text-align: center; color: #a0aec0; font-size: 12px;">
        <p>© 2024 오늘의 나. All rights reserved.</p>
      </div>
    </div>
  `;
}