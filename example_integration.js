/**
 * 이 파일은 웹훅 엔드포인트 테스트를 위한 예제 스크립트입니다.
 * 실제 프론트엔드(`script.js`)는 Formspree를 통해 데이터를 전송합니다.
 * 이 스크립트는 로컬에서 Flask 앱의 `/webhook` 엔드포인트가
 * Formspree로부터 받을 것과 유사한 데이터를 처리하는지 확인하는 데 사용됩니다.
 */

async function sendWebhookTest() {
    const webhookUrl = 'http://127.0.0.1:5001/webhook'; // 로컬 Flask 앱 URL

    // script.js에서 Formspree로 보내는 데이터와 유사하게 구성
    const testData = {
        email: 'testuser@example.com',
        // script.js에서 answers 배열을 JSON 문자열로 변환하여 보냄
        answers: JSON.stringify([
            // Rosenberg (10개)
            2, 3, 2, 3, 2, 3, 2, 2, 3, 2,
            // Self-Compassion (12개)
            3, 2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3,
            // Mindset (8개)
            3, 2, 3, 3, 3, 4, 3, 3,
            // Relational (10개)
            3, 2, 3, 2, 3, 3, 3, 3, 2, 3,
            // Implicit (10개)
            3, 3, 2, 3, 3, 3, 2, 3, 3, 3
        ]),
        // 기타 점수들은 백엔드에서 재계산되거나 필요에 따라 사용될 수 있습니다.
        // Formspree는 hidden 필드의 값들을 모두 전송합니다.
        total_score: 55,
        core_score: 60,
        compassion_score: 50,
        stability_score: 45,
        growth_score: 70,
        social_score: 55,
        profile_type: '균형 탐색자',
        _subject: '오늘의 나 - 자존감 분석 결과'
    };

    try {
        console.log('Sending test webhook to:', webhookUrl);
        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(testData)
        });

        const result = await response.json();
        console.log('Webhook response:', result);

        if (response.ok) {
            console.log('Test webhook successful!');
        } else {
            console.error('Test webhook failed with status:', response.status);
        }
    } catch (error) {
        console.error('Error sending test webhook:', error);
    }
}

// 스크립트 실행 시 자동으로 웹훅 테스트를 보냅니다.
sendWebhookTest();