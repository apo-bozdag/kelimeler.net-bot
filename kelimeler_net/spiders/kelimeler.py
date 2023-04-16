import scrapy
import re


def tr_upper(self):
    self = re.sub(r"i", "İ", self)
    self = re.sub(r"ı", "I", self)
    self = re.sub(r"ç", "Ç", self)
    self = re.sub(r"ş", "Ş", self)
    self = re.sub(r"ü", "Ü", self)
    self = re.sub(r"ğ", "Ğ", self)
    self = self.upper()  # for the rest use default upper
    return self


def tr_lower(self):
    self = re.sub(r"İ", "i", self)
    self = re.sub(r"I", "ı", self)
    self = re.sub(r"Ç", "ç", self)
    self = re.sub(r"Ş", "ş", self)
    self = re.sub(r"Ü", "ü", self)
    self = re.sub(r"Ğ", "ğ", self)
    self = self.lower()  # for the rest use default lower
    return self


class KelimelerSpider(scrapy.Spider):
    name = "kelimeler"
    allowed_domains = ["kelimeler.net"]
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54'

    def __init__(self):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines any variables that will be used
        by other functions in the class.

        :param self: Represent the instance of the class
        :return: The base url of the website
        """
        self.base_url = 'https://kelimeler.net'

    def start_requests(self):
        """
        The start_requests function is the method called by Scrapy when the spider is
        opened for scraping.
        It must return an iterable with the first Requests to crawl for this spider.
        It is also possible to yield Request objects directly from this function,
        without using the typical start_requests method.

        :param self: Represent the instance of the class
        :return: An iterable object, which is a list of requests
        """
        letters = 'abcçdefgğhıijklmnoöprsştuüvyz'
        urls = [
            'https://kelimeler.net/%s-ile-baslayan-kelimeler' % chr(i) for i in
            [ord(c) for c in letters]
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        """
        The parse function is the default callback used by Scrapy to process downloaded responses,
        when their URLs don’t match any regular expression in the new_rules parameter
        (including requests recursively generated from other parse methods).

        :param self: Represent the instance of the class
        :param response: Pass the response object to the parse function
        :param **kwargs: Pass keyworded, variable-length argument list to a function
        :return: A request object
        """
        for word in response.css('section#content p.monospace a'):
            word_url = self.base_url + word.css('::attr(href)').get()
            yield scrapy.Request(url=word_url, callback=self.get_word_links)

    def get_word_links(self, response):
        """
        The get_word_links function is a callback function that will be called by the
        Scrapy engine when it has finished
        downloading the response from the URL we provided in our start_requests method.
        The get_word_links function parses
        the response and extracts all links to word detail pages, then yields scrapy.
        Request objects for each of them.

        :param self: Represent the instance of the class
        :param response: Pass the response object from the previous request
        :return: A list of links to the word detail pages
        """
        for word in response.css('div.WordList ul.monospace li a'):
            word_detail_url = self.base_url + word.css('::attr(href)').get()
            yield scrapy.Request(url=word_detail_url, callback=self.get_word)

    @staticmethod
    def get_word(response):
        """
        The get_word function takes a response object as an argument and yields the word from
        the WordMeaningList class.


        :param response: Get the response from the website
        :return: A list of words
        """
        answer = response.css('section#content h2::text').get()
        if 'bulunamadı' in answer.lower():
            return
        questions = []
        for word in response.css('ol.WordMeaningList li span.WordMeaning'):
            questions.append(word.css('::text').get().strip())
        yield {
            'answer': answer,
            'letter': tr_lower(answer[0]),
            'question': questions,
            'url': response.url
        }
