/**
 * 자존감 분석 시스템 - JavaScript/Node.js 연동 예시
 * 실제 웹 애플리케이션에 통합하기 위한 코드
 */

// ==================== 1. 데이터베이스 스키마 (예시) ====================

const userTestSchema = {
  userId: String,
  userName: String,
  userEmail: String,
  responses: [Number],  // 50개 응답 (1-4)
  responseTimes: [Number],  // 응답 시간 (초)
  submittedAt: Date,
  emailsSent: {
    basic: { sent: Boolean, sentAt: Date },
    intermediate: { sent: Boolean, sentAt: Date },
    detailed: { sent: Boolean, sentAt: Date }
  },
  analysis: {
    rosenbergScore: Number,
    esteemType: String,
    dimensions: Object,
    strengths: Array
  }
};


// ==================== 2. 테스트 제출 핸들러 ====================

async function handleTestSubmit(req, res) {
  try {
    const { userName, userEmail, responses, responseTimes } = req.body;
    
    // 1. 입력 검증
    if (!userName || !userEmail || !responses || responses.length !== 50) {
      return res.status(400).json({ 
        error: '입력 데이터가 올바르지 않습니다.' 
      });
    }
    
    // 2. Python 분석 시스템 호출 (또는 JavaScript로 재구현)
    const analysis = await runPythonAnalysis({
      userName,
      userEmail,
      responses,
      responseTimes
    });
    
    // 3. 데이터베이스에 저장
    const testResult = await saveToDatabase({
      userName,
      userEmail,
      responses,
      responseTimes,
      submittedAt: new Date(),
      analysis: analysis.profile,
      emailsSent: {
        basic: { sent: false },
        intermediate: { sent: false },
        detailed: { sent: false }
      }
    });
    
    // 4. 이메일 발송 스케줄링
    await scheduleEmails(testResult._id, analysis.emails);
    
    // 5. 사용자에게 응답
    res.json({
      success: true,
      message: '분석이 완료되었습니다. 이메일을 확인해주세요.',
      preview: {
        rosenbergScore: analysis.profile.scores.rosenberg,
        esteemType: analysis.profile.esteem_type
      }
    });
    
  } catch (error) {
    console.error('테스트 처리 오류:', error);
    res.status(500).json({ 
      error: '처리 중 오류가 발생했습니다.' 
    });
  }
}


// ==================== 3. Python 분석 시스템 호출 ====================

const { spawn } = require('child_process');
const path = require('path');

