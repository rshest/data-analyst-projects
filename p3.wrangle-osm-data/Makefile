.PHONY: download

download:
	wget https://s3.amazonaws.com/metro-extracts.mapzen.com/oslo_norway.osm.bz2
	bzip2 -d oslo_norway.osm.bz2

pdf:
	jupyter nbconvert --to pdf p3.wrangle-osm-data.ipynb

html:
	jupyter nbconvert --to html p3.wrangle-osm-data.ipynb

