"""Current state test

    This checks the current behaviour to ensure that changes do not regress except where desired.
"""

from itertools import product
from approvaltests import verify
from gilded_rose import *

ITEM_NAMES = [
    "+5 Dexterity Vest",
    "Aged Brie",
    "Backstage passes to a TAFKAL80ETC concert",
    "Sulfuras, Hand of Ragnaros",
    "Conjured Mana Cake",
]

SELL_IN_VALUES = range(12, -3, -1) # Straddles every threshold - 11/10 and 6/5 backstage tiers, and the sel-by boundary
 
# Floor, mid-range, both sides of the cap, and one out-of-range value (51)
QUALITY_VALUES = [0, 1, 2, 3, 6, 10, 48, 49, 50, 51]

def _after_one_day(name: str, sell_in: int, quality: int) -> Item:
    item = Item(name, sell_in, quality)
    GildedRose([item]).update_quality()
    return item

def test_one_day_for_every_item_across_all_boundaries() -> None:
    rows = [f"{'name':<42} | {'sell_in':>7} | {'quality':>7} -> {'sell_in':>7} | {'quality':>7}"]
    for name, sell_in, quality in product(ITEM_NAMES, SELL_IN_VALUES, QUALITY_VALUES):
        after = _after_one_day(name, sell_in, quality)
        rows.append(
            f"{name:<42} | {sell_in:>7} | {quality:>7} -> {after.sell_in:>7} | {after.quality:>7}"
        )
    verify("\n".join(rows)) 