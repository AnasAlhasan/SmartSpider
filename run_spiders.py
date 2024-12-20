import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from Spiders.DiamondStar_Spider import CrawlDiamondStar
from Spiders.BMS_Spider import CrawlBMS
from Spiders.SmartBuy_Spider import CrawlSmartBuy
from Spiders.Leaders_Spider import CrawlLeaders
from Spiders.LGvision_Spider import CrawlLGvision

def create_session(retries, backoff_factor, status_forcelist):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def RunSpiders(query):
    search_term = query
    pages = 3
    session = create_session(retries=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    spiders = [
        CrawlBMS,
        CrawlDiamondStar,
        CrawlLGvision,
        CrawlSmartBuy
    ]
    
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(spider, search_term, pages, session): spider.__name__ for spider in spiders}
        
        for future in as_completed(futures):
            spider_name = futures[future]
            try:
                future.result()
                print(f'{spider_name} completed successfully.')
            except Exception as e:
                print(f'{spider_name} generated an exception: {e}')


'''def RunSpiders():
    search_term = ''
    pages = 1
    CrawlBMS(search_term,pages)
    CrawlLeaders(search_term,pages)
    CrawlDiamondStar(search_term,pages)
    CrawlLGvision(search_term,pages)
    CrawlSmartBuy(search_term,pages)
    sequential function'''