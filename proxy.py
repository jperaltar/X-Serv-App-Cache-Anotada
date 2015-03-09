#!/usr/bin/python

import webapp
import urllib
import sys


class Proxy(webapp.app):
    cache = {}

    def parse(self, request, rest):
        host = request.splitlines()[1].split(' ')[1]
        return (request.split(' ', 2)[1][1:], host)

    def process(self, response):
        resourceName, host = response
        try:
            if len(resourceName.split('/')) == 1:
                f = urllib.urlopen("http://" + resourceName)
                httpCode = "200 OK"
                origHttp = f.read()
                pos = origHttp.find(">", origHttp.find("<body"))

                #Menu links
                orig_link = ("<a href='" + "http://" + resourceName
                                + "'>Original webpage</a>\t")
                reload_link = ("<a href='http://" + host + "/"
                                + resourceName + "'>Reload</a>\t")
                cache_link = ("<a href='http://" + host + "/cache/"
                                + resourceName + "'>Cache HTTP</a>")

                httpBody = (origHttp[:pos+1] + "<p><h1>" + orig_link + " | "
                            + reload_link + " | " + cache_link + "</h1></p>"
                            + origHttp[pos+1:])

                #Store in cache
                self.cache[resourceName] = httpBody
            else:
                try:
                    if resourceName.split('/')[0] == "cache":
                        httpCode = "200 OK"
                        httpBody = self.cache[resourceName.split('/')[1]]
                    else:
                        httpCode = "404 Not Available"
                        httpBody = "Error: Not avaliable resource"
                except KeyError:
                    httpCode = "404 Not Available"
                    httpBody = "Error: Not avaliable cache content"

        except IOError:
            httpCode = "404 Not Available"
            httpBody = "Error: Could not connect"

        return (httpCode, httpBody)

if __name__ == "__main__":
    proxy = Proxy()

    try:
        testProxyApp = webapp.webApp("localhost", 1235,
                                     {'/': proxy})
    except KeyboardInterrupt:
        print "Closing service"
        sys.exit()
