import scrapy

from tutorial.utils import parse_emploicd_job_to_dict, parse_mediacongo_job_to_dict, get_parsed_unique_jobs


class JobsSpider(scrapy.Spider):
    name = "jobs"
    custom_settings = {
        'FEEDS': {
            'jobs.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 4,
                'overwrite': True
            },
        },
    }

    async def start(self):
        jobs_websites = [
            {'name':'Media Congo', 'url':'https://www.mediacongo.net/emplois.html', 'parse': self.parse_mediacongo},
            {'name':'Emploi CD', 'url':'https://www.emploi.cd/recherche-jobs-congo-rdc', 'parse': self.parse_emploicd},
        ]
        for site in jobs_websites:
            yield scrapy.Request(url=site['url'], callback=site['parse'])


    def parse_mediacongo(self, response):
        jobs = response.xpath('//table[@class="table_datas"]/tr[1]/following-sibling::tr')
        yield from get_parsed_unique_jobs(parse_mediacongo_job_to_dict, jobs)

        next_page = response.css("a:has(img.nav_right)::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse_mediacongo)
    
    def parse_emploicd(self, response):
        jobs = response.css(".page-search-jobs-content .card-job")
        yield from get_parsed_unique_jobs(parse_emploicd_job_to_dict, jobs)

        next_page = response.css(".pagination-next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse_emploicd)