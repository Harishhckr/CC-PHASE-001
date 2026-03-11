from celery import shared_task

from app.crawlers.cppp_crawler import CpppCrawler
from app.crawlers.gem_crawler import GemCrawler
from app.crawlers.tender247_crawler import Tender247Crawler
from app.crawlers.tenderdetail_crawler import TenderDetailCrawler
from app.crawlers.tendertiger_crawler import TenderTigerCrawler


@shared_task(name="app.tasks.crawler_tasks.crawl_gem")
def crawl_gem():
    crawler = GemCrawler()
    return crawler.crawl()


@shared_task(name="app.tasks.crawler_tasks.crawl_cppp")
def crawl_cppp():
    crawler = CpppCrawler()
    return crawler.crawl()


@shared_task(name="app.tasks.crawler_tasks.crawl_tender247")
def crawl_tender247():
    crawler = Tender247Crawler()
    return crawler.crawl()


@shared_task(name="app.tasks.crawler_tasks.crawl_tendertiger")
def crawl_tendertiger():
    crawler = TenderTigerCrawler()
    return crawler.crawl()


@shared_task(name="app.tasks.crawler_tasks.crawl_tenderdetail")
def crawl_tenderdetail():
    crawler = TenderDetailCrawler()
    return crawler.crawl()
