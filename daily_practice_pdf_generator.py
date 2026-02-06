#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Practice Guide PDF Generator
28일 매일 실천 가이드 PDF 생성기
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


class DailyPracticePDFGenerator:
    """28일 매일 실천 가이드 PDF 생성기"""
    
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
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Day 제목 스타일
        self.styles.add(ParagraphStyle(
            name='DayTitle',
            parent=self.styles['Heading2'],
            fontName='NanumGothicBold',
            fontSize=18,
            textColor=colors.HexColor('#3498DB'),
            spaceBefore=20,
            spaceAfter=15,
            alignment=TA_LEFT
        ))
        
        # 섹션 제목 스타일
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontName='NanumGothicBold',
            fontSize=14,
            textColor=colors.HexColor('#2C3E50'),
            spaceBefore=12,
            spaceAfter=8
        ))
        
        # 본문 스타일 (진한 텍스트)
        self.styles.add(ParagraphStyle(
            name='KoreanBody',
            parent=self.styles['BodyText'],
            fontName='NanumGothic',
            fontSize=11,
            textColor=colors.HexColor('#212F3C'),  # 진한 텍스트
            leading=18,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        # 아침 의식 스타일
        self.styles.add(ParagraphStyle(
            name='MorningRitual',
            parent=self.styles['BodyText'],
            fontName='NanumGothicBold',
            fontSize=12,
            textColor=colors.HexColor('#F39C12'),
            leading=18,
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=15,
            borderPadding=10,
            backColor=colors.HexColor('#FEF5E7')
        ))
        
        # 작은 승리 스타일
        self.styles.add(ParagraphStyle(
            name='MicroWin',
            parent=self.styles['BodyText'],
            fontName='NanumGothicBold',
            fontSize=11,
            textColor=colors.HexColor('#27AE60'),
            leading=16,
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=10,
            borderPadding=8,
            backColor=colors.HexColor('#E8F8F5')
        ))
        
        # 축하 메시지 스타일
        self.styles.add(ParagraphStyle(
            name='Celebration',
            parent=self.styles['BodyText'],
            fontName='NanumGothicBold',
            fontSize=13,
            textColor=colors.HexColor('#8E44AD'),
            leading=20,
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=20,
            borderPadding=15,
            backColor=colors.HexColor('#F4ECF7')
        ))
        
    def generate_daily_practice_pdf(
        self,
        user_name: str,
        all_days: List[Dict],
        start_date: datetime,
        retest_link: str = "https://example.com/retest",
        output_filename: str = None
    ) -> str:
        """
        28일 실천 가이드 PDF 생성
        
        Args:
            user_name: 사용자 이름
            all_days: 28일 가이드 데이터
            start_date: 시작 날짜
            retest_link: 재검사 링크
            output_filename: 출력 파일명 (None이면 자동 생성)
            
        Returns:
            생성된 PDF 파일 경로
        """
        if output_filename is None:
            output_filename = f"daily_practice_guide_{user_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
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
        story.extend(self._create_cover_page(user_name, start_date))
        story.append(PageBreak())
        
        # 각 Day별 가이드 생성
        for day_data in all_days:
            # Day 28의 재검사 링크 처리
            if day_data.get('day') == 28 and 'celebration' in day_data:
                # celebration 텍스트에서 {RETEST_LINK} 치환
                day_data['celebration'] = day_data['celebration'].replace('{RETEST_LINK}', retest_link)
                if 'retest_link' in day_data:
                    day_data['retest_link'] = retest_link
            
            story.extend(self._create_day_page(day_data, start_date))
            story.append(PageBreak())
        
        # 마무리 페이지
        story.extend(self._create_closing_page(user_name))
        
        # PDF 빌드
        doc.build(story)
        
        return output_path
    
    def _create_cover_page(self, user_name: str, start_date: datetime) -> List:
        """표지 페이지 생성"""
        elements = []
        
        elements.append(Spacer(1, 3*cm))
        
        # 메인 제목
        title = Paragraph(
            "🌱 매일매일 실천 가이드 🌱",
            self.styles['KoreanTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # 부제
        subtitle = Paragraph(
            "28일 자기자비 여정",
            self.styles['Heading2']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 2*cm))
        
        # 사용자 정보
        info_text = f"""
        <para alignment="center">
        <b>참여자:</b> {user_name}<br/>
        <b>시작일:</b> {start_date.strftime('%Y년 %m월 %d일')}<br/>
        <b>완료 예정일:</b> {(start_date + timedelta(days=27)).strftime('%Y년 %m월 %d일')}
        </para>
        """
        info = Paragraph(info_text, self.styles['KoreanBody'])
        elements.append(info)
        elements.append(Spacer(1, 2*cm))
        
        # 인사말
        welcome_text = """
        <para alignment="center">
        <b>환영합니다!</b><br/><br/>
        28일 동안 매일 작은 실천을 통해<br/>
        자기자비를 배우는 여정에 함께합니다.<br/><br/>
        완벽하지 않아도 괜찮습니다.<br/>
        하루를 놓쳐도 다시 시작하면 됩니다.<br/><br/>
        중요한 것은 방향입니다.<br/>
        당신은 이미 첫 걸음을 내디뎠습니다.
        </para>
        """
        welcome = Paragraph(welcome_text, self.styles['KoreanBody'])
        elements.append(welcome)
        
        return elements
    
    def _create_day_page(self, day_data: Dict, start_date: datetime) -> List:
        """개별 Day 페이지 생성"""
        elements = []
        
        day_num = day_data.get('day')
        week_num = day_data.get('week')
        
        # Day 제목
        title_text = f"Week {week_num} | Day {day_num}: {day_data.get('title', '')}"
        title = Paragraph(title_text, self.styles['DayTitle'])
        elements.append(title)
        
        # 날짜 표시
        target_date = start_date + timedelta(days=day_num - 1)
        date_text = f"📅 {target_date.strftime('%Y년 %m월 %d일 (%A)')}"
        date_p = Paragraph(date_text, self.styles['KoreanBody'])
        elements.append(date_p)
        elements.append(Spacer(1, 0.5*cm))
        
        # Celebration (Week 마무리)
        if 'celebration' in day_data:
            celebration_text = day_data['celebration'].replace('\n', '<br/>')
            celebration = Paragraph(celebration_text, self.styles['Celebration'])
            elements.append(celebration)
            elements.append(Spacer(1, 0.5*cm))
            
            # Day 28 재검사 링크
            if day_data.get('day') == 28 and 'retest_link' in day_data:
                retest_box = Table(
                    [[Paragraph(
                        f'🔗 <link href="{day_data["retest_link"]}" color="blue">재검사 시작하기</link>',
                        self.styles['MicroWin']
                    )]],
                    colWidths=[15*cm]
                )
                retest_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2874A6')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'NanumGothicBold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 14),
                    ('PADDING', (0, 0), (-1, -1), 15),
                    ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1A5276'))
                ]))
                elements.append(retest_box)
                elements.append(Spacer(1, 0.5*cm))
        
        # 아침 의식
        if 'morning_ritual' in day_data:
            section = Paragraph("🌅 아침 의식", self.styles['SectionTitle'])
            elements.append(section)
            
            ritual_text = day_data['morning_ritual']
            ritual = Paragraph(ritual_text, self.styles['MorningRitual'])
            elements.append(ritual)
            elements.append(Spacer(1, 0.3*cm))
        
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
            win_p = Paragraph(day_data['micro_win'], self.styles['MicroWin'])
            elements.append(win_p)
        
        return elements
    
    def _create_closing_page(self, user_name: str) -> List:
        """마무리 페이지"""
        elements = []
        
        elements.append(Spacer(1, 3*cm))
        
        title = Paragraph("🎉 축하합니다! 🎉", self.styles['KoreanTitle'])
        elements.append(title)
        elements.append(Spacer(1, 1*cm))
        
        message = f"""
        <para alignment="center">
        <b>{user_name}님,</b><br/><br/>
        28일 여정을 완주하셨습니다!<br/><br/>
        당신은 매일 작은 실천을 통해<br/>
        자기자비를 배웠습니다.<br/><br/>
        이제 이 가이드는 필요할 때마다<br/>
        다시 펼쳐볼 수 있는 당신만의 도구입니다.<br/><br/>
        자기자비는 목적지가 아닌 여정입니다.<br/>
        앞으로도 계속 당신 편이 되어주세요.<br/><br/>
        <b>당신은 충분히 가치 있습니다.</b>
        </para>
        """
        message_p = Paragraph(message, self.styles['KoreanBody'])
        elements.append(message_p)
        
        return elements


