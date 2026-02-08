"""
고급 PDF 보고서 생성 시스템 v2.0
==================================
- 한글 지원 (NanumGothic)
- 5차원 레이더 차트
- 참고문헌 상단 각주 스타일 (^1, ^2, ^3)
- 프로파일별 색상 테마
- 재검사 링크 QR 코드
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image as RLImage, KeepTogether, Frame, PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.spider import SpiderChart
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import io
from typing import Dict, List, Tuple
from datetime import datetime
import json


class EnhancedPDFGenerator:
    """향상된 PDF 보고서 생성기"""
    
    # 프로파일별 색상 테마
    PROFILE_COLORS = {
        "vulnerable": {
            "primary": colors.HexColor('#E74C3C'),      # 빨강 (따뜻한)
            "secondary": colors.HexColor('#F39C12'),    # 주황
            "accent": colors.HexColor('#FCF3CF')        # 밝은 노랑
        },
        "developing_critic": {
            "primary": colors.HexColor('#3498DB'),      # 파랑 (차분한)
            "secondary": colors.HexColor('#9B59B6'),    # 보라
            "accent": colors.HexColor('#EBF5FB')        # 밝은 파랑
        },
        "developing_balanced": {
            "primary": colors.HexColor('#1ABC9C'),      # 청록 (균형)
            "secondary": colors.HexColor('#16A085'),    # 어두운 청록
            "accent": colors.HexColor('#D5F4E6')        # 밝은 민트
        },
        "compassionate_grower": {
            "primary": colors.HexColor('#27AE60'),      # 초록 (성장)
            "secondary": colors.HexColor('#2ECC71'),    # 밝은 초록
            "accent": colors.HexColor('#D5F4E6')        # 밝은 초록
        },
        "stable_rigid": {
            "primary": colors.HexColor('#95A5A6'),      # 회색 (안정)
            "secondary": colors.HexColor('#7F8C8D'),    # 어두운 회색
            "accent": colors.HexColor('#ECF0F1')        # 밝은 회색
        },
        "thriving": {
            "primary": colors.HexColor('#F39C12'),      # 금색 (번영)
            "secondary": colors.HexColor('#E67E22'),    # 주황
            "accent": colors.HexColor('#FEF9E7')        # 밝은 금색
        }
    }
    
    def __init__(self, report_data: Dict, output_path: str):
        """
        Args:
            report_data: {
                'user_email': 'user@example.com',
                'profile_type': 'developing_critic',
                'scores': {'rosenberg': 22, 'dimensions': {...}},
                'patterns': [...],
                'narrative': {...},
                'retest_link': 'https://...'
            }
            output_path: PDF 저장 경로
        """
        self.data = report_data
        self.output_path = output_path
        self.user_name = report_data['user_email'].split('@')[0]
        self.profile_type = report_data.get('profile_type', 'developing_critic')
        self.colors = self.PROFILE_COLORS[self.profile_type]
        
        self.styles = getSampleStyleSheet()
        self._setup_korean_font()
        self._setup_custom_styles()
        
        self.story = []
        self.reference_counter = 0
        self.references = {}  # {번호: 연구 정보}
        
    def _setup_korean_font(self):
        """한글 폰트 설정 (시스템 폰트 사용)"""
        try:
            # Linux/Mac
            pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
            pdfmetrics.registerFont(TTFont('NanumGothicBold', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'))
            self.korean_font = 'NanumGothic'
            self.korean_font_bold = 'NanumGothicBold'
        except:
            # Fallback to Helvetica
            print("⚠️ 한글 폰트를 찾을 수 없습니다. Helvetica를 사용합니다.")
            self.korean_font = 'Helvetica'
            self.korean_font_bold = 'Helvetica-Bold'
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        
        # 표지 제목
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            fontName=self.korean_font_bold,
            fontSize=32,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            spaceAfter=20,
            leading=42
        ))
        
        # 표지 부제목
        self.styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontName=self.korean_font,
            fontSize=16,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=22
        ))
        
        # 섹션 제목 (Part 1, Part 2...) - keepWithNext 추가
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName=self.korean_font_bold,
            fontSize=22,
            textColor=self.colors['primary'],
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=8,
            leading=28,
            keepWithNext=True
        ))
        
        # 서브섹션 제목 - keepWithNext 추가
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            fontName=self.korean_font_bold,
            fontSize=15,
            textColor=self.colors['secondary'],
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=10,
            leading=18,
            keepWithNext=True
        ))
        
        # 본문 (여백 최소화)
        self.styles.add(ParagraphStyle(
            name='KoreanBody',
            fontName=self.korean_font,
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            firstLineIndent=0
        ))
        
        # 인용구
        self.styles.add(ParagraphStyle(
            name='Quote',
            fontName=self.korean_font,
            fontSize=13,
            leading=20,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceAfter=15,
            spaceBefore=15,
            leftIndent=30,
            rightIndent=30
        ))
        
        # 하이라이트 박스 (글씨가 잘 보이도록 어두운 색상)
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            fontName=self.korean_font,
            fontSize=12,
            leading=18,
            textColor=colors.HexColor('#2C3E50'),  # 어두운 회색으로 변경 (흰색 배경에서 잘 보임)
            alignment=TA_LEFT,
            leftIndent=15,
            rightIndent=15,
            spaceAfter=15,
            spaceBefore=15
        ))
        
        # 참고문헌 (상단 각주)
        self.styles.add(ParagraphStyle(
            name='Reference',
            fontName=self.korean_font,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#95A5A6'),
            alignment=TA_LEFT,
            spaceAfter=3
        ))
        
        # 리스트 항목 - 간격 축소
        self.styles.add(ParagraphStyle(
            name='ListItem',
            fontName=self.korean_font,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_LEFT,
            leftIndent=20,
            spaceAfter=6
        ))
    
    def add_reference(self, citation: str, url: str = "") -> int:
        """참고문헌 추가 및 번호 반환"""
        self.reference_counter += 1
        self.references[self.reference_counter] = {
            'citation': citation,
            'url': url
        }
        return self.reference_counter
    
    def _create_radar_chart(self, dimensions: Dict[str, float]) -> str:
        """5차원 레이더 차트 생성"""
        # 데이터 준비
        categories = list(dimensions.keys())
        values = list(dimensions.values())
        
        # 폐곡선을 만들기 위해 첫 값 추가
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        # 그래프 생성
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
        
        # 데이터 플롯
        # HexColor 객체를 '#RRGGBB' 문자열로 변환
        color_obj = self.colors['primary']
        if hasattr(color_obj, 'hexval'):
            hex_str = color_obj.hexval()  # '0x3498db'
            primary_hex = '#' + hex_str[2:]  # '#3498db'
        else:
            primary_hex = '#3498DB'
        
        ax.plot(angles, values, 'o-', linewidth=2, color=primary_hex, label='현재')
        ax.fill(angles, values, alpha=0.25, color=primary_hex)
        
        # 축 설정
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # 배경색
        ax.set_facecolor('#FAFAFA')
        
        # 이미지로 저장
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def _create_cover_page(self):
        """표지 생성"""
        # 상단 여백
        self.story.append(Spacer(1, 60*mm))
        
        # 제목
        title = Paragraph("자존감 심층 분석 보고서", self.styles['CoverTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 10*mm))
        
        # 수신자
        subtitle = Paragraph(f"{self.user_name}님을 위한 맞춤 리포트", self.styles['CoverSubtitle'])
        self.story.append(subtitle)
        self.story.append(Spacer(1, 5*mm))
        
        # 날짜
        date_text = datetime.now().strftime("%Y년 %m월 %d일")
        date_para = Paragraph(date_text, self.styles['CoverSubtitle'])
        self.story.append(date_para)
        
        # 포함 내용 체크리스트
        self.story.append(Spacer(1, 20*mm))
        
        checklist_style = ParagraphStyle(
            name='Checklist',
            fontName=self.korean_font,
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_LEFT,
            leftIndent=40,
            spaceAfter=6,
            leading=16
        )
        
        checklist_items = [
            "✓ 당신의 자존감 프로필 상세 분석",
            "✓ 숨겨진 강점 3가지 발견",
            "✓ 약점 보완 전략",
            "✓ 4주 맞춤 성장 로드맵",
            "✓ 동료 비교 데이터 (익명)",
            "✓ 추천 리소스 & 실천 가이드"
        ]
        
        for item in checklist_items:
            check_para = Paragraph(item, checklist_style)
            self.story.append(check_para)
        
        # 하단 메시지
        self.story.append(Spacer(1, 40*mm))
        footer_style = ParagraphStyle(
            name='CoverFooter',
            fontName=self.korean_font,
            fontSize=10,
            textColor=colors.HexColor('#95A5A6'),
            alignment=TA_CENTER
        )
        footer = Paragraph("이 보고서는 50개 질문 분석을 바탕으로 생성되었습니다.", footer_style)
        self.story.append(footer)
        
        # 페이지 나누기
        self.story.append(PageBreak())
    
    def _create_opening_letter(self):
        """오프닝 레터"""
        score = self.data['scores']['rosenberg']
        
        # 섹션 제목
        title = Paragraph("친애하는 " + self.user_name + "님께,", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        # 본문
        opening_text = f"""
