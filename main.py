from bdscrawler.run_scraper import Scraper
import argparse
from bdscrawler.basecrawler.dao.MongoDB import MongoDB
from bdscrawler.bdscrawler.settings import *
def check_is_running(spider):
    check_running = False
    mongo_dao = MongoDB()
    client = mongo_dao.get_client()
    log_collection = client[LOGGING_DATABASE][LOGGING_COLLECTION]

    latest_doc = log_collection.find_one(
            {'source': spider},
            sort=[('runtime_id', -1), ('createdAt', -1)]
        )

    if latest_doc:
        latest_runtime_id = latest_doc['runtime_id']
        spider_closed = log_collection.find_one(
                {'source': spider,
                'runtime_id': latest_runtime_id,
                'event': 'spider_closed'}
            )
        if not spider_closed:
            check_running = True
        
    client.close()
    return check_running
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--ignore-runtime-before', default='true')
    parser.add_argument('--ignore_old_request', default='false')
    parser.add_argument('--spider', default='alonhadat')
    args = parser.parse_args()
    ignore_runtime_before = True if args.ignore_runtime_before == 'true' else False
    ignore_old_request = True if args.ignore_old_request == 'true' else False
    spider = args.spider
    if check_is_running(spider):
        print('This spider is running')
    else:
        print('Start')
        scraper = Scraper(ignore_runtime_before=ignore_runtime_before, ignore_old_request=ignore_old_request, spider=spider)
        scraper.run_spiders()
if __name__ == '__main__':
    main()
