"""
자존감 분석 시스템 v1.0
- 50개 질문 기반 다차원 자존감 분석
- 3단계 이메일 발송 시스템
- 개인화된 피드백 생성
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import hashlib

# 연구 참고문헌 임포트
from research_references import (
    get_short_citation, 
    format_inline_citation,
    format_reference_list
)

# 개인화된 컨텐츠 임포트
from personalized_content import (
    get_profile_explanation,
    generate_personalized_roadmap,
    generate_pentagon_chart_data
)


# ==================== 1. 점수 계산 엔진 ====================

class SelfEsteemScorer:
    """자존감 점수 계산 및 분류"""
    
    def __init__(self):
        # Rosenberg Self-Esteem Scale 문항 매핑 (50개 중 10개)
        self.rosenberg_items = {
            'positive': [0, 1, 3, 5, 6],  # 긍정 문항 인덱스
            'negative': [2, 4, 7, 8, 9]   # 부정 문항 인덱스 (역채점)
        }
        
        # Self-Compassion Scale 문항 매핑 (12개)
        self.self_compassion_items = {
            'self_kindness': [10, 11, 12],
            'self_judgment': [13, 14, 15],  # 역채점
            'common_humanity': [16, 17, 18],
            'isolation': [19, 20, 21]  # 역채점
        }
        
        # Growth Mindset 문항 (8개)
        self.mindset_items = {
            'fixed': [22, 23, 24, 25],  # 역채점
            'growth': [26, 27, 28, 29]
        }
        
        # 관계적 자존감 (10개)
        self.relational_items = {
            'dependent': [30, 31, 32, 33, 34],  # 역채점
            'independent': [35, 36, 37, 38, 39]
        }
        
        # 암묵적 자존감 (반응 시간 + 일관성, 10개)
        self.implicit_items = list(range(40, 50))
    
    def calculate_rosenberg_score(self, responses: List[int]) -> int:
        """
        Rosenberg 자존감 점수 계산 (0-40점)
        응답: 1(전혀 아니다) ~ 4(매우 그렇다)
        """
        positive_score = sum(responses[i] for i in self.rosenberg_items['positive'])
        negative_score = sum(5 - responses[i] for i in self.rosenberg_items['negative'])
        return positive_score + negative_score
    
    def calculate_self_compassion_score(self, responses: List[int]) -> float:
        """자기 자비 점수 (1-5점 척도)"""
        kindness = sum(responses[i] for i in self.self_compassion_items['self_kindness']) / 3
        judgment = sum(5 - responses[i] for i in self.self_compassion_items['self_judgment']) / 3
        humanity = sum(responses[i] for i in self.self_compassion_items['common_humanity']) / 3
        isolation = sum(5 - responses[i] for i in self.self_compassion_items['isolation']) / 3
        
        return (kindness + judgment + humanity + isolation) / 4
    
    def calculate_mindset_score(self, responses: List[int]) -> float:
        """성장 마인드셋 점수 (1-5점 척도)"""
        fixed_score = sum(5 - responses[i] for i in self.mindset_items['fixed']) / 4
        growth_score = sum(responses[i] for i in self.mindset_items['growth']) / 4
        return (fixed_score + growth_score) / 2
    
    def calculate_relational_score(self, responses: List[int]) -> float:
        """관계적 자존감 독립성 점수 (1-5점 척도)"""
        dependent_score = sum(5 - responses[i] for i in self.relational_items['dependent']) / 5
        independent_score = sum(responses[i] for i in self.relational_items['independent']) / 5
        return (dependent_score + independent_score) / 2
    
    def calculate_implicit_score(self, responses: List[int], response_times: List[float] = None) -> float:
        """암묵적 자존감 점수 (일관성 + 반응시간)"""
        # 일관성 점수 (변동성이 낮을수록 높은 점수)
        if response_times and len(response_times) >= 10:
            consistency = 5.0 - (max(response_times[-10:]) - min(response_times[-10:])) / 2
        else:
            consistency = 3.0  # 기본값
        
        # 긍정적 자기인식 문항 점수
        implicit_responses = [responses[i] for i in self.implicit_items]
        avg_response = sum(implicit_responses) / len(implicit_responses)
        
        return (consistency + avg_response) / 2
    
    def classify_esteem_type(self, rosenberg_score: int, sc_score: float) -> str:
        """자존감 유형 분류"""
        if rosenberg_score < 20:
            if sc_score < 2.5:
                return "vulnerable"  # 취약형
            else:
                return "compassionate_grower"  # 자비로운 성장형
        elif rosenberg_score < 30:
            if sc_score < 3.0:
                return "developing_critic"  # 발전형(자기비판)
            else:
                return "developing_balanced"  # 발전형(균형)
        else:
            if sc_score >= 3.5:
                return "thriving"  # 번영형
            else:
                return "stable_rigid"  # 안정형이나 경직
    
    def analyze_full_profile(self, responses: List[int], 
                            response_times: List[float] = None) -> Dict:
        """전체 프로파일 분석"""
        rosenberg = self.calculate_rosenberg_score(responses)
        sc_score = self.calculate_self_compassion_score(responses)
        mindset = self.calculate_mindset_score(responses)
        relational = self.calculate_relational_score(responses)
        implicit = self.calculate_implicit_score(responses, response_times)
        
        esteem_type = self.classify_esteem_type(rosenberg, sc_score)
        
        return {
            'scores': {
                'rosenberg': rosenberg,
                'rosenberg_max': 40,
                'self_compassion': round(sc_score, 2),
                'mindset': round(mindset, 2),
                'relational': round(relational, 2),
                'implicit': round(implicit, 2)
            },
            'esteem_type': esteem_type,
            'dimensions': {
                '자존감_안정성': round(rosenberg / 4, 1),  # 0-10 스케일
                '자기_자비': round(sc_score * 2, 1),  # 0-10 스케일
                '성장_마인드셋': round(mindset * 2, 1),
                '관계적_독립성': round(relational * 2, 1),
                '암묵적_자존감': round(implicit * 2, 1)
            }
        }


# ==================== 2. 강점 추출 엔진 ====================

class StrengthExtractor:
    """응답 패턴에서 숨겨진 강점 추출"""
    
    def __init__(self):
        self.strength_patterns = {
            'resilience': {
                'questions': [6, 18, 33, 41],
                'threshold': 2.5,
                'description': '회복탄력성 (Resilience)',
                'detail': '어려운 상황에서도 포기하지 않으려는 강한 의지'
            },
            'empathy': {
                'questions': [14, 27, 38, 45],
                'threshold': 2.5,
                'description': '공감 능력 (Empathy)',
                'detail': '타인의 감정을 이해하고 배려하는 따뜻한 마음'
            },
            'self_awareness': {
                'questions': [2, 12, 23, 36, 47],
                'threshold': 2.5,
                'description': '자기인식 (Self-Awareness)',
                'detail': '자신의 감정과 생각을 객관적으로 이해하는 능력'
            },
            'perseverance': {
                'questions': [8, 19, 29, 42],
                'threshold': 2.5,
                'description': '끈기 (Perseverance)',
                'detail': '목표를 향해 꾸준히 노력하는 성실함'
            },
            'optimism': {
                'questions': [5, 16, 26, 37, 48],
                'threshold': 2.5,
                'description': '낙관성 (Optimism)',
                'detail': '미래에 대한 희망과 긍정적 기대'
            }
        }
    
    def extract_strengths(self, responses: List[int]) -> List[Dict]:
        """상위 3가지 강점 추출"""
        strengths = []
        
        for strength_name, pattern in self.strength_patterns.items():
            questions = pattern['questions']
            scores = [responses[q] for q in questions if q < len(responses)]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            if avg_score >= pattern['threshold']:
                strengths.append({
                    'name': pattern['description'],
                    'detail': pattern['detail'],
                    'score': round(avg_score, 2),
                    'evidence_questions': questions[:3]  # 증거 질문 번호
                })
        
        # 점수순 정렬 후 상위 3개
        strengths.sort(key=lambda x: x['score'], reverse=True)
        return strengths[:3]


# ==================== 3. 이메일 템플릿 생성기 ====================

class EmailTemplateGenerator:
    """개인화된 이메일 템플릿 생성"""
    
    def __init__(self):
        self.scorer = SelfEsteemScorer()
        self.strength_extractor = StrengthExtractor()
    
    def generate_basic_email(self, user_name: str, user_email: str) -> str:
        """VERSION 1: 기본 이메일 (즉시 발송)"""
        template = f"""