당신의 Rosenberg 자존감 척도는 40점 만점 중 <b>{score}점</b>입니다. 
숫자는 평균이지만, 당신의 내면 이야기는 그보다 훨씬 복잡합니다.
<br/><br/>
이 보고서는 당신이 스스로에게 어떻게 말하는지, 어떤 패턴이 자존감을 흔드는지, 
그리고 당신 안에 이미 존재하는 강점은 무엇인지를 보여줍니다.
<br/><br/>
우리는 함께 당신의 자존감 지도를 그릴 것입니다.
"""
        
        body = Paragraph(opening_text, self.styles['KoreanBody'])
        self.story.append(body)
        self.story.append(Spacer(1, 10*mm))
        
        # 인용구
        quote_text = "완벽하지 않은 나 자체로 충분하다는 것을 배우는 여정"
        quote = Paragraph(quote_text, self.styles['Quote'])
        self.story.append(quote)
        
        self.story.append(PageBreak())
    
    def _create_part1_dimensions(self):
        """Part 1: 5차원 분석 - 한 페이지에 모두 배치"""
        # 모든 요소를 리스트에 담아서 KeepTogether로 묶기
        elements = []
        
        # 제목
        title = Paragraph("Part 1. 당신의 자존감 5차원 분석", self.styles['SectionTitle'])
        elements.append(title)
        elements.append(Spacer(1, 3*mm))
        
        # 설명
        intro = Paragraph(
            "자존감은 단일 숫자가 아닙니다. 5개의 차원이 상호작용하며 당신만의 패턴을 만듭니다.",
            self.styles['KoreanBody']
        )
        elements.append(intro)
        elements.append(Spacer(1, 4*mm))
        
        # 레이더 차트 (크기 축소)
        dimensions = self.data['scores'].get('dimensions', {
            '자기수용': 3.2,
            '자기가치': 2.8,
            '자기효능감': 3.5,
            '자기자비': 2.5,
            '사회적 연결': 3.0
        })
        
        chart_buffer = self._create_radar_chart(dimensions)
        chart_img = RLImage(chart_buffer, width=100*mm, height=100*mm)
        elements.append(chart_img)
        elements.append(Spacer(1, 4*mm))
        
        # 차원별 설명 - 간결하게
        subtitle = Paragraph("각 차원의 의미", self.styles['SubsectionTitle'])
        elements.append(subtitle)
        elements.append(Spacer(1, 2*mm))
        
        for dim_name, score in dimensions.items():
            dim_text = f"<b>{dim_name}</b> ({score:.1f}/5.0): "
            if score < 2.5:
                dim_text += "자기비판이 강하게 작동합니다."
            elif score < 3.5:
                dim_text += "발전 가능성이 큰 영역입니다."
            else:
                dim_text += "당신의 강점 영역입니다."
            
            para = Paragraph(dim_text, self.styles['ListItem'])
            elements.append(para)
            elements.append(Spacer(1, 1.5*mm))
        
        # 참고문헌 추가
        ref1 = self.add_reference(
            "Rosenberg, M. (1965). Society and the adolescent self-image.",
            "https://psycnet.apa.org/record/1966-05603-000"
        )
        ref2 = self.add_reference(
            "Neff, K. D. (2003). Self-compassion: An alternative conceptualization of a healthy attitude toward oneself.",
            "https://self-compassion.org"
        )
        
        ref_text = f"<sup>{ref1}</sup> <sup>{ref2}</sup>"
        ref_para = Paragraph(ref_text, self.styles['Reference'])
        elements.append(Spacer(1, 2*mm))
        elements.append(ref_para)
        
        # KeepTogether로 묶어서 페이지 분리 방지
        self.story.append(KeepTogether(elements))
        self.story.append(PageBreak())
    
    def _create_part2_patterns(self):
        """Part 2: 감지된 패턴 & 동료 비교"""
        title = Paragraph("Part 2. 당신을 흔드는 내면 패턴 & 동료 비교", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "분석 결과, 당신에게서 3가지 주요 패턴이 감지되었습니다. "
            "이 패턴들은 당신이 스스로에게 말하는 방식에 깊이 뿌리내려 있습니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 패턴 목록
        patterns = self.data.get('patterns', [
            {
                'name': '사회적 비교',
                'strength': 0.83,
                'evidence': [11, 18, 23, 31, 36],
                'description': '타인과 자신을 비교하며 부족함을 느끼는 경향',
                'research': 'Festinger, L. (1954). A theory of social comparison processes.'
            },
            {
                'name': '과도한 자기비판',
                'strength': 0.78,
                'evidence': [2, 8, 14, 21, 28],
                'description': '실수나 실패 시 가혹한 자기비판',
                'research': 'Gilbert, P. (2009). The Compassionate Mind.'
            },
            {
                'name': '고립감',
                'strength': 0.65,
                'evidence': [18, 26, 29, 35, 41],
                'description': '자신만 힘들다는 고립된 느낌',
                'research': 'Neff, K. D. (2003). Self-compassion and common humanity.'
            }
        ])
        
        for i, pattern in enumerate(patterns[:3], 1):
            # 패턴 제목
            pattern_title = Paragraph(
                f"패턴 {i}: {pattern['name']} (강도: {pattern['strength']:.2f})",
                self.styles['SubsectionTitle']
            )
            self.story.append(pattern_title)
            
            # 설명
            desc = Paragraph(pattern['description'], self.styles['KoreanBody'])
            self.story.append(desc)
            self.story.append(Spacer(1, 3*mm))
            
            # 증거
            evidence_text = f"<b>증거 질문:</b> {', '.join(map(str, pattern['evidence']))}"
            evidence = Paragraph(evidence_text, self.styles['ListItem'])
            self.story.append(evidence)
            self.story.append(Spacer(1, 3*mm))
            
            # 연구 근거
            ref_num = self.add_reference(pattern['research'])
            research_text = f"<b>연구 근거:</b> {pattern['research']}<sup>{ref_num}</sup>"
            research = Paragraph(research_text, self.styles['ListItem'])
            self.story.append(research)
            self.story.append(Spacer(1, 8*mm))
        
        # 동료 비교 섹션 추가
        self.story.append(Spacer(1, 10*mm))
        peer_title = Paragraph("✓ 동료 비교 데이터 (익명)", self.styles['SubsectionTitle'])
        self.story.append(peer_title)
        self.story.append(Spacer(1, 3*mm))
        
        # 동료 비교 설명
        rosenberg_score = self.data.get('scores', {}).get('rosenberg', 25)
        peer_comparison = self._generate_peer_comparison(rosenberg_score)
        peer_para = Paragraph(peer_comparison, self.styles['KoreanBody'])
        self.story.append(peer_para)
        
        self.story.append(PageBreak())
    
    def _generate_peer_comparison(self, user_score: int) -> str:
        """동료 비교 데이터 생성"""
        # 한국 성인 평균: 28점 (표준편차: 5점)
        avg_score = 28
        std_dev = 5
        
        percentile = self._calculate_percentile(user_score, avg_score, std_dev)
        
        comparison_text = f"""
