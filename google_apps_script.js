/**
 * [오늘의 나] 자존감 분석 시스템 v3.0 (GAS 버전)
 * - Python 분석 엔진(StrengthExtractor) 이식
 * - 맞춤형 심층 분석 보고서 생성 및 발송
 * - 1-4주차 자존감 향상 이메일 자동 발송
 * - 마무리 이메일 (5주차) 자동 발송
 */

function doPost(e) {
  try {
    // 스프레드시트 ID를 직접 지정 (Script Properties에서 가져오기)
    var properties = PropertiesService.getScriptProperties();
    var spreadsheetId = properties.getProperty('SPREADSHEET_ID');
    
    var params = e.parameter;
    
    Logger.log("=== doPost 시작 ===");
    Logger.log("수신 이메일: " + params.email);
    
    // 1. 답변 데이터 파싱 (JSON 문자열 -> 배열)
    var answers = [];
    try {
      answers = JSON.parse(params.answers || "[]");
      Logger.log("답변 파싱 완료: " + answers.length + "개");
    } catch (err) {
      Logger.log("JSON 파싱 오류: " + err);
      answers = [];
    }

    // 2. 부주의 응답 감지 (Low Variance Check)
    var variance = calculateVariance(answers);
    var reliability = variance < 0.3 ? "Low (Careless)" : "Normal";
    Logger.log("응답 신뢰도: " + reliability + " (variance: " + variance.toFixed(3) + ")");

    // 3. 스프레드시트에 데이터 저장 (ID가 있는 경우에만)
    if (spreadsheetId) {
      try {
        var spreadsheet = SpreadsheetApp.openById(spreadsheetId);
        var sheet = spreadsheet.getActiveSheet();
        
        // 시트 헤더 설정 (없을 경우)
        if (sheet.getLastRow() === 0) {
          sheet.appendRow([
            "Timestamp", "Email", "Total Score", "Core", "Compassion", 
            "Stability", "Growth", "Social", "Profile Type", "Answers", "Variance", "Reliability"
          ]);
        }
        
        // 4. 데이터 저장
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
          params.answers,
          variance.toFixed(3),
          reliability
        ]);
        
        Logger.log("✅ 스프레드시트 저장 완료");
      } catch (sheetError) {
        Logger.log("❌ 스프레드시트 저장 실패: " + sheetError);
      }
    } else {
      Logger.log("⚠️ SPREADSHEET_ID가 설정되지 않음");
    }
  
    // 5. 고급 분석: 강점 추출 (Python Logic 이식)
    var strengths = extractStrengths(answers);
    Logger.log("강점 추출 완료: " + strengths.length + "개");
    
    // 6. 즉시 발송: 진단 완료 알림 이메일
    var userName = params.email.split('@')[0];
    var welcomeEmailBody = createWelcomeEmail(userName);
    
    // 7. 즉시 이메일 발송 (진단 완료 알림)
    Logger.log("📧 이메일 발송 시도: " + params.email);
    MailApp.sendEmail({
      to: params.email,
      subject: "[자존감 진단 완료] " + userName + "님, 검사가 완료되었습니다 🎉",
      htmlBody: welcomeEmailBody,
      name: "bty Training Team"
    });
    Logger.log("✅ 환영 이메일 발송 완료!");
    
    // 8. 모든 후속 이메일을 위한 트리거 설정
    scheduleAllFollowUpEmails(params, userName, strengths);
    Logger.log("✅ 모든 트리거 설정 완료");
    
    // 성공 응답 반환
    return ContentService.createTextOutput(JSON.stringify({
      "result":"success",
      "message": "이메일이 발송되었습니다",
      "email": params.email
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    Logger.log("❌ 치명적 오류: " + error);
    Logger.log("오류 스택: " + error.stack);
    
    // 오류 응답 반환
    return ContentService.createTextOutput(JSON.stringify({
      "result":"error",
      "message": error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 모든 후속 이메일 스케줄링 (24시간 후 ~ 5주차)
 * 테스트용: 2~7분 간격으로 설정
 */
function scheduleAllFollowUpEmails(params, userName, strengths) {
  var properties = PropertiesService.getScriptProperties();
  var timestamp = new Date().getTime();
  
  var triggerData = {
    email: params.email,
    userName: userName,
    totalScore: params.total_score,
    coreScore: params.core_score,
    compassionScore: params.compassion_score,
    stabilityScore: params.stability_score,
    growthScore: params.growth_score,
    socialScore: params.social_score,
    profileType: params.profile_type,
    answers: params.answers,
    strengths: JSON.stringify(strengths),
    timestamp: timestamp
  };
  
  // 고유 키로 저장 (이메일 주소로 단순화)
  var dataKey = "user_" + params.email.replace(/[@.]/g, '_');
  properties.setProperty(dataKey, JSON.stringify(triggerData));
  Logger.log("사용자 데이터 저장: " + dataKey);
  
  try {
    // 1. 24시간 후: 상세 분석 보고서 (테스트: 2분)
    var trigger1 = ScriptApp.newTrigger('sendDelayedDetailedReport')
      .timeBased()
      .after(2 * 60 * 1000) // 테스트용: 2분 (실제: 24 * 60 * 60 * 1000)
      .create();
    Logger.log("트리거 1 생성: 상세 보고서 (2분 후) - " + trigger1.getUniqueId());
    
    // 2. 1주 후: 1주차 이메일 (테스트: 3분)
    var trigger2 = ScriptApp.newTrigger('sendWeek1Email')
      .timeBased()
      .after(3 * 60 * 1000) // 테스트용: 3분 (실제: 7 * 24 * 60 * 60 * 1000)
      .create();
    Logger.log("트리거 2 생성: Week 1 (3분 후) - " + trigger2.getUniqueId());
    
    // 3. 2주 후: 2주차 이메일 (테스트: 4분)
    var trigger3 = ScriptApp.newTrigger('sendWeek2Email')
      .timeBased()
      .after(4 * 60 * 1000) // 테스트용: 4분 (실제: 14 * 24 * 60 * 60 * 1000)
      .create();
    Logger.log("트리거 3 생성: Week 2 (4분 후) - " + trigger3.getUniqueId());
    
    // 4. 3주 후: 3주차 이메일 (테스트: 5분)
    var trigger4 = ScriptApp.newTrigger('sendWeek3Email')
      .timeBased()
      .after(5 * 60 * 1000) // 테스트용: 5분 (실제: 21 * 24 * 60 * 60 * 1000)
      .create();
    Logger.log("트리거 4 생성: Week 3 (5분 후) - " + trigger4.getUniqueId());
    
    // 5. 4주 후: 4주차 이메일 (테스트: 6분)
    var trigger5 = ScriptApp.newTrigger('sendWeek4Email')
      .timeBased()
      .after(6 * 60 * 1000) // 테스트용: 6분 (실제: 28 * 24 * 60 * 60 * 1000)
      .create();
    Logger.log("트리거 5 생성: Week 4 (6분 후) - " + trigger5.getUniqueId());
    
    // 6. 5주 후: 마무리 이메일 (테스트: 7분)
    var trigger6 = ScriptApp.newTrigger('sendCompletionEmail')
      .timeBased()
      .after(7 * 60 * 1000) // 테스트용: 7분 (실제: 35 * 24 * 60 * 60 * 1000)
      .create();
    Logger.log("트리거 6 생성: 완료 이메일 (7분 후) - " + trigger6.getUniqueId());
    
    // 트리거 ID 저장
    var triggerIds = {
      detailed: trigger1.getUniqueId(),
      week1: trigger2.getUniqueId(),
      week2: trigger3.getUniqueId(),
      week3: trigger4.getUniqueId(),
      week4: trigger5.getUniqueId(),
      completion: trigger6.getUniqueId()
    };
    properties.setProperty(dataKey + "_triggers", JSON.stringify(triggerIds));
    Logger.log("✅ 모든 트리거 ID 저장 완료");
    
  } catch (triggerError) {
    Logger.log("❌ 트리거 설정 실패: " + triggerError);
    throw triggerError;
  }
}

/**
 * 응답 분산 계산 (부주의 응답 감지용)
 */
function calculateVariance(arr) {
  if (!arr || arr.length === 0) return 0;
  
  var sum = 0;
  for (var i = 0; i < arr.length; i++) sum += parseInt(arr[i]);
  var mean = sum / arr.length;
  
  var sqDiffSum = 0;
  for (var i = 0; i < arr.length; i++) sqDiffSum += Math.pow(parseInt(arr[i]) - mean, 2);
  
  return sqDiffSum / arr.length;
}

/**
 * 강점 추출 엔진 (Python StrengthExtractor 이식)
 * 답변 패턴을 분석하여 상위 강점을 추출합니다.
 */
function extractStrengths(answers) {
  // Python 코드의 strength_patterns 정의
  var patterns = {
    'resilience': {
      name: '회복탄력성 (Resilience)',
      detail: '어려운 상황에서도 포기하지 않으려는 강한 의지',
      indices: [6, 18, 33, 41], // Python 코드의 인덱스
      threshold: 2.5 // 3.0 -> 2.5로 낮춤
    },
    'empathy': {
      name: '공감 능력 (Empathy)',
      detail: '타인의 감정을 이해하고 배려하는 따뜻한 마음',
      indices: [14, 27, 38, 45],
      threshold: 2.5
    },
    'self_awareness': {
      name: '자기인식 (Self-Awareness)',
      detail: '자신의 감정과 생각을 객관적으로 이해하는 능력',
      indices: [2, 12, 23, 36, 47],
      threshold: 2.5
    },
    'perseverance': {
      name: '끈기 (Perseverance)',
      detail: '목표를 향해 꾸준히 노력하는 성실함',
      indices: [8, 19, 29, 42],
      threshold: 2.5
    },
    'optimism': {
      name: '낙관성 (Optimism)',
      detail: '미래에 대한 희망과 긍정적 기대',
      indices: [5, 16, 26, 37, 48],
      threshold: 2.5
    }
  };

  var candidates = [];

  // 각 강점별 점수 계산
  for (var key in patterns) {
    var pattern = patterns[key];
    var sum = 0;
    var count = 0;
    
    for (var i = 0; i < pattern.indices.length; i++) {
      var idx = pattern.indices[i];
      // answers 배열 범위 체크
      if (idx < answers.length) {
        sum += parseInt(answers[idx]);
        count++;
      }
    }
    
    var avg = count > 0 ? sum / count : 0;
    
    candidates.push({
      name: pattern.name,
      detail: pattern.detail,
      score: avg,
      threshold: pattern.threshold
    });
  }

  // 점수 높은 순 정렬
  candidates.sort(function(a, b) { return b.score - a.score; });

  // 1차 필터: 임계값 넘는 것만 추출
  var results = candidates.filter(function(item) {
    return item.score >= item.threshold;
  });

  // Fallback: 만약 강점이 3개 미만이면, 점수가 높은 순서대로 채움 (임계값 무시)
  if (results.length < 3) {
    results = candidates.slice(0, 3);
  }

  return results.slice(0, 3);
}

/**
 * 심층 분석 이메일 템플릿 생성 (Python generate_detailed_email 이식)
 */
function createDetailedEmail(name, data, strengths) {
  var score = parseInt(data.total_score);
  var feedbackTitle = "";
  var feedbackContent = "";
  
  // 점수대별 피드백
  if (score >= 70) {
    feedbackTitle = "건강하고 단단한 마음을 가지셨군요!";
    feedbackContent = "당신은 자신을 있는 그대로 존중하며, 실패를 성장의 기회로 삼는 훌륭한 태도를 가지고 있습니다. 지금의 긍정적인 에너지를 주변 사람들에게도 나눠주세요.";
  } else if (score >= 40) {
    feedbackTitle = "성장의 여정에 계시는군요.";
    feedbackContent = "당신은 자신을 사랑하려고 노력하고 있습니다. 때로는 흔들릴 수 있지만, 그것은 더 단단해지기 위한 과정입니다. 스스로에게 조금 더 친절해지는 연습을 해보세요.";
  } else {
    feedbackTitle = "지금은 잠시 웅크리고 있는 시기입니다.";
    feedbackContent = "현재 마음이 조금 지쳐있는 것 같습니다. 하지만 기억하세요, 자존감은 고정된 것이 아니라 연습을 통해 얼마든지 키울 수 있는 근육과 같습니다. 당신은 충분히 가치 있는 사람입니다.";
  }

  // 강점 HTML 생성
  var strengthsHtml = "";
  if (strengths.length > 0) {
    strengthsHtml = '<div style="background-color: #f0fff4; border-left: 4px solid #48bb78; padding: 15px; margin: 20px 0; border-radius: 4px;">' +
      '<h3 style="margin: 0 0 10px; color: #2f855a;">💎 당신의 숨겨진 강점 3가지</h3>';
    
    for (var i = 0; i < strengths.length; i++) {
      strengthsHtml += '<div style="margin-bottom: 10px;">' +
        '<strong>' + (i+1) + '. ' + strengths[i].name + '</strong><br>' +
        '<span style="color: #4a5568; font-size: 14px;">' + strengths[i].detail + '</span>' +
        '</div>';
    }
    strengthsHtml += '</div>';
  } else {
    strengthsHtml = '<div style="background-color: #fffaf0; padding: 15px; margin: 20px 0; border-radius: 4px; color: #744210;">' +
      '아직 뚜렷한 강점이 발견되지 않았나요? 괜찮습니다. 이것은 당신이 무한한 잠재력을 가지고 있다는 뜻이기도 합니다.</div>';
  }

  // 5차원 점수 변환 (100점 만점 -> 10점 만점)
  var core = (data.core_score / 10).toFixed(1);
  var compassion = (data.compassion_score / 10).toFixed(1);
  var stability = (data.stability_score / 10).toFixed(1);
  var growth = (data.growth_score / 10).toFixed(1);
  var social = (data.social_score / 10).toFixed(1);

  return `
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 640px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
      <!-- 헤더 -->
      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; color: white;">
        <div style="font-size: 40px; margin-bottom: 10px;">✨</div>
        <h1 style="margin: 0; font-size: 26px; font-weight: 700;">자존감 심층 분석 보고서</h1>
        <p style="margin: 10px 0 0; opacity: 0.9; font-size: 16px;">${name}님의 분석 결과</p>
      </div>
      
      <!-- 본문 -->
      <div style="padding: 40px 30px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 30px;">
          <p style="color: #718096; font-size: 14px; margin-bottom: 5px;">종합 자존감 점수</p>
          <div style="font-size: 48px; font-weight: 800; color: #4a5568;">${data.total_score}<span style="font-size: 20px; color: #a0aec0; font-weight: 400;">/100</span></div>
          <div style="display: inline-block; background-color: #edf2f7; padding: 5px 15px; border-radius: 20px; font-size: 14px; color: #4a5568; margin-top: 10px;">
            유형: <strong>${data.profile_type}</strong>
          </div>
        </div>

        <div style="margin-bottom: 30px;">
          <h2 style="color: #2d3748; font-size: 20px; border-bottom: 2px solid #edf2f7; padding-bottom: 10px;">📊 분석 요약</h2>
          <p style="font-weight: bold; color: #4a5568; font-size: 18px; margin-bottom: 10px;">"${feedbackTitle}"</p>
          <p style="color: #4a5568; line-height: 1.7;">${feedbackContent}</p>
        </div>

        ${strengthsHtml}

        <div style="margin-top: 30px;">
          <h2 style="color: #2d3748; font-size: 20px; border-bottom: 2px solid #edf2f7; padding-bottom: 10px;">📈 5차원 상세 분석</h2>
          <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <tr style="border-bottom: 1px solid #edf2f7;">
              <td style="padding: 10px 0; color: #718096;">핵심 자존감 (Core)</td>
              <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #4a5568;">${core}/10</td>
            </tr>
            <tr style="border-bottom: 1px solid #edf2f7;">
              <td style="padding: 10px 0; color: #718096;">자기자비 (Self-Compassion)</td>
              <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #4a5568;">${compassion}/10</td>
            </tr>
            <tr style="border-bottom: 1px solid #edf2f7;">
              <td style="padding: 10px 0; color: #718096;">자존감 안정성 (Stability)</td>
              <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #4a5568;">${stability}/10</td>
            </tr>
            <tr style="border-bottom: 1px solid #edf2f7;">
              <td style="padding: 10px 0; color: #718096;">성장 마인드셋 (Growth)</td>
              <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #4a5568;">${growth}/10</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; color: #718096;">사회적 자존감 (Social)</td>
              <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #4a5568;">${social}/10</td>
            </tr>
          </table>
        </div>

        <div style="margin-top: 40px; text-align: center;">
          <a href="https://dentistchi.github.io/today-me/" style="background-color: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);">다시 검사하기</a>
          <p style="margin-top: 20px; font-size: 12px; color: #a0aec0;">이 결과는 의료적 진단이 아니며, 자기 이해를 돕기 위한 참고 자료입니다.</p>
        </div>
      </div>
      
      <!-- 푸터 -->
      <div style="background-color: #f7fafc; padding: 20px; text-align: center; color: #a0aec0; font-size: 12px;">
        <p>© 2024 오늘의 나. All rights reserved.</p>
      </div>
    </div>
  `;
}

/**
 * 환영 이메일 생성 (즉시 발송용)
 */
function createWelcomeEmail(userName) {
  return `
    <html>
    <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2C3E50;">안녕하세요, ${userName}님!</h2>
        
        <p>자존감 진단이 완료되었습니다. 용기 내어 자신을 돌아본 당신을 응원합니다. 🎉</p>
        
        <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
            <h3 style="color: #27AE60; margin-top: 0;">✅ 진단 완료</h3>
            <p>당신의 응답을 분석하여 맞춤형 보고서를 준비하고 있습니다.</p>
        </div>
        
        <h3 style="color: #3498DB;">📊 다음 단계</h3>
        <div style="background-color: #FEF5E7; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>💎 24시간 후</strong></p>
            <p>당신만을 위한 <strong>완전한 심층 분석 보고서 (PDF)</strong>를 이메일로 보내드립니다.</p>
            <ul style="margin-top: 10px;">
                <li>5차원 자존감 점수 상세 분석</li>
                <li>당신의 숨겨진 강점 발견</li>
                <li>개인 맞춤형 성장 제안</li>
                <li>4주 맞춤 성장 로드맵</li>
                <li>PDF 보고서 첨부</li>
            </ul>
        </div>
        
        <div style="background-color: #EBF5FB; padding: 15px; border-left: 4px solid #3498DB; margin: 20px 0;">
            <p style="margin: 0;"><strong>🗓️ 5주간의 자존감 향상 여정</strong></p>
            <p style="margin: 5px 0 0 0;">앞으로 5주 동안, 매주 당신의 성장을 돕는 맞춤형 이메일을 보내드립니다.<br/>
            - 1주차: 자기자비 연습<br/>
            - 2주차: 핵심 자존감 강화<br/>
            - 3주차: 성장 마인드셋 구축<br/>
            - 4주차: 사회적 자존감 향상<br/>
            - 5주차: 마무리 및 성장 리뷰</p>
        </div>
        
        <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
            <p style="margin: 0;"><strong>💚 응원 메시지</strong></p>
            <p style="margin: 5px 0 0 0;">완벽하지 않아도 괜찮습니다. 중요한 것은 방향입니다.<br/>
            24시간 후 상세한 분석 보고서를 통해 당신의 여정을 함께하겠습니다.</p>
        </div>
        
        <p style="margin-top: 30px;">
            24시간 후에 다시 만나요!<br/>
            bty Training Team 💚
        </p>
    </body>
    </html>
  `;
}

/**
 * 24시간 후 상세 보고서 발송
 * (트리거로 자동 실행됨)
 */
/**
 * 24시간 후 상세 보고서 발송 (테스트: 2분 후)
 * (트리거로 자동 실행됨)
 */
function sendDelayedDetailedReport() {
  Logger.log("=== sendDelayedDetailedReport 실행 시작 ===");
  var properties = PropertiesService.getScriptProperties();
  var allProperties = properties.getProperties();
  
  // 모든 사용자 데이터 찾기
  for (var key in allProperties) {
    if (key.startsWith("user_") && !key.endsWith("_triggers") && !key.endsWith("_detailed_sent")) {
      try {
        Logger.log("처리 중인 키: " + key);
        var triggerData = JSON.parse(allProperties[key]);
        
        // 이미 발송되었는지 확인
        var sentFlag = properties.getProperty(key + "_detailed_sent");
        if (sentFlag === "sent") {
          Logger.log("⏭️ 이미 발송됨: " + triggerData.email);
          continue;
        }
        
        Logger.log("📧 상세 보고서 발송 시작: " + triggerData.email);
        
        // 강점 데이터 복원
        var strengths = JSON.parse(triggerData.strengths);
        
        // 상세 분석 이메일 생성
        var params = {
          email: triggerData.email,
          total_score: triggerData.totalScore,
          core_score: triggerData.coreScore,
          compassion_score: triggerData.compassionScore,
          stability_score: triggerData.stabilityScore,
          growth_score: triggerData.growthScore,
          social_score: triggerData.socialScore,
          profile_type: triggerData.profileType,
          answers: triggerData.answers
        };
        
        var emailBody = createDetailedEmail(triggerData.userName, params, strengths);
        var textBody = createTextFallback(triggerData.userName, params);
        
        // 이메일 발송
        MailApp.sendEmail({
          to: triggerData.email,
          subject: "[자존감 분석 결과] " + triggerData.userName + "님, 당신의 진단 결과를 확인하세요 📊",
          htmlBody: emailBody,
          body: textBody,
          name: "bty Training Team"
        });
        
        // 발송 완료 표시
        properties.setProperty(key + "_detailed_sent", "sent");
        Logger.log("✅ 상세 보고서 발송 완료: " + triggerData.email);
        
      } catch (error) {
        Logger.log("❌ 발송 오류 (" + key + "): " + error);
      }
    }
  }
  Logger.log("=== sendDelayedDetailedReport 실행 완료 ===");
}
    }
  }
}

/**
 * 1주차 이메일 발송: 자기자비 연습
 */
function sendWeek1Email() {
  var properties = PropertiesService.getScriptProperties();
  var allProperties = properties.getProperties();
  
  for (var key in allProperties) {
    if (key.startsWith("week1_email_") && !key.endsWith("_scheduled") && !key.endsWith("_sent")) {
      try {
        var triggerData = JSON.parse(allProperties[key]);
        var currentTime = new Date().getTime();
        var elapsedDays = (currentTime - triggerData.timestamp) / (1000 * 60 * 60 * 24);
        
        if (elapsedDays >= 7) {
          var emailBody = createWeek1EmailContent(triggerData.userName, triggerData);
          
          MailApp.sendEmail({
            to: triggerData.email,
            subject: "[1주차] " + triggerData.userName + "님, 자기자비 연습으로 시작하세요 🌱",
            htmlBody: emailBody,
            name: "bty Training Team"
          });
          
          properties.setProperty(key + "_sent", "true");
          properties.deleteProperty(key);
          properties.deleteProperty(key + "_scheduled");
          
          Logger.log("1주차 이메일 발송 완료: " + triggerData.email);
        }
      } catch (error) {
        Logger.log("1주차 이메일 발송 중 오류: " + error);
      }
    }
  }
}

/**
 * 2주차 이메일 발송: 핵심 자존감 강화
 */
function sendWeek2Email() {
  var properties = PropertiesService.getScriptProperties();
  var allProperties = properties.getProperties();
  
  for (var key in allProperties) {
    if (key.startsWith("week2_email_") && !key.endsWith("_scheduled") && !key.endsWith("_sent")) {
      try {
        var triggerData = JSON.parse(allProperties[key]);
        var currentTime = new Date().getTime();
        var elapsedDays = (currentTime - triggerData.timestamp) / (1000 * 60 * 60 * 24);
        
        if (elapsedDays >= 14) {
          var emailBody = createWeek2EmailContent(triggerData.userName, triggerData);
          
          MailApp.sendEmail({
            to: triggerData.email,
            subject: "[2주차] " + triggerData.userName + "님, 핵심 자존감을 강화하세요 💪",
            htmlBody: emailBody,
            name: "bty Training Team"
          });
          
          properties.setProperty(key + "_sent", "true");
          properties.deleteProperty(key);
          properties.deleteProperty(key + "_scheduled");
          
          Logger.log("2주차 이메일 발송 완료: " + triggerData.email);
        }
      } catch (error) {
        Logger.log("2주차 이메일 발송 중 오류: " + error);
      }
    }
  }
}

/**
 * 3주차 이메일 발송: 성장 마인드셋 구축
 */
function sendWeek3Email() {
  var properties = PropertiesService.getScriptProperties();
  var allProperties = properties.getProperties();
  
  for (var key in allProperties) {
    if (key.startsWith("week3_email_") && !key.endsWith("_scheduled") && !key.endsWith("_sent")) {
      try {
        var triggerData = JSON.parse(allProperties[key]);
        var currentTime = new Date().getTime();
        var elapsedDays = (currentTime - triggerData.timestamp) / (1000 * 60 * 60 * 24);
        
        if (elapsedDays >= 21) {
          var emailBody = createWeek3EmailContent(triggerData.userName, triggerData);
          
          MailApp.sendEmail({
            to: triggerData.email,
            subject: "[3주차] " + triggerData.userName + "님, 성장 마인드셋을 키워보세요 🚀",
            htmlBody: emailBody,
            name: "bty Training Team"
          });
          
          properties.setProperty(key + "_sent", "true");
          properties.deleteProperty(key);
          properties.deleteProperty(key + "_scheduled");
          
          Logger.log("3주차 이메일 발송 완료: " + triggerData.email);
        }
      } catch (error) {
        Logger.log("3주차 이메일 발송 중 오류: " + error);
      }
    }
  }
}

/**
 * 4주차 이메일 발송: 사회적 자존감 향상
 */
function sendWeek4Email() {
  var properties = PropertiesService.getScriptProperties();
  var allProperties = properties.getProperties();
  
  for (var key in allProperties) {
    if (key.startsWith("week4_email_") && !key.endsWith("_scheduled") && !key.endsWith("_sent")) {
      try {
        var triggerData = JSON.parse(allProperties[key]);
        var currentTime = new Date().getTime();
        var elapsedDays = (currentTime - triggerData.timestamp) / (1000 * 60 * 60 * 24);
        
        if (elapsedDays >= 28) {
          var emailBody = createWeek4EmailContent(triggerData.userName, triggerData);
          
          MailApp.sendEmail({
            to: triggerData.email,
            subject: "[4주차] " + triggerData.userName + "님, 사회적 자존감을 높여보세요 🤝",
            htmlBody: emailBody,
            name: "bty Training Team"
          });
          
          properties.setProperty(key + "_sent", "true");
          properties.deleteProperty(key);
          properties.deleteProperty(key + "_scheduled");
          
          Logger.log("4주차 이메일 발송 완료: " + triggerData.email);
        }
      } catch (error) {
        Logger.log("4주차 이메일 발송 중 오류: " + error);
      }
    }
  }
}

/**
 * 마무리 이메일 발송 (5주차)
 */
function sendFinalEmail() {
  var properties = PropertiesService.getScriptProperties();
  var allProperties = properties.getProperties();
  
  for (var key in allProperties) {
    if (key.startsWith("final_email_") && !key.endsWith("_scheduled") && !key.endsWith("_sent")) {
      try {
        var triggerData = JSON.parse(allProperties[key]);
        var currentTime = new Date().getTime();
        var elapsedDays = (currentTime - triggerData.timestamp) / (1000 * 60 * 60 * 24);
        
        if (elapsedDays >= 35) {
          var emailBody = createFinalEmailContent(triggerData.userName, triggerData);
          
          MailApp.sendEmail({
            to: triggerData.email,
            subject: "[마무리] " + triggerData.userName + "님, 5주간의 여정을 돌아봅니다 🎊",
            htmlBody: emailBody,
            name: "bty Training Team"
          });
          
          properties.setProperty(key + "_sent", "true");
          properties.deleteProperty(key);
          properties.deleteProperty(key + "_scheduled");
          
          Logger.log("마무리 이메일 발송 완료: " + triggerData.email);
        }
      } catch (error) {
        Logger.log("마무리 이메일 발송 중 오류: " + error);
      }
    }
  }
}

/**
 * ========================================
 * 주차별 이메일 컨텐츠 생성 함수들
 * ========================================
 */

/**
 * 1주차: 자기자비 연습
 */
function createWeek1EmailContent(userName, data) {
  var compassionScore = (data.compassionScore / 10).toFixed(1);
  var compassionLevel = data.compassionScore >= 70 ? "높은" : data.compassionScore >= 40 ? "중간" : "낮은";
  
  return `
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 640px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); padding: 40px 30px; text-align: center; color: white;">
        <div style="font-size: 40px; margin-bottom: 10px;">🌱</div>
        <h1 style="margin: 0; font-size: 26px; font-weight: 700;">1주차: 자기자비 연습</h1>
        <p style="margin: 10px 0 0; opacity: 0.9; font-size: 16px;">${userName}님의 성장 여정</p>
      </div>
      
      <div style="padding: 40px 30px; background-color: #ffffff;">
        <p style="color: #4a5568; line-height: 1.8; font-size: 16px;">
          안녕하세요, ${userName}님! 🙌<br><br>
          5주간의 자존감 향상 여정이 시작되었습니다. 첫 번째 주제는 <strong>자기자비</strong>입니다.
        </p>
        
        <div style="background-color: #f0fff4; padding: 20px; border-left: 4px solid #48bb78; margin: 25px 0;">
          <h3 style="color: #2f855a; margin-top: 0;">📊 당신의 자기자비 점수</h3>
          <p style="font-size: 32px; font-weight: bold; color: #2f855a; margin: 10px 0;">${compassionScore} / 10</p>
          <p style="color: #4a5568; margin: 0;">현재 ${compassionLevel} 수준입니다.</p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">💚 자기자비란?</h2>
        <p style="color: #4a5568; line-height: 1.7;">
          자기자비는 실수했을 때 자신을 비난하는 대신, 친구를 대하듯 자신을 따뜻하게 위로하는 능력입니다.
          실패는 인간이라면 누구나 겪는 보편적인 경험이라는 것을 받아들이는 것입니다.
        </p>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">✍️ 이번 주 실천 과제</h2>
        
        <div style="background-color: #fff5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c53030; margin: 0 0 10px;">📝 과제 1: 자기자비 편지 쓰기</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            최근 실수했던 경험을 떠올려보세요. 그 상황에서 자신에게 보내는 편지를 써보세요.
            마치 가장 친한 친구를 위로하듯이요.
          </p>
        </div>
        
        <div style="background-color: #fffaf0; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c05621; margin: 0 0 10px;">🧘 과제 2: 자기자비 명상 (5분)</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            매일 5분간 조용한 곳에서 앉아, 자신에게 다음 문장을 반복해보세요:<br>
            <em>"나는 완벽하지 않아도 괜찮다. 나는 충분히 가치 있는 사람이다."</em>
          </p>
        </div>
        
        <div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #2c5282; margin: 0 0 10px;">📖 과제 3: 실패 일기</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            하루에 하나씩 작은 실수나 실패를 기록하고, 그것이 나를 어떻게 성장시킬 수 있는지 적어보세요.
          </p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">💡 실천 팁</h2>
        <ul style="color: #4a5568; line-height: 1.8;">
          <li>자신에게 하는 말투를 의식해보세요. 비난하는 말투라면 부드럽게 바꿔보세요.</li>
          <li>완벽주의를 내려놓으세요. 80%만 해도 충분합니다.</li>
          <li>실수는 성장의 증거입니다. 도전하지 않으면 실수도 없습니다.</li>
        </ul>
        
        <div style="background-color: #edf2f7; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
          <p style="margin: 0; color: #2d3748; font-weight: bold; font-size: 18px;">
            "자기자비는 나약함이 아니라, 진정한 강함입니다."
          </p>
          <p style="margin: 10px 0 0; color: #718096; font-size: 14px;">- 크리스틴 네프 박사</p>
        </div>
        
        <p style="color: #4a5568; line-height: 1.7; margin-top: 30px;">
          다음 주에는 <strong>핵심 자존감 강화</strong> 주제로 찾아뵙겠습니다!<br>
          1주일 동안 자신에게 친절해지는 연습을 해보세요. 💚
        </p>
        
        <div style="text-align: center; margin-top: 40px;">
          <a href="https://dentistchi.github.io/today-me/" style="background-color: #48bb78; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block;">다시 검사하기</a>
        </div>
      </div>
      
      <div style="background-color: #f7fafc; padding: 20px; text-align: center; color: #a0aec0; font-size: 12px;">
        <p>© 2024 오늘의 나. bty Training Team 💚</p>
      </div>
    </div>
  `;
}

/**
 * 2주차: 핵심 자존감 강화
 */
function createWeek2EmailContent(userName, data) {
  var coreScore = (data.coreScore / 10).toFixed(1);
  var coreLevel = data.coreScore >= 70 ? "높은" : data.coreScore >= 40 ? "중간" : "낮은";
  
  return `
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 640px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); padding: 40px 30px; text-align: center; color: white;">
        <div style="font-size: 40px; margin-bottom: 10px;">💪</div>
        <h1 style="margin: 0; font-size: 26px; font-weight: 700;">2주차: 핵심 자존감 강화</h1>
        <p style="margin: 10px 0 0; opacity: 0.9; font-size: 16px;">${userName}님의 성장 여정</p>
      </div>
      
      <div style="padding: 40px 30px; background-color: #ffffff;">
        <p style="color: #4a5568; line-height: 1.8; font-size: 16px;">
          안녕하세요, ${userName}님! 🙌<br><br>
          2주차에는 <strong>핵심 자존감</strong>을 강화하는 방법을 배워봅시다.
          핵심 자존감은 외부 평가와 무관하게 자신을 가치 있게 여기는 능력입니다.
        </p>
        
        <div style="background-color: #ebf8ff; padding: 20px; border-left: 4px solid #4299e1; margin: 25px 0;">
          <h3 style="color: #2c5282; margin-top: 0;">📊 당신의 핵심 자존감 점수</h3>
          <p style="font-size: 32px; font-weight: bold; color: #2c5282; margin: 10px 0;">${coreScore} / 10</p>
          <p style="color: #4a5568; margin: 0;">현재 ${coreLevel} 수준입니다.</p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">💙 핵심 자존감이란?</h2>
        <p style="color: #4a5568; line-height: 1.7;">
          핵심 자존감은 "나는 존재 자체로 가치 있다"는 깊은 믿음입니다.
          성과나 타인의 평가가 아닌, 내가 살아있다는 사실만으로도 충분하다는 것을 아는 것입니다.
        </p>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">✍️ 이번 주 실천 과제</h2>
        
        <div style="background-color: #fff5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c53030; margin: 0 0 10px;">📝 과제 1: 가치 선언문 작성</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            "나는 _____하기 때문에 가치 있다"가 아닌,<br>
            "나는 존재 자체로 가치 있다. 왜냐하면 _____"로 시작하는 문장 3개를 작성해보세요.
          </p>
        </div>
        
        <div style="background-color: #fffaf0; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c05621; margin: 0 0 10px;">🪞 과제 2: 거울 긍정 확언</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            매일 아침 거울을 보며 자신에게 말해보세요:<br>
            <em>"나는 충분하다. 나는 가치 있다. 나는 사랑받을 자격이 있다."</em>
          </p>
        </div>
        
        <div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #2c5282; margin: 0 0 10px;">🎯 과제 3: 강점 목록 만들기</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            자신의 강점을 10가지 이상 적어보세요. 작은 것도 좋습니다.
            (예: 시간 약속을 잘 지킨다, 친구의 말을 잘 들어준다 등)
          </p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">💡 실천 팁</h2>
        <ul style="color: #4a5568; line-height: 1.8;">
          <li>타인과 자신을 비교하지 마세요. 당신의 여정은 독특합니다.</li>
          <li>성과가 없어도 당신은 가치 있습니다.</li>
          <li>자신의 작은 성취를 축하해주세요.</li>
        </ul>
        
        <div style="background-color: #edf2f7; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
          <p style="margin: 0; color: #2d3748; font-weight: bold; font-size: 18px;">
            "자존감은 무엇을 하느냐가 아니라, 누구인가에서 나옵니다."
          </p>
          <p style="margin: 10px 0 0; color: #718096; font-size: 14px;">- 나다니엘 브랜든</p>
        </div>
        
        <p style="color: #4a5568; line-height: 1.7; margin-top: 30px;">
          다음 주에는 <strong>성장 마인드셋 구축</strong> 주제로 찾아뵙겠습니다!<br>
          이번 주는 자신의 존재 가치를 인정하는 연습을 해보세요. 💙
        </p>
        
        <div style="text-align: center; margin-top: 40px;">
          <a href="https://dentistchi.github.io/today-me/" style="background-color: #4299e1; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block;">다시 검사하기</a>
        </div>
      </div>
      
      <div style="background-color: #f7fafc; padding: 20px; text-align: center; color: #a0aec0; font-size: 12px;">
        <p>© 2024 오늘의 나. bty Training Team 💙</p>
      </div>
    </div>
  `;
}

/**
 * 3주차: 성장 마인드셋 구축
 */
function createWeek3EmailContent(userName, data) {
  var growthScore = (data.growthScore / 10).toFixed(1);
  var growthLevel = data.growthScore >= 70 ? "높은" : data.growthScore >= 40 ? "중간" : "낮은";
  
  return `
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 640px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); padding: 40px 30px; text-align: center; color: white;">
        <div style="font-size: 40px; margin-bottom: 10px;">🚀</div>
        <h1 style="margin: 0; font-size: 26px; font-weight: 700;">3주차: 성장 마인드셋 구축</h1>
        <p style="margin: 10px 0 0; opacity: 0.9; font-size: 16px;">${userName}님의 성장 여정</p>
      </div>
      
      <div style="padding: 40px 30px; background-color: #ffffff;">
        <p style="color: #4a5568; line-height: 1.8; font-size: 16px;">
          안녕하세요, ${userName}님! 🙌<br><br>
          3주차 주제는 <strong>성장 마인드셋</strong>입니다.
          실패를 두려워하지 않고 도전을 즐기는 태도를 기르는 시간입니다.
        </p>
        
        <div style="background-color: #fffaf0; padding: 20px; border-left: 4px solid #ed8936; margin: 25px 0;">
          <h3 style="color: #c05621; margin-top: 0;">📊 당신의 성장 마인드셋 점수</h3>
          <p style="font-size: 32px; font-weight: bold; color: #c05621; margin: 10px 0;">${growthScore} / 10</p>
          <p style="color: #4a5568; margin: 0;">현재 ${growthLevel} 수준입니다.</p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">🧡 성장 마인드셋이란?</h2>
        <p style="color: #4a5568; line-height: 1.7;">
          성장 마인드셋은 능력은 고정되어 있지 않으며, 노력과 학습을 통해 얼마든지 발전할 수 있다는 믿음입니다.
          실패는 끝이 아니라 배움의 기회입니다.
        </p>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">✍️ 이번 주 실천 과제</h2>
        
        <div style="background-color: #fff5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c53030; margin: 0 0 10px;">📝 과제 1: "아직" 추가하기</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            "나는 못해" 대신 "나는 아직 못해"라고 말해보세요.<br>
            "아직"이라는 단어가 가능성의 문을 엽니다.
          </p>
        </div>
        
        <div style="background-color: #fffaf0; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c05621; margin: 0 0 10px;">📚 과제 2: 실패 박물관</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            과거의 실패 3가지를 떠올리고, 그 실패에서 배운 교훈을 적어보세요.
            실패는 성장의 증거입니다.
          </p>
        </div>
        
        <div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #2c5282; margin: 0 0 10px;">🎯 과제 3: 도전 과제 설정</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            이번 주에 작은 도전을 하나 선택해보세요.
            (예: 처음 해보는 요리, 새로운 사람과 대화하기 등)
          </p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">💡 실천 팁</h2>
        <ul style="color: #4a5568; line-height: 1.8;">
          <li>완벽을 추구하지 말고, 진전을 축하하세요.</li>
          <li>타인의 성공을 위협이 아닌 영감으로 받아들이세요.</li>
          <li>노력의 과정을 칭찬하세요, 결과만이 아니라.</li>
        </ul>
        
        <div style="background-color: #edf2f7; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
          <p style="margin: 0; color: #2d3748; font-weight: bold; font-size: 18px;">
            "재능은 출발점일 뿐, 성장은 노력으로 만들어집니다."
          </p>
          <p style="margin: 10px 0 0; color: #718096; font-size: 14px;">- 캐롤 드웩 박사</p>
        </div>
        
        <p style="color: #4a5568; line-height: 1.7; margin-top: 30px;">
          다음 주에는 <strong>사회적 자존감 향상</strong> 주제로 찾아뵙겠습니다!<br>
          이번 주는 실패를 두려워하지 말고 작은 도전을 시도해보세요. 🧡
        </p>
        
        <div style="text-align: center; margin-top: 40px;">
          <a href="https://dentistchi.github.io/today-me/" style="background-color: #ed8936; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block;">다시 검사하기</a>
        </div>
      </div>
      
      <div style="background-color: #f7fafc; padding: 20px; text-align: center; color: #a0aec0; font-size: 12px;">
        <p>© 2024 오늘의 나. bty Training Team 🧡</p>
      </div>
    </div>
  `;
}

/**
 * 4주차: 사회적 자존감 향상
 */
function createWeek4EmailContent(userName, data) {
  var socialScore = (data.socialScore / 10).toFixed(1);
  var socialLevel = data.socialScore >= 70 ? "높은" : data.socialScore >= 40 ? "중간" : "낮은";
  
  return `
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 640px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%); padding: 40px 30px; text-align: center; color: white;">
        <div style="font-size: 40px; margin-bottom: 10px;">🤝</div>
        <h1 style="margin: 0; font-size: 26px; font-weight: 700;">4주차: 사회적 자존감 향상</h1>
        <p style="margin: 10px 0 0; opacity: 0.9; font-size: 16px;">${userName}님의 성장 여정</p>
      </div>
      
      <div style="padding: 40px 30px; background-color: #ffffff;">
        <p style="color: #4a5568; line-height: 1.8; font-size: 16px;">
          안녕하세요, ${userName}님! 🙌<br><br>
          4주차 주제는 <strong>사회적 자존감</strong>입니다.
          타인과의 관계 속에서도 자신의 가치를 지키는 법을 배워봅시다.
        </p>
        
        <div style="background-color: #faf5ff; padding: 20px; border-left: 4px solid #9f7aea; margin: 25px 0;">
          <h3 style="color: #6b46c1; margin-top: 0;">📊 당신의 사회적 자존감 점수</h3>
          <p style="font-size: 32px; font-weight: bold; color: #6b46c1; margin: 10px 0;">${socialScore} / 10</p>
          <p style="color: #4a5568; margin: 0;">현재 ${socialLevel} 수준입니다.</p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">💜 사회적 자존감이란?</h2>
        <p style="color: #4a5568; line-height: 1.7;">
          사회적 자존감은 타인의 시선이나 평가에 흔들리지 않고, 관계 속에서도 나다움을 유지하는 능력입니다.
          건강한 경계를 설정하고, 거절할 수 있는 용기를 갖는 것입니다.
        </p>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">✍️ 이번 주 실천 과제</h2>
        
        <div style="background-color: #fff5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c53030; margin: 0 0 10px;">📝 과제 1: 경계 설정 연습</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            이번 주에 불편한 부탁을 받으면, 정중하게 거절해보세요.<br>
            "미안하지만, 이번에는 어려울 것 같아요."라고 말하는 연습을 하세요.
          </p>
        </div>
        
        <div style="background-color: #fffaf0; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #c05621; margin: 0 0 10px;">👥 과제 2: 감사 표현하기</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            주변 사람 3명에게 진심 어린 감사의 말을 전해보세요.
            긍정적인 관계는 자존감을 높입니다.
          </p>
        </div>
        
        <div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <h4 style="color: #2c5282; margin: 0 0 10px;">🗣️ 과제 3: 나의 의견 말하기</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            이번 주에 의견을 묻는 상황이 생기면, 솔직하게 자신의 생각을 표현해보세요.
            "나는 이렇게 생각해."
          </p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">💡 실천 팁</h2>
        <ul style="color: #4a5568; line-height: 1.8;">
          <li>모든 사람에게 사랑받을 필요는 없습니다.</li>
          <li>거절은 거부가 아니라, 자기 존중의 표현입니다.</li>
          <li>타인의 감정에 책임을 느끼지 마세요.</li>
        </ul>
        
        <div style="background-color: #edf2f7; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
          <p style="margin: 0; color: #2d3748; font-weight: bold; font-size: 18px;">
            "타인의 승인을 구하지 않아도, 당신은 충분히 가치 있습니다."
          </p>
          <p style="margin: 10px 0 0; color: #718096; font-size: 14px;">- 브레네 브라운</p>
        </div>
        
        <p style="color: #4a5568; line-height: 1.7; margin-top: 30px;">
          다음 주에는 <strong>5주간의 여정 마무리</strong>로 찾아뵙겠습니다!<br>
          이번 주는 관계 속에서도 나다움을 지키는 연습을 해보세요. 💜
        </p>
        
        <div style="text-align: center; margin-top: 40px;">
          <a href="https://dentistchi.github.io/today-me/" style="background-color: #9f7aea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block;">다시 검사하기</a>
        </div>
      </div>
      
      <div style="background-color: #f7fafc; padding: 20px; text-align: center; color: #a0aec0; font-size: 12px;">
        <p>© 2024 오늘의 나. bty Training Team 💜</p>
      </div>
    </div>
  `;
}

/**
 * 마무리 이메일 (5주차): 성장 리뷰 및 축하
 */
function createFinalEmailContent(userName, data) {
  var totalScore = parseInt(data.totalScore);
  
  return `
    <div style="font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 640px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 40px 30px; text-align: center; color: white;">
        <div style="font-size: 50px; margin-bottom: 10px;">🎊</div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">5주간의 여정을 마치며</h1>
        <p style="margin: 10px 0 0; opacity: 0.9; font-size: 16px;">${userName}님, 정말 수고하셨습니다!</p>
      </div>
      
      <div style="padding: 40px 30px; background-color: #ffffff;">
        <p style="color: #4a5568; line-height: 1.8; font-size: 16px;">
          안녕하세요, ${userName}님! 🎉<br><br>
          5주간의 자존감 향상 여정을 완주하셨습니다!<br>
          처음 진단을 받았던 그날부터 오늘까지, 당신은 스스로에게 관심을 기울이고 성장하려고 노력했습니다.
        </p>
        
        <div style="background-color: #fff5f7; padding: 25px; border-left: 4px solid #f5576c; margin: 25px 0;">
          <h3 style="color: #c53030; margin-top: 0;">🎯 당신의 시작점</h3>
          <p style="font-size: 28px; font-weight: bold; color: #c53030; margin: 10px 0;">자존감 점수: ${totalScore} / 100</p>
          <p style="color: #4a5568; margin: 5px 0 0;">유형: ${data.profileType}</p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 30px;">📖 5주간 우리가 배운 것들</h2>
        
        <div style="background-color: #f0fff4; padding: 15px; margin: 15px 0; border-radius: 8px;">
          <h4 style="color: #2f855a; margin: 0 0 10px;">🌱 1주차: 자기자비</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            실수했을 때 자신을 비난하는 대신, 따뜻하게 위로하는 법을 배웠습니다.
          </p>
        </div>
        
        <div style="background-color: #ebf8ff; padding: 15px; margin: 15px 0; border-radius: 8px;">
          <h4 style="color: #2c5282; margin: 0 0 10px;">💪 2주차: 핵심 자존감</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            외부 평가와 무관하게, 존재 자체로 가치 있다는 것을 인식했습니다.
          </p>
        </div>
        
        <div style="background-color: #fffaf0; padding: 15px; margin: 15px 0; border-radius: 8px;">
          <h4 style="color: #c05621; margin: 0 0 10px;">🚀 3주차: 성장 마인드셋</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            실패를 두려워하지 않고, 도전을 통해 성장하는 태도를 키웠습니다.
          </p>
        </div>
        
        <div style="background-color: #faf5ff; padding: 15px; margin: 15px 0; border-radius: 8px;">
          <h4 style="color: #6b46c1; margin: 0 0 10px;">🤝 4주차: 사회적 자존감</h4>
          <p style="color: #4a5568; margin: 0; line-height: 1.7;">
            관계 속에서도 나다움을 지키고, 건강한 경계를 설정하는 법을 배웠습니다.
          </p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 40px;">💝 앞으로의 여정</h2>
        <p style="color: #4a5568; line-height: 1.7;">
          자존감은 한 번 키운다고 끝나는 것이 아닙니다. 
          근육처럼 꾸준히 사용하고 연습해야 합니다.
        </p>
        
        <div style="background-color: #edf2f7; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h4 style="color: #2d3748; margin: 0 0 15px;">🌟 계속해서 실천해보세요:</h4>
          <ul style="color: #4a5568; line-height: 1.8; margin: 0; padding-left: 20px;">
            <li>매일 자신에게 한 가지 친절한 말을 건네세요.</li>
            <li>작은 성취를 축하하고 기록하세요.</li>
            <li>완벽을 추구하지 말고, 진전을 즐기세요.</li>
            <li>실수해도 괜찮다고 스스로에게 말해주세요.</li>
            <li>타인의 평가가 아닌, 자신의 가치를 믿으세요.</li>
          </ul>
        </div>
        
        <div style="background-color: #fff5f7; padding: 25px; border-radius: 8px; margin: 30px 0; text-align: center;">
          <p style="margin: 0 0 15px; color: #2d3748; font-weight: bold; font-size: 20px;">
            "당신은 이미 충분합니다."
          </p>
          <p style="margin: 0; color: #718096; line-height: 1.7;">
            5주 전 용기 내어 자신을 돌아본 그 순간부터,<br>
            당신은 이미 성장의 길을 걷고 있었습니다.
          </p>
        </div>
        
        <h2 style="color: #2d3748; font-size: 20px; margin-top: 40px;">🔄 다시 검사해보시겠어요?</h2>
        <p style="color: #4a5568; line-height: 1.7;">
          5주간 실천한 결과, 당신의 자존감이 얼마나 성장했는지 궁금하지 않으세요?<br>
          다시 검사를 받아보고, 변화를 확인해보세요!
        </p>
        
        <div style="text-align: center; margin-top: 40px;">
          <a href="https://dentistchi.github.io/today-me/" style="background-color: #f5576c; color: white; padding: 18px 40px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block; font-size: 16px; box-shadow: 0 4px 6px rgba(245, 87, 108, 0.3);">지금 다시 검사하기 🎯</a>
        </div>
        
        <div style="background-color: #e8f8f5; padding: 25px; border-left: 4px solid #27AE60; margin: 40px 0 20px;">
          <p style="margin: 0; color: #2d3748; line-height: 1.8;">
            <strong>💌 마지막 응원의 말</strong><br><br>
            ${userName}님, 5주간 함께해주셔서 감사합니다.<br>
            당신은 자신을 사랑하고 성장시키려는 용기를 보여주었습니다.<br>
            앞으로도 스스로에게 친절하고, 자신의 가치를 믿으세요.<br><br>
            당신은 충분히 가치 있고, 사랑받을 자격이 있습니다. 💚
          </p>
        </div>
        
        <p style="text-align: center; color: #718096; font-size: 14px; margin-top: 40px;">
          언제든 다시 돌아오셔도 좋습니다.<br>
          우리는 항상 당신을 응원합니다.
        </p>
      </div>
      
      <div style="background-color: #f7fafc; padding: 25px; text-align: center; color: #a0aec0; font-size: 12px;">
        <p style="margin: 0 0 10px; font-size: 14px; color: #718096;">
          <strong>bty Training Team</strong>
        </p>
        <p style="margin: 0;">© 2024 오늘의 나. All rights reserved.</p>
        <p style="margin: 10px 0 0;">💚 💙 🧡 💜 ❤️</p>
      </div>
    </div>
  `;
}