제목: 🌟 테스트 완료! 당신에 대한 특별한 이야기를 준비하고 있습니다

안녕하세요, {user_name}님!

먼저, 50개의 질문에 솔직하게 답해주셔서 진심으로 감사드립니다.
많은 사람들이 자신을 들여다보는 것을 두려워하는데,
당신은 그 용기를 보여주셨습니다.

━━━━━━━━━━━━━━━━━━━━━━

지금 이 순간에도, 당신의 답변을 바탕으로
당신만을 위한 분석이 진행되고 있습니다.

우리가 발견하고 있는 것들:
✓ 당신이 인식하지 못했던 3가지 강점
✓ 당신이 스스로를 바라보는 독특한 방식
✓ 당신의 성장을 가로막던 오해들
✓ 당신에게 꼭 맞는 4주 실천 로드맵

━━━━━━━━━━━━━━━━━━━━━━

📬 앞으로 받으실 내용:

• 지금부터 2시간 후
  → 당신의 자존감 프로파일 (기본 분석)

• 지금부터 24시간 후  
  → 완전한 심층 분석 보고서 (PDF)
  → 개인 맞춤형 성장 가이드

━━━━━━━━━━━━━━━━━━━━━━

💡 미리 말씀드리고 싶은 것:

당신이 받을 결과는 "좋다/나쁘다"의 판단이 아닙니다.
이것은 당신이 어떻게 자신을 바라보고 있는지를 
거울처럼 비춰주는 이야기입니다.