async function runPythonAnalysis(data) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      path.join(__dirname, 'self_esteem_system.py'),
      '--json-input',
      JSON.stringify(data)
    ]);
    
    let outputData = '';
    let errorData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python 프로세스 오류: ${errorData}`));
      } else {
        try {
          const result = JSON.parse(outputData);
          resolve(result);
        } catch (e) {
          reject(new Error('JSON 파싱 오류'));
        }
      }
    });
  });
}


// ==================== 4. 이메일 발송 스케줄링 ====================

async function scheduleEmails(testResultId, emails) {
  // 방법 1: Node-Cron 사용
  // 방법 2: Bull Queue 사용 (추천)
  // 방법 3: 클라우드 스케줄러 (AWS EventBridge, GCP Scheduler)
  
  // Bull Queue 예시
  const emailQueue = require('./queues/emailQueue');
  
  // 즉시 발송
  await emailQueue.add('send-email', {
    testResultId,
    emailType: 'basic',
    subject: emails.basic.subject,
    body: emails.basic.body,
    to: emails.basic.to
  }, {
    delay: 0
  });
  
  // 2시간 후 발송
  await emailQueue.add('send-email', {
    testResultId,
    emailType: 'intermediate',
    subject: emails.intermediate.subject,
    body: emails.intermediate.body,
    to: emails.intermediate.to
  }, {
    delay: 2 * 60 * 60 * 1000  // 2시간 (밀리초)
  });
  
  // 24시간 후 발송
  await emailQueue.add('send-email', {
    testResultId,
    emailType: 'detailed',
    subject: emails.detailed.subject,
    body: emails.detailed.body,
    to: emails.detailed.to,
    attachments: await generatePDFAttachments(testResultId)
  }, {
    delay: 24 * 60 * 60 * 1000  // 24시간
  });
}


// ==================== 5. 이메일 발송 워커 ====================

// emailWorker.js
const nodemailer = require('nodemailer');

// 이메일 전송 설정
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  secure: true,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD
  }
});

async function sendEmail(job) {
  const { testResultId, emailType, subject, body, to, attachments } = job.data;
  
  try {
    // 이메일 발송
    const info = await transporter.sendMail({
      from: '"자존감 연구팀" <noreply@selfesteem.com>',
      to: to,
      subject: subject,
      text: body,
      html: convertToHTML(body),  // 텍스트를 HTML로 변환
      attachments: attachments
    });
    
    console.log(`✅ 이메일 발송 성공 [${emailType}]: ${info.messageId}`);
    
    // 데이터베이스 업데이트
    await updateEmailStatus(testResultId, emailType, true);
    
    return { success: true, messageId: info.messageId };
    
  } catch (error) {
    console.error(`❌ 이메일 발송 실패 [${emailType}]:`, error);
    
    // 재시도 로직
    if (job.attemptsMade < 3) {
      throw error;  // Bull이 자동으로 재시도
    }
    
    return { success: false, error: error.message };
  }
}


// ==================== 6. HTML 변환 함수 ====================

function convertToHTML(text) {
  /**
   * 텍스트 이메일을 HTML로 변환
   * - 이모지 유지
   - 구분선 스타일링
   * - 적절한 폰트와 여백
   */
  
  let html = text
    .replace(/━{20,}/g, '<hr style="border: 1px solid #e0e0e0; margin: 20px 0;">')
    .replace(/^(#{1,3})\s+(.+)$/gm, (match, hashes, content) => {
      const level = hashes.length;
      return `<h${level} style="color: #333; margin-top: 24px;">${content}</h${level}>`;
    })
    .replace(/^•\s+(.+)$/gm, '<li style="margin-bottom: 8px;">$1</li>')
    .replace(/\n\n/g, '</p><p style="line-height: 1.6; color: #555;">');
  
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Malgun Gothic', sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #f9f9f9;
    }
    .container {
      background: white;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
      color: #2c3e50;
    }
    .highlight {
      background-color: #fff3cd;
      padding: 2px 4px;
      border-radius: 3px;
    }
    .button {
      display: inline-block;
      padding: 12px 24px;
      background-color: #4CAF50;
      color: white;
      text-decoration: none;
      border-radius: 5px;
      margin: 20px 0;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #e0e0e0;
      font-size: 12px;
      color: #999;
    }
  </style>
</head>
<body>
  <div class="container">
    <p style="line-height: 1.6; color: #555;">
      ${html}
    </p>
  </div>
  <div class="footer">
    <p>이 이메일은 자존감 테스트 결과 발송을 위해 자동으로 생성되었습니다.</p>
    <p>더 이상 이메일을 받고 싶지 않으시면 <a href="#">여기</a>를 클릭하세요.</p>
  </div>
</body>
</html>
  `;
}


// ==================== 7. PDF 생성 함수 ====================

const PDFDocument = require('pdfkit');
const fs = require('fs');