# 테스트 코드
if __name__ == "__main__":
    from daily_practice_guide_v1 import DailyPracticeGuide
    
    print("=" * 60)
    print("28일 실천 가이드 PDF 생성 테스트")
    print("=" * 60)
    
    # 샘플 데이터
    sample_results = {
        "scores": {"rosenberg": 22},
        "profile_type": "developing_critic",
        "detected_patterns": [
            {"type": "SELF_CRITICISM", "strength": 0.85},
            {"type": "PERFECTIONISM", "strength": 0.78}
        ],
        "hidden_strengths": [
            {"name": "회복탄력성", "description": "어려움 속에서도 다시 일어서는 힘"}
        ]
    }
    
    # 28일 가이드 생성
    guide = DailyPracticeGuide("테스트사용자", sample_results)
    all_days = guide.generate_all_days()
    
    print(f"✅ {len(all_days)}일 가이드 데이터 생성 완료\n")
    
    # PDF 생성
    pdf_gen = DailyPracticePDFGenerator()
    
    start_date = datetime(2026, 2, 10)  # 시작 날짜
    retest_link = "https://example.com/self-esteem/retest"
    
    output_path = pdf_gen.generate_daily_practice_pdf(
        user_name="테스트사용자",
        all_days=all_days,
        start_date=start_date,
        retest_link=retest_link,
        output_filename="daily_practice_guide_sample.pdf"
    )
    
    print(f"✅ PDF 생성 완료:")
    print(f"   📄 {output_path}")
    print(f"   📊 총 {len(all_days)}일 가이드 포함")
    print(f"   📅 시작일: {start_date.strftime('%Y-%m-%d')}")
    print(f"   📅 종료일: {(start_date + timedelta(days=27)).strftime('%Y-%m-%d')}")
    print("\n" + "=" * 60)
