.PHONY: download

download:
	wget https://s3.amazonaws.com/metro-extracts.mapzen.com/oslo_norway.osm.bz2
	bzip2 -d oslo_norway.osm.bz2

doc:
	ipython nbconvert --to pdf wrangle-osm-data.ipynb
