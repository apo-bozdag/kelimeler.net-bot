# -*- coding: utf-8 -*-
""" FileDescription """
__author__ = 'abdullahbozdag'
__creation_date__ = '22.05.2023'

import json
import re

import scrapy


class BulurumSpider(scrapy.Spider):
    name = "bulurum"
    allowed_domains = ["bulurum.com"]
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'

    def __init__(self, what: str = 'eczane', where: str = 'izmir', *args, **kwargs):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines any variables that will be used
        by other functions in the class.

        :param self: Represent the instance of the class
        :return: The base url of the website
        """
        super(BulurumSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://www.bulurum.com'
        self.total_count = 0
        self.per_page = 20
        self.what = what
        self.where = where

    def start_requests(self):
        """
        The start_requests function is called when the spider is run.
        It is the first function that is run, and acts as the main entry point for the spider.

        :param self: Represent the instance of the class
        :return: The first url to crawl
        """
        search_url = f'{self.base_url}/search/{self.what}/{self.where}'
        urls = []
        for page in range(1, 10):
            urls.append(f'{search_url}?page={page}')

        print('urls', urls)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        """
        The parse function is called when the spider is run.
        :param response:
        :return:
        """
        # if not self.total_count:
        #     get_total_count = response.css(
        #         'div#mainCountContainer span.mainCountTitle::text'
        #     ).get()
        #     if get_total_count:
        #         self.total_count = int(get_total_count.split(' ')[0].replace('.', ''))
        # total_pages = int(self.total_count / self.per_page) + 1

        telephone_numbers = []
        company_names = []
        addresses = []
        for phone in response.css('div.PhonesBox label::text').getall():
            telephone_numbers.append(phone)

        script_tags = response.xpath('//script/text()').getall()
        map_data = []
        for script in script_tags:
            match = re.search(r'mapInfo\.results\s*=\s*(.*?);', script)
            if match:
                map_data = json.loads(match.group(1))
                break
        for map_info in map_data:
            company_names.append(map_info.get('CompanyName').strip())
            addresses.append(map_info.get('Address').strip())

        if not map_data:
            for company in response.css('h2.CompanyName a'):
                company_name = company.css('meta[itemprop="name"]::attr(content)').get()
                print('company_name', company_name)
                if company_name == '' or company_name is None:
                    company_info = company.css('span::text').getall()
                    if len(company_info) == 1:
                        company_name = company_info[0].strip()
                    else:
                        company_name = f'{company_info[0].strip()} {company_info[1].strip()}'

                company_names.append(company_name)

        for i in range(len(telephone_numbers)):
            yield {
                'company_name': company_names[i],
                'telephone_number': telephone_numbers[i],
                'address': addresses[i],
            }

        # for page in range(1, total_pages + 1):
        #     url = f'{self.base_url}/search/{self.what}/{self.where}?page={page}'
        #     yield scrapy.Request(url=url, callback=self.parse)
        # next_page = response.css('link[rel="next"]::attr(href)').get()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)
