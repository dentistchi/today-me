"""
응답 스타일 보정기 (Response Style Corrector)
Phase 1 핵심 모듈

학술 근거:
- Böckenholt & Meiser (2017): British Journal of Mathematical and Statistical Psychology
- Van Vaerenbergh & Thomas (2013): International Journal of Public Opinion Research
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CorrectionResult:
    """보정 결과"""
    corrected_responses: List[int]
    corrections_applied: List[str]
    original_responses: List[int]
    style_scores: Dict
    timestamp: str


class ResponseStyleCorrector:
    """
    응답 스타일 편향 보정
    
    3가지 보정 기법:
    1. Extreme Responding (극단 응답)
    2. Midpoint Responding (중간 응답)
    3. Acquiescence Bias (긍정 편향)
    """
    
    def __init__(self,
                 extreme_threshold: float = 0.7,
                 midpoint_threshold: float = 0.7,
                 acquiescence_threshold: float = 0.7):
        """
        Parameters:
            extreme_threshold: 극단 응답 비율 임계값
            midpoint_threshold: 중간 응답 비율 임계값
            acquiescence_threshold: 긍정 편향 임계값
        """
        self.extreme_threshold = extreme_threshold
        self.midpoint_threshold = midpoint_threshold
        self.acquiescence_threshold = acquiescence_threshold
    
    def correct(self, 
                responses: List[int], 
                reverse_items: List[int] = None) -> CorrectionResult:
        """
        통합 보정 실행
        
        Args:
            responses: 응답 리스트 (1-4 척도)
            reverse_items: 역문항 인덱스 리스트 (선택)
        
        Returns:
            CorrectionResult 객체
        """
        corrected = responses.copy()
        corrections = []
        
        # 스타일 점수 계산
        ers = self._calc_extreme_responding(responses)
        mrs = self._calc_midpoint_responding(responses)
        aq = 0.0
        
        # 1) Extreme Responding 보정
        if ers > self.extreme_threshold:
            corrected = self._correct_extreme(corrected)
            corrections.append("extreme_responding")
        
        # 2) Midpoint Responding 보정
        if mrs > self.midpoint_threshold:
            corrected = self._correct_midpoint(corrected)
            corrections.append("midpoint_responding")
        
        # 3) Acquiescence Bias 보정
        if reverse_items is not None and len(reverse_items) > 0:
            aq = self._calc_acquiescence(responses, reverse_items)
            if aq > self.acquiescence_threshold:
                corrected = self._correct_acquiescence(corrected, reverse_items)
                corrections.append("acquiescence_bias")
        
        return CorrectionResult(
            corrected_responses=corrected,
            corrections_applied=corrections,
            original_responses=responses.copy(),
            style_scores={
                "extreme_responding": round(ers, 3),
                "midpoint_responding": round(mrs, 3),
                "acquiescence": round(aq, 3) if reverse_items else None
            },
            timestamp=datetime.now().isoformat()
        )
    
    def _calc_extreme_responding(self, responses: List[int]) -> float:
        """
        극단 응답 비율 계산
        
        ERS = (N_1 + N_4) / N_total
        
        연구 근거:
        - Greenleaf (1992): ERS > 0.7 → 보정 필요
        """
        extreme_count = responses.count(1) + responses.count(4)
        return extreme_count / len(responses)
    
    def _calc_midpoint_responding(self, responses: List[int]) -> float:
        """
        중간 응답 비율 계산
        
        MRS = (N_2 + N_3) / N_total
        """
        midpoint_count = responses.count(2) + responses.count(3)
        return midpoint_count / len(responses)
    
    def _calc_acquiescence(self, 
                          responses: List[int], 
                          reverse_items: List[int]) -> float:
        """
        긍정 편향 비율 계산
        
        정방향-역방향 질문 쌍의 불일치 비율
        
        연구 근거:
        - Paulhus (1991): Acquiescence bias 이론
        """
        mismatches = 0
        pairs = 0
        
        # 연속된 정방향-역방향 쌍 찾기
        for i in range(len(responses) - 1):
            # 현재 질문이 역방향이고 다음이 정방향 (or 반대)
            if (i in reverse_items) != ((i+1) in reverse_items):
                pairs += 1
                
                # 예상: 질문이 반대이므로 응답도 반대여야 함
                # 1↔4, 2↔3 형태로 대응
                expected_sum = 5  # 1+4=5, 2+3=5
                actual_sum = responses[i] + responses[i+1]
                
                # 허용 오차 1 (2+2=4, 3+3=6도 일부 허용)
                if abs(actual_sum - expected_sum) > 1:
                    mismatches += 1
        
        return mismatches / pairs if pairs > 0 else 0.0
    
    def _correct_extreme(self, responses: List[int]) -> List[int]:
        """
        극단 응답 정규화
        
        방법: Z-score 정규화 후 1-4 척도로 재매핑
        
        연구 근거:
        - Greenleaf (1992): 극단 응답 보정 알고리즘
        """
        # 분산이 너무 작으면 보정 불가
        std = np.std(responses)
        if std < 0.1:
            return responses
        
        # Z-score 정규화
        mean = np.mean(responses)
        normalized = [(r - mean) / std for r in responses]
        
        # Z-score → 1-4 척도
        # Z=-2 → 1, Z=0 → 2.5, Z=+2 → 4
        corrected = []
        for z in normalized:
            # 표준편차 0.75로 스케일 (너무 극단적이지 않게)
            score = 2.5 + z * 0.75
            score = max(1.0, min(4.0, score))  # 1-4 범위 제한
            corrected.append(int(round(score)))
        
        return corrected
    
    def _correct_midpoint(self, responses: List[int]) -> List[int]:
        """
        중간 응답 분산 증가
        
        방법: 2,3 응답에 미세한 변화 추가
        
        연구 근거:
        - Van Vaerenbergh & Thomas (2013): 중간 응답 보정
        """
        mean = np.mean(responses)
        corrected = []
        
        for r in responses:
            if r in [2, 3]:
                # 평균 대비 위치에 따라 조정
                if r > mean:
                    # 평균보다 높으면 더 올림
                    adjustment = 0.5
                elif r < mean:
                    # 평균보다 낮으면 더 내림
                    adjustment = -0.5
                else:
                    # 평균과 같으면 약간의 랜덤성
                    adjustment = 0.3 if r == 3 else -0.3
                
                new_score = r + adjustment
                corrected.append(int(round(max(1, min(4, new_score)))))
            else:
                corrected.append(r)
        
        return corrected
    
    def _correct_acquiescence(self, 
                             responses: List[int],
                             reverse_items: List[int]) -> List[int]:
        """
        긍정 편향 보정
        
        방법: 역방향 문항의 스케일을 뒤집기
        
        연구 근거:
        - Paulhus (1991): 긍정 편향 제거 알고리즘
        """
        corrected = responses.copy()
        
        for idx in reverse_items:
            if idx < len(corrected):
                # 1↔4, 2↔3 뒤집기
                corrected[idx] = 5 - responses[idx]
        
        return corrected
    
    def get_style_interpretation(self, style_scores: Dict) -> Dict:
        """
        스타일 점수 해석
        
        Returns:
            각 스타일에 대한 해석 메시지
        """
        interpretations = {}
        
        # Extreme Responding
        ers = style_scores.get("extreme_responding", 0)
        if ers > 0.8:
            interpretations["extreme_responding"] = {
                "level": "very_high",
                "message": "거의 모든 질문에 극단적으로 응답하셨습니다 (1번 또는 4번).",
                "recommendation": "중간 정도의 응답도 고려해보세요."
            }
        elif ers > 0.6:
            interpretations["extreme_responding"] = {
                "level": "high",
                "message": "많은 질문에 극단적으로 응답하셨습니다.",
                "recommendation": "일부 질문에서 2번이나 3번도 선택해보세요."
            }
        else:
            interpretations["extreme_responding"] = {
                "level": "normal",
                "message": "극단 응답 경향이 정상 범위입니다.",
                "recommendation": None
            }
        
        # Midpoint Responding
        mrs = style_scores.get("midpoint_responding", 0)
        if mrs > 0.8:
            interpretations["midpoint_responding"] = {
                "level": "very_high",
                "message": "대부분 2번이나 3번으로 응답하셨습니다.",
                "recommendation": "확신이 있다면 1번이나 4번도 선택해보세요."
            }
        elif mrs > 0.6:
            interpretations["midpoint_responding"] = {
                "level": "high",
                "message": "중간 응답을 많이 선택하셨습니다.",
                "recommendation": "명확한 의견이 있다면 극단을 선택해도 괜찮습니다."
            }
        else:
            interpretations["midpoint_responding"] = {
                "level": "normal",
                "message": "중간 응답 경향이 정상 범위입니다.",
                "recommendation": None
            }
        
        # Acquiescence
        aq = style_scores.get("acquiescence")
        if aq is not None:
            if aq > 0.7:
                interpretations["acquiescence"] = {
                    "level": "high",
                    "message": "모든 질문에 긍정적으로 응답하는 경향이 있습니다.",
                    "recommendation": "반대 의견을 묻는 질문도 주의 깊게 읽어주세요."
                }
            else:
                interpretations["acquiescence"] = {
                    "level": "normal",
                    "message": "긍정 편향이 정상 범위입니다.",
                    "recommendation": None
                }
        
        return interpretations


# ==================== 테스트 코드 ====================

def test_corrector():
    """보정기 테스트"""
    corrector = ResponseStyleCorrector()
    
    print("="*60)
    print("응답 스타일 보정기 테스트")
    print("="*60)
    
    # 테스트 1: 극단 응답
    print("\n[테스트 1] 극단 응답 (Extreme Responding)")
    extreme_responses = [1, 4, 1, 4, 1, 4, 1, 4, 1, 4] * 5
    
    result = corrector.correct(extreme_responses)
    print(f"  보정 전 ERS: {result.style_scores['extreme_responding']:.2f}")
    print(f"  적용된 보정: {result.corrections_applied}")
    print(f"  보정 전 (처음 10개): {result.original_responses[:10]}")
    print(f"  보정 후 (처음 10개): {result.corrected_responses[:10]}")
    
    # 테스트 2: 중간 응답
    print("\n[테스트 2] 중간 응답 (Midpoint Responding)")
    midpoint_responses = [2, 3, 2, 3, 2, 3, 2, 3, 2, 3] * 5
    
    result = corrector.correct(midpoint_responses)
    print(f"  보정 전 MRS: {result.style_scores['midpoint_responding']:.2f}")
    print(f"  적용된 보정: {result.corrections_applied}")
    print(f"  보정 전 (처음 10개): {result.original_responses[:10]}")
    print(f"  보정 후 (처음 10개): {result.corrected_responses[:10]}")
    
    # 테스트 3: 긍정 편향
    print("\n[테스트 3] 긍정 편향 (Acquiescence Bias)")
    aq_responses = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4] * 5  # 모두 4번
    reverse_items = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]  # 짝수 인덱스를 역문항으로
    
    result = corrector.correct(aq_responses, reverse_items)
    print(f"  보정 전 AQ: {result.style_scores['acquiescence']:.2f}")
    print(f"  적용된 보정: {result.corrections_applied}")
    print(f"  보정 전 (처음 10개): {result.original_responses[:10]}")
    print(f"  보정 후 (처음 10개): {result.corrected_responses[:10]}")
    print(f"  역문항 인덱스: {reverse_items[:5]}...")
    
    # 테스트 4: 정상 응답 (보정 불필요)
    print("\n[테스트 4] 정상 응답")
    normal_responses = [3, 2, 4, 1, 3, 4, 2, 3, 1, 2] * 5
    
    result = corrector.correct(normal_responses, reverse_items)
    print(f"  ERS: {result.style_scores['extreme_responding']:.2f}")
    print(f"  MRS: {result.style_scores['midpoint_responding']:.2f}")
    print(f"  AQ: {result.style_scores['acquiescence']:.2f}")
    print(f"  적용된 보정: {result.corrections_applied if result.corrections_applied else '없음'}")
    
    # 테스트 5: 해석 메시지
    print("\n[테스트 5] 스타일 해석")
    interpretations = corrector.get_style_interpretation({
        "extreme_responding": 0.85,
        "midpoint_responding": 0.10,
        "acquiescence": 0.75
    })
    
    for style, interp in interpretations.items():
        print(f"\n  [{style}]")
        print(f"    수준: {interp['level']}")
        print(f"    메시지: {interp['message']}")
        if interp['recommendation']:
            print(f"    권장사항: {interp['recommendation']}")
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    test_corrector()
