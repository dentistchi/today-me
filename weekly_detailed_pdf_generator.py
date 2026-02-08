#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Detailed Practice Guide PDF Generator
주차별 상세 실천 가이드 PDF 생성기 (각 주 7일 치 상세 내용)
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


class WeeklyDetailedPDFGenerator:
    """주차별 상세 실천 가이드 PDF 생성기 (각 주 7일 치)"""
    
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
        
        # Day 제목 스타일
        self.styles.add(ParagraphStyle(
            name='DayTitle',
            parent=self.styles['Heading2'],
            fontName='NanumGothicBold',
            fontSize=16,
            textColor=colors.HexColor('#3498DB'),
            spaceBefore=20,
            spaceAfter=12,
            alignment=TA_LEFT,
            keepWithNext=True
        ))
        
        # 섹션 제목 스타일
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontName='NanumGothicBold',
            fontSize=13,
            textColor=colors.HexColor('#2C3E50'),
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True
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
        
        # 아침 의식 스타일
        self.styles.add(ParagraphStyle(
            name='MorningRitual',
            parent=self.styles['BodyText'],
            fontName='NanumGothicBold',
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            leading=16,
            alignment=TA_LEFT,
            spaceBefore=5,
            spaceAfter=5
        ))
    
    def generate_weekly_detailed_pdf(
        self,
        user_name: str,
        week_num: int,
        week_days: List[Dict],
        start_date: datetime,
        output_filename: str = None
    ) -> str:
        """
        주차별 상세 실천 가이드 PDF 생성
        
        Args:
            user_name: 사용자 이름
            week_num: 주차 (1-4)
            week_days: 해당 주의 7일 데이터
            start_date: 시작 날짜
            output_filename: 출력 파일명
            
        Returns:
            생성된 PDF 파일 경로
        """
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"week{week_num}_detailed_{user_name}_{timestamp}.pdf"
        
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
        
        # 각 Day별 상세 가이드
        for day_data in week_days:
            story.extend(self._create_detailed_day_page(day_data, start_date))
            story.append(PageBreak())
        
        # PDF 빌드
        doc.build(story)
        
        return output_path
    
    def _create_cover_page(self, user_name: str, week_num: int, start_date: datetime) -> List:
        """표지 페이지"""
        elements = []
        
        week_themes = {
            1: "자기자비 기초\n자기비판 알아차리기",
            2: "완벽주의 내려놓기\n80%의 용기",
            3: "공통 인간성 인식\n나만이 아니야",
            4: "안정적 자기가치\n존재 그 자체로"
        }
        
        elements.append(Spacer(1, 3*cm))
        
        # 타이틀
        theme = week_themes.get(week_num, f'Week {week_num}')
        title = Paragraph(f"Week {week_num}<br/>{theme}", self.styles['KoreanTitle'])
        elements.append(title)
        
        elements.append(Spacer(1, 1*cm))
        
        # 사용자 이름
        user_p = Paragraph(f"{user_name}님을 위한<br/>7일 상세 실천 가이드", self.styles['KoreanBody'])
        user_p.alignment = TA_CENTER
        elements.append(user_p)
        
        elements.append(Spacer(1, 2*cm))
        
        # 날짜 범위
        end_date = start_date + timedelta(days=6)
        date_range = f"{start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%m월 %d일')}"
        date_p = Paragraph(f"<b>{date_range}</b>", self.styles['KoreanBody'])
        date_p.alignment = TA_CENTER
        elements.append(date_p)
        
        elements.append(Spacer(1, 3*cm))
        
        # 함께합니다 메시지
        together_table = Table(
            [[Paragraph("<b>저희가 함께합니다 💚</b><br/>매일 5-10분, 당신의 변화를 응원합니다.", 
                       self.styles['KoreanBody'])]],
            colWidths=[14*cm]
        )
        together_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F8F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#27AE60'))
        ]))
        elements.append(together_table)
        
        return elements
    
    def _create_detailed_day_page(self, day_data: Dict, start_date: datetime) -> List:
        """상세 Day 페이지"""
        elements = []
        
        day_num = day_data.get('day')
        
        # Day 제목
        title_text = f"Day {day_num}: {day_data.get('title', '')}"
        title = Paragraph(title_text, self.styles['DayTitle'])
        elements.append(title)
        
        # 날짜
        target_date = start_date + timedelta(days=day_num - 1)
        date_text = f"📅 {target_date.strftime('%Y년 %m월 %d일 (%A)')}"
        date_p = Paragraph(date_text, self.styles['KoreanBody'])
        elements.append(date_p)
        elements.append(Spacer(1, 0.5*cm))
        
        # 아침 의식 (Table로 노란색 배경)
        if 'morning_ritual' in day_data:
            section = Paragraph("🌅 아침 의식", self.styles['SectionTitle'])
            elements.append(section)
            
            ritual_text = day_data['morning_ritual']
            ritual = Paragraph(ritual_text, self.styles['MorningRitual'])
            
            ritual_table = Table(
                [[ritual]],
                colWidths=[15*cm]
            )
            ritual_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF5E7')),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F39C12')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            elements.append(ritual_table)
            elements.append(Spacer(1, 0.4*cm))
        
        # 핵심 실천
        if 'core_practice' in day_data:
            practice = day_data['core_practice']
            
            section = Paragraph("📖 핵심 실천", self.styles['SectionTitle'])
            elements.append(section)
            
            practice_name = f"<b>{practice.get('name', '')}</b> ({practice.get('duration', '')})"
            name_p = Paragraph(practice_name, self.styles['KoreanBody'])
            elements.append(name_p)
            elements.append(Spacer(1, 0.2*cm))
            
            # Steps
            if 'steps' in practice:
                for step in practice['steps']:
                    step_p = Paragraph(step, self.styles['KoreanBody'])
                    elements.append(step_p)
            
            elements.append(Spacer(1, 0.3*cm))
            
            # Why it works
            if 'why_it_works' in practice:
                why_title = Paragraph("🧠 왜 효과가 있을까?", self.styles['SectionTitle'])
                elements.append(why_title)
                why_p = Paragraph(practice['why_it_works'], self.styles['KoreanBody'])
                elements.append(why_p)
                elements.append(Spacer(1, 0.3*cm))
        
        # 예상되는 저항
        if 'expected_resistance' in day_data:
            section = Paragraph("⚠️ 예상되는 저항", self.styles['SectionTitle'])
            elements.append(section)
            resistance_p = Paragraph(day_data['expected_resistance'], self.styles['KoreanBody'])
            elements.append(resistance_p)
            elements.append(Spacer(1, 0.3*cm))
        
        # 돌파 전략
        if 'breakthrough_strategy' in day_data:
            section = Paragraph("💡 돌파 전략", self.styles['SectionTitle'])
            elements.append(section)
            strategy_p = Paragraph(day_data['breakthrough_strategy'], self.styles['KoreanBody'])
            elements.append(strategy_p)
            elements.append(Spacer(1, 0.3*cm))
        
        # 저녁 성찰
        if 'evening_reflection' in day_data:
            section = Paragraph("🌙 저녁 성찰", self.styles['SectionTitle'])
            elements.append(section)
            reflection_p = Paragraph(day_data['evening_reflection'], self.styles['KoreanBody'])
            elements.append(reflection_p)
            elements.append(Spacer(1, 0.3*cm))
        
        # 작은 승리
        if 'micro_win' in day_data:
            section = Paragraph("✅ 오늘의 작은 승리", self.styles['SectionTitle'])
            elements.append(section)
            
            win_text = day_data['micro_win']
            win_p = Paragraph(win_text, self.styles['KoreanBody'])
            
            win_table = Table(
                [[win_p]],
                colWidths=[15*cm]
            )
            win_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F8F5')),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#27AE60')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            elements.append(win_table)
        
        return elements


