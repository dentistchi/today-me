"""
PDF 보고서 생성 시스템 v3.0 - 데모 스크립트
=============================================
다양한 프로파일로 PDF 보고서를 생성하는 예제
"""

from pdf_generator_v3 import ProfessionalPDFGenerator
import os

def create_sample_report(profile_type: str, output_filename: str):
    """특정 프로파일 타입으로 샘플 보고서 생성"""
    
    # 프로파일별 맞춤 데이터
    profile_configs = {
        'vulnerable': {
            'rosenberg': 15,
            'dimensions': {
                '자기수용': 2.1,
                '자기가치': 1.8,
                '자기효능감': 2.3,
                '자기자비': 1.9,
                '사회적 연결': 2.0
            },
            'patterns': [
                {
                    'name': '전반적 자기부정',
                    'strength': 0.92,
                    'evidence': [1, 3, 5, 8, 10],
                    'description': '자신의 가치를 전반적으로 부정하며, 지속적인 무가치감을 느끼는 패턴. 실수나 실패에 과도하게 반응하고, 자신을 용납하기 어려워합니다.',
                    'research': 'Rosenberg, M. (1965). Society and the adolescent self-image. Princeton University Press.'
                },
                {
                    'name': '사회적 고립감',
                    'strength': 0.87,
                    'evidence': [15, 22, 31],
                    'description': '타인과의 연결을 느끼지 못하고, 혼자라는 느낌이 강한 상태. 사회적 상황에서 불안과 부적응을 경험합니다.',
                    'research': 'Baumeister, R. F., & Leary, M. R. (1995). The need to belong. Psychological Bulletin.'
                }
            ]
        },
        'developing_critic': {
            'rosenberg': 22,
            'dimensions': {
                '자기수용': 3.2,
                '자기가치': 2.8,
                '자기효능감': 3.5,
                '자기자비': 2.5,
                '사회적 연결': 3.0
            },
            'patterns': [
                {
                    'name': '사회적 비교',
                    'strength': 0.83,
                    'evidence': [11, 18, 23],
                    'description': '타인과 자신을 지속적으로 비교하며 부족함을 느끼는 경향. SNS나 주변 사람들의 성취를 보며 자신을 낮게 평가합니다.',
                    'research': 'Festinger, L. (1954). A theory of social comparison processes. Human Relations.'
                },
                {
                    'name': '완벽주의 경향',
                    'strength': 0.76,
                    'evidence': [4, 12, 29],
                    'description': '높은 기준을 설정하고 그에 미치지 못할 때 자신을 강하게 비판. 실수를 용납하지 못하고 끊임없이 더 나아지려 합니다.',
                    'research': 'Hewitt, P. L., & Flett, G. L. (1991). Perfectionism in the self. Journal of Personality and Social Psychology.'
                }
            ]
        },
        'compassionate_grower': {
            'rosenberg': 28,
            'dimensions': {
                '자기수용': 3.8,
                '자기가치': 3.5,
                '자기효능감': 4.0,
                '자기자비': 4.2,
                '사회적 연결': 3.9
            },
            'patterns': [
                {
                    'name': '상황적 자기의심',
                    'strength': 0.52,
                    'evidence': [7, 19],
                    'description': '대부분의 경우 건강한 자존감을 유지하지만, 특정 상황(예: 새로운 도전, 실패 경험)에서 일시적으로 자신감이 흔들리는 패턴.',
                    'research': 'Brown, J. D., & Marshall, M. A. (2006). The three faces of self-esteem. Self and Identity.'
                }
            ]
        },
        'thriving': {
            'rosenberg': 35,
            'dimensions': {
                '자기수용': 4.5,
                '자기가치': 4.3,
                '자기효능감': 4.6,
                '자기자비': 4.4,
                '사회적 연결': 4.5
            },
            'patterns': []  # 패턴 없음
        }
    }
    
    config = profile_configs.get(profile_type, profile_configs['developing_critic'])
    
    report_data = {
        'user_email': f'{profile_type}@example.com',
        'profile_type': profile_type,
        'scores': {
            'rosenberg': config['rosenberg'],
            'dimensions': config['dimensions']
        },
        'patterns': config['patterns'],
        'strengths': [
            {
                'name': '회복탄력성',
                'evidence': '50개의 질문을 모두 완료하신 것 자체가 당신의 회복탄력성을 보여줍니다. 힘든 순간에도 포기하지 않고 계속 나아가는 힘이 있습니다.',
                'how_to_use': '앞으로 힘든 순간이 올 때, "나는 50개 질문을 다 답했어. 이것도 해낼 수 있어"라고 상기하세요.'
            },
            {
                'name': '높은 기준',
                'evidence': '자기비판의 역설적 강점 - 당신이 스스로에게 엄격한 것은 성장하고 싶다는 증거입니다. 이는 방향만 바꾸면 강력한 동력이 됩니다.',
                'how_to_use': '기준을 완전히 버리지 말고, "완벽이 아닌 발전"으로 방향을 전환하세요. "더 나은"이 목표가 되어야 합니다.'
            },
            {
                'name': '자기 성찰 능력',
                'evidence': '이 보고서를 여기까지 읽고 있다는 것 자체가 당신의 자기 성찰 능력을 보여줍니다. 많은 사람들이 자신을 들여다보길 두려워합니다.',
                'how_to_use': '이 능력을 자기비판이 아닌 자기이해에 활용하세요. "왜 나는 이렇게 느낄까?"라는 호기심 있는 질문을 던지세요.'
            }
        ],
        'retest_link': f'https://example.com/retest?profile={profile_type}'
    }
    
    output_path = f"/home/user/webapp/outputs/{output_filename}"
    generator = ProfessionalPDFGenerator(report_data, output_path)
    generator.generate()
    
    return output_path


def main():
    """다양한 프로파일로 샘플 PDF 생성"""
    
    print("=" * 60)
    print("PDF 보고서 생성 시스템 v3.0 - 데모")
    print("=" * 60)
    print()
    
    profiles = [
        ('vulnerable', 'report_vulnerable.pdf', '위기 상태'),
        ('developing_critic', 'report_developing_critic.pdf', '자기비판 경향'),
        ('compassionate_grower', 'report_compassionate_grower.pdf', '자비로운 성장'),
        ('thriving', 'report_thriving.pdf', '번영 상태')
    ]
    
    for profile_type, filename, description in profiles:
        print(f"📄 {description} ({profile_type}) 보고서 생성 중...")
        try:
            output_path = create_sample_report(profile_type, filename)
            file_size = os.path.getsize(output_path) / 1024  # KB
            print(f"   ✅ 생성 완료: {filename} ({file_size:.1f}KB)")
        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}")
        print()
    
    print("=" * 60)
    print("✨ 모든 보고서 생성 완료!")
    print("=" * 60)
    print()
    print("📁 출력 위치: /home/user/webapp/outputs/")
    print()
    print("🎨 생성된 보고서:")
    for _, filename, description in profiles:
        print(f"   • {filename} - {description}")
    print()
    print("💡 각 보고서는 프로파일에 맞는 색상 테마와 내용을 포함합니다.")


if __name__ == "__main__":
    main()
