# Gathering data from billboard and saving into ../data/billboard.csv

import scrapy
from datetime import date, timedelta
from scrapy.crawler import CrawlerProcess


class Row:
    def __init__(self):
        self.artist = None
        self.title = None
        self.position = None
        self.date = None

    def export(self, sep):
        return sep.join([
            self.artist.replace(sep, '\\' + sep),
            self.title.replace(sep, '\\' + sep),
            self.position.replace(sep, '\\' + sep),
            self.date.replace(sep, '\\' + sep)
        ])

class Billboard(scrapy.Spider):
    name = 'billboard'

    def start_requests(self):
        today = date.today()
        first = date(year=2012, month=3, day=24)
        diff = today - first
        dates = [ today - timedelta(days=x) for x in range(0, diff.days) ]
        for date_chart in dates:
            formatted_year = '%02d-%02d-%02d' % (date_chart.year, date_chart.month, date_chart.day)
            yield scrapy.Request(url='https://www.billboard.com/charts/on-demand-songs/' + formatted_year, callback=self.parse)

    def parse(self, response):
        date_chart = response.url.split('/')[-1]
        chart = []

        row = Row()
        row.artist = response.css('.chart-number-one__title::text').extract_first()
        row.title = response.css('.chart-number-one__artist>a::text').extract_first()
        if row.title is None or len(row.title) == 0:
            row.title = response.css('.chart-number-one__artist::text').extract_first()
        row.title = row.title.replace('\n', '')
        row.position = '1'
        row.date = date_chart
        chart.append(row)

        for position in response.css('.chart-list-item'):
            row = Row()
            row.artist = position.xpath('@data-artist').extract_first()
            row.title = position.xpath('@data-title').extract_first()
            row.position = position.xpath('@data-rank').extract_first()
            row.date = date_chart
            chart.append(row)

        if len(chart) == 0:
            return

        with open('../data/billboard.csv', 'a') as file:
            file.write('\n'.join([ row.export(';') for row in chart ]))
            file.write('\n')


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
})
process.crawl(Billboard)
process.start()