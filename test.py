import cfscrape
scraper = cfscrape.create_scraper()
print scraper.get("https://androidfilehost.com/api/?action=devices&limit=1").content
