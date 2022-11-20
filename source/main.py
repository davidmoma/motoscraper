from scraper import MotoScraper

output_file = "dataset.csv"

scraper = MotoScraper()
scraper.scrape()
scraper.data2csv(output_file)
