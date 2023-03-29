import scrapy


class KelimelerSpider(scrapy.Spider):
    name = "kelimeler"
    allowed_domains = ["kelimeler.net"]
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54'

    def __init__(self):
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
        urls = [
            'https://kelimeler.net/%s-ile-baslayan-kelimeler' % chr(i) for i in
            range(ord('a'), ord('z') + 1)
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
            'letter': answer[0].lower(),
            'question': questions,
            'url': response.url
        }