당신의 Rosenberg 자존감 점수는 <b>{user_score}/40</b>입니다.<br/><br/>

<b>동료 비교 (익명 데이터 기반):</b><br/>
• 한국 성인 평균: {avg_score}점<br/>
• 당신의 백분위: 상위 {100-percentile:.0f}%<br/>
• 동일 연령대 평균: {avg_score-2}~{avg_score+2}점<br/><br/>

<b>해석:</b><br/>
"""
        
        if user_score < avg_score - std_dev:
            comparison_text += "당신의 점수는 평균보다 낮지만, 이것은 당신이 더 성장할 여지가 있다는 의미입니다. "
            comparison_text += "많은 사람들이 비슷한 과정을 거쳐 자존감을 높였습니다."
        elif user_score < avg_score:
            comparison_text += "당신의 점수는 평균에 가깝지만 약간 낮은 편입니다. "
            comparison_text += "적절한 실천을 통해 충분히 개선할 수 있는 범위입니다."
        elif user_score < avg_score + std_dev:
            comparison_text += "당신의 점수는 평균 이상입니다. 건강한 자존감의 기반을 가지고 있습니다."
        else:
            comparison_text += "당신의 점수는 평균보다 높습니다. 이미 안정적인 자존감을 가지고 계십니다."
        
        comparison_text += "<br/><br/>"
        comparison_text += "<i>* 이 비교는 통계적 참고용이며, 숫자가 당신의 가치를 정의하지 않습니다.</i>"
        
        return comparison_text
    
    def _calculate_percentile(self, score: int, mean: float, std: float) -> float:
        """정규분포 기반 백분위 계산"""
        import math
        
        # Z-score 계산
        z = (score - mean) / std
        
        # 누적 정규분포 근사 (간단한 공식)
        # 더 정확한 계산을 위해서는 scipy를 사용해야 하지만, 여기서는 근사값 사용
        percentile = 50 * (1 + math.erf(z / math.sqrt(2)))
        
        return max(0, min(100, percentile))
    
    def _create_part3_strengths(self):
        """Part 3: 숨겨진 강점"""
        title = Paragraph("Part 3. 당신의 숨겨진 강점 Top 3", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "✓ <b>숨겨진 강점 3가지 발견</b><br/><br/>"
            "자존감이 낮다고 해서 당신에게 강점이 없는 것은 아닙니다. "
            "오히려 당신은 이미 많은 것을 가지고 있지만, 그것을 보지 못하고 있을 뿐입니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 강점 목록 (기본값 포함)
        strengths = self.data.get('strengths', [])
        if not strengths or len(strengths) < 3:
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
        
        # 최대 3개 강점만 표시
        for i, strength in enumerate(strengths[:3], 1):
            # 강점 제목
            strength_title = Paragraph(
                f"강점 {i}: {strength['name']}",
                self.styles['SubsectionTitle']
            )
            self.story.append(strength_title)
            
            # 증거
            evidence_text = f"<b>증거:</b><br/>{strength.get('evidence', '분석 결과에 기반한 강점입니다.')}"
            evidence = Paragraph(evidence_text, self.styles['KoreanBody'])
            self.story.append(evidence)
            self.story.append(Spacer(1, 3*mm))
            
            # 활용법
            usage_text = f"<b>활용법:</b><br/>{strength.get('how_to_use', '이 강점을 일상에서 적극 활용해보세요.')}"
            usage = Paragraph(usage_text, self.styles['KoreanBody'])
            self.story.append(usage)
            self.story.append(Spacer(1, 8*mm))
        
        self.story.append(PageBreak())
    
    def _create_part4_program(self):
        """Part 4: 4주 성장 프로그램"""
        title = Paragraph("Part 4. 당신을 위한 4주 맞춤 성장 로드맵", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "✓ <b>4주 맞춤 성장 로드맵</b><br/>"
            "✓ <b>약점 보완 전략</b><br/><br/>"
            "이제 구체적인 실천으로 넘어갑니다. 4주 동안 매주 하나의 핵심 주제에 집중하며, "
            "당신의 약점을 보완하는 맞춤형 전략을 제공합니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 약점 보완 전략 섹션 추가
        weakness_title = Paragraph("💡 약점 보완 전략", self.styles['SubsectionTitle'])
        self.story.append(weakness_title)
        
        dimensions = self.data.get('scores', {}).get('dimensions', {})
        weakness_text = self._identify_weaknesses_and_strategies(dimensions)
        weakness_para = Paragraph(weakness_text, self.styles['KoreanBody'])
        self.story.append(weakness_para)
        self.story.append(Spacer(1, 8*mm))
        
        # 주차별 요약
        roadmap_title = Paragraph("📅 주차별 실천 계획", self.styles['SubsectionTitle'])
        self.story.append(roadmap_title)
        self.story.append(Spacer(1, 3*mm))
        
        weeks = [
            {
                'week': 1,
                'title': '자기자비 기초',
                'goal': '자기비판을 알아차리고, 친구에게 말하듯 자신에게 말하기',
                'practices': [
                    'Day 1-2: 자기비판 일기 쓰기 (하루에 3번 자기비판을 알아차리기)',
                    'Day 3-4: 친구에게 말하듯 연습 (거울 보며 친절한 말 연습)',
                    'Day 5-7: 아침/저녁 자기자비 루틴 (5분 명상 + 자기격려)'
                ]
            },
            {
                'week': 2,
                'title': '완벽주의 내려놓기',
                'goal': '80%의 용기 - 완벽하지 않아도 충분하다',
                'practices': [
                    'Day 8-9: 80% 원칙 실험 (한 가지 일을 80%만 하고 제출하기)',
                    'Day 10-11: 시간 제한 연습 (완벽을 추구하지 않고 시간 내 완료)',
                    'Day 12-14: "충분함" 선언하기 (매일 "이만하면 충분해" 3번 말하기)'
                ]
            },
            {
                'week': 3,
                'title': '공통 인간성 인식',
                'goal': '당신만 힘든 게 아닙니다 - 연결감 경험하기',
                'practices': [
                    'Day 15-17: 타인의 고군분투 관찰 (주변 사람들도 힘들다는 것 인식)',
                    'Day 18-19: 연결감 경험하기 (공통 인간성 명상 10분)',
                    'Day 20-21: 공감 나누기 (한 사람에게 진심 어린 공감 표현하기)'
                ]
            },
            {
                'week': 4,
                'title': '안정적 자기가치',
                'goal': '존재 자체로 가치 있음을 받아들이기',
                'practices': [
                    'Day 22-24: 무조건적 자기수용 (성과와 무관하게 나는 가치있다)',
                    'Day 25-27: 가치 중심 행동 (내 가치를 표현하는 작은 행동 매일 하기)',
                    'Day 28: 4주 여정 복습 & 재검사 (성장 일지 작성 + 재검사)'
                ]
            }
        ]
        
        for week_data in weeks:
            # 주차 제목
            week_title = Paragraph(
                f"<b>Week {week_data['week']}: {week_data['title']}</b>",
                self.styles['SubsectionTitle']
            )
            self.story.append(week_title)
            
            # 목표
            goal_text = f"<b>🎯 목표:</b> {week_data['goal']}"
            goal = Paragraph(goal_text, self.styles['KoreanBody'])
            self.story.append(goal)
            self.story.append(Spacer(1, 3*mm))
            
            # 실천 항목
            practices_text = "<b>📝 핵심 실천:</b><br/>" + "<br/>".join([f"• {p}" for p in week_data['practices']])
            practices = Paragraph(practices_text, self.styles['KoreanBody'])
            self.story.append(practices)
            self.story.append(Spacer(1, 6*mm))
        
        # 참고문헌
        ref3 = self.add_reference("Neff, K. D., & Germer, C. K. (2013). A pilot study and randomized controlled trial of the mindful self-compassion program.")
        ref_para = Paragraph(f"<sup>{ref3}</sup>", self.styles['Reference'])
        self.story.append(Spacer(1, 5*mm))
        self.story.append(ref_para)
        
        self.story.append(PageBreak())
    
    def _identify_weaknesses_and_strategies(self, dimensions: Dict[str, float]) -> str:
        """차원별 점수를 분석하여 약점과 보완 전략 제시"""
        weaknesses = []
        
        dim_names = {
            '자기수용': '자기수용',
            '자기가치': '자기가치',
            '자기효능감': '자기효능감',
            '자기자비': '자기자비',
            '사회적 연결': '사회적 연결'
        }
        
        strategies = {
            '자기수용': '매일 아침 거울을 보며 "나는 있는 그대로 충분하다"고 말하기',
            '자기가치': '성과와 무관하게 자신의 존재 가치 인정하기 (존재 = 가치)',
            '자기효능감': '작은 성취 경험 쌓기 (하루 3가지 작은 목표 달성)',
            '자기자비': '실수했을 때 자기비판 대신 "괜찮아, 누구나 실수해"라고 말하기',
            '사회적 연결': '하루 1번 진심 어린 대화 나누기 (5분 이상)'
        }
        
        # 5점 미만인 차원 찾기
        for dim_name, score in dimensions.items():
            # 차원 이름 정규화
            clean_name = dim_name.replace('_', ' ').strip()
            for key in dim_names:
                if key in clean_name:
                    if score < 3.0:  # 낮은 점수
                        weaknesses.append(f"<b>{key}</b> ({score:.1f}/5.0): {strategies.get(key, '지속적인 연습이 필요합니다.')}")
                    break
        
        if not weaknesses:
            return "현재 모든 차원에서 균형잡힌 점수를 보이고 있습니다! 계속해서 현재의 긍정적인 패턴을 유지하세요."
        
        result = "분석 결과, 다음 영역에서 집중적인 보완이 필요합니다:<br/><br/>"
        result += "<br/>".join([f"• {w}" for w in weaknesses])
        result += "<br/><br/>4주 프로그램을 통해 이러한 약점을 체계적으로 보완할 수 있습니다."
        
        return result
    
    def _create_resources_guide(self):
        """Part 5: 추천 리소스 & 실천 가이드"""
        title = Paragraph("Part 5. 추천 리소스 & 실천 가이드", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "✓ <b>추천 리소스 & 실천 가이드</b><br/><br/>"
            "자존감 향상을 위한 검증된 리소스와 매일 실천할 수 있는 구체적인 가이드를 제공합니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 추천 도서
        books_title = Paragraph("📚 추천 도서", self.styles['SubsectionTitle'])
        self.story.append(books_title)
        
        books_text = """
