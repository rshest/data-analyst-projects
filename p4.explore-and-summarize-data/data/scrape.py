import argparse
import urllib
import csv
import time

from bs4 import BeautifulSoup


SITE = 'http://www.vgchartz.com/gamedb/'
RESULTS_PER_PAGE = 1000
MAIN_TABLE_CLASS = 'chart'
OUT_FILE = 'vgtitles.csv'
TITLE = 'Web-scraper for {}'.format(SITE)


def preprocess(str):
	if str == 'N/A':
		# replace missing data with empty fields
		return u''
	else:
		return str.encode('utf-8')


def parse_page(data, parse_header=False):
	bs = BeautifulSoup(data, 'lxml')
	
	table = bs.find('table', class_=MAIN_TABLE_CLASS)
	rows = table.find_all('tr')

	def get_cols(row, tag):
		cols = (c.string.strip() for c in row.find_all(tag))
		return [preprocess(col) for col in cols]

	if parse_header:
		first_row = rows[0]
		yield get_cols(first_row, 'th')

	for row in rows[1:]:
		try: 
			cols = get_cols(row, 'td')
			if len(cols) > 0:
				yield cols
		except:
			pass


def scrape(out_file, start_page=1, sleep_seconds=1):
	params = {'results': RESULTS_PER_PAGE}

	cur_page = start_page

	f = open(out_file, 'ab')
	csv_writer = csv.writer(f)

	while True:	
		params['page'] = cur_page
		url  = SITE + '?' + urllib.urlencode(params)

		print 'Parsing page {}: {}'.format(cur_page, url)

		data = urllib.urlopen(url).read()		
		rows = list(parse_page(data, cur_page == 1))

		if len(rows) == 0:
			break

		for row in rows:
			csv_writer.writerow(row)
		
		cur_page += 1
		
		f.flush()
		time.sleep(sleep_seconds)

	f.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=TITLE)
	parser.add_argument('-s', '--start-page', dest='start_page', required=False, type=int, default=1,
                    	help='number of the starting page to scrape')
	parser.add_argument('-f', '--file', dest='file', required=False, default=OUT_FILE,
                    	help='output CSV file')
	parser.add_argument('-t', '--sleep', dest='sleep', required=False, type=int, default=1,
                    	help='period to sleep between pages')
	params = parser.parse_args()

	scrape(params.file, params.start_page, params.sleep)
