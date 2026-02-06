#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Integration Test - 통합 시스템 최종 검증
"""

from datetime import datetime
from email_scheduler import EmailScheduler
import os
import json

def run_final_test():
    """최종 통합 테스트 실행"""
    
    print("=" * 70)
    print("28일 매일 실천 가이드 시스템 - 최종 통합 테스트")
    print("=" * 70)
    print()
    
    # 테스트 데이터
    test_cases = [
        {
            "name": "취약형",
            "email": "vulnerable@example.com",
            "profile": "vulnerable",
            "score": 12
        },
        {
            "name": "자기비판형",
            "email": "critic@example.com",
            "profile": "developing_critic",
            "score": 22
        },
        {
            "name": "자비성장형",
            "email": "grower@example.com",
            "profile": "compassionate_grower",
            "score": 28
        }
    ]
    
    scheduler = EmailScheduler()
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[테스트 {i}/{len(test_cases)}] {test_case['name']} 프로필")
        print("-" * 70)
        
        analysis_results = {
            "scores": {"rosenberg": test_case["score"]},
            "profile_type": test_case["profile"],
            "detected_patterns": [
                {"type": "SELF_CRITICISM", "strength": 0.85}
            ],
            "hidden_strengths": [
                {"name": "회복탄력성", "description": "어려움 속에서도 다시 일어서는 힘"}
            ]
        }
        
        start_date = datetime(2026, 2, 10, 9, 0, 0)
        retest_link = f"https://example.com/retest?user={test_case['name']}"
        
        try:
            # 이메일 스케줄 생성
            schedule = scheduler.create_email_schedule(
                user_email=test_case["email"],
                user_name=test_case["name"],
                analysis_results=analysis_results,
                start_date=start_date,
                retest_link=retest_link,
                pdf_report_path=None
            )
            
            # JSON 저장
            json_path = f"outputs/test_schedule_{test_case['profile']}.json"
            scheduler.save_schedule_to_json(schedule, json_path)
            
            # PDF 파일 확인
            pdf_path = schedule['daily_guide_pdf']
            pdf_exists = os.path.exists(pdf_path)
            pdf_size = os.path.getsize(pdf_path) if pdf_exists else 0
            
            result = {
                "name": test_case["name"],
                "profile": test_case["profile"],
                "email_count": schedule["total_emails"],
                "pdf_exists": pdf_exists,
                "pdf_size_kb": pdf_size // 1024,
                "json_path": json_path,
                "status": "✅ 성공"
            }
            
            print(f"   ✅ 이메일 스케줄: {result['email_count']}개")
            print(f"   ✅ 28일 가이드 PDF: {pdf_path} ({result['pdf_size_kb']}KB)")
            print(f"   ✅ JSON 스케줄: {json_path}")
            print()
            
        except Exception as e:
            result = {
                "name": test_case["name"],
                "profile": test_case["profile"],
                "status": f"❌ 실패: {str(e)}"
            }
            print(f"   ❌ 오류: {str(e)}")
            print()
        
        results.append(result)
    
    # 결과 요약
    print("=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    
    success_count = sum(1 for r in results if "✅" in r["status"])
    
    for result in results:
        print(f"{result['status']} {result['name']} ({result['profile']})")
        if "email_count" in result:
            print(f"   - 이메일: {result['email_count']}개")
            print(f"   - PDF: {result['pdf_size_kb']}KB")
    
    print()
    print(f"총 {len(test_cases)}개 테스트 중 {success_count}개 성공")
    print()
    
    # 파일 목록
    print("=" * 70)
    print("생성된 파일 목록")
    print("=" * 70)
    os.system("ls -lh outputs/*.pdf outputs/*.json | tail -10")
    print()
    
    return success_count == len(test_cases)

if __name__ == "__main__":
    success = run_final_test()
    
    if success:
        print("🎉 모든 테스트 통과! 시스템이 정상 작동합니다.")
        exit(0)
    else:
        print("⚠️  일부 테스트 실패. 로그를 확인하세요.")
        exit(1)
