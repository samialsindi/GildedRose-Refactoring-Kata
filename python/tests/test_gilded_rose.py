""" Replacing this stub with what the rules say the system should do.
    This with test_currentstate.py, which records behaviour today, answer the problem statement when completed.

    The requirements name four thresholds. Every one of them is an inequality, so
    every one of them has an off-by-one on either side:

        "once the sell by date has passed"        -> boundary at sell_in 0 / -1
        "10 days or less"  -> +2                  -> boundary at sell_in 11 / 10
        "5 days or less"   -> +3                  -> boundary at sell_in 6 / 5
        "never negative" / "never more than 50"   -> boundaries at quality 0 and 50

    Rule of thumb used throughout: for every threshold, test the value on each side
    of it, not a value comfortably inside the range. A test at sell_in 8 proves
    almost nothing; a pair at 11 and 10 proves the tier edge is where it claims.

    The expected values below were not reasoned out of the source. They were read
    off the running code, before any of it was changed:

    def step(name, s, q):
        it = Item(name, s, q)
        GildedRose([it]).update_quality()
        return it.sell_in, it.quality

    step("+5 Dexterity Vest", 1, 20)   -> (0, 19)     loses 1
    step("+5 Dexterity Vest", 0, 20)   -> (-1, 18)    loses 2   <-- surprise
    step(BACKSTAGE_PASS,     11, 20)   -> (10, 21)    +1
    step(BACKSTAGE_PASS,     10, 20)   -> (9, 22)     +2
    step(BACKSTAGE_PASS,      6, 20)   -> (5, 22)     +2
    step(BACKSTAGE_PASS,      5, 20)   -> (4, 23)     +3
    step(SULFURAS,            0, 10)   -> (0, 10)     untouched, not forced to 80

    
    1. An item starting the day ON its sell-by date (sell_in == 0) loses TWO, not
    one. The code decrements sell_in first and tests expiry afterwards, so by
    the time quality is settled the date has already passed. Writing this test
    from the requirements alone gives 19, and it fails.

    2. A cap test starting at quality 49 cannot tell the tiers apart: +1, +2 and
    +3 all land on 50, so it passes whether the tier logic works or not. The
    +3 case therefore starts at 48, where 48+3 overshoots and must clamp, but
    48+1 would give 49 and fail. The +2 case keeps 49 on purpose: it is there
    to exercise the clamp itself, not the tier. Two tests, two different jobs.
    """

import pytest
from gilded_rose import GildedRose, Item

DEXTERITY_VEST = "+5 Dexterity Vest"
AGED_BRIE = "Aged Brie"
BACKSTAGE_PASS = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"

def update(name: str, sell_in: int, quality: int) -> Item:
    item = Item(name, sell_in, quality)
    GildedRose([item]).update_quality()
    return item

class TestOrdinaryItems:
    def test_sell_in_and_quality_both_drop_by_one(self):
        item = update(DEXTERITY_VEST, 10, 20)
        assert (item.sell_in, item.quality) == (9, 19)

    @pytest.mark.parametrize(("sell_in", "expected"), [
        pytest.param(2, 19, id="before-sell-by"),
        pytest.param(1, 19, id="last-day-before-sell-by"),
        pytest.param(0, 18, id="sell-by-day-itself-degrades-twice"),
        pytest.param(-1, 18, id="past-sell-by"),
    ])
    def test_degrades_twice_as_fast_once_sell_by_passed(self, sell_in, expected):
        assert update(DEXTERITY_VEST, sell_in, 20).quality == expected

    @pytest.mark.parametrize(("sell_in", "quality"), [
        pytest.param(5, 0, id="before-sell-by"),
        pytest.param(0, 0, id="on-sell-by-date"),
        pytest.param(-5, 1, id="past-sell-by-one-left"),
    ])
    def test_quality_never_negative(self, sell_in, quality):
        assert update(DEXTERITY_VEST, sell_in, quality).quality == 0

class TestAgedBrie:
    @pytest.mark.parametrize(("sell_in", "expected"), [
        pytest.param(2, 11, id="before-sell-by-gains-one"),
        pytest.param(0, 12, id="on-sell-by-date-gains-two"),
        pytest.param(-1, 12, id="past-sell-by-gains-two"),
    ])
    def test_improves_with_age(self, sell_in, expected):
        assert update(AGED_BRIE, sell_in, 10).quality == expected

    @pytest.mark.parametrize("sell_in", [5, 0, -5])
    def test_never_above_fifty(self, sell_in):
        assert update(AGED_BRIE, sell_in, 50).quality == 50

    def test_stops_at_fifty_not_overshoot(self):
        assert update(AGED_BRIE, -1, 49).quality == 50

class TestBackstagePasses:
    @pytest.mark.parametrize(("sell_in", "expected"), [
        pytest.param(12, 21, id="over-ten-days-gains-one"),
        pytest.param(11, 21, id="eleven-days-still-one"),
        pytest.param(10, 22, id="ten-days-gains-two"),
        pytest.param(6, 22, id="six-days-gains-two"),
        pytest.param(5, 23, id="five-days-gains-three"),
        pytest.param(1, 23, id="final-day-gains-three"),
    ])
    def test_gains_faster_as_concert_nears(self, sell_in, expected):
        assert update(BACKSTAGE_PASS, sell_in, 20).quality == expected

    @pytest.mark.parametrize("quality", [0, 20, 50])
    @pytest.mark.parametrize("sell_in", [0, -1])
    def test_worthless_after_concert(self, sell_in, quality):
        assert update(BACKSTAGE_PASS, sell_in, quality).quality == 0

    @pytest.mark.parametrize(("sell_in", "quality"), [
        pytest.param(10, 49, id="would-gain-two"),
        pytest.param(5, 48, id="would-gain-three"),
    ])
    def test_never_above_fifty(self, sell_in, quality):
        assert update(BACKSTAGE_PASS, sell_in, quality).quality == 50

class TestSulfuras:
    @pytest.mark.parametrize("sell_in", [5, 0, -1])
    def test_never_changes(self, sell_in):
        item = update(SULFURAS, sell_in, 80)
        assert (item.sell_in, item.quality) == (sell_in, 80)

class TestWholeInventory:
    def test_every_item_in_list_updated(self):
        items = [Item(DEXTERITY_VEST, 10, 20), Item(AGED_BRIE, 2, 0),
                 Item(SULFURAS, 0, 80), Item(BACKSTAGE_PASS, 15, 20)]
        GildedRose(items).update_quality()
        assert [(i.sell_in, i.quality) for i in items] == [(9, 19), (1, 1), (0, 80), (14, 21)]