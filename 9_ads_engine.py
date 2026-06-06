"""
Ads Engine — Auction system, targeting, budgeting, frequency capping
Powers Facebook's ad serving with real-time bidding simulation.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class BidType(Enum):
    CPM = "CPM"  # Cost Per Mille (1000 impressions)
    CPC = "CPC"  # Cost Per Click
    CPA = "CPA"  # Cost Per Action


@dataclass
class AdTargeting:
    age_range: Tuple[int, int]  # (min, max)
    countries: List[str]
    interests: List[str]
    lookalike_seed: Optional[str] = None
    excluded_audiences: List[str] = None


@dataclass
class Ad:
    id: str
    advertiser_id: str
    title: str
    description: str
    cta_text: str  # Call-To-Action button text
    targeting: AdTargeting
    bid_amount: float
    bid_type: str  # "CPM", "CPC", "CPA"
    daily_budget: float
    lifetime_budget: float
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0


@dataclass
class UserProfile:
    user_id: str
    age: int
    gender: str  # "M", "F", "Other"
    country: str
    interests: List[str]
    past_purchases: Dict  # category -> [items]


@dataclass
class AdServeResult:
    winning_ad: Ad
    predicted_ctr: float  # Click-through rate
    clearing_price: float  # Price advertiser pays


class AdsEngine:
    """Auction-based ad serving engine."""

    def __init__(self):
        self.ads: Dict[str, Ad] = {}  # ad_id -> ad
        self.freq_cap: Dict[str, int] = {}  # user_id -> count (ads shown today)
        self.max_freq_per_day = 5  # Max ads per user per day

    def register_ad(self, ad: Ad):
        """Register an ad in the system."""
        self.ads[ad.id] = ad

    def serve(self, user: UserProfile) -> Optional[AdServeResult]:
        """Serve the best ad for a user using auction."""
        # Check frequency cap
        if user.user_id in self.freq_cap and self.freq_cap[user.user_id] >= self.max_freq_per_day:
            return None
        
        # Find eligible ads
        eligible = self._get_eligible_ads(user)
        if not eligible:
            return None
        
        # Auction: rank by score
        ranked = []
        for ad in eligible:
            score = self._compute_auction_score(ad, user)
            ranked.append((ad, score))
        
        # Sort by score (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        if not ranked:
            return None
        
        winning_ad = ranked[0][0]
        
        # Check budget
        if winning_ad.spend >= winning_ad.daily_budget:
            return None
        
        # Compute metrics
        predicted_ctr = self._predict_ctr(winning_ad, user)
        clearing_price = self._second_price_auction(ranked)
        
        # Update ad
        winning_ad.impressions += 1
        winning_ad.spend += clearing_price
        
        # Update frequency cap
        self.freq_cap[user.user_id] = self.freq_cap.get(user.user_id, 0) + 1
        
        return AdServeResult(
            winning_ad=winning_ad,
            predicted_ctr=predicted_ctr,
            clearing_price=clearing_price
        )

    def _get_eligible_ads(self, user: UserProfile) -> List[Ad]:
        """Filter ads eligible for a user based on targeting."""
        eligible = []
        
        for ad in self.ads.values():
            # Check age
            if not (ad.targeting.age_range[0] <= user.age <= ad.targeting.age_range[1]):
                continue
            
            # Check country
            if user.country not in ad.targeting.countries:
                continue
            
            # Check interests (at least one match)
            if ad.targeting.interests:
                if not any(i in user.interests for i in ad.targeting.interests):
                    continue
            
            # Check budget
            if ad.spend >= ad.daily_budget:
                continue
            
            eligible.append(ad)
        
        return eligible

    def _compute_auction_score(self, ad: Ad, user: UserProfile) -> float:
        """Compute auction score (bid + quality)."""
        # Base score from bid
        score = ad.bid_amount
        
        # Quality multiplier (CTR prediction)
        ctr = self._predict_ctr(ad, user)
        score *= (1 + ctr)
        
        return score

    def _predict_ctr(self, ad: Ad, user: UserProfile) -> float:
        """Predict click-through rate (ML model simplified)."""
        ctr = 0.02  # baseline 2%
        
        # Boost if interests match
        matches = sum(1 for i in ad.targeting.interests if i in user.interests)
        ctr += matches * 0.01
        
        # Boost if past purchase history matches
        if ad.id in user.past_purchases:
            ctr += 0.05
        
        return min(ctr, 0.15)  # Cap at 15%

    def _second_price_auction(self, ranked: List[Tuple[Ad, float]]) -> float:
        """Compute second-price auction (Vickrey auction)."""
        if len(ranked) < 2:
            return ranked[0][0].bid_amount * 0.5  # No competition, pay 50% of bid
        
        # Pay second-highest score's bid
        second_price = ranked[1][0].bid_amount
        return second_price