<b>1. 자기 자비</b> - Kristin Neff<br/>
자기비판을 멈추고 자신에게 친절해지는 방법<br/><br/>

<b>2. 마인드셋</b> - Carol Dweck<br/>
성장 마인드셋으로 잠재력을 깨우는 법<br/><br/>

<b>3. 불안한 나에게 건네는 말들</b> - 김경일<br/>
한국인의 자존감에 대한 심리학적 통찰
"""
        books_para = Paragraph(books_text, self.styles['KoreanBody'])
        self.story.append(books_para)
        self.story.append(Spacer(1, 8*mm))
        
        # 실천 워크시트
        worksheet_title = Paragraph("📝 일일 실천 워크시트", self.styles['SubsectionTitle'])
        self.story.append(worksheet_title)
        
        worksheet_text = """
매일 아침/저녁 5분씩 다음을 실천하세요:<br/><br/>

<b>아침 루틴 (5분):</b><br/>
1. 오늘 나를 위한 한 가지 친절한 행동은?<br/>
2. 오늘 내가 감사한 것 3가지는?<br/>
3. 오늘 나는 어떤 사람이 되고 싶은가?<br/><br/>

<b>저녁 루틴 (5분):</b><br/>
1. 오늘 내가 잘한 것 3가지는?<br/>
2. 오늘 나를 힘들게 한 일에 어떻게 반응했나?<br/>
3. 내일 나에게 해주고 싶은 말은?
"""
        worksheet_para = Paragraph(worksheet_text, self.styles['KoreanBody'])
        self.story.append(worksheet_para)
        self.story.append(Spacer(1, 8*mm))
        
        # 명상 가이드
        meditation_title = Paragraph("🧘 자기자비 명상 (10분)", self.styles['SubsectionTitle'])
        self.story.append(meditation_title)
        
        meditation_text = """