그리고 그 이야기 속에서,
당신도 몰랐던 당신의 아름다움을 발견하게 될 것입니다.

━━━━━━━━━━━━━━━━━━━━━━

📌 잠깐! 이메일이 안 보이시나요?

• 스팸함을 확인해주세요
• noreply@selfesteem.com을 주소록에 추가해주세요
• 프로모션 탭도 확인해보세요

━━━━━━━━━━━━━━━━━━━━━━

당신의 여정을 응원합니다.

따뜻한 마음으로,
bty Training Team 드림

P.S. 궁금한 점이 있으시면 이 이메일에 답장해주세요.
     우리는 당신의 이야기를 듣고 싶습니다.
"""
        return template
    
    def generate_intermediate_email(self, user_name: str, profile: Dict, 
                                   strengths: List[Dict]) -> str:
        """VERSION 2: 중간 이메일 (2시간 후)"""
        rosenberg = profile['scores']['rosenberg']
        esteem_type = profile['esteem_type']
        
        # 점수대별 맞춤 내용
        if rosenberg < 20:
            score_interpretation = self._get_low_score_text(user_name, strengths)
        elif rosenberg < 30:
            score_interpretation = self._get_medium_score_text(user_name, strengths)
        else:
            score_interpretation = self._get_high_score_text(user_name, strengths)
        
        template = f"""
제목: 📊 {user_name}님의 자존감 프로파일이 완성되었습니다

{user_name}님, 안녕하세요.

약속드린 대로, 당신의 첫 번째 분석 결과를 보내드립니다.

━━━━━━━━━━━━━━━━━━━━━━
📊 당신의 자존감 프로파일
━━━━━━━━━━━━━━━━━━━━━━

당신의 Rosenberg 자존감 점수: {rosenberg}/40
(한국 성인 평균: 28점)

━━━━━━━━━━━━━━━━━━━━━━
🔍 이 숫자가 의미하는 것
━━━━━━━━━━━━━━━━━━━━━━

{score_interpretation}

━━━━━━━━━━━━━━━━━━━━━━
✨ 당신이 몰랐던 당신의 강점
━━━━━━━━━━━━━━━━━━━━━━

{self._format_strengths(strengths)}

━━━━━━━━━━━━━━━━━━━━━━
🎯 당신을 위한 제안
━━━━━━━━━━━━━━━━━━━━━━

내일 보내드릴 상세 보고서에서는:

1️⃣ 당신만의 성장 로드맵 (4주 프로그램)
2️⃣ 당신이 주목해야 할 3가지 패턴
3️⃣ 과학적 연구에 기반한 구체적 실천법
4️⃣ 당신의 자존감 유형별 맞춤 조언

━━━━━━━━━━━━━━━━━━━━━━
💪 오늘부터 시작하는 작은 실천
━━━━━━━━━━━━━━━━━━━━━━

{self._get_daily_practice(rosenberg)}

━━━━━━━━━━━━━━━━━━━━━━

