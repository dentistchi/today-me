/**
 * [오늘의 나] 자존감 분석 시스템 v2.0 (GAS 버전)
 * - Python 분석 엔진(StrengthExtractor) 이식
 * - 맞춤형 심층 분석 보고서 생성 및 발송
 */

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var params = e.parameter;
  
  // 1. 답변 데이터 파싱 (JSON 문자열 -> 배열)
  var answers = [];
  try {
    answers = JSON.parse(params.answers || "[]");
  } catch (err) {
    console.error("JSON 파싱 오류: " + err);
    answers = [];
  }

  // 2. 부주의 응답 감지 (Low Variance Check)
  var variance = calculateVariance(answers);
  var reliability = variance < 0.3 ? "Low (Careless)" : "Normal";

  // 3. 시트 헤더 설정 (없을 경우)
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
  
  // 5. 고급 분석: 강점 추출 (Python Logic 이식)
  var strengths = extractStrengths(answers);
  
  // 6. 이메일 본문 생성 (심층 분석 보고서)
  var userName = params.email.split('@')[0]; // 이메일 아이디를 이름으로 사용
  var emailBody = createDetailedEmail(userName, params, strengths);
  var textBody = createTextFallback(userName, params);
  
  // 7. 이메일 발송
  try {
    MailApp.sendEmail({
      to: params.email,
      subject: "[오늘의 나] " + userName + "님을 위한 자존감 심층 분석 보고서",
      htmlBody: emailBody,
      body: textBody,
      name: "오늘의 나 연구팀",
      replyTo: Session.getActiveUser().getEmail()
    });
    
    // 관리자 알림
    MailApp.sendEmail({
      to: Session.getActiveUser().getEmail(),
      subject: "[Admin] 새로운 진단: " + params.profile_type + " (" + params.total_score + "점)",
      htmlBody: "<p>사용자: " + params.email + "</p><p>유형: " + params.profile_type + "</p>"
    });
    
  } catch (error) {
    console.error("이메일 발송 실패: " + error);
  }
  
  // 성공 응답 반환
  return ContentService.createTextOutput(JSON.stringify({"result":"success"}))
    .setMimeType(ContentService.MimeType.JSON);
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

function createTextFallback(name, data) {
  return `[오늘의 나] 자존감 분석 결과\n\n${name}님, 안녕하세요.\n당신의 자존감 총점은 ${data.total_score}점입니다.\n유형: ${data.profile_type}\n\n자세한 분석 결과와 강점은 HTML 지원 환경에서 확인해주세요.`;
}