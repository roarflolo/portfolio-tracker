import csv
import datetime
from decimal import *
from collections import deque


def Currency(num):
    return "${:,.2f}".format(num)


def Pct(num):
    return "{:,.2f}%".format(num * Decimal(100.0))


class GainLoss:
    def __init__(self, name):
        self.name = name
        self.realizedPctSum = Decimal(0)
        self.realizedPctCount = Decimal(0)
        self.unrealizedPctSum = Decimal(0)
        self.unrealizedPctCount = Decimal(0)
        self.realized = Decimal(0)
        self.unrealized = Decimal(0)

    def add_realized(self, quantity, buy, sell):
        self.realizedPctSum += (sell / buy) - 1
        self.realizedPctCount += Decimal(1)
        self.realized += quantity * (sell - buy)

    def add_unrealized(self, quantity, buy, sell):
        self.unrealizedPctSum += (sell / buy) - 1
        self.unrealizedPctCount += Decimal(1)
        self.unrealized += quantity * (sell - buy)

    def __str__(self):
        realizedPct = Decimal(0)
        unrealizedPct = Decimal(0)
        if self.realizedPctCount > 0:
            realizedPct = self.realizedPctSum / self.realizedPctCount
        if self.unrealizedPctCount > 0:
            unrealizedPct = self.unrealizedPctSum / self.unrealizedPctCount
        # return f'{self.name} - Realized Gain: {Currency(self.realized)} ({Pct(realizedPct)}), Unrealized Gain: {Currency(self.unrealized)} ({Pct(unrealizedPct)})'
        return f'{self.name} - Realized Gain: {Pct(realizedPct)}, Unrealized Gain: {Pct(unrealizedPct)}'


class Trade:
    def __init__(self, name, type, date, quantity, price):
        self.name = name
        self.type = type
        self.date = date
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f'{self.name} {self.date} {self.type} {self.quantity} @ {Currency(self.price)}'


class TradeLog:
    def __init__(self, name):
        self.name = name
        self.trades = {}

    def insert(self, name, type, date, quantity, price):

        if not name in self.trades:
            self.trades[name] = []

        t = Trade(name, type, date, Decimal(quantity), Decimal(price))
        self.trades[name].append(t)

    def buy(self, name, date, quantity, price):
        self.insert(name, "buy", date, quantity, price)

    def dividend(self, name, date, quantity, price):
        self.insert(name, "div", date, quantity, price)

    def sell(self, name, date, quantity, price):
        self.insert(name, "sell", date, quantity, price)

    # Last-In-First-Out Value calculation
    def calc_gain_loss(self, name, currentValue):
        currentValue = Decimal(currentValue)

        # TODO: group realized value by year/month
        # TODO: break down of where gain/loss is from, increase in value, dividends, ...
        result = GainLoss(name)

        stack = deque()
        if name in self.trades:
            arr = self.trades[name]
            for t in arr:
                if t.type == "buy":
                    stack.append(t)
                elif t.type == "div":
                    stack.append(t)
                elif t.type == "sell":
                    quantity = t.quantity
                    # TODO: Short (selling more than you've bought) doesn't work
                    while quantity > 0 and len(stack) > 0:
                        top = stack.pop()
                        get = min(top.quantity, quantity)
                        top.quantity -= get
                        quantity -= get
                        result.add_realized(get, top.price, t.price)
                        if top.quantity > 0:
                            stack.append(top)

            while len(stack) > 0:
                top = stack.pop()
                result.add_unrealized(top.quantity, top.price, currentValue)

        return result

    def save(self, filename):
        with open(filename, 'w', newline='') as f:
            w = csv.writer(f)
            for arr in self.trades.values():
                for t in arr:
                    w.writerow(
                        [
                            t.name,
                            t.type,
                            t.date.date(),
                            t.quantity,
                            t.price
                        ])

    def load(self, filename):
        with open(filename, newline='', encoding='utf-8') as f:
            r = csv.reader(f)
            for line in r:
                name = line[0]
                type = line[1]
                #date = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S')
                date = datetime.datetime.strptime(line[2], '%Y-%m-%d')
                quantity = Decimal(line[3])
                price = Decimal(line[4])
                self.insert(name, type, date, quantity, price)
