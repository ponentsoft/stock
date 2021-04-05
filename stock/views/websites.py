"""

Created by ponentsoft@gmail.com on 2021/4/5
Ponentsoft Technology(c) 2011-2021
"""
import numpy
from django.shortcuts import render

from pstock.data import symbol
from pstock.data.quotes import Quotes
from pstock.utils import dateutils
from pstock.extras.trend import TrendChains
from stock.views import webutils


def home(request):
    render_data = {'code': '000001.XSHE'}
    return render(request, 'home.html', render_data)


UP_COLOR = '#CD6155'
DOWN_COLOR = '#45B39D'


def query_echart(request):
    code = symbol.format_code(webutils.get_post(request, 'code'))
    day = int(webutils.get_post(request, 'day'))  # 趋势最小天数，对应均线
    rate = int(webutils.get_post(request, 'rate'))  # 期望盈亏比
    lost = int(webutils.get_post(request, 'lost'))  # 最大损失比例

    # 此处获取对应股票的行情数据。
    quotes_datas = Quotes(code).find(start='2015-01-01', end=dateutils.today())

    tc = TrendChains(day)
    web_datas = process_quotes(quotes_datas, tc, day)

    dates = web_datas['dates']
    last_date = dates[-1]
    for i in range(20):
        dates.append(str(dateutils.get_next(dates[-1])))

    start_date = str(dateutils.get_next(last_date))
    end_date = dates[-1]
    close = web_datas['close_datas'][-1]

    stop_rate = (100 - lost) / 100
    gain_rate = (100 + lost * rate) / 100

    stop_close = round(close * stop_rate, 2)
    high_close = round(close * gain_rate, 2)

    # 盈亏比区域
    areas = [
        [{'coord': [start_date, close], 'itemStyle': {'color': '#E8F6F3'}}, {'coord': [end_date, high_close]}],
        [{'coord': [start_date, close], 'itemStyle': {'color': '#F9EBEA'}}, {'coord': [end_date, stop_close]}]
    ]

    lines = process_trend_lines(tc)
    lines.append({'yAxis': close})  # 当前价格线
    lines.append({'yAxis': stop_close})  # 止损线
    lines.append({'yAxis': high_close})  # 盈亏比上沿

    options = {
        'dates': dates,
        'candel': {
            'id': 'candle', 'type': 'candlestick', 'data': web_datas['candle_datas'],
            'itemStyle': {'color': UP_COLOR, 'color0': DOWN_COLOR, 'borderColor': UP_COLOR, 'borderColor0': DOWN_COLOR},
            'markLine': {'symbol': ['none', 'none'], 'data': lines, 'lineStyle': {'color': '#5DADE2', 'width': 1},
                         'label': {'position': 'middle', 'color': '#E74C3C'}},
            'markArea': {'data': areas, 'silent': True},
        },
        'ma': {'id': f'ma', 'name': f'ma{day}', 'type': 'line', 'data': web_datas['ma_datas'], 'showSymbol': False,
               'smooth': True, 'lineStyle': {'width': 1}}
    }

    return webutils.response_json({'options': options})


def process_quotes(quotes_datas, trend_chains, day):
    dates, candle_datas, ma_datas, close_datas = [], [], [], []
    for quotes_data in quotes_datas:
        date, close = str(quotes_data['date']), float(quotes_data['close'])
        trend_chains.update(date, close)
        close_datas.append(close)

        ma_datas.append(round(numpy.mean(close_datas[-day:]), 2) if len(close_datas) >= day else None)

        dates.append(date)
        candle_datas.append([float(quotes_data[name]) for name in ['open', 'close', 'low', 'high']])

    return {'dates': dates, 'candle_datas': candle_datas, 'ma_datas': ma_datas, 'close_datas': close_datas}


def process_trend_lines(tc):
    trend_lines = [[
        {'coord': [tc.cursor.start.date, tc.cursor.start.close], 'value': process_line_label(tc.cursor)},
        {'coord': [tc.cursor.end.date, tc.cursor.end.close]},
    ]]
    pre_trend = tc.cursor.pre_trend
    while pre_trend:
        trend_lines.append([
            {'coord': [pre_trend.start.date, pre_trend.start.close], 'value': process_line_label(pre_trend)},
            {'coord': [pre_trend.end.date, pre_trend.end.close]},
        ])
        pre_trend = pre_trend.pre_trend

    return trend_lines


def process_line_label(trend):
    rate = round((trend.end.close - trend.start.close) / trend.start.close * 100, 2)
    return f'{rate}%({trend.days})'
