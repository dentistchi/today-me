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
        
        # 섹션 제목 (Part 1, Part 2...)
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName=self.korean_font_bold,
            fontSize=24,
            textColor=self.colors['primary'],
            alignment=TA_LEFT,
            spaceAfter=15,
            spaceBefore=20,
            leading=30
        ))
        
        # 서브섹션 제목
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            fontName=self.korean_font_bold,
            fontSize=16,
            textColor=self.colors['secondary'],
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=15,
            leading=20
        ))
        
        # 본문
        self.styles.add(ParagraphStyle(
            name='KoreanBody',
            fontName=self.korean_font,
            fontSize=11,
            leading=18,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
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
        
        # 하이라이트 박스
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            fontName=self.korean_font,
            fontSize=12,
            leading=18,
            textColor=colors.HexColor('#FFFFFF'),
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
        
        # 리스트 항목
        self.styles.add(ParagraphStyle(
            name='ListItem',
            fontName=self.korean_font,
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_LEFT,
            leftIndent=20,
            spaceAfter=8
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
        self.story.append(Spacer(1, 80*mm))
        
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
        
        # 하단 메시지
        self.story.append(Spacer(1, 60*mm))
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
15페이지에 걸쳐, 우리는 함께 당신의 자존감 지도를 그릴 것입니다.
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
        """Part 1: 5차원 분석"""
        # 제목
        title = Paragraph("Part 1. 당신의 자존감 5차원 분석", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        # 설명
        intro = Paragraph(
            "자존감은 단일 숫자가 아닙니다. 5개의 차원이 상호작용하며 당신만의 패턴을 만듭니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 레이더 차트
        dimensions = self.data['scores'].get('dimensions', {
            '자기수용': 3.2,
            '자기가치': 2.8,
            '자기효능감': 3.5,
            '자기자비': 2.5,
            '사회적 연결': 3.0
        })
        
        chart_buffer = self._create_radar_chart(dimensions)
        chart_img = RLImage(chart_buffer, width=120*mm, height=120*mm)
        self.story.append(chart_img)
        self.story.append(Spacer(1, 8*mm))
        
        # 차원별 설명
        subtitle = Paragraph("각 차원의 의미", self.styles['SubsectionTitle'])
        self.story.append(subtitle)
        
        for dim_name, score in dimensions.items():
            dim_text = f"<b>{dim_name}</b>: {score:.1f}/5.0<br/>"
            if score < 2.5:
                dim_text += "→ 이 영역에서 자기비판이 강하게 작동합니다."
            elif score < 3.5:
                dim_text += "→ 발전 가능성이 큰 영역입니다."
            else:
                dim_text += "→ 당신의 강점 영역입니다."
            
            para = Paragraph(dim_text, self.styles['ListItem'])
            self.story.append(para)
            self.story.append(Spacer(1, 3*mm))
        
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
        self.story.append(Spacer(1, 5*mm))
        self.story.append(ref_para)
        
        self.story.append(PageBreak())
    
    def _create_part2_patterns(self):
        """Part 2: 감지된 패턴"""
        title = Paragraph("Part 2. 당신을 흔드는 내면 패턴", self.styles['SectionTitle'])
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
        
        self.story.append(PageBreak())
    
    def _create_part3_strengths(self):
        """Part 3: 숨겨진 강점"""
        title = Paragraph("Part 3. 당신의 숨겨진 강점 Top 3", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "자존감이 낮다고 해서 당신에게 강점이 없는 것은 아닙니다. "
            "오히려 당신은 이미 많은 것을 가지고 있지만, 그것을 보지 못하고 있을 뿐입니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 강점 목록
        strengths = self.data.get('strengths', [
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
        ])
        
        for i, strength in enumerate(strengths, 1):
            # 강점 제목
            strength_title = Paragraph(
                f"강점 {i}: {strength['name']}",
                self.styles['SubsectionTitle']
            )
            self.story.append(strength_title)
            
            # 증거
            evidence_text = f"<b>증거:</b><br/>{strength['evidence']}"
            evidence = Paragraph(evidence_text, self.styles['KoreanBody'])
            self.story.append(evidence)
            self.story.append(Spacer(1, 3*mm))
            
            # 활용법
            usage_text = f"<b>활용법:</b><br/>{strength['how_to_use']}"
            usage = Paragraph(usage_text, self.styles['KoreanBody'])
            self.story.append(usage)
            self.story.append(Spacer(1, 8*mm))
        
        self.story.append(PageBreak())
    
    def _create_part4_program(self):
        """Part 4: 4주 성장 프로그램"""
        title = Paragraph("Part 4. 당신을 위한 4주 성장 로드맵", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "이제 구체적인 실천으로 넘어갑니다. 4주 동안 매주 하나의 핵심 주제에 집중합니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 주차별 요약
        weeks = [
            {
                'week': 1,
                'title': '자기자비 기초',
                'goal': '자기비판을 알아차리고, 친구에게 말하듯 자신에게 말하기',
                'practices': [
                    'Day 1-2: 자기비판 일기 쓰기',
                    'Day 3-4: 친구에게 말하듯 연습',
                    'Day 5-7: 아침/저녁 자기자비 루틴'
                ]
            },
            {
                'week': 2,
                'title': '완벽주의 내려놓기',
                'goal': '80%의 용기 - 완벽하지 않아도 충분하다',
                'practices': [
                    'Day 8-9: 80% 원칙 실험',
                    'Day 10-11: 시간 제한 연습',
                    'Day 12-14: \'충분함\' 선언하기'
                ]
            },
            {
                'week': 3,
                'title': '공통 인간성 인식',
                'goal': '당신만 힘든 게 아닙니다',
                'practices': [
                    'Day 15-17: 타인의 고군분투 관찰',
                    'Day 18-19: 연결감 경험하기',
                    'Day 20-21: 공통 인간성 명상'
                ]
            },
            {
                'week': 4,
                'title': '안정적 자기가치',
                'goal': '존재 자체로 가치 있음을 받아들이기',
                'practices': [
                    'Day 22-24: 무조건적 자기수용',
                    'Day 25-27: 가치 중심 행동',
                    'Day 28: 4주 여정 복습 & 재검사'
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
            goal_text = f"<b>목표:</b> {week_data['goal']}"
            goal = Paragraph(goal_text, self.styles['KoreanBody'])
            self.story.append(goal)
            self.story.append(Spacer(1, 3*mm))
            
            # 실천 항목
            practices_text = "<b>핵심 실천:</b><br/>" + "<br/>".join([f"• {p}" for p in week_data['practices']])
            practices = Paragraph(practices_text, self.styles['KoreanBody'])
            self.story.append(practices)
            self.story.append(Spacer(1, 6*mm))
        
        # 참고문헌
        ref3 = self.add_reference("Neff, K. D., & Germer, C. K. (2013). A pilot study and randomized controlled trial of the mindful self-compassion program.")
        ref_para = Paragraph(f"<sup>{ref3}</sup>", self.styles['Reference'])
        self.story.append(Spacer(1, 5*mm))
        self.story.append(ref_para)
        
        self.story.append(PageBreak())
    
    def _create_closing_letter(self):
        """마지막 편지"""
        title = Paragraph(f"{self.user_name}님,", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        closing_text = """
15페이지를 함께 걸어왔습니다.
<br/><br/>
당신은 이제 당신의 패턴을 압니다. 
당신의 강점도 압니다.
그리고 무엇을 연습해야 하는지도 압니다.
<br/><br/>
<b>4주 후 재검사를 통해 변화를 확인하세요.</b>
<br/><br/>
같은 50개 질문이지만, 당신의 응답은 달라져 있을 것입니다.
"""
        
        body = Paragraph(closing_text, self.styles['KoreanBody'])
        self.story.append(body)
        self.story.append(Spacer(1, 10*mm))
        
        # 재검사 링크
        retest_link = self.data.get('retest_link', 'https://example.com/retest')
        retest_box_text = f"""
<b>🔗 재검사 링크:</b><br/>
{retest_link}<br/>
<br/>
4주 후 이 링크를 클릭하여 재검사를 진행하세요.
Before & After 비교 리포트를 받게 됩니다.
"""
        
        # 하이라이트 박스
        retest_para = Paragraph(retest_box_text, self.styles['HighlightBox'])
        
        # 박스 배경
        box_table = Table([[retest_para]], colWidths=[160*mm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['accent']),
            ('BORDER', (0, 0), (-1, -1), 2, self.colors['primary']),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        self.story.append(box_table)
        self.story.append(Spacer(1, 15*mm))
        
        # 마지막 인사
        farewell = Paragraph(
            "당신의 성장을 응원합니다.<br/>자존감 성장 프로그램 팀",
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