{user_name}님,

숫자는 당신을 정의하지 않습니다.
이것은 단지 지금 이 순간의 당신이
자신을 어떻게 바라보고 있는지를 보여주는 것입니다.

그리고 좋은 소식은:
이것은 언제든 변할 수 있다는 것입니다.

내일 더 깊은 이야기로 찾아뵙겠습니다.

따뜻한 마음으로,
bty Training Team 드림
"""
        return template
    
    def generate_detailed_email(self, user_name: str, profile: Dict,
                               strengths: List[Dict]) -> str:
        """VERSION 3: 상세 이메일 (24시간 후) - 개인화"""
        dimensions = profile['dimensions']
        esteem_type = profile['esteem_type']
        
        # 프로파일 설명 가져오기
        profile_info = get_profile_explanation(esteem_type)
        
        # 오각형 차트 데이터
        chart_data = generate_pentagon_chart_data(dimensions)
        
        # 개인화된 4주 로드맵
        roadmap = generate_personalized_roadmap(profile, dimensions)
        
        template = f"""
제목: 💎 {user_name}님을 위한 완전한 분석 보고서 (PDF 첨부)

{user_name}님께,

24시간 동안 당신의 답변을 깊이 분석했습니다.

이제 당신에 대한 완전한 이야기를 
들려드릴 준비가 되었습니다.

━━━━━━━━━━━━━━━━━━━━━━
📄 첨부 파일을 먼저 열어주세요
━━━━━━━━━━━━━━━━━━━━━━

이 이메일에 첨부된 PDF에는:
• 당신의 완전한 심리학적 프로파일
• 5가지 차원 분석 차트 (오각형 그래프)
• 당신만의 4주 성장 로드맵 (개인 맞춤형)
• 50개 질문 상세 해석

이 모두가 담겨 있습니다.

━━━━━━━━━━━━━━━━━━━━━━
{profile_info['emoji']} 당신의 자존감 프로파일
━━━━━━━━━━━━━━━━━━━━━━

당신은 <{profile_info['name']}> 유형입니다.

{profile_info['short_desc']}

{profile_info['full_desc']}

━━━━━━━━━━━━━━━━━━━━━━
📊 당신의 5차원 분석 (오각형 그래프)
━━━━━━━━━━━━━━━━━━━━━━

당신의 자존감은 5가지 차원으로 구성됩니다:

1️⃣ 자존감 안정성: {dimensions['자존감_안정성']}/10
   {format_inline_citation('crocker_park_2004', '외부 평가에 흔들리지 않는 안정적 자기가치')}
   {self._get_dimension_explanation('자존감_안정성', dimensions['자존감_안정성'])}

2️⃣ 자기 자비: {dimensions['자기_자비']}/10  
   {format_inline_citation('neff_2003', '실수했을 때 자신을 대하는 방식')}
   {self._get_dimension_explanation('자기_자비', dimensions['자기_자비'])}
   
   💡 연구 결과: {format_inline_citation('neff_germer_2013', '8주간 자기자비 훈련 후 자존감 23% 상승, 우울 32% 감소')}

3️⃣ 성장 마인드셋: {dimensions['성장_마인드셋']}/10
   {format_inline_citation('dweck_2006', '능력에 대한 믿음: 고정 vs 성장 가능')}
   {self._get_dimension_explanation('성장_마인드셋', dimensions['성장_마인드셋'])}

4️⃣ 관계적 독립성: {dimensions['관계적_독립성']}/10
   타인의 인정에 대한 의존도
   {self._get_dimension_explanation('관계적_독립성', dimensions['관계적_독립성'])}

5️⃣ 암묵적 자존감: {dimensions['암묵적_자존감']}/10
   의식적 자존감 vs 무의식적 자존감의 일치도
   {self._get_dimension_explanation('암묵적_자존감', dimensions['암묵적_자존감'])}

📈 오각형 그래프 보기:
첨부된 PDF에서 당신의 5차원 균형을 시각적으로 확인하세요!
균형잡힌 오각형에 가까울수록 건강한 자존감입니다.

━━━━━━━━━━━━━━━━━━━━━━
🗓️ 당신만의 맞춤형 4주 성장 로드맵
━━━━━━━━━━━━━━━━━━━━━━

당신의 점수 분석 결과, 다음 순서로 성장하는 것을 추천합니다:

