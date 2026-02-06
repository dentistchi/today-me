"""
통합 보고서 시스템
===================
PDF 보고서 + 28일 실천 가이드 통합 버전
"""

from pdf_generator_v3 import ProfessionalPDFGenerator
from daily_practice_guide_v1 import DailyPracticeGuide
from datetime import datetime, timedelta

class IntegratedReportSystem:
    """PDF 보고서와 28일 가이드를 통합하는 시스템"""
    
    def __init__(self, user_email: str, analysis_results: dict):
        self.user_email = user_email
        self.user_name = user_email.split('@')[0]
        self.results = analysis_results
        
    def generate_complete_report(self, output_dir: str = "/home/user/webapp/outputs"):
        """완전한 보고서 생성: PDF + 28일 가이드"""
        
        print("="*70)
        print("📊 통합 보고서 생성 시작")
        print("="*70)
        
        # 1. PDF 심층 분석 보고서 생성
        print("\n1️⃣ PDF 심층 분석 보고서 생성 중...")
        pdf_path = self._generate_pdf_report(output_dir)
        print(f"   ✅ PDF 완료: {pdf_path}")
        
        # 2. 28일 실천 가이드 생성
        print("\n2️⃣ 28일 실천 가이드 생성 중...")
        guide_summary = self._generate_daily_guide()
        print(f"   ✅ 가이드 완료: 총 {len(guide_summary)}일")
        
        # 3. 통합 요약 출력
        print("\n" + "="*70)
        print("🎉 통합 보고서 생성 완료!")
        print("="*70)
        print(f"\n📦 생성된 파일:")
        print(f"   📄 PDF 보고서: {pdf_path}")
        print(f"   📅 28일 가이드: {len(guide_summary)}일치 데이터")
        
        print(f"\n💡 다음 단계:")
        print(f"   1. PDF 보고서를 읽고 자신의 패턴 이해하기")
        print(f"   2. Week 1 (Day 1-7)부터 실천 시작하기")
        print(f"   3. 28일 후 재검사 진행하기")
        
        return {
            "pdf_path": pdf_path,
            "guide_days": len(guide_summary),
            "user_email": self.user_email,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_pdf_report(self, output_dir: str) -> str:
        """PDF 심층 분석 보고서 생성"""
        output_path = f"{output_dir}/report_{self.user_name}.pdf"
        
        # PDF 데이터 준비
        pdf_data = {
            'user_email': self.user_email,
            'profile_type': self.results.get('profile_type', 'developing_critic'),
            'scores': self.results.get('scores', {
                'rosenberg': self.results.get('scores', {}).get('rosenberg', 22),
                'dimensions': {
                    '자기수용': 3.2,
                    '자기가치': 2.8,
                    '자기효능감': 3.5,
                    '자기자비': 2.5,
                    '사회적 연결': 3.0
                }
            }),
            'patterns': self.results.get('patterns', []),
            'strengths': self.results.get('strengths', [
                {
                    'name': '회복탄력성',
                    'evidence': '50개 질문을 모두 완료한 것은 당신의 회복탄력성을 보여줍니다.',
                    'how_to_use': '힘든 순간에 "나는 50개 질문을 다 답했어"라고 상기하세요.'
                },
                {
                    'name': '높은 기준',
                    'evidence': '자기비판은 성장하고 싶다는 증거입니다.',
                    'how_to_use': '기준을 버리지 말고 "완벽이 아닌 발전"으로 방향 전환하세요.'
                },
                {
                    'name': '자기 성찰',
                    'evidence': '이 보고서를 읽고 있다는 것이 자기 성찰 능력을 보여줍니다.',
                    'how_to_use': '자기비판이 아닌 자기이해에 이 능력을 활용하세요.'
                }
            ]),
            'retest_link': f'https://example.com/retest?user={self.user_name}'
        }
        
        # PDF 생성
        generator = ProfessionalPDFGenerator(pdf_data, output_path)
        generator.generate()
        
        return output_path
    
    def _generate_daily_guide(self) -> list:
        """28일 실천 가이드 생성"""
        guide = DailyPracticeGuide(self.user_name, self.results)
        all_days = guide.generate_all_days()
        
        return all_days
    
    def print_week_preview(self, week_num: int):
        """특정 주차 미리보기"""
        guide = DailyPracticeGuide(self.user_name, self.results)
        all_days = guide.generate_all_days()
        
        week_days = [d for d in all_days if d['week'] == week_num]
        
        print(f"\n{'='*70}")
        print(f"📅 Week {week_num} 미리보기 (Day {week_days[0]['day']}-{week_days[-1]['day']})")
        print(f"{'='*70}\n")
        
        for day in week_days:
            print(f"Day {day['day']}: {day['title']}")
            print(f"  🌅 {day['morning_ritual']}")
            
            if 'core_practice' in day and isinstance(day['core_practice'], dict):
                print(f"  📖 {day['core_practice'].get('name', 'N/A')}")
                print(f"  ⏱️  {day['core_practice'].get('duration', 'N/A')}")
            
            print(f"  ✅ {day.get('micro_win', 'N/A')}")
            print()


# ==========================================
# 사용 예시
# ==========================================

def example_usage():
    """통합 시스템 사용 예시"""
    
    # 샘플 분석 결과
    sample_results = {
        "scores": {
            "rosenberg": 22,
            "dimensions": {
                '자기수용': 3.2,
                '자기가치': 2.8,
                '자기효능감': 3.5,
                '자기자비': 2.5,
                '사회적 연결': 3.0
            }
        },
        "profile_type": "developing_critic",
        "detected_patterns": [
            {
                "type": "SELF_CRITICISM",
                "name": "자기비판",
                "strength": 0.85,
                "evidence": [1, 5, 10],
                "description": "자신에게 가혹한 기준을 적용하며 실수를 용납하지 못하는 패턴",
                "research": "Neff, K. D. (2003). Self-compassion: An alternative conceptualization."
            },
            {
                "type": "PERFECTIONISM",
                "name": "완벽주의",
                "strength": 0.78,
                "evidence": [4, 12, 18],
                "description": "100%가 아니면 의미 없다고 느끼며 끊임없이 더 나아지려 하는 패턴",
                "research": "Hewitt, P. L., & Flett, G. L. (1991). Perfectionism in the self."
            }
        ],
        "patterns": [
            {
                'name': '자기비판',
                'strength': 0.85,
                'evidence': [1, 5, 10],
                'description': '자신에게 가혹한 기준을 적용하며 실수를 용납하지 못하는 패턴',
                'research': 'Neff, K. D. (2003). Self-compassion.'
            }
        ],
        "strengths": [
            {
                'name': '회복탄력성',
                'evidence': '50개 질문을 모두 완료한 것은 당신의 회복탄력성을 보여줍니다.',
                'how_to_use': '힘든 순간에 "나는 50개 질문을 다 답했어"라고 상기하세요.'
            }
        ],
        "hidden_strengths": [
            {"name": "회복탄력성", "description": "어려움 속에서도 다시 일어서는 힘"}
        ]
    }
    
    # 통합 시스템 실행
    system = IntegratedReportSystem("example_user@email.com", sample_results)
    
    # 완전한 보고서 생성
    result = system.generate_complete_report()
    
    # Week 1 미리보기
    system.print_week_preview(1)
    
    return result


if __name__ == "__main__":
    example_usage()
