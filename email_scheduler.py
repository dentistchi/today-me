#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Scheduling System for 28-Day Practice Guide
28일 실천 가이드 이메일 스케줄링 시스템
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from daily_practice_guide_v1 import DailyPracticeGuide
from daily_practice_pdf_generator import DailyPracticePDFGenerator
from weekly_pdf_generator import WeeklyPDFGenerator
from weekly_detailed_pdf_generator import WeeklyDetailedPDFGenerator
from real_email_sender import RealEmailSender


class EmailScheduler:
    """이메일 스케줄링 시스템"""
    
    def __init__(self):
        self.practice_guide = None
        self.pdf_generator = DailyPracticePDFGenerator()
        self.weekly_pdf_generator = WeeklyPDFGenerator()
        self.weekly_detailed_pdf_generator = WeeklyDetailedPDFGenerator()
        # 실제 이메일 발송을 위한 RealEmailSender 초기화
        self.email_sender = RealEmailSender()
        # 이메일 발송 활성화 여부 (환경 변수에서 확인)
        self.enable_email = os.getenv('ENABLE_EMAIL', 'false').lower() == 'true'
        
    def create_email_schedule(
        self,
        user_email: str,
        user_name: str,
        analysis_results: Dict,
        start_date: datetime,
        retest_link: str,
        pdf_report_path: Optional[str] = None
    ) -> Dict:
        """
        28일 가이드 이메일 스케줄 생성
        
        Args:
            user_email: 사용자 이메일
            user_name: 사용자 이름
            analysis_results: 분석 결과 데이터
            start_date: 시작 날짜
            retest_link: 재검사 링크
            pdf_report_path: PDF 보고서 경로 (선택사항)
            
        Returns:
            이메일 스케줄 데이터
        """
        # 28일 가이드 생성
        self.practice_guide = DailyPracticeGuide(user_name, analysis_results)
        all_days = self.practice_guide.generate_all_days()
        
        # 28일 가이드 PDF 생성
        daily_guide_pdf_path = self.pdf_generator.generate_daily_practice_pdf(
            user_name=user_name,
            all_days=all_days,
            start_date=start_date,
            retest_link=retest_link,
            output_filename=f"daily_practice_guide_{user_name}.pdf"
        )
        
        # 이메일 스케줄 구성
        emails = []
        
        # 1. 진단 완료 이메일 (개발자용, 즉시 발송)
        emails.append(self._create_diagnosis_complete_email(
            user_email=user_email,
            user_name=user_name,
            send_at=start_date,
            pdf_report_path=pdf_report_path,
            daily_guide_pdf_path=daily_guide_pdf_path,
            analysis_results=analysis_results
        ))
        
        # 2. Week 1 시작 리마인더 (Day 1, 시작일)
        emails.append(self._create_week_start_email(
            user_email=user_email,
            user_name=user_name,
            week_num=1,
            send_at=start_date,
            day_data=all_days[0],
            week_days=all_days[0:7],
            start_date=start_date
        ))
        
        # 3. Week 2 시작 리마인더 (Day 8)
        emails.append(self._create_week_start_email(
            user_email=user_email,
            user_name=user_name,
            week_num=2,
            send_at=start_date + timedelta(days=7),
            day_data=all_days[7],
            week_days=all_days[7:14],
            start_date=start_date + timedelta(days=7)
        ))
        
        # 4. Week 3 시작 리마인더 (Day 15)
        emails.append(self._create_week_start_email(
            user_email=user_email,
            user_name=user_name,
            week_num=3,
            send_at=start_date + timedelta(days=14),
            day_data=all_days[14],
            week_days=all_days[14:21],
            start_date=start_date + timedelta(days=14)
        ))
        
        # 5. Week 4 시작 리마인더 (Day 22)
        emails.append(self._create_week_start_email(
            user_email=user_email,
            user_name=user_name,
            week_num=4,
            send_at=start_date + timedelta(days=21),
            day_data=all_days[21],
            week_days=all_days[21:28],
            start_date=start_date + timedelta(days=21)
        ))
        
        # 6. 24시간 후 결과 리포트 (Day 2, +1일)
        emails.append(self._create_24h_report_email(
            user_email=user_email,
            user_name=user_name,
            send_at=start_date + timedelta(days=1),
            pdf_report_path=pdf_report_path
        ))
        
        # 7. Day 28 완료 & 재검사 초대 이메일
        emails.append(self._create_completion_email(
            user_email=user_email,
            user_name=user_name,
            send_at=start_date + timedelta(days=27),
            retest_link=retest_link,
            day_data=all_days[27]
        ))
        
        # 전체 스케줄 구성
        schedule = {
            "user_email": user_email,
            "user_name": user_name,
            "start_date": start_date.isoformat(),
            "total_emails": len(emails),
            "daily_guide_pdf": daily_guide_pdf_path,
            "emails": emails
        }
        
        return schedule
    
    def _create_diagnosis_complete_email(
        self,
        user_email: str,
        user_name: str,
        send_at: datetime,
        pdf_report_path: Optional[str],
        daily_guide_pdf_path: str,
        analysis_results: Optional[Dict] = None
    ) -> Dict:
        """진단 완료 이메일 (사용자용 간단 안내)"""
        
        subject = f"[자존감 진단 완료] {user_name}님, 검사가 완료되었습니다 🎉"
        
        body_html = f"""
        <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2C3E50;">안녕하세요, {user_name}님!</h2>
            
            <p>자존감 진단이 완료되었습니다. 용기 내어 자신을 돌아본 당신을 응원합니다. 🎉</p>
            
            <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
                <h3 style="color: #27AE60; margin-top: 0;">✅ 진단 완료</h3>
                <p>당신의 응답을 분석하여 맞춤형 보고서를 준비하고 있습니다.</p>
            </div>
            
            <h3 style="color: #3498DB;">📊 다음 단계</h3>
            <div style="background-color: #FEF5E7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>🕐 24시간 후</strong></p>
                <p>당신만을 위한 <strong>상세 자존감 분석 보고서</strong>를 이메일로 보내드립니다.</p>
                <ul style="margin-top: 10px;">
                    <li>5차원 자존감 점수 상세 분석</li>
                    <li>당신의 숨겨진 강점 발견</li>
                    <li>개인 맞춤형 성장 제안</li>
                    <li>PDF 보고서 첨부</li>
                </ul>
            </div>
            
            <h3 style="color: #3498DB;">🌱 내일부터 시작합니다</h3>
            <p><strong>내일</strong>부터 <strong>28일 자기자비 여정</strong>의 첫 번째 실천 가이드를 보내드립니다.</p>
            
            <div style="background-color: #F4ECF7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4 style="color: #8E44AD; margin-top: 0;">💡 28일 여정 미리보기</h4>
                <p>
                    <strong>Week 1:</strong> 자기자비 기초 (자기비판 알아차리기)<br/>
                    <strong>Week 2:</strong> 완벽주의 내려놓기<br/>
                    <strong>Week 3:</strong> 공통 인간성 인식 (나만이 아니야)<br/>
                    <strong>Week 4:</strong> 안정적 자기가치 확립
                </p>
            </div>
            
            <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
                <p style="margin: 0;"><strong>💚 응원 메시지</strong></p>
                <p style="margin: 5px 0 0 0;">완벽하지 않아도 괜찮습니다. 중요한 것은 방향입니다.<br/>
                내일부터 매주 실천 가이드를 보내드리며, 당신의 여정을 함께하겠습니다.</p>
            </div>
            
            <p style="margin-top: 30px;">
                24시간 후에 다시 만나요!<br/>
                bty Training Team 💚
            </p>
        </body>
        </html>
        """
        
        return {
            "type": "diagnosis_complete",
            "send_at": send_at.isoformat(),
            "to": user_email,  # 사용자에게 발송
            "subject": subject,
            "body_html": body_html,
            "attachments": []  # 첨부 파일 없음
        }
    
    def _create_week_start_email(
        self,
        user_email: str,
        user_name: str,
        week_num: int,
        send_at: datetime,
        day_data: Dict,
        week_days: List[Dict],
        start_date: datetime,
        daily_guide_pdf_path: Optional[str] = None  # 더 이상 사용하지 않음
    ) -> Dict:
        """주간 시작 리마인더 이메일 (마인드셋 + 주차별 PDF 2개 첨부)"""
        week_themes = {
            1: "자기자비 기초 - 자기비판 알아차리기",
            2: "완벽주의 내려놓기 - 80%의 용기",
            3: "공통 인간성 인식 - 나만이 아니야",
            4: "안정적 자기가치 - 존재 그 자체로"
        }
        
        week_mindsets = {
            1: "\"나는 나를 비판하는 목소리를 알아차릴 수 있다.\"",
            2: "\"80%로도 충분히 가치 있다.\"",
            3: "\"힘들어하는 건 나만이 아니다.\"",
            4: "\"나는 무언가를 성취해서가 아니라, 존재 그 자체로 가치 있다.\""
        }
        
        theme = week_themes.get(week_num, "")
        mindset = week_mindsets.get(week_num, "")
        subject = f"[Week {week_num} 시작] {user_name}님, {theme} 🌟"
        
        body_html = f"""
        <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2C3E50;">안녕하세요, {user_name}님! 🌟</h2>
            
            <p>Week {week_num}이 시작되었습니다. 지금까지 여정을 함께해주셔서 감사합니다.</p>
            
            <div style="background-color: #E8F8F5; padding: 20px; border-left: 4px solid #27AE60; margin: 20px 0; border-radius: 5px;">
                <h3 style="color: #27AE60; margin-top: 0;">🌟 Week {week_num} 시작!</h3>
                <p style="font-size: 15px; margin: 10px 0;"><strong>이번 주 테마:</strong> {theme}</p>
                <p style="font-size: 14px; font-style: italic; color: #555; margin: 10px 0;">
                    핵심 마인드셋: {mindset}
                </p>
            </div>
            
            <h3 style="color: #3498DB;">💚 응원 메시지</h3>
            <p>완벽하지 않아도 괜찮습니다. 중요한 것은 방향입니다.</p>
            <p>하루에 단 <strong>5-10분</strong>만 투자하면 됩니다. 매일 작은 실천이 큰 변화를 만듭니다.</p>
            <p><strong>저희가 함께합니다. 당신은 혼자가 아닙니다. 💚</strong></p>
            
            <h3 style="color: #3498DB;">📎 첨부 파일 안내</h3>
            <p>이번 주 실천을 위한 <strong>2개의 PDF 가이드</strong>를 첨부했습니다:</p>
            <div style="background-color: #E3F2FD; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <ol style="margin: 10px 0;">
                    <li style="margin-bottom: 10px;"><strong>Week {week_num} 요약 가이드</strong><br/>
                        <span style="color: #555; font-size: 13px;">→ 7일 전체 흐름을 한눈에 파악하세요 (3분 소요)</span></li>
                    <li><strong>Week {week_num} 상세 실천 가이드</strong><br/>
                        <span style="color: #555; font-size: 13px;">→ 매일 아침 해당 날짜 페이지를 확인하세요 (5-10분 소요)</span></li>
                </ol>
            </div>
            
            <h3 style="color: #3498DB;">🎯 이렇게 실천하세요</h3>
            <div style="background-color: #FEF5E7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>1단계:</strong> 첨부된 PDF를 다운로드하여 스마트폰이나 PC에 저장하세요</p>
                <p style="margin: 5px 0;"><strong>2단계:</strong> 요약 가이드로 이번 주 전체 계획을 먼저 파악하세요</p>
                <p style="margin: 5px 0;"><strong>3단계:</strong> 매일 아침, 상세 가이드에서 오늘 날짜를 찾아 읽으세요</p>
                <p style="margin: 5px 0;"><strong>4단계:</strong> 5-10분 실천하고, 내일 다시 돌아오세요</p>
            </div>
            
            <div style="background-color: #E8F8F5; padding: 15px; border-left: 4px solid #27AE60; margin: 20px 0;">
                <p style="margin: 0;"><strong>💡 중요한 팁</strong></p>
                <p style="margin: 5px 0 0 0;">하루를 놓쳐도 괜찮습니다. 다시 시작하면 됩니다.<br/>
                완벽하게 하려고 하지 마세요. 꾸준함이 완벽함을 이깁니다.</p>
            </div>
            
            <p style="margin-top: 30px;">
                당신을 응원합니다,<br/>
                bty Training Team 💚
            </p>
        </body>
        </html>
        """
        
        # 주간 요약 PDF 생성
        week_summary_pdf = self.weekly_pdf_generator.generate_weekly_pdf(
            user_name=user_name,
            week_num=week_num,
            week_days=week_days,
            start_date=send_at,
            output_filename=f"week{week_num}_summary_{user_name}.pdf"
        )
        
        # 주간 상세 PDF 생성 (7일치 상세 내용)
        week_detailed_pdf = self.weekly_detailed_pdf_generator.generate_weekly_detailed_pdf(
            user_name=user_name,
            week_num=week_num,
            week_days=week_days,
            start_date=send_at,
            output_filename=f"week{week_num}_detailed_{user_name}.pdf"
        )
        
        # 파일명을 영문+숫자로만 구성 (한글 인코딩 문제 방지)
        attachments = [
            {
                "type": "pdf",
                "path": week_summary_pdf,
                "filename": f"Week{week_num}_Summary.pdf"
            },
            {
                "type": "pdf",
                "path": week_detailed_pdf,
                "filename": f"Week{week_num}_Detailed_Guide.pdf"
            }
        ]
        
        return {
            "type": f"week_{week_num}_start",
            "send_at": send_at.isoformat(),
            "to": user_email,
            "subject": subject,
            "body_html": body_html,
            "attachments": attachments
        }
    
    def _create_completion_email(
        self,
        user_email: str,
        user_name: str,
        send_at: datetime,
        retest_link: str,
        day_data: Dict
    ) -> Dict:
        """완료 & 재검사 초대 이메일"""
        subject = f"[28일 완주!] {user_name}님, 축하합니다! 🎉🏆"
        
        body_html = f"""
        <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #8E44AD; text-align: center;">🎊🎊🎊 28일 완주! 축하합니다! 🎊🎊🎊</h1>
            
            <h2 style="color: #2C3E50;">정말 대단합니다, {user_name}님!</h2>
            
            <p>28일 동안 매일 자기자비를 실천한 당신을 진심으로 축하합니다.</p>
            
            <div style="background-color: #E8F8F5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: #27AE60; margin-top: 0;">✅ 당신이 이룬 것들</h3>
                <ul>
                    <li>자기비판을 알아차렸습니다</li>
                    <li>완벽주의를 내려놓기 시작했습니다</li>
                    <li>혼자가 아님을 깨달았습니다</li>
                    <li>존재 자체로 가치 있음을 배웠습니다</li>
                    <li>나만의 자기자비 방법을 찾았습니다</li>
                </ul>
            </div>
            
            <h3 style="color: #3498DB;">🔍 이제 재검사를 통해 변화를 확인하세요</h3>
            
            <p>28일 전과 비교해서 무엇이 달라졌는지 확인해보세요.<br/>
            숫자의 변화뿐 아니라, 당신 안의 변화를 느껴보세요.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{retest_link}" style="display: inline-block; background-color: #2874A6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold;">
                    🔗 재검사 시작하기
                </a>
            </div>
            
            <div style="background-color: #FEF5E7; padding: 20px; border-left: 4px solid #F39C12; margin: 20px 0;">
                <h4 style="color: #F39C12; margin-top: 0;">💡 다음 단계</h4>
                <ol>
                    <li>재검사 완료하기</li>
                    <li>Day 25에서 만든 '매일 루틴' 지속하기</li>
                    <li>Day 26 미래 편지 6개월 후 열어보기</li>
                    <li>Day 27 선언문 매일 보기</li>
                    <li>필요할 때마다 28일 가이드 다시 읽기</li>
                </ol>
            </div>
            
            <h3 style="color: #2C3E50;">💌 마지막 메시지</h3>
            
            <p>자기자비는 목적지가 아닌 여정입니다.<br/>
            완벽하지 않아도 괜찮습니다.<br/>
            때로 놓치고, 실패하고, 다시 시작해도 괜찮습니다.</p>
            
            <p><strong>중요한 것은 방향입니다.<br/>
            당신은 이미 올바른 방향으로 가고 있습니다.</strong></p>
            
            <p>6개월 후, 1년 후, 당신은 더욱 성장해 있을 것입니다.<br/>
            그때도 이 여정을 기억하며,<br/>
            다시 한번 나에게 자비를 베푸세요.</p>
            
            <p style="font-size: 20px; font-weight: bold; color: #8E44AD; text-align: center; margin: 30px 0;">
                당신은 충분히 가치 있습니다.<br/>
                그 자체로.
            </p>
            
            <p style="margin-top: 40px; text-align: center;">
                당신을 응원합니다. 항상.<br/>
                bty Training Team 일동 💚
            </p>
        </body>
        </html>
        """
        
        return {
            "type": "completion_and_retest",
            "send_at": send_at.isoformat(),
            "to": user_email,
            "subject": subject,
            "body_html": body_html,
            "attachments": []
        }
    
    def _create_24h_report_email(
        self,
        user_email: str,
        user_name: str,
        send_at: datetime,
        pdf_report_path: Optional[str]
    ) -> Dict:
        """24시간 후 결과 리포트 이메일"""
        subject = f"[자존감 분석 결과] {user_name}님, 당신의 진단 결과를 확인하세요 📊"
        
        body_html = f"""
        <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2C3E50;">안녕하세요, {user_name}님!</h2>
            
            <p>어제 진단을 완료하신 것을 축하드립니다. 🎉</p>
            
            <p>자신을 돌아보는 것은 쉽지 않은 일입니다.<br/>
            용기 내어 첫 걸음을 내디딘 당신을 진심으로 응원합니다.</p>
            
            <div style="background-color: #E8F8F5; padding: 20px; border-left: 4px solid #27AE60; margin: 20px 0;">
                <h3 style="color: #27AE60; margin-top: 0;">📊 당신의 진단 결과</h3>
                <p>첨부된 <strong>자존감 분석 보고서 PDF</strong>에서 다음을 확인하실 수 있습니다:</p>
                <ul>
                    <li><strong>현재 상태:</strong> 객관적인 자존감 점수와 분석</li>
                    <li><strong>행동 패턴:</strong> 무의식적으로 반복하는 패턴 발견</li>
                    <li><strong>숨겨진 강점:</strong> 당신이 놓치고 있던 내면의 자원</li>
                    <li><strong>구체적 실천법:</strong> 오늘부터 시작할 수 있는 작은 변화</li>
                </ul>
            </div>
            
            <h3 style="color: #3498DB;">🚀 다음 단계</h3>
            
            <p>매주 실천 가이드 이메일을 통해 구체적인 실천 방법을 안내해드립니다.<br/>
            첨부된 PDF와 함께 차근차근 따라오시면 됩니다.</p>
            
            <div style="background-color: #FEF5E7; padding: 15px; border-left: 4px solid #F39C12; margin: 20px 0;">
                <h4 style="color: #F39C12; margin-top: 0;">💡 보고서 읽는 방법</h4>
                <ol>
                    <li><strong>분석 보고서:</strong> 천천히 읽으며 자신을 이해하세요 (15-20분)</li>
                    <li><strong>감정 확인:</strong> 읽으면서 어떤 감정이 드는지 알아차리세요</li>
                    <li><strong>강점 찾기:</strong> '숨겨진 강점' 섹션을 특히 주의 깊게 보세요</li>
                    <li><strong>실천 준비:</strong> 매주 받는 가이드를 통해 단계별로 실천하세요</li>
                </ol>
            </div>
            
            <h3 style="color: #2C3E50;">📌 기억하세요</h3>
            
            <p>이 보고서는 당신을 판단하기 위한 것이 아닙니다.<br/>
            <strong>변화의 출발점을 찾기 위한 도구</strong>입니다.</p>
            
            <p>낮은 점수는 실패가 아니라 <strong>성장의 여지</strong>입니다.<br/>
            높은 점수도 완벽함이 아니라 <strong>계속 가꿔야 할 것</strong>입니다.</p>
            
            <div style="background-color: #E8F4F8; padding: 20px; border-radius: 10px; margin: 30px 0;">
                <p style="font-size: 18px; font-weight: bold; color: #2874A6; margin: 0; text-align: center;">
                    당신은 이미 변화를 시작했습니다.<br/>
                    오늘도 한 걸음 더 나아가세요. 💚
                </p>
            </div>
            
            <p>궁금한 점이 있으시면 언제든 답장해 주세요.<br/>
            28일 동안 함께 하겠습니다.</p>
            
            <p style="margin-top: 30px;">
                당신을 응원합니다,<br/>
                bty Training Team 💚
            </p>
        </body>
        </html>
        """
        
        attachments = []
        if pdf_report_path:
            attachments.append({
                "type": "pdf",
                "path": pdf_report_path,
                "filename": f"{user_name}_자존감분석보고서.pdf"
            })
        
        return {
            "type": "24h_report",
            "send_at": send_at.isoformat(),
            "to": user_email,
            "subject": subject,
            "body_html": body_html,
            "attachments": attachments
        }
    
    def save_schedule_to_json(self, schedule: Dict, output_path: str = "email_schedule.json"):
        """이메일 스케줄을 JSON 파일로 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)
        return output_path
    
    def shutdown(self):
        """스케줄러 종료 (API 서버 shutdown 시 호출)"""
        print("EmailScheduler shutdown called")
        # 필요한 정리 작업 수행
        pass
    
    def send_email_now(self, email_data: Dict) -> Dict:
        """
        이메일 즉시 발송
        
        Args:
            email_data: 이메일 데이터 (to, subject, body_html, attachments)
            
        Returns:
            발송 결과
        """
        if not self.enable_email:
            print(f"📧 [테스트 모드] 이메일 발송 스킵: {email_data['to']}")
            print(f"   제목: {email_data['subject']}")
            return {
                "success": True,
                "mode": "test",
                "message": "테스트 모드 - 실제 발송하지 않음"
            }
        
        # SMTP 설정 확인
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_user or not smtp_password:
            error_msg = "SMTP 설정이 없습니다. SMTP_USER와 SMTP_PASSWORD 환경 변수를 설정하세요."
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        # 실제 이메일 발송
        try:
            result = self.email_sender.send_email(
                to_email=email_data['to'],
                subject=email_data['subject'],
                html_body=email_data['body_html'],
                attachments=email_data.get('attachments', [])
            )
            return result
        except Exception as e:
            print(f"❌ 이메일 발송 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_all_emails_now(self, schedule: Dict) -> List[Dict]:
        """
        스케줄의 모든 이메일 즉시 발송 (테스트용)
        
        Args:
            schedule: create_email_schedule()에서 생성된 스케줄
            
        Returns:
            발송 결과 리스트
        """
        results = []
        emails = schedule.get('emails', [])
        
        print(f"\n{'='*70}")
        print(f"이메일 발송 시작: {len(emails)}개")
        print(f"{'='*70}\n")
        
        for i, email in enumerate(emails, 1):
            print(f"[{i}/{len(emails)}] 발송 중...")
            print(f"   수신자: {email['to']}")
            print(f"   제목: {email['subject'][:50]}...")
            
            result = self.send_email_now(email)
            results.append({
                "email_type": email['type'],
                "result": result
            })
            
            if result.get('success'):
                print(f"   ✅ 성공\n")
            else:
                print(f"   ❌ 실패: {result.get('error', 'Unknown')}\n")
        
        # 요약
        success_count = sum(1 for r in results if r['result'].get('success'))
        print(f"{'='*70}")
        print(f"발송 완료: {success_count}/{len(emails)} 성공")
        print(f"{'='*70}\n")
        
        return results
    
    def schedule_three_stage_emails(
        self,
        user_email: str,
        user_name: str,
        emails: Dict,  # Dict로 변경 (basic, intermediate, detailed 키 포함)
        pdf_path: Optional[str] = None,
        profile: Optional[Dict] = None
    ) -> Dict:
        """
        3단계 이메일 발송
        1단계: 즉시 발송 - 진단 완료 알림
        2단계: 2시간 후 - 중간 분석 보고서 (실제로는 즉시 발송)
        3단계: 24시간 후 - 상세 분석 보고서 (실제로는 즉시 발송)
        
        Args:
            user_email: 사용자 이메일
            user_name: 사용자 이름
            emails: 이메일 콘텐츠 딕셔너리 (basic, intermediate, detailed)
            pdf_path: PDF 보고서 경로
            profile: 프로파일 정보
            
        Returns:
            발송 스케줄 정보
        """
        now = datetime.now()
        
        # 이메일 데이터 준비
        email_data_list = []
        
        # emails가 딕셔너리인 경우 처리
        if isinstance(emails, dict):
            for stage_name, email_content in emails.items():
                email_data = {
                    "to": user_email,
                    "subject": email_content.get("subject", "자존감 분석 결과"),
                    "body_html": email_content.get("body", ""),
                    "attachments": [],
                    "stage": stage_name
                }
                
                # PDF 첨부 파일 추가 (detailed 단계에만)
                if stage_name == "detailed" and pdf_path and os.path.exists(pdf_path):
                    email_data["attachments"].append({
                        "path": pdf_path,
                        "filename": f"{user_name}_자존감분석보고서.pdf"
                    })
                
                email_data_list.append(email_data)
        else:
            # 리스트인 경우 (이전 방식 호환)
            for email_content in emails:
                email_data = {
                    "to": user_email,
                    "subject": email_content.get("subject", "자존감 분석 결과"),
                    "body_html": email_content.get("body", ""),
                    "attachments": []
                }
                
                if pdf_path and os.path.exists(pdf_path):
                    email_data["attachments"].append({
                        "path": pdf_path,
                        "filename": f"{user_name}_자존감분석보고서.pdf"
                    })
                
                email_data_list.append(email_data)
        
        # 모든 이메일 즉시 발송
        results = []
        for i, email_data in enumerate(email_data_list, 1):
            stage = email_data.get('stage', f'email_{i}')
            print(f"\n[{stage}] 발송 중...")
            result = self.send_email_now(email_data)
            results.append({
                "stage": stage,
                "result": result
            })
        
        # 발송 결과 요약
        success_count = sum(1 for r in results if r.get('result', {}).get('success'))
        
        return {
            "total_emails": len(email_data_list),
            "sent": success_count,
            "failed": len(email_data_list) - success_count,
            "results": results,
            "timestamp": now.isoformat()
        }


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("28일 가이드 이메일 스케줄링 시스템 테스트")
    print("=" * 60)
    
    # 샘플 데이터
    user_email = "sample@example.com"
    user_name = "샘플사용자"
    
    analysis_results = {
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
    
    start_date = datetime(2026, 2, 10, 9, 0, 0)  # 2026년 2월 10일 오전 9시
    retest_link = "https://example.com/self-esteem/retest"
    pdf_report_path = "outputs/report_example_user.pdf"
    
    # 스케줄러 생성
    scheduler = EmailScheduler()
    
    # 이메일 스케줄 생성
    schedule = scheduler.create_email_schedule(
        user_email=user_email,
        user_name=user_name,
        analysis_results=analysis_results,
        start_date=start_date,
        retest_link=retest_link,
        pdf_report_path=pdf_report_path
    )
    
    # JSON으로 저장
    json_path = scheduler.save_schedule_to_json(schedule, "outputs/email_schedule_sample.json")
    
    print(f"\n✅ 이메일 스케줄 생성 완료:")
    print(f"   📧 수신자: {schedule['user_email']}")
    print(f"   👤 이름: {schedule['user_name']}")
    print(f"   📅 시작일: {schedule['start_date']}")
    print(f"   📨 총 이메일 수: {schedule['total_emails']}")
    print(f"   📄 28일 가이드 PDF: {schedule['daily_guide_pdf']}")
    
    print(f"\n📋 이메일 발송 스케줄:")
    for i, email in enumerate(schedule['emails'], 1):
        send_time = datetime.fromisoformat(email['send_at'])
        print(f"   {i}. [{email['type']}]")
        print(f"      발송 시각: {send_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"      제목: {email['subject'][:50]}...")
        if email.get('attachments'):
            print(f"      첨부 파일: {len(email['attachments'])}개")
        print()
    
    print(f"✅ JSON 스케줄 저장: {json_path}")
    print("\n" + "=" * 60)
