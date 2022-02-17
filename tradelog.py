import csv
import datetime
from decimal import *
from collections import deque


def Currency(num):
    return "${:,.2f}".format(num)


class GainLoss:
    def __init__(self, name):
        self.name = name
        self.realized = Decimal(0)
        self.unrealized = Decimal(0)

    def __str__(self):
        return f'{self.name} - Realized Gain: {Currency(self.realized)}, Unrealized Gain: {Currency(self.unrealized)}'


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
    def __init__(self):
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
                        result.realized += get * (t.price - top.price)
                        if top.quantity > 0:
                            stack.append(top)

            while len(stack) > 0:
                top = stack.pop()
                result.unrealized += top.quantity * (currentValue - top.price)

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
                            t.date,
                            t.quantity,
                            t.price
                        ])

    def load(self, filename):
        with open(filename, newline='', encoding='utf-8') as f:
            r = csv.reader(f)
            for line in r:
                name = line[0]
                type = line[1]
                date = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S')
                quantity = Decimal(line[3])
                price = Decimal(line[4])
                self.insert(name, type, date, quantity, price)