async function generatePDFReport(testResultId) {
  // 테스트 결과 조회
  const testResult = await getTestResultFromDB(testResultId);
  const analysis = testResult.analysis;
  
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({
      size: 'A4',
      margins: { top: 50, bottom: 50, left: 50, right: 50 }
    });
    
    const filename = `/tmp/${testResultId}_report.pdf`;
    const stream = fs.createWriteStream(filename);
    doc.pipe(stream);
    
    // 한글 폰트 등록 (필수)
    doc.registerFont('NanumGothic', 'fonts/NanumGothic.ttf');
    doc.font('NanumGothic');
    
    // 표지
    doc.fontSize(24)
       .text('자존감 분석 보고서', { align: 'center' })
       .moveDown();
    
    doc.fontSize(16)
       .text(testResult.userName + '님을 위한', { align: 'center' })
       .moveDown(2);
    
    // 5차원 분석
    doc.fontSize(18).text('5차원 분석', { underline: true }).moveDown();
    
    Object.entries(analysis.dimensions).forEach(([key, value]) => {
      doc.fontSize(12)
         .text(`${key}: ${value}/10`, { indent: 20 })
         .moveDown(0.5);
    });
    
    doc.addPage();
    
    // 강점 분석
    doc.fontSize(18).text('당신의 강점', { underline: true }).moveDown();
    
    testResult.analysis.strengths.forEach((strength, index) => {
      doc.fontSize(14)
         .text(`${index + 1}. ${strength.name}`, { bold: true })
         .fontSize(11)
         .text(strength.detail, { indent: 20 })
         .moveDown();
    });
    
    doc.addPage();
    
    // 4주 로드맵
    doc.fontSize(18).text('4주 성장 로드맵', { underline: true }).moveDown();
    
    const weeks = [
      { title: 'Week 1: 자기친절의 기초', content: '자기비판 → 자기친절' },
      { title: 'Week 2: 완벽주의 내려놓기', content: '완벽주의 → 건강한 노력' },
      { title: 'Week 3: 공통 인간성 인식', content: '"나만 힘들다" → "우리 모두 힘들다"' },
      { title: 'Week 4: 안정적 자기가치 구축', content: '조건부 자존감 → 무조건적 자기가치' }
    ];
    
    weeks.forEach(week => {
      doc.fontSize(14).text(week.title, { bold: true })
         .fontSize(11).text(week.content, { indent: 20 })
         .moveDown(1.5);
    });
    
    // PDF 생성 완료
    doc.end();
    
    stream.on('finish', () => {
      resolve(filename);
    });
    
    stream.on('error', reject);
  });
}


// ==================== 8. Express 라우터 설정 ====================

const express = require('express');
const router = express.Router();

// 테스트 제출
router.post('/api/test/submit', handleTestSubmit);

// 재검사
router.post('/api/test/retest', async (req, res) => {
  // 4주 후 재검사 로직
});

// 결과 조회
router.get('/api/test/result/:id', async (req, res) => {
  try {
    const result = await getTestResultFromDB(req.params.id);
    res.json(result);
  } catch (error) {
    res.status(404).json({ error: '결과를 찾을 수 없습니다.' });
  }
});

module.exports = router;


// ==================== 9. 환경 변수 예시 (.env) ====================

/*
# SMTP 설정
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 데이터베이스
MONGODB_URI=mongodb://localhost:27017/selfesteem
REDIS_URL=redis://localhost:6379

# 기타
NODE_ENV=production
PORT=3000
*/


// ==================== 10. 사용 예시 ====================

/*
// 프론트엔드에서 호출 예시

const submitTest = async (responses) => {
  const response = await fetch('/api/test/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      userName: '홍길동',
      userEmail: 'user@example.com',
      responses: responses,  // [1, 2, 3, 4, ...] (50개)
      responseTimes: responseTimes  // [2.3, 1.8, ...] (50개, 선택)
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    // 성공 화면 표시
    showSuccessPage({
      message: '분석이 완료되었습니다!',
      score: result.preview.rosenbergScore
    });
  }
};
*/


// ==================== 11. Bull Queue 설정 ====================

// queues/emailQueue.js
const Queue = require('bull');

const emailQueue = new Queue('email-sending', {
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379
  }
});

// 워커 프로세스
emailQueue.process('send-email', async (job) => {
  return await sendEmail(job);
});

// 이벤트 리스너
emailQueue.on('completed', (job, result) => {
  console.log(`✅ Job ${job.id} 완료:`, result);
});

emailQueue.on('failed', (job, err) => {
  console.error(`❌ Job ${job.id} 실패:`, err.message);
});

module.exports = emailQueue;


// ==================== 12. 배포 체크리스트 ====================

/*
배포 전 확인사항:

✅ 1. 환경 변수 설정
   - SMTP 계정 (Gmail, SendGrid 등)
   - 데이터베이스 연결
   - Redis 연결

✅ 2. 한글 폰트 설치
   - PDF 생성을 위해 NanumGothic.ttf 등 필요

✅ 3. 이메일 발송 테스트
   - 스팸 폴더 확인
   - SPF, DKIM 설정

✅ 4. 큐 시스템 테스트
   - Redis 연결 확인
   - Bull Dashboard 설정

✅ 5. 에러 처리
   - 이메일 발송 실패 시 재시도
   - 로그 수집 (Sentry, LogRocket 등)

✅ 6. 보안
   - 개인정보 암호화
   - HTTPS 적용
   - Rate limiting

✅ 7. 모니터링
   - 발송 성공률 추적
   - 응답 시간 모니터링
*/
