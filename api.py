"""
Phase 1 통합 API
FastAPI 기반 REST API 엔드포인트

엔드포인트:
- POST /api/assess: 평가 실행 (Phase 1 개선 적용)
- GET /api/quality/{user_id}: 품질 리포트 조회
- POST /api/assess-ab: A/B 테스트 버전
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import json
import os

# .env 파일 로드
def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print(f"✅ .env 파일 로드: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print(f"⚠️  .env 파일 없음: {env_path}")
        print("   SMTP 설정을 환경 변수로 지정하거나 .env 파일을 생성하세요.")

# 환경 변수 로드 (앱 시작 시 실행)
load_env()

# Phase 1 모듈 임포트
from careless_response_detector import CarelessResponseDetector, QualityCheckResult
from response_style_corrector import ResponseStyleCorrector, CorrectionResult

# 이메일 및 분석 모듈 임포트
from email_scheduler import EmailScheduler
from self_esteem_system import SelfEsteemSystem


# ==================== FastAPI 초기화 ====================

app = FastAPI(
    title="자존감 평가 API (Phase 1)",
    description="부주의 응답 감지 + 응답 스타일 보정",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 초기화
detector = CarelessResponseDetector()
corrector = ResponseStyleCorrector()

# 이메일 스케줄러 초기화 (EmailConfig 제거)
email_scheduler = EmailScheduler()

# 자존감 분석 시스템 초기화
esteem_system = SelfEsteemSystem()

# PDF 출력 디렉토리 설정
PDF_OUTPUT_DIR = "/home/user/webapp/pdf_reports"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


# ==================== 데이터 모델 ====================

class AssessmentRequest(BaseModel):
    """평가 요청"""
    user_id: str = Field(..., description="사용자 ID")
    responses: List[int] = Field(..., description="응답 리스트 (1-4 척도, 50개)", min_length=50, max_length=50)
    response_times: List[float] = Field(..., description="응답 시간 (초 단위, 50개)", min_length=50, max_length=50)
    reverse_items: Optional[List[int]] = Field(
        default=[2, 4, 7, 8, 9, 13, 14, 15, 19, 20, 21],
        description="역문항 인덱스 (Rosenberg 기본값)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "responses": [3, 2, 4, 1] * 12 + [3, 2],
                "response_times": [4.5, 3.2, 5.1, 3.8] * 12 + [4.2, 3.9],
                "reverse_items": [2, 4, 7, 8, 9]
            }
        }


class AssessmentResponse(BaseModel):
    """평가 응답"""
    user_id: str
    status: str  # "success", "invalid", "warning"
    message: str
    data_quality: Dict
    corrected_responses: List[int]
    style_corrections: Dict
    timestamp: str


class QualityReportResponse(BaseModel):
    """품질 리포트"""
    user_id: str
    quality_score: float
    flags: List[str]
    recommendation: str
    details: Dict


class TestGroup(str, Enum):
    """A/B 테스트 그룹"""
    CONTROL = "control"
    TREATMENT = "treatment"


# ==================== API 엔드포인트 ====================

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "자존감 평가 API (Phase 1)",
        "version": "1.0.0",
        "features": [
            "부주의 응답 감지",
            "응답 스타일 보정",
            "A/B 테스트 지원"
        ],
        "endpoints": {
            "assess": "/api/assess",
            "quality": "/api/quality/{user_id}",
            "ab_test": "/api/assess-ab"
        }
    }


@app.post("/api/assess", response_model=AssessmentResponse)
async def assess_responses(request: AssessmentRequest):
    """
    자존감 평가 실행 (Phase 1 개선 적용)
    
    Process:
    1. 데이터 품질 검증 (부주의 응답 감지)
    2. 응답 스타일 보정
    3. 자존감 분석 및 이메일 생성
    4. 3단계 이메일 예약 발송
    
    Returns:
        - status: "success", "invalid", "warning"
        - 품질 정보 + 보정된 응답
        - 이메일 스케줄 정보
    """
    try:
        # Step 1: 데이터 품질 검증
        quality_result: QualityCheckResult = detector.analyze(
            responses=request.responses,
            response_times=request.response_times
        )
        
        # 품질 점수가 너무 낮으면 거부
        if quality_result.recommendation == "reject":
            return AssessmentResponse(
                user_id=request.user_id,
                status="invalid",
                message=_get_quality_warning_message(quality_result),
                data_quality={
                    "quality_score": quality_result.quality_score,
                    "flags": quality_result.flags,
                    "recommendation": quality_result.recommendation,
                    "details": quality_result.details
                },
                corrected_responses=request.responses,
                style_corrections={},
                timestamp=datetime.now().isoformat()
            )
        
        # Step 2: 응답 스타일 보정
        correction_result: CorrectionResult = corrector.correct(
            responses=request.responses,
            reverse_items=request.reverse_items
        )
        
        # Step 3: 자존감 분석 및 이메일 생성
        analysis_results = esteem_system.process_test_results(
            user_name=request.user_id.split('@')[0] if '@' in request.user_id else request.user_id,
            user_email=request.user_id,
            responses=correction_result.corrected_responses,
            response_times=request.response_times
        )
        
        # Step 3.5: PDF 보고서 생성
        try:
            from pdf_generator_v2 import EnhancedPDFGenerator
            
            # PDF 파일명 생성
            user_name = request.user_id.split('@')[0] if '@' in request.user_id else request.user_id
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"{user_name}_자존감분석_{timestamp}.pdf"
            pdf_path = os.path.join(PDF_OUTPUT_DIR, pdf_filename)
            
            # 강점 데이터 변환 (올바른 형식으로)
            strengths_for_pdf = []
            for strength in analysis_results.get('strengths', []):
                strengths_for_pdf.append({
                    'name': strength.get('name', '강점'),
                    'evidence': strength.get('detail', ''),
                    'how_to_use': f"이 강점을 활용하여 자존감을 높일 수 있습니다. (증거 질문: {', '.join([str(q+1) for q in strength.get('evidence_questions', [])])})"
                })
            
            # 패턴 데이터 생성 (기본 패턴 제공)
            patterns_for_pdf = [
                {
                    'name': '자기 성찰',
                    'strength': 0.85,
                    'evidence': [1, 12, 23, 36, 47],
                    'description': '당신은 자신의 감정과 행동을 깊이 성찰하는 능력이 있습니다.',
                    'research': 'Neff, K. D. (2003). Self-compassion: An alternative conceptualization.'
                },
                {
                    'name': '성장 의지',
                    'strength': 0.78,
                    'evidence': [26, 27, 28, 29],
                    'description': '당신은 변화하고 성장하려는 강한 동기를 가지고 있습니다.',
                    'research': 'Dweck, C. S. (2006). Mindset: The new psychology of success.'
                },
                {
                    'name': '진정성',
                    'strength': 0.72,
                    'evidence': [40, 41, 42, 43, 44],
                    'description': '당신은 솔직하고 진정성 있게 자신을 표현합니다.',
                    'research': 'Kernis, M. H. (2003). Toward a conceptualization of optimal self-esteem.'
                }
            ]
            
            # 보고서 데이터 준비
            report_data = {
                'user_email': request.user_id,
                'profile_type': analysis_results['profile']['esteem_type'],
                'scores': analysis_results['profile']['scores'],
                'patterns': patterns_for_pdf,
                'strengths': strengths_for_pdf,
                'retest_link': 'https://yoursite.com/retest'
            }
            
            # PDF 생성기 초기화 및 생성
            pdf_gen = EnhancedPDFGenerator(report_data, pdf_path)
            pdf_gen.generate()
            print(f"✅ PDF 생성 완료: {pdf_path}")
            
        except Exception as e:
            import traceback
            print(f"❌ PDF 생성 실패: {e}")
            print(traceback.format_exc())
            pdf_path = None
        
        # Step 4: 3단계 이메일 예약 발송
        email_schedule = email_scheduler.schedule_three_stage_emails(
            user_email=request.user_id,
            user_name=analysis_results['profile']['esteem_type'],
            emails=analysis_results['emails'],
            pdf_path=pdf_path,  # 생성된 PDF 경로
            profile=analysis_results['profile']  # 개발자 알림용 프로파일 정보
        )
        
        # 경고 메시지 생성
        status = "success"
        message = "평가가 성공적으로 완료되었습니다. 이메일을 확인해주세요!"
        
        if quality_result.recommendation == "warning":
            status = "warning"
            message = "평가가 완료되었지만 응답 품질에 약간의 문제가 있습니다. 이메일을 확인해주세요."
        
        return AssessmentResponse(
            user_id=request.user_id,
            status=status,
            message=message,
            data_quality={
                "quality_score": quality_result.quality_score,
                "flags": quality_result.flags,
                "recommendation": quality_result.recommendation,
                "details": quality_result.details
            },
            corrected_responses=correction_result.corrected_responses,
            style_corrections={
                "corrections_applied": correction_result.corrections_applied,
                "style_scores": correction_result.style_scores,
                "email_schedule": email_schedule  # 이메일 스케줄 정보 추가
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quality/{user_id}", response_model=QualityReportResponse)
async def get_quality_report(user_id: str):
    """
    사용자별 품질 리포트 조회
    (관리자 대시보드용)
    
    실제로는 DB에서 조회하지만, 여기서는 예시 응답
    """
    # TODO: DB에서 실제 데이터 조회
    # quality_data = db.quality_logs.find_one({"user_id": user_id})
    
    # 예시 응답
    return QualityReportResponse(
        user_id=user_id,
        quality_score=0.85,
        flags=["speeding"],
        recommendation="acceptable",
        details={
            "response_time": {
                "avg_time": 2.8,
                "fast_ratio": 0.12
            },
            "longstring": {
                "max_streak": 5
            },
            "consistency": {
                "correlation": 0.72
            }
        }
    )


@app.post("/api/assess-ab")
async def assess_with_ab_test(request: AssessmentRequest):
    """
    A/B 테스트 버전
    
    사용자를 Control/Treatment 그룹에 할당하고
    각각 다른 알고리즘 적용
    """
    # 사용자 ID 해시로 일관된 그룹 할당
    group = _assign_test_group(request.user_id)
    
    if group == TestGroup.TREATMENT:
        # Phase 1 개선 적용
        result = await assess_responses(request)
        
        # A/B 테스트 로그 기록
        _log_ab_test(request.user_id, group, result)
        
        return {
            **result.dict(),
            "test_group": group.value
        }
    else:
        # Control: 기존 시스템 (Phase 1 미적용)
        # TODO: 기존 로직 호출
        return {
            "user_id": request.user_id,
            "status": "success",
            "message": "Control 그룹 - 기존 시스템",
            "test_group": group.value,
            "data_quality": {},
            "corrected_responses": request.responses,
            "style_corrections": {},
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/ab-stats")
async def get_ab_test_stats():
    """
    A/B 테스트 통계
    (관리자 대시보드용)
    """
    # TODO: DB에서 실제 통계 조회
    return {
        "total_users": 1000,
        "control_group": {
            "count": 500,
            "avg_quality_score": 0.72,
            "flagged_rate": 0.25,
            "completion_rate": 0.65
        },
        "treatment_group": {
            "count": 500,
            "avg_quality_score": 0.85,
            "flagged_rate": 0.10,
            "completion_rate": 0.75
        },
        "improvement": {
            "quality_score": "+18%",
            "flagged_rate": "-60%",
            "completion_rate": "+15%"
        }
    }


@app.get("/api/scheduled-emails")
async def get_scheduled_emails():
    """
    예약된 이메일 목록 조회
    (관리자용)
    """
    jobs = email_scheduler.get_scheduled_jobs()
    return {
        "total_scheduled": len(jobs),
        "jobs": jobs
    }


@app.post("/api/cancel-email/{job_id}")
async def cancel_scheduled_email(job_id: str):
    """
    예약된 이메일 취소
    (관리자용)
    """
    result = email_scheduler.cancel_job(job_id)
    if result:
        return {"status": "success", "message": f"Job {job_id} cancelled"}
    else:
        raise HTTPException(status_code=404, detail="Job not found")


@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료시 스케줄러 정리"""
    email_scheduler.shutdown()


