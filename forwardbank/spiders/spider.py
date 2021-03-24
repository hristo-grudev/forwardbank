import scrapy

from scrapy.loader import ItemLoader

from ..items import ForwardbankItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.forward.bank/services/news_service.php"

payload="page_id=595&detail=the-hangout&cats=%3A%3Aall%3A%3A%2C&instance=cnt_pcomplex_100_t403262_news&cat=&limit=999999&start=0"
headers = {
  'authority': 'www.forward.bank',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': '*/*',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.forward.bank',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.forward.bank/about/the-hangout/',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': '__cfduid=db07648926310e6b9f97e25d5889927ac1616573180; PHPSESSID=70a78dce7e578023ce960cd133fbb2d1; _ga=GA1.2.546386546.1616573188; _gid=GA1.2.970280725.1616573188; sc_last_visit=Wed%2C%2024%20Mar%202021%2004%3A05%3A14%20-0400; _gat_UA-79238482-2=1'
}


class ForwardbankSpider(scrapy.Spider):
	name = 'forwardbank'
	start_urls = ['https://www.forward.bank/about/the-hangout/']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)

		post_links = raw_data.xpath('//a[@class="cta-btn"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		title = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "mod-blog-header", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "title", " " ))]/text()').get()
		description = response.xpath('//div[@class="mod-blog-details"]//div[@class="news-description" or @class="custom-blog-blocks"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//p[@class="published"]/text()').get()

		item = ItemLoader(item=ForwardbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
