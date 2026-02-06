"""
과학적 연구 참고문헌 데이터베이스
================================
이메일 템플릿에서 사용할 연구 근거 및 링크
"""

from typing import Dict, List

# 연구 참고문헌 데이터베이스
RESEARCH_DATABASE = {
    'rosenberg_1965': {
        'id': 'rosenberg_1965',
        'short_cite': 'Rosenberg (1965)',
        'full_cite': 'Rosenberg, M. (1965). Society and the adolescent self-image. Princeton, NJ: Princeton University Press.',
        'year': 1965,
        'authors': 'Morris Rosenberg',
        'title': 'Society and the adolescent self-image',
        'journal': 'Princeton University Press',
        'doi': '10.1515/9781400876136',
        'url': 'https://doi.org/10.1515/9781400876136',
        'google_scholar': 'https://scholar.google.com/scholar?q=rosenberg+1965+self+esteem+scale',
        'citations': '60,000+',
        'description': '자존감 측정의 황금 표준, Rosenberg 자존감 척도 개발'
    },
    'neff_2003': {
        'id': 'neff_2003',
        'short_cite': 'Neff (2003)',
        'full_cite': 'Neff, K. D. (2003). Self-compassion: An alternative conceptualization of a healthy attitude toward oneself. Self and Identity, 2(2), 85-101.',
        'year': 2003,
        'authors': 'Kristin D. Neff',
        'title': 'Self-compassion: An alternative conceptualization of a healthy attitude toward oneself',
        'journal': 'Self and Identity',
        'volume': '2(2)',
        'pages': '85-101',
        'doi': '10.1080/15298860309032',
        'url': 'https://doi.org/10.1080/15298860309032',
        'google_scholar': 'https://scholar.google.com/scholar?q=neff+2003+self+compassion',
        'citations': '15,000+',
        'description': '자기자비(Self-Compassion) 개념 정립 및 측정 도구 개발'
    },
    'neff_germer_2013': {
        'id': 'neff_germer_2013',
        'short_cite': 'Neff & Germer (2013)',
        'full_cite': 'Neff, K. D., & Germer, C. K. (2013). A pilot study and randomized controlled trial of the mindful self‐compassion program. Journal of Clinical Psychology, 69(1), 28-44.',
        'year': 2013,
        'authors': 'Kristin D. Neff, Christopher K. Germer',
        'title': 'A pilot study and randomized controlled trial of the mindful self‐compassion program',
        'journal': 'Journal of Clinical Psychology',
        'volume': '69(1)',
        'pages': '28-44',
        'doi': '10.1002/jclp.21923',
        'url': 'https://doi.org/10.1002/jclp.21923',
        'google_scholar': 'https://scholar.google.com/scholar?q=neff+germer+2013+mindful+self+compassion',
        'citations': '3,500+',
        'description': '8주 자기자비 훈련의 효과 검증 (자존감 23% 상승, 우울 32% 감소)'
    },
    'dweck_2006': {
        'id': 'dweck_2006',
        'short_cite': 'Dweck (2006)',
        'full_cite': 'Dweck, C. S. (2006). Mindset: The new psychology of success. New York: Random House.',
        'year': 2006,
        'authors': 'Carol S. Dweck',
        'title': 'Mindset: The new psychology of success',
        'journal': 'Random House',
        'isbn': '978-0345472328',
        'url': 'https://www.penguinrandomhouse.com/books/44330/mindset-by-carol-s-dweck-phd/',
        'google_scholar': 'https://scholar.google.com/scholar?q=dweck+2006+mindset+growth',
        'citations': '30,000+',
        'description': '성장 마인드셋(Growth Mindset) vs 고정 마인드셋(Fixed Mindset) 연구'
    },
    'curran_2016': {
        'id': 'curran_2016',
        'short_cite': 'Curran (2016)',
        'full_cite': 'Curran, P. G. (2016). Methods for the detection of carelessly invalid responses in survey data. Journal of Experimental Social Psychology, 66, 4-19.',
        'year': 2016,
        'authors': 'Paul G. Curran',
        'title': 'Methods for the detection of carelessly invalid responses in survey data',
        'journal': 'Journal of Experimental Social Psychology',
        'volume': '66',
        'pages': '4-19',
        'doi': '10.1016/j.jesp.2015.07.006',
        'url': 'https://doi.org/10.1016/j.jesp.2015.07.006',
        'google_scholar': 'https://scholar.google.com/scholar?q=curran+2016+careless+responding',
        'citations': '1,700+',
        'description': '부주의 응답 감지 방법론 (응답 시간, Longstring 등)'
    },
    'ward_meade_2023': {
        'id': 'ward_meade_2023',
        'short_cite': 'Ward & Meade (2023)',
        'full_cite': 'Ward, M. K., & Meade, A. W. (2023). Dealing with careless responding in survey data: Prevention, identification, and recommended best practices. Annual Review of Psychology, 74, 577-596.',
        'year': 2023,
        'authors': 'Megan K. Ward, Adam W. Meade',
        'title': 'Dealing with careless responding in survey data: Prevention, identification, and recommended best practices',
        'journal': 'Annual Review of Psychology',
        'volume': '74',
        'pages': '577-596',
        'doi': '10.1146/annurev-psych-040422-045007',
        'url': 'https://doi.org/10.1146/annurev-psych-040422-045007',
        'google_scholar': 'https://scholar.google.com/scholar?q=ward+meade+2023+careless+responding',
        'citations': '494+',
        'description': '부주의 응답의 예방, 식별, 권장 사례 종합 리뷰'
    },
    'festinger_1954': {
        'id': 'festinger_1954',
        'short_cite': 'Festinger (1954)',
        'full_cite': 'Festinger, L. (1954). A theory of social comparison processes. Human Relations, 7(2), 117-140.',
        'year': 1954,
        'authors': 'Leon Festinger',
        'title': 'A theory of social comparison processes',
        'journal': 'Human Relations',
        'volume': '7(2)',
        'pages': '117-140',
        'doi': '10.1177/001872675400700202',
        'url': 'https://doi.org/10.1177/001872675400700202',
        'google_scholar': 'https://scholar.google.com/scholar?q=festinger+1954+social+comparison',
        'citations': '18,000+',
        'description': '사회적 비교 이론 (Social Comparison Theory)'
    },
    'gilbert_2009': {
        'id': 'gilbert_2009',
        'short_cite': 'Gilbert (2009)',
        'full_cite': 'Gilbert, P. (2009). The compassionate mind: A new approach to life\'s challenges. London: Constable.',
        'year': 2009,
        'authors': 'Paul Gilbert',
        'title': 'The compassionate mind: A new approach to life\'s challenges',
        'journal': 'Constable',
        'isbn': '978-1849010986',
        'url': 'https://www.goodreads.com/book/show/6734493-the-compassionate-mind',
        'google_scholar': 'https://scholar.google.com/scholar?q=gilbert+2009+compassionate+mind',
        'citations': '2,500+',
        'description': '자기비판의 신경과학적 메커니즘 및 자비 중심 치료(CFT)'
    },
    'baumeister_1995': {
        'id': 'baumeister_1995',
        'short_cite': 'Baumeister et al. (1995)',
        'full_cite': 'Baumeister, R. F., Campbell, J. D., Krueger, J. I., & Vohs, K. D. (1995). Exploding the self-esteem myth. Scientific American, 292(1), 84-91.',
        'year': 2005,
        'authors': 'Roy F. Baumeister, Jennifer D. Campbell, Joachim I. Krueger, Kathleen D. Vohs',
        'title': 'Exploding the self-esteem myth',
        'journal': 'Scientific American',
        'volume': '292(1)',
        'pages': '84-91',
        'doi': '10.1038/scientificamerican0105-84',
        'url': 'https://www.scientificamerican.com/article/exploding-the-self-esteem-myth/',
        'google_scholar': 'https://scholar.google.com/scholar?q=baumeister+2005+self+esteem+myth',
        'citations': '1,000+',
        'description': '높은 자존감이 항상 좋은 것은 아니다 (안정성의 중요성)'
    },
    'crocker_park_2004': {
        'id': 'crocker_park_2004',
        'short_cite': 'Crocker & Park (2004)',
        'full_cite': 'Crocker, J., & Park, L. E. (2004). The costly pursuit of self-esteem. Psychological Bulletin, 130(3), 392-414.',
        'year': 2004,
        'authors': 'Jennifer Crocker, Lora E. Park',
        'title': 'The costly pursuit of self-esteem',
        'journal': 'Psychological Bulletin',
        'volume': '130(3)',
        'pages': '392-414',
        'doi': '10.1037/0033-2909.130.3.392',
        'url': 'https://doi.org/10.1037/0033-2909.130.3.392',
        'google_scholar': 'https://scholar.google.com/scholar?q=crocker+park+2004+costly+pursuit+self+esteem',
        'citations': '2,800+',
        'description': '조건부 자존감(Contingent Self-Esteem)의 심리적 비용'
    }
}