# ==================== 헬퍼 함수 ====================

def _get_quality_warning_message(quality_result: QualityCheckResult) -> str:
    """품질 경고 메시지 생성"""
    messages = ["응답 품질이 낮습니다:\n"]
    
    if "speeding" in quality_result.flags:
        messages.append("⚠️ 너무 빠르게 응답하셨습니다.")
    
    if "longstring" in quality_result.flags:
        messages.append("⚠️ 동일한 답변이 너무 많습니다.")
    
    if "inconsistent" in quality_result.flags:
        messages.append("⚠️ 응답이 일관되지 않습니다.")
    
    if "statistical_outlier" in quality_result.flags:
        messages.append("⚠️ 통계적으로 비정상적인 응답 패턴입니다.")
    
    messages.append("\n천천히 다시 응답해주시면 더 정확한 결과를 받을 수 있습니다.")
    
    return "\n".join(messages)


def _assign_test_group(user_id: str) -> TestGroup:
    """사용자를 A/B 테스트 그룹에 할당"""
    hash_value = hash(user_id)
    return TestGroup.TREATMENT if hash_value % 2 == 0 else TestGroup.CONTROL


def _log_ab_test(user_id: str, group: TestGroup, result: AssessmentResponse):
    """A/B 테스트 메트릭 기록"""
    # TODO: DB에 저장
    log_entry = {
        "user_id": user_id,
        "group": group.value,
        "timestamp": datetime.now().isoformat(),
        "quality_score": result.data_quality.get("quality_score"),
        "flags": result.data_quality.get("flags", []),
        "corrections_applied": result.style_corrections.get("corrections_applied", []),
        "status": result.status
    }
    
    # 예시: print로 로그 출력 (실제로는 DB에 insert)
    print(f"[A/B TEST LOG] {json.dumps(log_entry, indent=2)}")


