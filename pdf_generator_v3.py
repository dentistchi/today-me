"""
PDF 보고서 생성 시스템 v3.0 - 사용자 피드백 반영
================================================
수정사항:
1. 텍스트 색상 진하게 (가독성 향상)
2. 5차원 설명을 한 페이지에 모두 표시
3. 각 섹션 제목이 새 페이지에서 시작 (PageBreak 전 추가)
4. 동료 비교 데이터 제거 (나이 정보 없음)
5. 온라인 리소스에 실제 클릭 가능한 링크 추가
6. 재검사 링크 박스 배경색 변경 (가독성 향상)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image as RLImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import io
from typing import Dict, List
from datetime import datetime


class ProfessionalPDFGenerator:
    """전문적이고 가독성 높은 PDF 생성기"""
    
    # 프로파일별 색상 테마 (더 진하고 전문적)
    PROFILE_COLORS = {
        "vulnerable": {
            "primary": colors.HexColor('#C0392B'),      # 진한 빨강
            "secondary": colors.HexColor('#E67E22'),    # 진한 주황
            "accent": colors.HexColor('#FEF5E7'),       # 밝은 크림
            "link_bg": colors.HexColor('#FADBD8')       # 링크 배경
        },
        "developing_critic": {
            "primary": colors.HexColor('#2874A6'),      # 진한 파랑
            "secondary": colors.HexColor('#8E44AD'),    # 진한 보라
            "accent": colors.HexColor('#EBF5FB'),       # 밝은 파랑
            "link_bg": colors.HexColor('#D6EAF8')       # 링크 배경
        },
        "developing_balanced": {
            "primary": colors.HexColor('#117A65'),      # 진한 청록
            "secondary": colors.HexColor('#138D75'),    
            "accent": colors.HexColor('#E8F8F5'),       
            "link_bg": colors.HexColor('#A9DFBF')       
        },
        "compassionate_grower": {
            "primary": colors.HexColor('#1E8449'),      # 진한 초록
            "secondary": colors.HexColor('#27AE60'),    
            "accent": colors.HexColor('#EAFAF1'),       
            "link_bg": colors.HexColor('#A9DFBF')       
        },
        "stable_rigid": {
            "primary": colors.HexColor('#5D6D7E'),      # 진한 회색
            "secondary": colors.HexColor('#34495E'),    
            "accent": colors.HexColor('#F8F9F9'),       
            "link_bg": colors.HexColor('#D5D8DC')       
        },
        "thriving": {
            "primary": colors.HexColor('#D68910'),      # 진한 금색
            "secondary": colors.HexColor('#CA6F1E'),    
            "accent": colors.HexColor('#FEF9E7'),       
            "link_bg": colors.HexColor('#FAD7A0')       
        }
    }
    
    def __init__(self, report_data: Dict, output_path: str):
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
        self.references = {}
        
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        try:
            pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
            pdfmetrics.registerFont(TTFont('NanumGothicBold', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'))
            self.korean_font = 'NanumGothic'
            self.korean_font_bold = 'NanumGothicBold'
        except:
            print("⚠️ 한글 폰트를 찾을 수 없습니다.")
            self.korean_font = 'Helvetica'
            self.korean_font_bold = 'Helvetica-Bold'
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정 (진한 색상, 전문적)"""
        
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
            textColor=colors.HexColor('#34495E'),  # 더 진하게
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
        
        # 본문 (진한 색상)
        self.styles.add(ParagraphStyle(
            name='KoreanBody',
            fontName=self.korean_font,
            fontSize=11,
            leading=18,
            textColor=colors.HexColor('#212F3C'),  # 거의 검은색에 가깝게
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # 인용구
        self.styles.add(ParagraphStyle(
            name='Quote',
            fontName=self.korean_font,
            fontSize=13,
            leading=20,
            textColor=colors.HexColor('#566573'),  # 진한 회색
            alignment=TA_CENTER,
            spaceAfter=15,
            spaceBefore=15,
            leftIndent=30,
            rightIndent=30
        ))
        
        # 리스트 항목 (진한 색상)
        self.styles.add(ParagraphStyle(
            name='ListItem',
            fontName=self.korean_font,
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#212F3C'),  # 진하게
            alignment=TA_LEFT,
            leftIndent=20,
            spaceAfter=8
        ))
        
        # 링크 스타일 (클릭 가능)
        self.styles.add(ParagraphStyle(
            name='Hyperlink',
            fontName=self.korean_font,
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#2874A6'),  # 파란색
            alignment=TA_LEFT,
            leftIndent=20,
            spaceAfter=8
        ))
        
        # 재검사 링크 박스 (진한 배경)
        self.styles.add(ParagraphStyle(
            name='RetestLink',
            fontName=self.korean_font_bold,
            fontSize=13,
            leading=20,
            textColor=colors.HexColor('#FFFFFF'),  # 흰색 텍스트
            alignment=TA_CENTER,
            spaceAfter=10,
            spaceBefore=10
        ))
    
    def add_reference(self, citation: str, url: str = "") -> int:
        """참고문헌 추가"""
        self.reference_counter += 1
        self.references[self.reference_counter] = {
            'citation': citation,
            'url': url
        }
        return self.reference_counter
    
    def _create_radar_chart(self, dimensions: Dict[str, float]) -> io.BytesIO:
        """5차원 레이더 차트 생성 (진한 색상)"""
        categories = list(dimensions.keys())
        values = list(dimensions.values())
        
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
        
        # 진한 색상으로 플롯
        color_hex = self.colors['primary'].hexval()[2:]  # '0x' 제거
        color_hex = '#' + color_hex
        
        ax.plot(angles, values, 'o-', linewidth=3, color=color_hex, label='현재')
        ax.fill(angles, values, alpha=0.3, color=color_hex)
        
        # 축 설정
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, weight='bold')
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.7, linewidth=1.5)
        
        ax.set_facecolor('#FAFAFA')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def _create_cover_page(self):
        """표지"""
        self.story.append(Spacer(1, 80*mm))
        
        title = Paragraph("자존감 심층 분석 보고서", self.styles['CoverTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 10*mm))
        
        subtitle = Paragraph(f"{self.user_name}님을 위한 맞춤 리포트", self.styles['CoverSubtitle'])
        self.story.append(subtitle)
        self.story.append(Spacer(1, 5*mm))
        
        date_text = datetime.now().strftime("%Y년 %m월 %d일")
        date_para = Paragraph(date_text, self.styles['CoverSubtitle'])
        self.story.append(date_para)
        
        self.story.append(Spacer(1, 60*mm))
        footer_style = ParagraphStyle(
            name='CoverFooter',
            fontName=self.korean_font,
            fontSize=10,
            textColor=colors.HexColor('#566573'),  # 진하게
            alignment=TA_CENTER
        )
        footer = Paragraph("이 보고서는 50개 질문 분석을 바탕으로 생성되었습니다.", footer_style)
        self.story.append(footer)
        
        self.story.append(PageBreak())
    
    def _create_opening_letter(self):
        """오프닝 레터"""
        score = self.data['scores']['rosenberg']
        
        title = Paragraph("친애하는 " + self.user_name + "님께,", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        opening_text = f"""
당신의 Rosenberg 자존감 척도는 40점 만점 중 <b>{score}점</b>입니다. 
숫자는 평균이지만, 당신의 내면 이야기는 그보다 훨씬 복잡합니다.
<br/><br/>
이 보고서는 당신이 스스로에게 어떻게 말하는지, 어떤 패턴이 자존감을 흔드는지, 
그리고 당신 안에 이미 존재하는 강점은 무엇인지를 보여줍니다.
<br/><br/>
이 보고서를 통해, 우리는 함께 당신의 자존감 지도를 그릴 것입니다.
"""
        
        body = Paragraph(opening_text, self.styles['KoreanBody'])
        self.story.append(body)
        self.story.append(Spacer(1, 10*mm))
        
        quote_text = "완벽하지 않은 나 자체로 충분하다는 것을 배우는 여정"
        quote = Paragraph(quote_text, self.styles['Quote'])
        self.story.append(quote)
        
        self.story.append(PageBreak())
    
    def _create_part1_dimensions(self):
        """Part 1: 5차원 분석 (한 페이지에 모두)"""
        title = Paragraph("Part 1. 당신의 자존감 5차원 분석", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
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
        chart_img = RLImage(chart_buffer, width=110*mm, height=110*mm)
        self.story.append(chart_img)
        self.story.append(Spacer(1, 8*mm))
        
        # 차원별 설명 (한 페이지에 모두 표시)
        subtitle = Paragraph("각 차원의 의미", self.styles['SubsectionTitle'])
        self.story.append(subtitle)
        self.story.append(Spacer(1, 3*mm))
        
        # 컴팩트하게 표시
        for dim_name, score in dimensions.items():
            if score < 2.5:
                desc = "→ 이 영역에서 자기비판이 강하게 작동합니다."
            elif score < 3.5:
                desc = "→ 발전 가능성이 큰 영역입니다."
            else:
                desc = "→ 당신의 강점 영역입니다."
            
            dim_text = f"<b>{dim_name}</b>: {score:.1f}/5.0 {desc}"
            para = Paragraph(dim_text, self.styles['ListItem'])
            self.story.append(para)
            self.story.append(Spacer(1, 2*mm))  # 간격 줄임
        
        # 참고문헌
        ref1 = self.add_reference("Rosenberg, M. (1965). Society and the adolescent self-image.")
        ref2 = self.add_reference("Neff, K. D. (2003). Self-compassion.")
        
        self.story.append(PageBreak())
    
    def _create_part2_patterns(self):
        """Part 2: 감지된 패턴"""
        # 새 페이지에서 시작
        title = Paragraph("Part 2. 당신을 흔드는 내면 패턴", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "분석 결과, 당신에게서 주요 패턴이 감지되었습니다. "
            "이 패턴들은 당신이 스스로에게 말하는 방식에 깊이 뿌리내려 있습니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 5*mm))
        
        # 강도 해석 가이드 추가
        guide_title = Paragraph(
            "<b>📊 패턴 강도 해석 가이드</b>",
            self.styles['SubsectionTitle']
        )
        self.story.append(guide_title)
        self.story.append(Spacer(1, 3*mm))
        
        guide_data = [
            ['강도 범위', '해석', '권장 조치'],
            ['0.81 - 1.0', '매우 강함 (빨강)', '즉시 개입 필요, Week 1부터 집중 실천'],
            ['0.61 - 0.80', '강함 (주황)', '핵심 과제, 4주 동안 우선 집중'],
            ['0.41 - 0.60', '중간 (노랑)', '주의 필요, 꾸준한 모니터링'],
            ['0.21 - 0.40', '약함 (초록)', '경미한 패턴, 인식만으로도 개선 가능']
        ]
        
        guide_table = Table(guide_data, colWidths=[45*mm, 60*mm, 65*mm])
        guide_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), self.korean_font_bold),
            ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        self.story.append(guide_table)
        self.story.append(Spacer(1, 8*mm))
        
        patterns = self.data.get('patterns', [])
        
        if len(patterns) == 0:
            # 패턴 없음 메시지
            no_pattern = Paragraph(
                "<b>좋은 소식:</b> 자존감을 심각하게 저해하는 패턴은 감지되지 않았습니다. "
                "당신의 자기 대화는 비교적 건강한 상태입니다.",
                self.styles['KoreanBody']
            )
            self.story.append(no_pattern)
        else:
            for i, pattern in enumerate(patterns[:3], 1):
                pattern_title = Paragraph(
                    f"패턴 {i}: {pattern['name']} (강도: {pattern['strength']:.2f})",
                    self.styles['SubsectionTitle']
                )
                self.story.append(pattern_title)
                
                desc = Paragraph(pattern['description'], self.styles['KoreanBody'])
                self.story.append(desc)
                self.story.append(Spacer(1, 3*mm))
                
                evidence_text = f"<b>증거 질문:</b> {', '.join(map(str, pattern['evidence']))}"
                evidence = Paragraph(evidence_text, self.styles['ListItem'])
                self.story.append(evidence)
                self.story.append(Spacer(1, 3*mm))
                
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
        
        strengths = self.data.get('strengths', [])
        
        for i, strength in enumerate(strengths, 1):
            strength_title = Paragraph(
                f"강점 {i}: {strength['name']}",
                self.styles['SubsectionTitle']
            )
            self.story.append(strength_title)
            
            evidence_text = f"<b>증거:</b><br/>{strength['evidence']}"
            evidence = Paragraph(evidence_text, self.styles['KoreanBody'])
            self.story.append(evidence)
            self.story.append(Spacer(1, 3*mm))
            
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
            # Week 4만 새 페이지에서 시작
            if week_data['week'] == 4:
                self.story.append(PageBreak())
            
            week_title = Paragraph(
                f"<b>Week {week_data['week']}: {week_data['title']}</b>",
                self.styles['SubsectionTitle']
            )
            self.story.append(week_title)
            
            goal_text = f"<b>목표:</b> {week_data['goal']}"
            goal = Paragraph(goal_text, self.styles['KoreanBody'])
            self.story.append(goal)
            self.story.append(Spacer(1, 3*mm))
            
            practices_text = "<b>핵심 실천:</b><br/>" + "<br/>".join([f"• {p}" for p in week_data['practices']])
            practices = Paragraph(practices_text, self.styles['KoreanBody'])
            self.story.append(practices)
            self.story.append(Spacer(1, 6*mm))
        
        ref3 = self.add_reference("Neff, K. D., & Germer, C. K. (2013). Mindful self-compassion program.")
        
        self.story.append(PageBreak())
    
    def _create_meditation_guide(self):
        """자기자비 명상 가이드 (새 페이지 시작)"""
        # 새 페이지 시작
        title = Paragraph("자기자비 명상 (10분)", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "하루 10분, 자기자비 명상은 자존감을 높이는 가장 효과적인 방법 중 하나입니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        steps = [
            "1. 편안한 자세로 앉아 눈을 감습니다",
            "2. 심호흡을 3번 합니다",
            "3. 최근 힘들었던 순간을 떠올립니다",
            "4. 가슴에 손을 얹고 말합니다:",
            "   '이것은 힘든 순간이다'",
            "   '많은 사람들이 이런 어려움을 겪는다'",
            "   '나는 나에게 친절할 수 있다'",
            "5. 이 문구를 5분간 반복합니다",
            "6. 천천히 눈을 뜨고 마무리합니다"
        ]
        
        for step in steps:
            para = Paragraph(step, self.styles['ListItem'])
            self.story.append(para)
            self.story.append(Spacer(1, 2*mm))
        
        self.story.append(PageBreak())
    
    def _create_online_resources(self):
        """온라인 리소스 (클릭 가능한 링크)"""
        title = Paragraph("온라인 리소스", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        intro = Paragraph(
            "추가 학습을 위한 권장 리소스입니다. 링크를 클릭하여 바로 이동할 수 있습니다.",
            self.styles['KoreanBody']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 8*mm))
        
        # 클릭 가능한 링크 리스트
        resources = [
            {
                'title': 'Self-Compassion 공식 사이트',
                'url': 'https://self-compassion.org',
                'desc': 'Kristin Neff 박사의 자기자비 연구 및 실천 가이드'
            },
            {
                'title': 'Mindful Self-Compassion 프로그램',
                'url': 'https://centerformsc.org',
                'desc': '8주 온라인 자기자비 훈련 프로그램'
            },
            {
                'title': '자존감 향상을 위한 TED 강연',
                'url': 'https://www.ted.com/talks',
                'desc': '추천: Guy Winch "Why we all need to practice emotional first aid"'
            },
            {
                'title': 'Headspace 명상 앱',
                'url': 'https://www.headspace.com',
                'desc': '초보자를 위한 가이드 명상 (한국어 지원)'
            }
        ]
        
        for resource in resources:
            # 제목 + 링크
            title_text = f"<b>{resource['title']}</b>"
            title_para = Paragraph(title_text, self.styles['SubsectionTitle'])
            self.story.append(title_para)
            
            # 클릭 가능한 링크
            link_text = f"<link href='{resource['url']}' color='#2874A6'>{resource['url']}</link>"
            link_para = Paragraph(link_text, self.styles['Hyperlink'])
            self.story.append(link_para)
            self.story.append(Spacer(1, 2*mm))
            
            # 설명
            desc_para = Paragraph(resource['desc'], self.styles['ListItem'])
            self.story.append(desc_para)
            self.story.append(Spacer(1, 6*mm))
        
        self.story.append(PageBreak())
    
    def _create_closing_letter(self):
        """마지막 편지"""
        title = Paragraph(f"{self.user_name}님,", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        closing_text = """
이 보고서를 함께 걸어왔습니다.
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
        
        # 재검사 링크 (진한 배경색으로 가독성 향상)
        retest_link = self.data.get('retest_link', 'https://example.com/retest')
        
        retest_box_text = f"""
<b>🔗 재검사 링크</b><br/>
<br/>
4주 후 아래 링크를 클릭하여 재검사를 진행하세요.<br/>
Before & After 비교 리포트를 받게 됩니다.<br/>
<br/>
<link href='{retest_link}' color='#FFFFFF'><u>{retest_link}</u></link>
"""
        
        retest_para = Paragraph(retest_box_text, self.styles['RetestLink'])
        
        # 진한 배경색 박스
        box_table = Table([[retest_para]], colWidths=[160*mm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['primary']),  # 진한 배경
            ('BORDER', (0, 0), (-1, -1), 3, self.colors['secondary']),  # 진한 테두리
            ('PADDING', (0, 0), (-1, -1), 15),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        self.story.append(box_table)
        self.story.append(Spacer(1, 15*mm))
        
        farewell = Paragraph(
            "당신의 성장을 응원합니다.<br/>자존감 성장 프로그램 팀",
            self.styles['Quote']
        )
        self.story.append(farewell)
        
        self.story.append(PageBreak())
    
    def _create_references_page(self):
        """참고문헌"""
        title = Paragraph("참고문헌", self.styles['SectionTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        for num in sorted(self.references.keys()):
            ref_data = self.references[num]
            ref_text = f"<b>[{num}]</b> {ref_data['citation']}"
            if ref_data['url']:
                ref_text += f"<br/><link href='{ref_data['url']}' color='#2874A6'>{ref_data['url']}</link>"
            
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
        self._create_meditation_guide()        # 새 페이지 시작
        self._create_online_resources()        # 클릭 가능한 링크
        self._create_closing_letter()
        self._create_references_page()
        
        # PDF 빌드
        doc.build(self.story)
        print(f"✅ PDF 생성 완료: {self.output_path}")
        return self.output_path


# 사용 예시
if __name__ == "__main__":
    sample_data = {
        'user_email': 'improved@example.com',
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
                'evidence': [11, 18, 23],
                'description': '타인과 자신을 비교하며 부족함을 느끼는 경향',
                'research': 'Festinger, L. (1954). A theory of social comparison.'
            }
        ],
        'strengths': [
            {'name': '회복탄력성', 'evidence': '50개 질문 완료', 'how_to_use': '힘들 때 상기'},
            {'name': '높은 기준', 'evidence': '자기비판의 역설', 'how_to_use': '관대해지기'},
            {'name': '자기 성찰', 'evidence': '보고서 읽기', 'how_to_use': '자기이해에 활용'}
        ],
        'retest_link': 'https://example.com/retest?user=improved'
    }
    
    output_path = "/home/user/webapp/outputs/report_improved_v3.pdf"
    generator = ProfessionalPDFGenerator(sample_data, output_path)
    generator.generate()
    
    print(f"\n✅ 개선된 PDF 생성 완료!")
    print(f"   경로: {output_path}")
    print(f"\n📝 개선 사항:")
    print(f"   1. 텍스트 색상 진하게 (#212F3C)")
    print(f"   2. 5차원 설명 한 페이지에 모두 표시")
    print(f"   3. 명상/리소스 섹션 새 페이지 시작")
    print(f"   4. 온라인 리소스 클릭 가능한 링크")
    print(f"   5. 재검사 링크 진한 배경 (가독성 향상)")
    print(f"   6. 동료 비교 데이터 제거")