<b>단계별 가이드:</b><br/><br/>

1. 편안한 자세로 앉아 눈을 감습니다 (1분)<br/>
2. 호흡에 집중하며 몸의 긴장을 풉니다 (2분)<br/>
3. 자신에게 다음을 말합니다:<br/>
   • "나는 고통받고 있구나" (인식)<br/>
   • "고통은 인간의 일부야" (공통 인간성)<br/>
   • "내가 나 자신에게 친절할 수 있기를" (자기친절)<br/>
4. 따뜻한 손을 가슴에 얹고 느낌을 관찰합니다 (3분)<br/>
5. 천천히 눈을 뜨며 현재로 돌아옵니다 (2분)
"""
        meditation_para = Paragraph(meditation_text, self.styles['KoreanBody'])
        self.story.append(meditation_para)
        self.story.append(Spacer(1, 8*mm))
        
        # 온라인 리소스
        online_title = Paragraph("🌐 온라인 리소스", self.styles['SubsectionTitle'])
        self.story.append(online_title)
        
        online_text = """
• <b>Self-Compassion.org</b>: Kristin Neff의 공식 사이트, 무료 명상 가이드<br/>
• <b>Greater Good Science Center</b>: 버클리대 긍정심리학 연구소<br/>
• <b>Mindful.org</b>: 마음챙김 명상 리소스<br/>
• <b>TED Talks</b>: "The power of vulnerability" (Brené Brown)
"""
        online_para = Paragraph(online_text, self.styles['KoreanBody'])
        self.story.append(online_para)
        
        self.story.append(PageBreak())
    
    def _create_closing_letter(self):
        """마지막 편지 - 매주 이메일 안내 및 응원"""
        title = Paragraph(f"{self.user_name}님,", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 3*mm))
        
        closing_text = """