# ==================== 테스트용 엔드포인트 ====================

@app.post("/api/test/simulate")
async def simulate_test():
    """
    테스트용: 다양한 응답 패턴 시뮬레이션
    """
    import random
    
    scenarios = {
        "normal": {
            "responses": [random.randint(1, 4) for _ in range(50)],
            "times": [random.uniform(3.0, 6.0) for _ in range(50)]
        },
        "speeder": {
            "responses": [random.randint(2, 3) for _ in range(50)],
            "times": [random.uniform(0.3, 0.8) for _ in range(50)]
        },
        "longstring": {
            "responses": [2] * 50,
            "times": [random.uniform(3.0, 5.0) for _ in range(50)]
        }
    }
    
    results = {}
    
    for scenario_name, data in scenarios.items():
        request = AssessmentRequest(
            user_id=f"test_{scenario_name}",
            responses=data["responses"],
            response_times=data["times"]
        )
        
        result = await assess_responses(request)
        results[scenario_name] = {
            "status": result.status,
            "quality_score": result.data_quality["quality_score"],
            "flags": result.data_quality["flags"]
        }
    
    return results


# ==================== 실행 ====================

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("자존감 평가 API 서버 시작")
    print("="*60)
    print("\n엔드포인트:")
    print("  - POST http://localhost:8000/api/assess")
    print("  - GET  http://localhost:8000/api/quality/{user_id}")
    print("  - POST http://localhost:8000/api/assess-ab")
    print("  - GET  http://localhost:8000/api/ab-stats")
    print("\n문서:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
