#! /usr/bin/env python
# coding: utf-8
import urllib
url = "http://boardgamegeek.com/xmlapi/collection/" + urllib.quote(u"Rémido".encode("utf-8"))
print url
urllib.urlretrieve(url, "remido-quote.xml")