{self._format_personalized_roadmap(roadmap)}

━━━━━━━━━━━━━━━━━━━━━━
📊 4주 후 재검사 초대
━━━━━━━━━━━━━━━━━━━━━━

4주 프로그램을 마친 후,
같은 테스트를 다시 받아보세요.

당신의 성장 곡선을 시각화해서
"Before & After" 리포트를 보내드립니다.

• 5차원 점수 변화
• 오각형 그래프 비교
• 성장률 분석
• 다음 단계 제안

[4주 후 재검사 링크]

━━━━━━━━━━━━━━━━━━━━━━
❤️ 마지막으로
━━━━━━━━━━━━━━━━━━━━━━

{user_name}님,

50개 질문을 분석하면서
저는 당신에 대해 많은 것을 알게 되었습니다.

당신이 얼마나 진지하게 자신을 성찰하는지,
얼마나 성장하고 싶어하는지,
얼마나 아름다운 마음을 가졌는지.

숫자는 당신을 정의하지 않습니다.
점수는 단지 지금 이 순간의 스냅샷일 뿐입니다.

당신은 이미 충분히 가치있는 사람입니다.
이제 필요한 것은 당신이 그것을 믿는 것뿐입니다.

당신을 응원합니다.

진심을 담아,
bty Training Team

P.S. 4주 후 당신의 변화 이야기를 듣고 싶습니다. 💚

{format_reference_list()}

━━━━━━━━━━━━━━━━━━━━━━

📎 첨부 파일:
• {user_name}님_자존감분석보고서.pdf
• 자기자비워크시트.pdf
• 4주프로그램_체크리스트.pdf

━━━━━━━━━━━━━━━━━━━━━━

본 분석은 자기 이해를 돕기 위한 과학적 도구이며, 
의료적 진단을 대체하지 않습니다.

© 2026 bty Training Team. All rights reserved.
"""
        return template
    
    def _get_low_score_text(self, user_name: str, strengths: List[Dict]) -> str:
        """낮은 점수 해석"""
        return f"""{user_name}님, 당신은 지금 스스로에게 매우 엄격합니다.

당신의 답변을 보면서 제가 가장 먼저 느낀 것은
"이 사람은 자신에게 너무 가혹하다"였습니다.

당신은 아마도:
• 실수했을 때 자신을 강하게 비난합니다
• "내가 부족해"라는 생각이 자주 듭니다  
• 다른 사람들은 나를 어떻게 볼까 걱정됩니다
• 칭찬을 받아도 믿기 어렵습니다

하지만 제가 발견한 진실은 이것입니다:

당신의 자기비판은 당신이 "나쁜 사람"이라는 증거가 아닙니다.
오히려 당신은 "더 나은 사람이 되고 싶은" 
아름다운 마음을 가진 것입니다.

심리학자 Kristin Neff의 연구에 따르면,
자기비판이 강한 사람들은 실제로는
매우 높은 기준을 가진 성실한 사람들입니다."""
    
    def _get_medium_score_text(self, user_name: str, strengths: List[Dict]) -> str:
        """중간 점수 해석"""
        return f"""{user_name}님, 당신은 지금 성장의 한가운데에 있습니다.

당신의 점수는 "애매한" 것이 아닙니다.
이것은 당신이 자신을 정직하게 바라보고 있으며,
동시에 변화할 준비가 되어 있다는 신호입니다.

당신은 아마도:
• 좋은 날과 힘든 날이 반복됩니다
• 때로는 자신감이 넘치다가도 갑자기 불안해집니다
• "나는 괜찮은 사람인가?" 질문할 때가 있습니다
• 성장하고 싶지만 방법을 모르겠습니다

좋은 소식:

당신은 이미 자존감의 기초를 가지고 있습니다.
이제 필요한 것은 그것을 '안정화'시키는 것입니다.

Stanford 대학의 연구에 따르면,
당신과 같은 단계에 있는 사람들이
적절한 개입을 받았을 때
가장 극적인 성장을 보입니다."""
    
    def _get_high_score_text(self, user_name: str, strengths: List[Dict]) -> str:
        """높은 점수 해석"""
        return f"""{user_name}님, 축하드립니다!

당신은 이미 건강한 자존감을 가지고 계십니다.

당신의 답변을 자세히 보면서,
제가 발견한 흥미로운 패턴이 있습니다:

