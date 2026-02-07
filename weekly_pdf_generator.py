#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Practice Guide PDF Generator
주간 실천 가이드 PDF 생성기 (Week 1~4별로 7일 치 플랜)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime, timedelta
from typing import List, Dict
import os

# 한글 폰트 등록
try:
    pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
    pdfmetrics.registerFont(TTFont('NanumGothicBold', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'))
except:
    print("Warning: NanumGothic font not found. Using default font.")


class WeeklyPDFGenerator:
    """주간 실천 가이드 PDF 생성기"""
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Args:
            output_dir: PDF 출력 디렉토리
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 스타일 초기화
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # 주차별 마인드셋
        self.week_mindsets = {
            1: {
                "theme": "자기자비 기초 - 자기비판 알아차리기",
                "mindset": """
                <b>이번 주의 핵심 마인드셋:</b><br/><br/>
                
                "나는 나를 비판하는 목소리를 알아차릴 수 있다."<br/><br/>
                
                자기비판은 우리를 더 나아지게 만든다고 믿지만, 실제로는 우리를 위축시킵니다. 
                이번 주는 자기비판적인 생각을 알아차리고, 그것이 '사실'이 아닌 '생각'임을 배웁니다.<br/><br/>
                
                <b>Week 1의 목표:</b><br/>
                • 자기비판적 사고 패턴 인식하기<br/>
                • 내면의 비판자(Inner Critic)와 자기자비적 자아 구별하기<br/>
                • 실수를 '학습의 기회'로 재해석하기<br/><br/>
                
                <b>이번 주를 시작하며:</b><br/>
                완벽하지 않아도 괜찮습니다. 자기비판을 알아차리는 것만으로도 이미 큰 변화의 시작입니다.
                """,
                "color": "#3498DB"
            },
            2: {
                "theme": "완벽주의 내려놓기 - 80%의 용기",
                "mindset": """
                <b>이번 주의 핵심 마인드셋:</b><br/><br/>
                
                "80%로도 충분히 가치 있다."<br/><br/>
                
                완벽주의는 우리를 보호한다고 믿지만, 실제로는 시도조차 못하게 만듭니다. 
                이번 주는 '80%의 완성도'로도 시도하는 용기를 배웁니다.<br/><br/>
                
                <b>Week 2의 목표:</b><br/>
                • 완벽주의와 건강한 성취 욕구 구별하기<br/>
                • 불완전함을 받아들이는 연습<br/>
                • '과정'에 집중하고 '결과'에 덜 집착하기<br/><br/>
                
                <b>이번 주를 시작하며:</b><br/>
                완벽하게 하려다가 시작도 못하는 것보다, 80%로 시작하고 배우는 것이 훨씬 가치 있습니다.
                """,
                "color": "#27AE60"
            },
            3: {
                "theme": "공통 인간성 인식 - 나만이 아니야",
                "mindset": """
                <b>이번 주의 핵심 마인드셋:</b><br/><br/>
                
                "힘들어하는 건 나만이 아니다."<br/><br/>
                
                우리는 혼자만 힘든 것처럼 느낍니다. 하지만 고통과 불완전함은 인간이라면 누구나 경험하는 것입니다. 
                이번 주는 '공통 인간성(Common Humanity)'을 통해 연결감을 느낍니다.<br/><br/>
                
                <b>Week 3의 목표:</b><br/>
                • 고통을 개인적 결함이 아닌 인간 경험으로 재해석하기<br/>
                • 타인과의 연결감 느끼기<br/>
                • 자신의 어려움을 정상화하기<br/><br/>
                
                <b>이번 주를 시작하며:</b><br/>
                당신이 느끼는 두려움, 불안, 부족함은 모든 인간이 공유하는 경험입니다. 혼자가 아닙니다.
                """,
                "color": "#9B59B6"
            },
            4: {
                "theme": "안정적 자기가치 - 존재 그 자체로",
                "mindset": """
                <b>이번 주의 핵심 마인드셋:</b><br/><br/>
                
                "나는 무언가를 성취해서가 아니라, 존재 그 자체로 가치 있다."<br/><br/>
                
                우리는 '무엇을 했는가'로 자신의 가치를 판단합니다. 하지만 진정한 자기가치는 
                성취와 무관하게 '존재 그 자체'에서 나옵니다. 이번 주는 조건 없는 자기가치를 배웁니다.<br/><br/>
                
                <b>Week 4의 목표:</b><br/>
                • 조건적 자기가치와 무조건적 자기가치 구별하기<br/>
                • 성취와 무관한 자기가치 느끼기<br/>
                • 존재 자체에 대한 감사 연습하기<br/><br/>
                
                <b>이번 주를 시작하며:</b><br/>
                당신은 이미 충분히 가치 있습니다. 더 증명할 필요가 없습니다. 존재 그 자체로 완전합니다.
                """,
                "color": "#E74C3C"
            }
        }
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 제목 스타일
        self.styles.add(ParagraphStyle(
            name='KoreanTitle',
            parent=self.styles['Heading1'],
            fontName='NanumGothicBold',
            fontSize=22,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            leading=28
        ))
        
        # 주차 테마 스타일
        self.styles.add(ParagraphStyle(
            name='WeekTheme',
            parent=self.styles['Heading2'],
            fontName='NanumGothicBold',
            fontSize=16,
            textColor=colors.white,
            spaceAfter=15,
            alignment=TA_CENTER,
            leading=22
        ))
        
        # Day 제목 스타일
        self.styles.add(ParagraphStyle(
            name='DayTitle',
            parent=self.styles['Heading3'],
            fontName='NanumGothicBold',
            fontSize=14,
            textColor=colors.HexColor('#3498DB'),
            spaceBefore=15,
            spaceAfter=10,
            alignment=TA_LEFT
        ))
        
        # 본문 스타일
        self.styles.add(ParagraphStyle(
            name='KoreanBody',
            parent=self.styles['BodyText'],
            fontName='NanumGothic',
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=8
        ))
        
        # 마인드셋 스타일
        self.styles.add(ParagraphStyle(
            name='Mindset',
            parent=self.styles['BodyText'],
            fontName='NanumGothic',
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            leading=18,
            alignment=TA_LEFT,
            spaceAfter=10
        ))
    
    def generate_weekly_pdf(
        self,
        user_name: str,
        week_num: int,
        week_days: List[Dict],
        start_date: datetime,
        output_filename: str = None
    ) -> str:
        """
        주간 실천 가이드 PDF 생성
        
        Args:
            user_name: 사용자 이름
            week_num: 주차 (1-4)
            week_days: 해당 주의 7일 데이터
            start_date: 시작 날짜
            output_filename: 출력 파일명 (None이면 자동 생성)
            
        Returns:
            생성된 PDF 파일 경로
        """
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"week{week_num}_guide_{user_name}_{timestamp}.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # 표지
        story.extend(self._create_cover_page(user_name, week_num, start_date))
        story.append(PageBreak())
        
        # 마인드셋 페이지
        story.extend(self._create_mindset_page(week_num))
        story.append(PageBreak())
        
        # 각 Day별 요약
        for day_data in week_days:
            story.extend(self._create_day_summary(day_data, start_date))
        
        # PDF 빌드
        doc.build(story)
        
        return output_path
    
    def _create_cover_page(self, user_name: str, week_num: int, start_date: datetime) -> List:
        """표지 페이지"""
        elements = []
        
        elements.append(Spacer(1, 3*cm))
        
        # 타이틀
        mindset_data = self.week_mindsets.get(week_num, {})
        theme = mindset_data.get('theme', f'Week {week_num}')
        
        title = Paragraph(f"Week {week_num}<br/>{theme}", self.styles['KoreanTitle'])
        elements.append(title)
        
        elements.append(Spacer(1, 1*cm))
        
        # 사용자 이름
        user_p = Paragraph(f"{user_name}님을 위한<br/>7일 실천 가이드", self.styles['KoreanBody'])
        user_p.alignment = TA_CENTER
        elements.append(user_p)
        
        elements.append(Spacer(1, 2*cm))
        
        # 날짜 범위
        end_date = start_date + timedelta(days=6)
        date_range = f"{start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%m월 %d일')}"
        date_p = Paragraph(f"<b>{date_range}</b>", self.styles['KoreanBody'])
        date_p.alignment = TA_CENTER
        elements.append(date_p)
        
        return elements
    
    def _create_mindset_page(self, week_num: int) -> List:
        """마인드셋 페이지"""
        elements = []
        
        mindset_data = self.week_mindsets.get(week_num, {})
        theme = mindset_data.get('theme', '')
        mindset_text = mindset_data.get('mindset', '')
        color = mindset_data.get('color', '#3498DB')
        
        # 테마 헤더 (색상 박스)
        theme_table = Table(
            [[Paragraph(f"Week {week_num}: {theme}", self.styles['WeekTheme'])]],
            colWidths=[15*cm]
        )
        theme_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(color)),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        elements.append(theme_table)
        elements.append(Spacer(1, 0.8*cm))
        
        # 마인드셋 내용
        mindset_p = Paragraph(mindset_text, self.styles['Mindset'])
        
        # 마인드셋 박스
        mindset_table = Table(
            [[mindset_p]],
            colWidths=[15*cm]
        )
        mindset_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('PADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(color)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        elements.append(mindset_table)
        
        return elements
    
    def _create_day_summary(self, day_data: Dict, start_date: datetime) -> List:
        """일별 요약"""
        elements = []
        
        day_num = day_data.get('day')
        
        # Day 제목
        title_text = f"Day {day_num}: {day_data.get('title', '')}"
        title = Paragraph(title_text, self.styles['DayTitle'])
        
        # 날짜
        target_date = start_date + timedelta(days=day_num - 1)
        date_text = f"📅 {target_date.strftime('%m월 %d일 (%A)')}"
        date_p = Paragraph(date_text, self.styles['KoreanBody'])
        
        # 아침 의식
        morning = ""
        if 'morning_ritual' in day_data:
            morning = f"<b>🌅 아침 의식:</b> {day_data['morning_ritual']}"
        
        # 핵심 실천
        practice = ""
        if 'core_practice' in day_data:
            practice_data = day_data['core_practice']
            practice_name = practice_data.get('name', '')
            practice_duration = practice_data.get('duration', '')
            practice = f"<b>📖 핵심 실천:</b> {practice_name} ({practice_duration})"
        
        # 작은 승리
        micro_win = ""
        if 'micro_win' in day_data:
            micro_win = f"<b>✅ 작은 승리:</b> {day_data['micro_win']}"
        
        # 모든 내용을 하나의 셀로 합치기
        content_html = f"{date_text}<br/>{morning}<br/>{practice}<br/>{micro_win}"
        content_p = Paragraph(content_html, self.styles['KoreanBody'])
        
        # Day 박스
        day_table = Table(
            [[title], [content_p]],
            colWidths=[15*cm]
        )
        day_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F8F5')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(day_table)
        elements.append(Spacer(1, 0.4*cm))
        
        return elements


# 테스트 코드
if __name__ == "__main__":
    print("Weekly PDF Generator 테스트")
    
    # 샘플 데이터 (Week 1)
    sample_week_days = [
        {
            "day": 1,
            "week": 1,
            "title": "자기비판 인식하기",
            "morning_ritual": "오늘 하루 나는 나에게 친절할 것입니다.",
            "core_practice": {
                "name": "내면의 비판자 알아차리기",
                "duration": "5분"
            },
            "micro_win": "자기비판적 생각 1개 알아차리기"
        }
        # ... 나머지 6일 데이터
    ]
    
    generator = WeeklyPDFGenerator()
    pdf_path = generator.generate_weekly_pdf(
        user_name="테스트사용자",
        week_num=1,
        week_days=sample_week_days,
        start_date=datetime.now()
    )
    
    print(f"✅ PDF 생성 완료: {pdf_path}")
