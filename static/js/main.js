function getCookie(name) {
    let value = undefined
    $(document.cookie.split("; ")).each(function () {
        let tmp = this.split('=')
        if (tmp[0] === name) {
            value = decodeURI(tmp[1])
            return false // 跳出each循环
        }
    })
    return value
}

function post(url, post_data, callback) {
    $.ajax({
        url: url,
        type: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        data: post_data,
        success: callback
    })
}

const quotes_echart = function (dom) {
    this.options = {}

    this.chart = echarts.init(dom)
    this.chart.setOption({
        legend: {},
        tooltip: {
            trigger: 'axis', axisPointer: {type: 'cross'},
            position: function (pos, params, el, elRect, size) {
                let obj = {top: 10};
                obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
                return obj;
            }
        },
        grid: {left: 0, right: 50},
        dataZoom: [{type: 'inside', start: 80, end: 100}],
        xAxis: {id: 'main', scale: true, splitLine: {show: true}, data: []},
        yAxis: {scale: true, splitLine: {show: true}, position: 'right'},
        series: []
    })
}

quotes_echart.prototype.load = function (url, post_data) {
    this.chart.showLoading()
    post(url, post_data, (data => {
        this.chart.hideLoading()
        this.options = data.options

        let series = Array()
        series.push(this.options['candel'])
        series.push(this.options['ma'])

        this.chart.setOption({
            title: this.options['title'],
            xAxis: {data: this.options['dates']},
            series: series
        })
    }))
}