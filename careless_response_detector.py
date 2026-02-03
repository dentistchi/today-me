"""
부주의 응답 감지기 (Careless Response Detector)
Phase 1 핵심 모듈

학술 근거:
- Ward & Meade (2023): Annual Review of Psychology
- Curran (2016): Journal of Experimental Social Psychology
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QualityCheckResult:
    """품질 검사 결과"""
    is_careless: bool
    flags: List[str]
    quality_score: float  # 0-1
    details: Dict
    recommendation: str
    timestamp: str


class CarelessResponseDetector:
    """
    부주의 응답 감지기
    
    4가지 감지 기법:
    1. Response Time Analysis (응답 시간)
    2. Longstring Analysis (동일 응답 연속)
    3. Even-Odd Consistency (짝수/홀수 일관성)
    4. Mahalanobis Distance (통계적 이상치)
    5. Low Variance Analysis (낮은 변동성)
    """
    
    def __init__(self,
                 min_time_per_item: float = 2.0,
                 longstring_threshold: int = 10,
                 correlation_threshold: float = 0.3,
                 mahalanobis_p_threshold: float = 0.001,
                 variance_threshold: float = 0.3):
        """
        Parameters:
            min_time_per_item: 최소 응답 시간 (초)
            longstring_threshold: 동일 응답 연속 임계값
            correlation_threshold: 짝수/홀수 상관계수 최소값
            mahalanobis_p_threshold: Mahalanobis distance p-value 임계값
            variance_threshold: 응답 분산 임계값
        """
        self.min_time_per_item = min_time_per_item
        self.longstring_threshold = longstring_threshold
        self.correlation_threshold = correlation_threshold
        self.mahalanobis_p_threshold = mahalanobis_p_threshold
        self.variance_threshold = variance_threshold
    
    def analyze(self, 
                responses: List[int], 
                response_times: List[float],
                reference_data: Optional[np.ndarray] = None) -> QualityCheckResult:
        """
        종합 품질 분석 실행
        
        Args:
            responses: 응답 리스트 (1-4 척도, 50개)
            response_times: 응답 시간 리스트 (초 단위, 50개)
            reference_data: 참조 데이터셋 (선택, Mahalanobis용)
        
        Returns:
            QualityCheckResult 객체
        """
        flags = []
        details = {}
        
        # 1) 응답 시간 분석
        time_flag, time_details = self._check_response_time(response_times)
        if time_flag:
            flags.append("speeding")
        details["response_time"] = time_details
        
        # 2) Longstring 분석
        longstring_flag, longstring_details = self._check_longstring(responses)
        if longstring_flag:
            flags.append("longstring")
        details["longstring"] = longstring_details
        
        # 3) 짝수/홀수 일관성
        consistency_flag, consistency_details = self._check_consistency(responses)
        if consistency_flag:
            flags.append("inconsistent")
        details["consistency"] = consistency_details
        
        # 4) Mahalanobis distance (reference_data 있을 때만)
        if reference_data is not None:
            outlier_flag, outlier_details = self._check_mahalanobis(
                responses, reference_data
            )
            if outlier_flag:
                flags.append("statistical_outlier")
            details["mahalanobis"] = outlier_details
        
        # 5) Low Variance 분석 (추가됨)
        variance_flag, variance_details = self._check_low_variance(responses)
        if variance_flag:
            flags.append("low_variance")
        details["variance"] = variance_details
        
        # 품질 점수 계산 (0-1)
        quality_score = self._calculate_quality_score(flags, details)
        
        # 권장사항 결정
        recommendation = self._get_recommendation(quality_score, flags)
        
        return QualityCheckResult(
            is_careless=len(flags) >= 2,  # 2개 이상 플래그 → 부주의
            flags=flags,
            quality_score=quality_score,
            details=details,
            recommendation=recommendation,
            timestamp=datetime.now().isoformat()
        )
    
    def _check_response_time(self, times: List[float]) -> Tuple[bool, Dict]:
        """
        응답 시간 분석
        
        감지 패턴:
        - 평균 응답 시간 < 2초
        - 연속 3개 이상 질문에 1초 미만 응답
        
        연구 근거:
        - Huang et al. (2012): 2초 미만은 질문을 읽지 않음
        - Curran (2016): 평균 < 3초 → 95% 부주의
        """
        avg_time = np.mean(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        # 연속 빠른 응답 감지
        consecutive_fast = 0
        max_consecutive_fast = 0
        fast_count = 0
        
        for t in times:
            if t < 1.0:  # 1초 미만
                consecutive_fast += 1
                fast_count += 1
                max_consecutive_fast = max(max_consecutive_fast, consecutive_fast)
            else:
                consecutive_fast = 0
        
        is_speeder = (
            avg_time < self.min_time_per_item or 
            max_consecutive_fast >= 3
        )
        
        return is_speeder, {
            "avg_time": round(avg_time, 2),
            "min_time": round(min_time, 2),
            "max_time": round(max_time, 2),
            "max_consecutive_fast": max_consecutive_fast,
            "fast_count": fast_count,
            "fast_ratio": round(fast_count / len(times), 3),
            "threshold": self.min_time_per_item,
            "is_flagged": is_speeder
        }
    
    def _check_longstring(self, responses: List[int]) -> Tuple[bool, Dict]:
        """
        동일 응답 연속 횟수 분석
        
        감지 패턴:
        - 동일 응답이 10개 이상 연속
        
        연구 근거:
        - Johnson (2005): 연속 10+ → 부주의 의심
        - Meade & Craig (2012): 연속 15+ → 99% 부주의
        """
        max_streak = 1
        current_streak = 1
        streaks = []  # 모든 연속 구간 기록
        
        for i in range(1, len(responses)):
            if responses[i] == responses[i-1]:
                current_streak += 1
            else:
                if current_streak >= 5:  # 5개 이상만 기록
                    streaks.append({
                        "value": responses[i-1],
                        "length": current_streak,
                        "start_index": i - current_streak
                    })
                max_streak = max(max_streak, current_streak)
                current_streak = 1
        
        # 마지막 구간 체크
        if current_streak >= 5:
            streaks.append({
                "value": responses[-1],
                "length": current_streak,
                "start_index": len(responses) - current_streak
            })
        max_streak = max(max_streak, current_streak)
        
        is_longstring = max_streak >= self.longstring_threshold
        
        return is_longstring, {
            "max_streak": max_streak,
            "threshold": self.longstring_threshold,
            "long_streaks": streaks,
            "is_flagged": is_longstring
        }
    
    def _check_consistency(self, responses: List[int]) -> Tuple[bool, Dict]:
        """
        짝수/홀수 일관성 검사
        
        감지 패턴:
        - 짝수 번호 질문과 홀수 번호 질문의 상관계수 < 0.3
        
        연구 근거:
        - Jackson (1976): r < 0.5 → 부주의 의심
        - Ward & Meade (2023): r < 0.3 → 제거 권장
        """
        # 최소 20개 이상 응답이 있어야 신뢰 가능
        if len(responses) < 20:
            return False, {
                "error": "Too few responses for consistency check",
                "is_flagged": False
            }
        
        even_items = [responses[i] for i in range(0, len(responses), 2)]
        odd_items = [responses[i] for i in range(1, len(responses), 2)]
        
        # 길이 맞추기 (홀수 개수일 경우)
        min_len = min(len(even_items), len(odd_items))
        even_items = even_items[:min_len]
        odd_items = odd_items[:min_len]
        
        # Pearson 상관계수
        try:
            correlation = np.corrcoef(even_items, odd_items)[0, 1]
            
            # NaN 체크 (분산이 0일 때 발생)
            if np.isnan(correlation):
                correlation = 0.0
        except:
            correlation = 0.0
        
        is_inconsistent = correlation < self.correlation_threshold
        
        return is_inconsistent, {
            "correlation": round(float(correlation), 3),
            "threshold": self.correlation_threshold,
            "even_items_count": len(even_items),
            "odd_items_count": len(odd_items),
            "even_mean": round(float(np.mean(even_items)), 2),
            "odd_mean": round(float(np.mean(odd_items)), 2),
            "is_flagged": is_inconsistent
        }
    
    def _check_mahalanobis(self, 
                          responses: List[int], 
                          reference_data: np.ndarray) -> Tuple[bool, Dict]:
        """
        통계적 이상치 감지 (Mahalanobis Distance)
        
        감지 패턴:
        - D² > χ²(p=0.001) → 통계적으로 매우 이상한 응답 패턴
        
        연구 근거:
        - Mahalanobis (1936): 다변량 이상치 감지 기법
        - Ward & Meade (2023): D² 기반 스크리닝 권장
        """
        try:
            mean = np.mean(reference_data, axis=0)
            cov = np.cov(reference_data.T)
            
            # 특이값 방지 (공분산 행렬이 singular일 때)
            try:
                inv_cov = np.linalg.inv(cov)
            except np.linalg.LinAlgError:
                # 역행렬 계산 실패 시 pseudo-inverse 사용
                inv_cov = np.linalg.pinv(cov)
            
            diff = np.array(responses) - mean
            distance = np.sqrt(diff.T @ inv_cov @ diff)
            
            # Chi-square 임계값
            df = len(responses)
            chi2_threshold = stats.chi2.ppf(1 - self.mahalanobis_p_threshold, df)
            
            is_outlier = distance**2 > chi2_threshold
            p_value = float(1 - stats.chi2.cdf(distance**2, df))
            
            return is_outlier, {
                "distance": round(float(distance), 3),
                "distance_squared": round(float(distance**2), 3),
                "chi2_threshold": round(float(chi2_threshold), 3),
                "p_value": round(p_value, 6),
                "is_flagged": is_outlier
            }
        except Exception as e:
            return False, {
                "error": str(e),
                "is_flagged": False
            }
    
    def _check_low_variance(self, responses: List[int]) -> Tuple[bool, Dict]:
        """
        응답 분산 분석 (너무 일관된 응답 감지)
        
        감지 패턴:
        - 응답의 분산 < 0.3 (예: 거의 모든 응답이 동일)
        """
        variance = np.var(responses)
        is_low_variance = variance < self.variance_threshold
        
        return is_low_variance, {
            "variance": round(float(variance), 3),
            "threshold": self.variance_threshold,
            "is_flagged": is_low_variance
        }

    def _calculate_quality_score(self, flags: List[str], details: Dict) -> float:
        """
        품질 점수 계산 (0-1)
        
        가중치:
        - response_time: 30%
        - longstring: 25%
        - consistency: 25%
        - mahalanobis: 20%
        """
        score = 1.0
        
        # 응답 시간 (30%)
        if "response_time" in details and "avg_time" in details["response_time"]:
            rt = details["response_time"]
            avg_time = rt["avg_time"]
            
            if avg_time < self.min_time_per_item:
                # 2초 미만 → 최대 30% 감점
                penalty = 0.3 * (self.min_time_per_item - avg_time) / self.min_time_per_item
                score -= penalty
            
            # 너무 빠른 응답 비율 추가 감점
            if "fast_ratio" in rt and rt["fast_ratio"] > 0.3:
                score -= 0.1 * rt["fast_ratio"]
        
        # Longstring (25%)
        if "longstring" in details and "max_streak" in details["longstring"]:
            ls = details["longstring"]
            max_streak = ls["max_streak"]
            
            if max_streak >= self.longstring_threshold:
                # 10개 이상 → 최대 25% 감점
                penalty = 0.25 * min(max_streak / 20, 1.0)
                score -= penalty
        
        # 일관성 (25%)
        if "consistency" in details and "correlation" in details["consistency"]:
            cons = details["consistency"]
            correlation = cons["correlation"]
            
            if correlation < self.correlation_threshold:
                # r < 0.3 → 최대 25% 감점
                penalty = 0.25 * (self.correlation_threshold - correlation) / self.correlation_threshold
                score -= penalty
        
        # Mahalanobis (20%)
        if "mahalanobis" in details and "p_value" in details["mahalanobis"]:
            maha = details["mahalanobis"]
            p_value = maha["p_value"]
            
            if p_value < 0.01:
                score -= 0.20
        
        # Low Variance (20%)
        if "variance" in details and details["variance"]["is_flagged"]:
            # 분산이 너무 낮으면 감점
            score -= 0.20
        
        return max(0.0, min(1.0, score))
    
    def _get_recommendation(self, quality_score: float, flags: List[str]) -> str:
        """
        품질 점수 기반 권장사항
        
        Returns:
            - "excellent": 우수 (0.8+)
            - "acceptable": 허용 가능 (0.6-0.8)
            - "warning": 경고 (0.4-0.6)
            - "reject": 거부 (0.4 미만)
        """
        if quality_score >= 0.8:
            return "excellent"
        elif quality_score >= 0.6:
            return "acceptable"
        elif quality_score >= 0.4:
            return "warning"
        else:
            return "reject"


# ==================== 테스트 코드 ====================

def test_detector():
    """감지기 테스트"""
    detector = CarelessResponseDetector()
    
    print("="*60)
    print("부주의 응답 감지기 테스트")
    print("="*60)
    
    # 테스트 1: 정상 응답
    print("\n[테스트 1] 정상 응답")
    good_responses = [3, 2, 4, 1, 3, 4, 2, 3, 1, 2] * 5
    good_times = [4.5, 3.2, 5.1, 3.8, 4.2, 3.9, 4.6, 3.7, 4.1, 3.5] * 5
    
    result = detector.analyze(good_responses, good_times)
    print(f"  부주의 여부: {result.is_careless}")
    print(f"  품질 점수: {result.quality_score:.2f}")
    print(f"  플래그: {result.flags}")
    print(f"  권장사항: {result.recommendation}")
    
    # 테스트 2: 부주의 응답 (Speeder)
    print("\n[테스트 2] 부주의 응답 - Speeder")
    fast_responses = [2, 3, 2, 4, 2, 3, 2, 4, 2, 3] * 5
    fast_times = [0.5, 0.4, 0.6, 0.5, 0.5, 0.4, 0.5, 0.6, 0.5, 0.4] * 5
    
    result = detector.analyze(fast_responses, fast_times)
    print(f"  부주의 여부: {result.is_careless}")
    print(f"  품질 점수: {result.quality_score:.2f}")
    print(f"  플래그: {result.flags}")
    print(f"  권장사항: {result.recommendation}")
    print(f"  평균 응답 시간: {result.details['response_time']['avg_time']}초")
    
    # 테스트 3: 부주의 응답 (Longstring)
    print("\n[테스트 3] 부주의 응답 - Longstring")
    long_responses = [2] * 50  # 모두 2번
    normal_times = [3.5] * 50
    
    result = detector.analyze(long_responses, normal_times)
    print(f"  부주의 여부: {result.is_careless}")
    print(f"  품질 점수: {result.quality_score:.2f}")
    print(f"  플래그: {result.flags}")
    print(f"  권장사항: {result.recommendation}")
    print(f"  최대 연속: {result.details['longstring']['max_streak']}개")
    
    # 테스트 4: 부주의 응답 (불일치)
    print("\n[테스트 4] 부주의 응답 - 불일치")
    random_responses = list(np.random.randint(1, 5, 50))
    normal_times2 = [3.5] * 50
    
    result = detector.analyze(random_responses, normal_times2)
    print(f"  부주의 여부: {result.is_careless}")
    print(f"  품질 점수: {result.quality_score:.2f}")
    print(f"  플래그: {result.flags}")
    print(f"  권장사항: {result.recommendation}")
    if "consistency" in result.details:
        print(f"  짝수/홀수 상관: {result.details['consistency']['correlation']:.3f}")
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    test_detector()