당신은 실패를 '성장의 기회'로 보는 
성장 마인드셋을 보여주었습니다.

자신과 타인을 모두 존중하는
균형잡힌 시각이 드러났습니다.

자신의 가치가 외부 평가에 흔들리지 않는
안정적인 자기인식이 보였습니다.

이것은 심리학자들이 말하는 
"True Self-Esteem"입니다."""
    
    def _format_strengths(self, strengths: List[Dict]) -> str:
        """강점 포맷팅"""
        if not strengths:
            return "분석 중입니다. 상세 보고서에서 확인하세요."
        
        result = []
        for i, strength in enumerate(strengths, 1):
            result.append(f"""
💎 강점 {i}: {strength['name']}

{strength['detail']}

증거: {', '.join([f'{q+1}번 질문' for q in strength['evidence_questions']])}
""")
        return '\n'.join(result)
    
    def _get_daily_practice(self, rosenberg_score: int) -> str:
        """일일 실천 가이드"""
        if rosenberg_score < 20:
            return """🌱 자기친절 연습:
실수했을 때 "에이 멍청이"가 아니라
"괜찮아, 실수는 인간적인 거야"라고 말해보세요.

마치 가장 친한 친구에게 하듯이요."""
        
        elif rosenberg_score < 30:
            return """🌱 성취 일기:
오늘 당신이 '잘한 것' 3가지를 
작은 것이라도 적어보세요.
"점심 맛있게 먹었다"도 좋습니다."""
        
        else:
            return """🌱 감사 나누기:
당신의 안정된 자존감을
누군가에게 나눠주세요.
한 사람에게 진심 어린 칭찬을 해보세요."""
    
    def _get_dimension_explanation(self, dimension_name: str, score: float) -> str:
        """차원별 점수 해석"""
        explanations = {
            '자존감_안정성': {
                'low': '외부 평가(성적, 외모, 타인의 인정)에 자존감이 많이 흔들립니다. 안정적 자기가치 구축이 필요합니다.',
                'medium': '때로는 흔들리지만, 기본적인 자기가치는 유지하고 있습니다. 조금 더 안정화가 필요합니다.',
                'high': '외부 평가와 무관하게 자신의 가치를 인정합니다. 건강한 자존감의 모습입니다.'
            },
            '자기_자비': {
                'low': '실수나 실패 시 자신을 가혹하게 비판하는 경향이 있습니다. 자기친절 연습이 도움이 됩니다.',
                'medium': '때때로 자신에게 엄격하지만, 친절을 베풀 줄도 압니다. 자기자비를 더 연습해보세요.',
                'high': '실수를 인간적 경험으로 받아들이며, 자신에게 친절합니다. 훌륭한 자기 돌봄입니다.'
            },
            '성장_마인드셋': {
                'low': '능력이 고정되어 있다고 믿는 경향이 있습니다. 실패를 두려워할 수 있습니다.',
                'medium': '성장 가능성을 믿지만, 때로는 고정관념에 갇힙니다. 더 유연해질 수 있습니다.',
                'high': '노력과 학습을 통해 성장할 수 있다고 믿습니다. 도전을 기회로 봅니다.'
            },
            '관계적_독립성': {
                'low': '타인의 인정과 승인에 자존감이 많이 의존합니다. 내적 기준 개발이 필요합니다.',
                'medium': '타인의 의견을 고려하되, 자신의 판단도 존중합니다. 균형잡힌 모습입니다.',
                'high': '자신의 가치를 스스로 정의합니다. 건강한 독립성을 보입니다.'
            },
            '암묵적_자존감': {
                'low': '의식적 자존감과 무의식적 자존감 사이에 큰 간극이 있을 수 있습니다.',
                'medium': '대체로 일치하지만, 때때로 불일치가 나타날 수 있습니다.',
                'high': '의식적/무의식적 자존감이 잘 일치합니다. 진정성 있는 자존감입니다.'
            }
        }
        
        if score < 5:
            level = 'low'
        elif score < 7:
            level = 'medium'
        else:
            level = 'high'
        
        return explanations.get(dimension_name, {}).get(level, '')
    
    def _format_personalized_roadmap(self, roadmap: List[Dict]) -> str:
        """개인화된 로드맵 포맷팅"""
        formatted = ""
        
        for week_plan in roadmap:
            formatted += f"""
