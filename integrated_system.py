"""
전체 통합 시스템 (Main Orchestrator)
====================================
A (패턴 추출) → B (서사 생성) → C (4주 프로그램) → D (PDF 생성) → E (이메일 스케줄링)

단 하나의 함수 호출로 전체 워크플로우 실행:
    responses = [3, 2, 4, 1, 3, ...]  # 50개 응답
    result = generate_full_report(responses, user_email="user@example.com")
"""

from typing import Dict, List, Tuple
from datetime import datetime
import json
import os

# 우리가 만든 모듈들 (실제 환경에서는 import)
# from pattern_extraction_engine import PatternDetector
# from narrative_templates import NarrativeGenerator
# from daily_practice_guide import DailyPracticeGuide
# from weekly_reminder_system import ReminderSystem
# from pdf_generator_v2 import EnhancedPDFGenerator


class SelfEsteemAnalysisSystem:
    """자존감 분석 통합 시스템"""
    
    def __init__(self):
        self.version = "2.0"
        self.created_at = datetime.now()
        
    def calculate_rosenberg_score(self, responses: List[int]) -> int:
        """
        Rosenberg 자존감 척도 계산
        
        Args:
            responses: 50개 응답 중 Rosenberg 10문항 (1-4 척도)
                      예: [3, 2, 4, 1, 3, 4, 2, 3, 4, 2]
        
        Returns:
            점수 (0-40), 높을수록 높은 자존감
        """
        # 실제로는 50개 중 Rosenberg 10개만 추출
        # 간단화: 처음 10개 사용
        rosenberg_items = responses[:10]
        
        # 역채점 항목 (3, 5, 8, 9, 10번)
        reverse_items = [2, 4, 7, 8, 9]  # 0-based index
        
        score = 0
        for i, response in enumerate(rosenberg_items):
            if i in reverse_items:
                score += (5 - response)  # 역채점
            else:
                score += response
        
        return score
    
    def calculate_dimensions(self, responses: List[int]) -> Dict[str, float]:
        """
        5차원 점수 계산
        
        Returns:
            각 차원의 점수 (1-5 척도)
        """
        # 실제로는 각 차원별 질문 인덱스 매핑 필요
        # 간단화: 구간별로 나눔
        return {
            '자기수용': sum(responses[0:10]) / 10 / 4 * 5,      # 문항 1-10
            '자기가치': sum(responses[10:20]) / 10 / 4 * 5,     # 문항 11-20
            '자기효능감': sum(responses[20:30]) / 10 / 4 * 5,   # 문항 21-30
            '자기자비': sum(responses[30:40]) / 10 / 4 * 5,     # 문항 31-40
            '사회적 연결': sum(responses[40:50]) / 10 / 4 * 5   # 문항 41-50
        }
    
    def detect_patterns(self, responses: List[int]) -> List[Dict]:
        """
        패턴 감지 (Part A)
        
        Returns:
            감지된 패턴 리스트
        """
        # 실제로는 PatternDetector 사용
        # 간단화: 하드코딩
        patterns = []
        
        # 패턴 1: 사회적 비교 (질문 11, 18, 23, 31, 36, 44)
        comparison_questions = [10, 17, 22, 30, 35, 43]  # 0-based
        comparison_avg = sum([responses[i] for i in comparison_questions]) / len(comparison_questions)
        if comparison_avg >= 3.0:
            patterns.append({
                'name': '사회적 비교',
                'strength': min(comparison_avg / 4.0, 1.0),
                'evidence': [i+1 for i in comparison_questions],
                'description': '타인과 자신을 비교하며 부족함을 느끼는 경향',
                'research': 'Festinger, L. (1954). A theory of social comparison processes.'
            })
        
        # 패턴 2: 과도한 자기비판 (질문 2, 8, 14, 21, 28, 40)
        criticism_questions = [1, 7, 13, 20, 27, 39]
        criticism_avg = sum([responses[i] for i in criticism_questions]) / len(criticism_questions)
        if criticism_avg >= 3.0:
            patterns.append({
                'name': '과도한 자기비판',
                'strength': min(criticism_avg / 4.0, 1.0),
                'evidence': [i+1 for i in criticism_questions],
                'description': '실수나 실패 시 가혹한 자기비판',
                'research': 'Gilbert, P. (2009). The Compassionate Mind.'
            })
        
        # 패턴 3: 고립감 (질문 18, 26, 29, 35, 41, 47)
        isolation_questions = [17, 25, 28, 34, 40, 46]
        isolation_avg = sum([responses[i] for i in isolation_questions]) / len(isolation_questions)
        if isolation_avg >= 3.0:
            patterns.append({
                'name': '고립감',
                'strength': min(isolation_avg / 4.0, 1.0),
                'evidence': [i+1 for i in isolation_questions],
                'description': '자신만 힘들다는 고립된 느낌',
                'research': 'Neff, K. D. (2003). Self-compassion and common humanity.'
            })
        
        # 강도 순으로 정렬
        patterns.sort(key=lambda x: x['strength'], reverse=True)
        return patterns[:3]  # 상위 3개만
    
    def determine_profile_type(self, rosenberg_score: int, dimensions: Dict[str, float]) -> str:
        """
        프로파일 유형 결정
        
        Returns:
            6가지 프로파일 중 하나:
            - vulnerable: 취약함
            - developing_critic: 발전 중 (자기비판)
            - developing_balanced: 발전 중 (균형)
            - compassionate_grower: 자비로운 성장자
            - stable_rigid: 안정적이나 경직
            - thriving: 번영
        """
        self_compassion = dimensions.get('자기자비', 3.0)
        self_worth = dimensions.get('자기가치', 3.0)
        
        # 간단한 규칙 기반 분류
        if rosenberg_score < 15:
            return 'vulnerable'
        elif rosenberg_score < 20:
            if self_compassion < 2.5:
                return 'developing_critic'
            else:
                return 'developing_balanced'
        elif rosenberg_score < 25:
            return 'compassionate_grower'
        elif rosenberg_score < 30:
            return 'stable_rigid'
        else:
            return 'thriving'
    
    def extract_hidden_strengths(self, responses: List[int], patterns: List[Dict]) -> List[Dict]:
        """
        숨겨진 강점 추출
        
        Returns:
            Top 3 강점
        """
        strengths = [
            {
                'name': '회복탄력성',
                'evidence': '당신은 50개의 질문에 끝까지 답했습니다. 이것은 불편한 진실 앞에서도 도망가지 않은 용기입니다.',
                'how_to_use': '힘든 순간에 "나는 이전에도 이겨냈다"고 상기하세요.'
            },
            {
                'name': '높은 기준',
                'evidence': '자기비판은 역설적으로 높은 기준의 증거입니다. 당신은 더 나은 사람이 되고 싶어합니다.',
                'how_to_use': '기준을 낮추지 말고, 자신에게 관대해지세요.'
            },
            {
                'name': '자기 성찰',
                'evidence': '이 보고서를 읽고 있다는 것 자체가 자기 성찰 능력의 증거입니다.',
                'how_to_use': '이 능력을 자기비판이 아닌 자기이해에 사용하세요.'
            }
        ]
        
        return strengths
    
    def generate_narrative(self, analysis_result: Dict) -> Dict:
        """
        서사 생성 (Part B)
        
        실제로는 NarrativeGenerator 사용
        여기서는 구조만 반환
        """
        return {
            'opening_letter': f"{analysis_result['user_name']}님께 드리는 편지",
            'part1_dimensions': "5차원 분석 서사",
            'part2_patterns': "패턴 서사",
            'part3_strengths': "강점 서사",
            'part4_program': "4주 프로그램 서사",
            'closing_letter': "마지막 편지"
        }
    
    def generate_daily_practices(self, patterns: List[Dict]) -> List[Dict]:
        """
        28일 실천 가이드 생성 (Part C)
        
        실제로는 DailyPracticeGuide 사용
        """
        # 간단화: 구조만 반환
        return [
            {'day': i, 'title': f'Day {i} 실천', 'practices': []}
            for i in range(1, 29)
        ]
    
    def generate_weekly_reminders(self, analysis_result: Dict) -> List[Dict]:
        """
        주간 리마인더 생성 (Part C)
        
        실제로는 ReminderSystem 사용
        """
        return [
            {
                'week': 1,
                'send_at': '2026-02-10T09:00:00',
                'subject': 'Week 1: 자기자비 시작',
                'body': 'Week 1 격려 메시지...'
            },
            {
                'week': 2,
                'send_at': '2026-02-17T09:00:00',
                'subject': 'Week 2: 완벽주의 내려놓기',
                'body': 'Week 2 격려 메시지...'
            },
            {
                'week': 3,
                'send_at': '2026-02-24T09:00:00',
                'subject': 'Week 3: 공통 인간성',
                'body': 'Week 3 격려 메시지...'
            },
            {
                'week': 4,
                'send_at': '2026-03-03T09:00:00',
                'subject': 'Week 4: 안정적 자기가치',
                'body': 'Week 4 격려 메시지...'
            },
            {
                'type': 'retest',
                'send_at': '2026-03-03T09:00:00',
                'subject': '4주 후 재검사 초대',
                'body': '재검사 링크...'
            }
        ]
    
    def generate_pdf_report(self, report_data: Dict, output_path: str) -> str:
        """
        PDF 생성 (Part D)
        
        실제로는 EnhancedPDFGenerator 사용
        """
        # 여기서는 이미 만든 pdf_generator_v2.py를 동적 import
        try:
            import sys
            sys.path.insert(0, '/home/user')
            from pdf_generator_v2 import EnhancedPDFGenerator
            
            generator = EnhancedPDFGenerator(report_data, output_path)
            generator.generate()
            return output_path
        except Exception as e:
            print(f"⚠️  PDF 생성 실패: {e}")
            return None
    
    def generate_full_report(
        self,
        responses: List[int],
        user_email: str,
        output_dir: str = "/mnt/user-data/outputs"
    ) -> Dict:
        """
        전체 워크플로우 실행 (A → B → C → D → E)
        
        Args:
            responses: 50개 응답 (1-4 척도)
            user_email: 사용자 이메일
            output_dir: 출력 디렉토리
        
        Returns:
            {
                'success': True/False,
                'rosenberg_score': 22,
                'profile_type': 'developing_critic',
                'pdf_path': '/path/to/report.pdf',
                'reminders': [...],
                'daily_practices': [...],
                'timestamp': '2026-02-03T...'
            }
        """
        print("=" * 60)
        print("🚀 자존감 분석 통합 시스템 시작")
        print("=" * 60)
        
        user_name = user_email.split('@')[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # ========================================
            # STEP 1: 기본 점수 계산
            # ========================================
            print("\n[1/6] 📊 Rosenberg 점수 계산 중...")
            rosenberg_score = self.calculate_rosenberg_score(responses)
            print(f"      ✅ 점수: {rosenberg_score}/40")
            
            # ========================================
            # STEP 2: 5차원 분석
            # ========================================
            print("\n[2/6] 🔍 5차원 분석 중...")
            dimensions = self.calculate_dimensions(responses)
            print(f"      ✅ 차원 계산 완료")
            for dim, score in dimensions.items():
                print(f"         • {dim}: {score:.2f}/5.0")
            
            # ========================================
            # STEP 3: 패턴 감지 (Part A)
            # ========================================
            print("\n[3/6] 🧠 심리 패턴 감지 중...")
            patterns = self.detect_patterns(responses)
            print(f"      ✅ 감지된 패턴: {len(patterns)}개")
            for p in patterns:
                print(f"         • {p['name']} (강도: {p['strength']:.2f})")
            
            # ========================================
            # STEP 4: 프로파일 & 강점 (Part A)
            # ========================================
            print("\n[4/6] 🎯 프로파일 및 강점 분석 중...")
            profile_type = self.determine_profile_type(rosenberg_score, dimensions)
            strengths = self.extract_hidden_strengths(responses, patterns)
            print(f"      ✅ 프로파일: {profile_type}")
            print(f"      ✅ 강점: {len(strengths)}개")
            
            # ========================================
            # STEP 5: PDF 보고서 생성 (Part B + D)
            # ========================================
            print("\n[5/6] 📄 PDF 보고서 생성 중...")
            
            report_data = {
                'user_email': user_email,
                'profile_type': profile_type,
                'scores': {
                    'rosenberg': rosenberg_score,
                    'dimensions': dimensions
                },
                'patterns': patterns,
                'strengths': strengths,
                'retest_link': f'https://example.com/retest?user={user_name}&t={timestamp}'
            }
            
            pdf_filename = f"report_{user_name}_{timestamp}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            generated_pdf = self.generate_pdf_report(report_data, pdf_path)
            
            if generated_pdf:
                file_size = os.path.getsize(pdf_path) / 1024  # KB
                print(f"      ✅ PDF 생성 완료: {pdf_path}")
                print(f"         크기: {file_size:.1f} KB")
            else:
                print(f"      ⚠️  PDF 생성 실패 (경로: {pdf_path})")
            
            # ========================================
            # STEP 6: 4주 프로그램 & 리마인더 (Part C)
            # ========================================
            print("\n[6/6] 📅 4주 프로그램 및 리마인더 생성 중...")
            
            daily_practices = self.generate_daily_practices(patterns)
            reminders = self.generate_weekly_reminders(report_data)
            
            print(f"      ✅ 매일 실천 가이드: {len(daily_practices)}일")
            print(f"      ✅ 주간 리마인더: {len(reminders)}개")
            
            # 리마인더 JSON 저장
            reminders_filename = f"reminders_{user_name}_{timestamp}.json"
            reminders_path = os.path.join(output_dir, reminders_filename)
            with open(reminders_path, 'w', encoding='utf-8') as f:
                json.dump(reminders, f, ensure_ascii=False, indent=2)
            print(f"      ✅ 리마인더 저장: {reminders_path}")
            
            # ========================================
            # 최종 결과 반환
            # ========================================
            print("\n" + "=" * 60)
            print("✅ 전체 워크플로우 완료!")
            print("=" * 60)
            
            result = {
                'success': True,
                'user_email': user_email,
                'user_name': user_name,
                'rosenberg_score': rosenberg_score,
                'dimensions': dimensions,
                'profile_type': profile_type,
                'patterns': patterns,
                'strengths': strengths,
                'pdf_path': pdf_path if generated_pdf else None,
                'reminders_path': reminders_path,
                'daily_practices_count': len(daily_practices),
                'timestamp': timestamp
            }
            
            # 결과 요약 출력
            print(f"\n📊 분석 결과 요약:")
            print(f"   • 사용자: {user_name}")
            print(f"   • Rosenberg 점수: {rosenberg_score}/40")
            print(f"   • 프로파일: {profile_type}")
            print(f"   • 주요 패턴: {', '.join([p['name'] for p in patterns])}")
            print(f"   • PDF 리포트: {pdf_path if generated_pdf else 'N/A'}")
            print(f"   • 리마인더: {reminders_path}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': timestamp
            }


# ==========================================
# 사용 예시
# ==========================================

if __name__ == "__main__":
    # 샘플 응답 생성 (실제로는 사용자 입력)
    import random
    random.seed(42)
    
    # 50개 응답 (1-4 척도)
    # 중간~낮은 자존감 시뮬레이션
    sample_responses = []
    for i in range(50):
        if i % 3 == 0:
            sample_responses.append(random.choice([1, 2]))  # 낮음
        elif i % 3 == 1:
            sample_responses.append(random.choice([2, 3]))  # 중간
        else:
            sample_responses.append(random.choice([3, 4]))  # 높음
    
    print("📝 샘플 응답 생성 완료")
    print(f"   응답 수: {len(sample_responses)}개")
    print(f"   평균: {sum(sample_responses)/len(sample_responses):.2f}/4.0")
    print(f"   샘플: {sample_responses[:10]}...")
    
    # 시스템 초기화
    system = SelfEsteemAnalysisSystem()
    
    # 전체 워크플로우 실행
    result = system.generate_full_report(
        responses=sample_responses,
        user_email="testuser@example.com",
        output_dir="/mnt/user-data/outputs"
    )
    
    # 결과 저장
    if result['success']:
        result_filename = f"analysis_result_{result['user_name']}_{result['timestamp']}.json"
        result_path = f"/mnt/user-data/outputs/{result_filename}"
        
        with open(result_path, 'w', encoding='utf-8') as f:
            # PDF 경로는 JSON 직렬화 가능하도록 처리
            json_safe_result = {k: v for k, v in result.items() if k != 'daily_practices'}
            json.dump(json_safe_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장: {result_path}")
        print(f"\n🎉 모든 작업 완료!")
        print(f"\n📥 다운로드 가능한 파일:")
        print(f"   1. PDF 리포트: {result['pdf_path']}")
        print(f"   2. 리마인더: {result['reminders_path']}")
        print(f"   3. 분석 결과: {result_path}")
    else:
        print(f"\n❌ 워크플로우 실패")
