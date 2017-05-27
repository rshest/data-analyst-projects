# Video Game Titles Data 

The CSV file, `game-titles.csv`, contains data about the video game title releases and sales numbers for some of them.

The data was scraped from the [vgchartz](http://www.vgchartz.com) website, using an ad-hoc Python script that I specifically wrote for this.

The script's name is `scrape.py`, it's also located in this folder.

The columns are as following:

* **Pos** - position in the sales charts, if the sales number is available, highest sales to lowest. This number is unique.
* **Game** - game title (name)
* **Platform** - hardware platform the game was shipped on (e.g. "PC", "iOS" etc)
* **Year** - year of release
* **Genre** - game genre (e.g. "Action", "Puzzle") 
* **Publisher** - the publishing company
* **North America** - sales in North America
* **Europe** - sales in Europe
* **Japan** - sales in Japan
* **Rest of World** - total sales minus the three above
* **Global** - total sales