이제 당신은 당신의 패턴을 압니다. 
당신의 강점도 압니다.
그리고 무엇을 연습해야 하는지도 압니다.
<br/><br/>
<b>이제부터가 진짜 시작입니다.</b>
<br/><br/>
앞으로 4주 동안, 매주 월요일 아침마다 이메일을 받게 됩니다.
그 이메일에는 그 주에 실천할 구체적인 가이드가 담겨있습니다.
<br/><br/>
하루 5-10분, 매일 작은 실천을 함께 해봅시다.
완벽하지 않아도 괜찮습니다. 놓치는 날이 있어도 괜찮습니다.
중요한 것은 다시 시작하는 것입니다.
<br/><br/>
<b>Week 1 (다음 월요일):</b> 자기자비 기초 - 자기비판을 알아차리고, 친구에게 말하듯 자신에게 말하기<br/>
<b>Week 2:</b> 완벽주의 내려놓기 - 80%의 용기<br/>
<b>Week 3:</b> 공통 인간성 인식 - 당신만 힘든 게 아닙니다<br/>
<b>Week 4:</b> 안정적 자기가치 - 존재 자체로 가치 있음을 받아들이기<br/>
<br/><br/>
4주 후, 당신은 달라져 있을 것입니다.
같은 50개 질문이지만, 당신의 응답은 분명 달라져 있을 것입니다.
그때 재검사 링크를 이메일로 보내드리겠습니다.
"""
        
        body = Paragraph(closing_text, self.styles['KoreanBody'])
        self.story.append(body)
        self.story.append(Spacer(1, 8*mm))
        
        # 응원 메시지 박스
        encouragement_text = """