━━━ Week {week_plan['week']}: {week_plan['focus_area']} (현재 {week_plan['score']}/10) ━━━

🎯 목표: {week_plan['goal']}

❓ 왜 이것부터?: {week_plan['why']}

📅 매일 실천할 것:
"""
            for i, practice in enumerate(week_plan['practices'], 1):
                formatted += f"   {i}. {practice}\n"
            
            formatted += f"""
🏆 이번 주 미션:
   {week_plan['mission']}

"""
        
        return formatted


# ==================== 4. 메인 시스템 ====================

class SelfEsteemSystem:
    """자존감 분석 및 이메일 발송 시스템"""
    
    def __init__(self):
        self.scorer = SelfEsteemScorer()
        self.strength_extractor = StrengthExtractor()
        self.email_generator = EmailTemplateGenerator()
    
    def process_test_results(self, user_name: str, user_email: str,
                            responses: List[int], 
                            response_times: List[float] = None) -> Dict:
        """테스트 결과 처리 및 이메일 생성"""
        
        # 1. 전체 프로파일 분석
        profile = self.scorer.analyze_full_profile(responses, response_times)
        
        # 2. 강점 추출
        strengths = self.strength_extractor.extract_strengths(responses)
        
        # 3. 3단계 이메일 생성
        emails = {
            'basic': {
                'subject': '🌟 테스트 완료! 당신에 대한 특별한 이야기를 준비하고 있습니다',
                'body': self.email_generator.generate_basic_email(user_name, user_email),
                'send_delay_minutes': 0
            },
            'intermediate': {
                'subject': f'📊 {user_name}님의 자존감 프로파일이 완성되었습니다',
                'body': self.email_generator.generate_intermediate_email(
                    user_name, profile, strengths
                ),
                'send_delay_minutes': 120  # 2시간
            },
            'detailed': {
                'subject': f'💎 {user_name}님을 위한 완전한 분석 보고서',
                'body': self.email_generator.generate_detailed_email(
                    user_name, profile, strengths
                ),
                'send_delay_minutes': 1440  # 24시간
            }
        }
        
        return {
            'profile': profile,
            'strengths': strengths,
            'emails': emails,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results: Dict, filename: str = None):
        """결과를 JSON 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'self_esteem_results_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return filename


# ==================== 5. 사용 예시 ====================

def example_usage():
    """시스템 사용 예시"""
    
    # 시스템 초기화
    system = SelfEsteemSystem()
    
    # 예시 응답 (50개 질문, 1-4 척도)
    # 실제로는 사용자의 실제 응답 데이터를 사용
    example_responses = [
        # Rosenberg (10개)
        2, 3, 2, 3, 2, 3, 2, 2, 3, 2,
        # Self-Compassion (12개)
        3, 2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3,
        # Mindset (8개)
        3, 2, 3, 3, 3, 4, 3, 3,
        # Relational (10개)
        3, 2, 3, 2, 3, 3, 3, 3, 2, 3,
        # Implicit (10개)
        3, 3, 2, 3, 3, 3, 2, 3, 3, 3
    ]
    
    # 응답 시간 (초 단위, 선택사항)
    example_response_times = [2.3, 1.8, 3.2, 2.1] * 12 + [2.5, 2.7]
    
    # 테스트 처리
    results = system.process_test_results(
        user_name="홍길동",
        user_email="user@example.com",
        responses=example_responses,
        response_times=example_response_times
    )
    
    # 결과 저장
    filename = system.save_results(results)
    
    print(f"✅ 분석 완료! 결과가 {filename}에 저장되었습니다.")
    print(f"\n📊 프로파일 요약:")
    print(f"- Rosenberg 점수: {results['profile']['scores']['rosenberg']}/40")
    print(f"- 자존감 유형: {results['profile']['esteem_type']}")
    print(f"\n✨ 발견된 강점: {len(results['strengths'])}개")
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("자존감 분석 시스템 v1.0")
    print("=" * 60)
    print()
    
    # 예시 실행
    results = example_usage()
    
    print("\n" + "=" * 60)
    print("📧 생성된 이메일 템플릿:")
    print("=" * 60)
    
    for email_type, email_data in results['emails'].items():
        print(f"\n[{email_type.upper()}] - {email_data['send_delay_minutes']}분 후 발송")
        print(f"제목: {email_data['subject']}")
        print("-" * 60)