def get_research(research_id: str) -> Dict:
    """연구 참고문헌 조회"""
    return RESEARCH_DATABASE.get(research_id, {})


def get_short_citation(research_id: str) -> str:
    """짧은 인용 형식"""
    research = get_research(research_id)
    return research.get('short_cite', '')


def get_citation_link(research_id: str) -> str:
    """인용 + 링크"""
    research = get_research(research_id)
    if not research:
        return ''
    
    short = research.get('short_cite', '')
    url = research.get('url', research.get('google_scholar', ''))
    
    return f"{short} → {url}"


def format_reference_list() -> str:
    """이메일 하단용 참고문헌 목록 (HTML)"""
    html = """
━━━━━━━━━━━━━━━━━━━━━━
📚 과학적 근거 (참고문헌)
━━━━━━━━━━━━━━━━━━━━━━

본 분석은 다음 연구들에 기반합니다:

"""
    
    # 주요 연구만 선택 (이메일에 포함할 것들)
    key_researches = [
        'rosenberg_1965',
        'neff_2003',
        'neff_germer_2013',
        'dweck_2006',
        'crocker_park_2004'
    ]
    
    for i, research_id in enumerate(key_researches, 1):
        research = get_research(research_id)
        if research:
            html += f"""
{i}. {research['full_cite']}
   [{research['citations']} 인용]
   📖 {research['description']}
   🔗 자세히 보기: {research.get('url', research.get('google_scholar', ''))}

"""
    
    html += """
━━━━━━━━━━━━━━━━━━━━━━

💡 더 많은 연구 자료는 우리 웹사이트의 '연구 근거' 페이지에서 확인하실 수 있습니다.
"""
    
    return html


def format_inline_citation(research_id: str, text: str) -> str:
    """
    텍스트 중간에 연구 인용 추가
    
    예: "자기자비를 실천하면 자존감이 23% 상승합니다" 
        → "자기자비를 실천하면 자존감이 23% 상승합니다¹"
    """
    research = get_research(research_id)
    if not research:
        return text
    
    # 상첨자 번호는 이메일 하단 참고문헌의 번호와 매칭
    citation_markers = {
        'rosenberg_1965': '¹',
        'neff_2003': '²',
        'neff_germer_2013': '³',
        'dweck_2006': '⁴',
        'crocker_park_2004': '⁵'
    }
    
    marker = citation_markers.get(research_id, '')
    return f"{text} {marker}"


# 사용 예시
if __name__ == "__main__":
    print("=" * 60)
    print("연구 참고문헌 데이터베이스")
    print("=" * 60)
    
    # 예시 1: 짧은 인용
    print("\n짧은 인용:")
    print(get_short_citation('neff_2003'))
    
    # 예시 2: 링크 포함 인용
    print("\n링크 포함:")
    print(get_citation_link('neff_2003'))
    
    # 예시 3: 참고문헌 목록
    print("\n참고문헌 목록:")
    print(format_reference_list())
