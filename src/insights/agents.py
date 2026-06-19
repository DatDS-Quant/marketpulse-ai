from typing import List
from .schemas import InsightCard

class BannedPhrasesReviewerAgent:
    BANNED_PHRASES = [
        "will dominate", "guarantees", "definitely", 
        "revenue will", "invest immediately", "guaranteed demand",
        "guaranteed growth", "must invest", "certain to", "explode in revenue"
    ]
    
    @classmethod
    def contains_banned_phrases(cls, text: str) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        for phrase in cls.BANNED_PHRASES:
            if phrase in text_lower:
                return True
        return False
        
    @classmethod
    def review_insights(cls, insights: List[InsightCard]) -> bool:
        """Returns True if all insights pass the check, False if any insight violates rules."""
        for card in insights:
            if cls.contains_banned_phrases(card.factual_explanation) or \
               cls.contains_banned_phrases(card.business_implication) or \
               cls.contains_banned_phrases(card.recommended_next_step) or \
               cls.contains_banned_phrases(card.limitation):
                return False
        return True
