from bdscrawler.run_scraper import Scraper
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ignore-runtime-before', default='true')
    parser.add_argument('--ignore_old_request', default='false')
    parser.add_argument('--spider', default='alonhadat')
    args = parser.parse_args()
    ignore_runtime_before = True if args.ignore_runtime_before == 'true' else False
    ignore_old_request = True if args.ignore_old_request == 'true' else False
    spider = args.spider

    scraper = Scraper(ignore_runtime_before=ignore_runtime_before, ignore_old_request=ignore_old_request, spider=spider)
    scraper.run_spiders()

if __name__ == '__main__':
    main()
