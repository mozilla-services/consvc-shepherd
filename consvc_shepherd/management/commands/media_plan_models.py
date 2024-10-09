"""Dataclasses for working with Media Plans"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List


@dataclass(frozen=True)
class BoostrDealMediaPlanLineItem:
    """Line Items for Boostr Media plans. These have the CPM/CPC and impression count data we're looking for"""

    media_plan_line_item_id: int
    boostr_deal: int
    boostr_product: int
    rate_type: str
    rate: Decimal
    quantity: Decimal
    budget: Decimal
    month: str

    def __str__(self) -> str:
        return f"{self.boostr_product}"


@dataclass
class BoostrMediaPlan:
    """Media Plan For Boostr Deals. Each Media Plan can have multiple line items which links BoostrDeals
    to Products. It also stores the cost, and quantity """

    media_plan_id: int
    name: str
    boostr_deal: int
    line_items: Dict[
        int,
        Dict[int, List[BoostrDealMediaPlanLineItem]],
    ] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.name}"

    def add_line_item(self, line_item: BoostrDealMediaPlanLineItem):
        """Add a line item to a media plan"""
        if self.boostr_deal not in self.line_items:
            self.line_items[self.boostr_deal] = {}
        if line_item.boostr_product not in self.line_items[self.boostr_deal]:
            self.line_items[self.boostr_deal][line_item.boostr_product] = []
            self.line_items[self.boostr_deal][line_item.boostr_product].append(
                line_item
            )


@dataclass
class MediaPlanCollection:
    """An in-memory collection for storing Media Plans as they are read from the Boostr API."""

    media_plans: Dict[int, BoostrMediaPlan] = field(default_factory=dict)

    def add_media_plan(self, boostr_plan: int, media_plan: BoostrMediaPlan):
        """Add a media plan to the collection"""
        if boostr_plan not in self.media_plans:
            self.media_plans[boostr_plan] = media_plan