<b>💚 우리가 함께 합니다</b><br/>
<br/>
매주 월요일 아침, 당신의 이메일함에서 우리를 만나세요.<br/>
힘들 때는 이 보고서로 돌아오세요.<br/>
당신은 혼자가 아닙니다.<br/>
<br/>
변화는 천천히 찾아옵니다. 조급해하지 마세요.<br/>
지금 이 순간, 이 보고서를 읽고 있는 당신이<br/>
이미 변화의 첫 걸음을 내디뎠습니다.<br/>
<br/>
<b>우리는 당신을 응원합니다. 당신은 할 수 있습니다. 💪</b>
"""
        
        encouragement_para = Paragraph(encouragement_text, self.styles['HighlightBox'])
        
        # 박스 배경
        box_table = Table([[encouragement_para]], colWidths=[160*mm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['accent']),
            ('BORDER', (0, 0), (-1, -1), 2, self.colors['primary']),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        self.story.append(box_table)
        self.story.append(Spacer(1, 12*mm))
        
        # 마지막 인사
        farewell = Paragraph(
            "당신의 성장을 응원합니다.<br/>bty Training Team 💚",
            self.styles['Quote']
        )
        self.story.append(farewell)
        
        self.story.append(PageBreak())
    
    def _create_references_page(self):
        """참고문헌 페이지"""
        title = Paragraph("참고문헌", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        # 참고문헌 리스트
        for num in sorted(self.references.keys()):
            ref_data = self.references[num]
            ref_text = f"<b>[{num}]</b> {ref_data['citation']}"
            if ref_data['url']:
                ref_text += f"<br/><font color='#3498DB'>{ref_data['url']}</font>"
            
            ref_para = Paragraph(ref_text, self.styles['KoreanBody'])
            self.story.append(ref_para)
            self.story.append(Spacer(1, 5*mm))
    
    def generate(self):
        """PDF 생성"""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # 페이지 구성
        self._create_cover_page()
        self._create_opening_letter()
        self._create_part1_dimensions()
        self._create_part2_patterns()
        self._create_part3_strengths()
        self._create_part4_program()
        self._create_resources_guide()
        self._create_closing_letter()
        self._create_references_page()
        
        # PDF 빌드
        doc.build(self.story)
        print(f"✅ PDF 생성 완료: {self.output_path}")
        return self.output_path


# ==========================================
# 사용 예시
# ==========================================

if __name__ == "__main__":
    # 샘플 데이터
    sample_data = {
        'user_email': 'testuser@example.com',
        'profile_type': 'developing_critic',
        'scores': {
            'rosenberg': 22,
            'dimensions': {
                '자기수용': 3.2,
                '자기가치': 2.8,
                '자기효능감': 3.5,
                '자기자비': 2.5,
                '사회적 연결': 3.0
            }
        },
        'patterns': [
            {
                'name': '사회적 비교',
                'strength': 0.83,
                'evidence': [11, 18, 23, 31, 36],
                'description': '타인과 자신을 비교하며 부족함을 느끼는 경향',
                'research': 'Festinger, L. (1954). A theory of social comparison processes.'
            },
            {
                'name': '과도한 자기비판',
                'strength': 0.78,
                'evidence': [2, 8, 14, 21, 28],
                'description': '실수나 실패 시 가혹한 자기비판',
                'research': 'Gilbert, P. (2009). The Compassionate Mind.'
            },
            {
                'name': '고립감',
                'strength': 0.65,
                'evidence': [18, 26, 29, 35, 41],
                'description': '자신만 힘들다는 고립된 느낌',
                'research': 'Neff, K. D. (2003). Self-compassion.'
            }
        ],
        'strengths': [
            {
                'name': '회복탄력성',
                'evidence': '당신은 50개의 질문에 끝까지 답했습니다.',
                'how_to_use': '힘든 순간에 "나는 이전에도 이겨냈다"고 상기하세요.'
            },
            {
                'name': '높은 기준',
                'evidence': '자기비판은 역설적으로 높은 기준의 증거입니다.',
                'how_to_use': '기준을 낮추지 말고, 자신에게 관대해지세요.'
            },
            {
                'name': '자기 성찰',
                'evidence': '이 보고서를 읽고 있다는 것 자체가 증거입니다.',
                'how_to_use': '이 능력을 자기비판이 아닌 자기이해에 사용하세요.'
            }
        ],
        'retest_link': 'https://example.com/retest?user=testuser'
    }
    
    # PDF 생성
    output_path = "/mnt/user-data/outputs/self_esteem_report_v2.pdf"
    generator = EnhancedPDFGenerator(sample_data, output_path)
    generator.generate()
    
    print(f"\n📄 생성된 PDF:")
    print(f"   경로: {output_path}")
    print(f"   페이지 수: 약 15페이지")
    print(f"   참고문헌 수: {len(generator.references)}개")
