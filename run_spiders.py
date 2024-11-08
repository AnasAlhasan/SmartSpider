from concurrent.futures import ThreadPoolExecutor, as_completed
from Spiders.DiamondStar_Spider import CrawlDiamondStar
from Spiders.BMS_Spider import CrawlBMS
from Spiders.SmartBuy_Spider import CrawlSmartBuy
from Spiders.Leaders_Spider import CrawlLeaders
from Spiders.LGvision_Spider import CrawlLGvision

def RunSpiders():
    search_term = 'tv'
    pages = 3
    # Create a list of functions to execute
    spiders = [
        CrawlBMS,
        CrawlLeaders,
        CrawlDiamondStar,
        CrawlLGvision,
        CrawlSmartBuy
    ]
    
    with ThreadPoolExecutor() as executor:
        # Submit all spiders to the executor
        futures = {executor.submit(spider, search_term, pages): spider.__name__ for spider in spiders}
        
        # Process results as they complete
        for future in as_completed(futures):
            spider_name = futures[future]
            try:
                future.result()  # This will raise an exception if the spider encountered an error
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