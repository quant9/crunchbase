import requests
from lxml import etree
import logging
# from datetime import datetime
import random
import calendar, time
from sqlalchemy.exc import IntegrityError

import model, constants


VC_URL = 'https://www.crunchbase.com/category/venture-capital/b37dbaebc825e6a036de84556a5d2e1f?page={}'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('crunchbase')


def _get_root(url):
    random_proxy = _get_random_proxy()
    headers = _get_headers()
    res = requests.get(url,
        proxies=random_proxy,
        headers= headers,
        timeout=4
    )
    parser = etree.HTMLParser()
    return etree.fromstring(res.content, parser), res.status_code

def _get_random_proxy():
    proxy = random.choice(constants.PROXIES)
    return {"https": "https://{}".format(proxy)}

def _get_headers():
    headers = constants.HEADERS
    user_agent = random.choice(constants.USER_AGENTS).format(random.randint(500,500)/100.0, \
        random.randint(0,100000)/100.0, random.randint(0,10000000)/100.0)
    headers['User-Agent'] = user_agent
    return headers

def scrape_crunchbase(page, run_id):
    url = VC_URL.format(page)
    logger.info('scraping page {}'.format(page))
    try:
        root, status = _get_root(url)
    except Exception as e:
        logger.warning('trying again. exception was {}'.format(e))
        return False
    vc_roots = root.xpath("//ul[@class='section-list container']/li")
    if status != 200 or len(vc_roots) == 0:
        logger.warning('trying again, status code {}'.format(status))
        return False
    for vc_root in vc_roots:
        vc_page = CrunchbasePage(vc_root)
        vc_basics = {
            'name': vc_page.name,
            'crunchbase_url': vc_page.crunchbase_url,
            'run_id': run_id
        }
        try:
            model.store_basics(vc_basics)
        except IntegrityError:
            pass
        for category, url in vc_page.categories:
            category_dict = {
                'vc_name': vc_page.name,
                'category': category,
                'category_url': 'https://www.crunchbase.com/{}'.format(url),
                'run_id': run_id
            }
            model.store_category(category_dict)
        logger.info('basics stored for {}'.format(vc_page.name))
    logger.info('done with page {}'.format(page))
    return True

class CrunchbasePage(object):

    def __init__(self, vc_root):
        self.root = vc_root

    @property
    def name(self):
        return self.root.xpath('.//a/@title')[0].encode('utf-8')

    @property
    def crunchbase_url(self):
        short_url = self.root.xpath('.//a/@href')[0]
        return 'https://www.crunchbase.com/{}'.format(short_url)

    @property
    def categories(self):
        raw_categories = self.root.xpath('.//span[@class="organization-categories"]/a/text()')
        urls = self.root.xpath('.//span[@class="organization-categories"]/a/@href')
        return zip(raw_categories, urls)


if __name__ == '__main__':
    run_id = int(calendar.timegm(time.gmtime()))
    for page in range(25, 260):
        x = False
        while x is False:
            x = scrape_crunchbase(page, run_id)