# 테스트 코드
if __name__ == "__main__":
    print("Weekly Detailed PDF Generator 테스트")
    
    # 샘플 데이터
    sample_days = [
        {
            "day": 1,
            "week": 1,
            "title": "자기비판 인식하기",
            "morning_ritual": "오늘 하루 나는 나에게 친절할 것입니다.",
            "core_practice": {
                "name": "내면의 비판자 알아차리기",
                "duration": "5분",
                "steps": ["1. 자기비판적 생각 관찰하기", "2. 비판 vs 현실 구분하기"],
                "why_it_works": "자기비판을 알아차리는 것이 변화의 첫 단계입니다."
            },
            "expected_resistance": "자기비판이 익숙해서 알아차리기 어려울 수 있습니다.",
            "breakthrough_strategy": "하루에 3번, 내가 나에게 한 말을 메모해보세요.",
            "evening_reflection": "오늘 나에게 어떤 말을 했나요?",
            "micro_win": "자기비판적 생각 1개 알아차리기"
        }
    ]
    
    generator = WeeklyDetailedPDFGenerator()
    pdf_path = generator.generate_weekly_detailed_pdf(
        user_name="테스트사용자",
        week_num=1,
        week_days=sample_days,
        start_date=datetime.now()
    )
    
    print(f"✅ PDF 생성 완료: {pdf_path}")
