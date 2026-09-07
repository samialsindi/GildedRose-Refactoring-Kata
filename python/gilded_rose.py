# -*- coding: utf-8 -*-
AGED_BRIE = "Aged Brie"
BACKSTAGE_PASS = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"

MIN_QUALITY = 0
MAX_QUALITY = 50

def _raise_quality(item, amount=1):
    # Cap restrains increases; it does not pull an out-of-range value down.
    if item.quality < MAX_QUALITY:
        item.quality = min(item.quality + amount, MAX_QUALITY)

def _lower_quality(item, amount=1):
    if item.quality > MIN_QUALITY:
        item.quality = max(item.quality - amount, MIN_QUALITY)

class ItemUpdater:
    'Age the quality, move a day closer, and if the date has passed, age again'

    def update(self, item):
        self._age(item)
        item.sell_in -= 1

        if item.sell_in < 0:
            self._age_past_sell_by(item)

    def _age(self, item):
        raise NotImplementedError

    def _age_past_sell_by(self, item):
        self._age(item)

class DegradingItemUpdater(ItemUpdater):
    RATE = 1

    def _age(self, item):
        _lower_quality(item, self.RATE)

class ConjuredItemUpdater(ItemUpdater):
    RATE = 2

    def _age(self, item):
        _lower_quality(item, self.RATE)

class AgedBrieUpdater(ItemUpdater):
    def _age(self, item):
        _raise_quality(item)

class BackstagePassUpdater(ItemUpdater):
    def _age(self, item):
        days = item.sell_in
        _raise_quality(item, 3 if days <= 5 else 2 if days <= 10 else 1)

    def _age_past_sell_by(self, item):
        item.quality = MIN_QUALITY

class LegendaryItemUpdater(ItemUpdater):
    def update(self, item):
        """Nothing moves, not even the sell-by date."""

updaters = {
    AGED_BRIE: AgedBrieUpdater(),
    BACKSTAGE_PASS: BackstagePassUpdater(),
    SULFURAS: LegendaryItemUpdater(),
}

def updater_for(name):
    updater = updaters.get(name)
    if updater is not None:
        return updater
    if name.startswith('Conjured'):
        return ConjuredItemUpdater()
    else:
        return DegradingItemUpdater()

class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            updater_for(item.name).update(item)

class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
