# -*- coding: utf-8 -*-
AGED_BRIE = "Aged Brie"
BACKSTAGE_PASS = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"

MIN_QUALITY = 0
MAX_QUALITY = 50

class GildedRose(object):

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            self._update_item(item)

    def _update_item(self, item):
        if item.name == SULFURAS:
            return
        if item.name == AGED_BRIE:
            self._update_aged_brie(item)
        elif item.name == BACKSTAGE_PASS:
            self._update_backstage_pass(item)
        else:
            self._update_ordinary_item(item)

    @staticmethod
    def _update_ordinary_item(item):
        if item.quality > MIN_QUALITY:
            item.quality -= 1
        item.sell_in -= 1
        if item.sell_in < 0 and item.quality > MIN_QUALITY:
            item.quality -= 1

    @staticmethod
    def _update_aged_brie(item):
        if item.quality < MAX_QUALITY:
            item.quality += 1
        item.sell_in -= 1
        if item.sell_in < 0 and item.quality < MAX_QUALITY:
            item.quality += 1

    @staticmethod
    def _update_backstage_pass(item):
        if item.quality < MAX_QUALITY:
            item.quality += 1
            if item.sell_in < 11 and item.quality < MAX_QUALITY:
                item.quality += 1
            if item.sell_in < 6 and item.quality < MAX_QUALITY:
                item.quality += 1
        item.sell_in -= 1
        if item.sell_in < 0:
            item.quality = MIN_QUALITY

class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
