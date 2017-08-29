
The main dataset (~1.4 GB) is downloaded from here via the makefile:
https://s3.amazonaws.com/metro-extracts.mapzen.com/oslo_norway.osm.bz2



The smaller test data, `stovner.osm` is an area inside Oslo, it's included with the code.

It can be retreived via e.g. [Overpass API](http://overpass-api.de/query_form.html) using a query:

```
(node(59.941,10.9095,59.9567,10.9452);<;);out meta; 
```
