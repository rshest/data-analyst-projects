import urllib
import csv
import time

from bs4 import BeautifulSoup

SITE = 'http://www.vgchartz.com/gamedb/'
RESULTS_PER_PAGE = 1000


def preprocess(str):
	if str == 'N/A':
		# replace missing data with empty fields
		return u''
	else:
		return str.encode('utf-8')


def parse_page(data, parse_header=False):
	bs = BeautifulSoup(data, 'lxml')
	
	table = bs.find('table', class_='chart')
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


def scrap():
	params = {'results': RESULTS_PER_PAGE}

	cur_page = 1

	f = open('vgtitles.csv', 'wb')
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
		time.sleep(1)

	f.close()

if __name__ == '__main__':
	scrap()
