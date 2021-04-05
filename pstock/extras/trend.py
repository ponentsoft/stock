"""

Created by ponentsoft@gmail.com on 2021/4/5
Ponentsoft Technology(c) 2011-2021
"""


class Point(object):
    def __init__(self, date, close):
        self.date = date
        self.close = close

    def __str__(self):
        return f'{self.date},{self.close}'


class Trend(object):
    def __init__(self, date, close, pre_trend=None):
        self.end = Point(date, close)
        self.days = 1
        self.pre_trend = pre_trend

        if pre_trend:
            self.start = pre_trend.end
            self.direction = 'down' if pre_trend.direction == 'up' else 'up'
        else:
            self.start = Point(date, close)
            self.direction = None

    def update(self, date, close, days=0):
        self.end = Point(date, close)
        self.days += (days + 1)

        if self.direction is None:
            if self.start.close > self.end.close:
                self.direction = 'down'
            elif self.start.close < self.end.close:
                self.direction = 'up'

    def same_direction(self, close):
        return (self.direction == 'up' and self.end.close < close) or (
                self.direction == 'down' and self.end.close > close)

    def __str__(self):
        rate = round((self.end.close - self.start.close) / self.start.close * 100, 3)
        return f'{self.start}, {self.end}, {rate}%, {self.days}, {self.direction}'


class TrendChains(object):
    def __init__(self, min_day=20):
        self.cursor = None
        self.min_day = min_day

    def update(self, date, close):
        if self.cursor is None:
            self.cursor = Trend(date, close)
        else:
            if self.cursor.direction is None or self.cursor.same_direction(close):
                self.cursor.update(date, close)
            else:
                self.cursor = Trend(date, close, self.cursor)

            # 沿着趋势链回溯，有两种可能，这个是一个新的趋势，或者恢复之前的某一个趋势。
            res = self.back_track(date, close)
            while res:
                res = self.back_track(date, close)

    def back_track(self, date, close):
        # 向前回溯，如果遇到一个相反方向的趋势，则终止回溯。
        if pre_trend := self.cursor.pre_trend:
            if self.break_back(self.cursor):
                return False

            days = self.cursor.days - 1
            while pre_trend:
                if pre_trend.same_direction(close):
                    pre_trend.update(date, close, days)

                    self.cursor = pre_trend
                    if self.cursor.days >= self.min_day:
                        return False

                    return True

                if self.break_back(pre_trend):
                    return False

                days += pre_trend.days
                pre_trend = pre_trend.pre_trend
        return False

    def break_back(self, trend):
        if trend and trend.pre_trend:
            return trend.pre_trend.days >= self.min_day and trend.days >= self.min_day
        return False
