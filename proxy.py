#!/usr/bin/python

import webapp
import urllib
import urllib2
import sys

class Proxy(webapp.app):
    cache = {}
    headers = {}
    srv_headers = ""

    def parse(self, request, rest):
        host = request.splitlines()[1].split(' ')[1]
        headers = request.split('\r\n')[1:]
        return (request.split(' ', 2)[1][1:], host, headers)

    def process(self, response):
        resourceName, host, headers = response
        try:
            if len(resourceName.split('/')) == 1:
                request = urllib.urlopen("http://" + resourceName)

                #Get server headers
                self.srv_headers = str(request.info())

                httpCode = "200 OK"
                origHttp = request.read()
                pos = origHttp.find(">", origHttp.find("<body"))

                #Menu links
                orig_link = ("<a href='" + "http://" + resourceName
                                + "'>Original webpage</a>\t")
                reload_link = ("<a href='http://" + host + "/"
                                + resourceName + "'>Reload</a>\t")
                cache_link = ("<a href='http://" + host + "/cache/"
                                + resourceName + "'>Cache HTTP</a>")
                head1_link = ("<a href='http://" + host + "/headers1/"
                                + resourceName + "'>Headers 1</a>")
                head2_link = ("<a href='http://" + host + "/headers2/"
                                + resourceName + "'>Headers 2</a>")
                head3_link = ("<a href='http://" + host + "/headers3/"
                                + resourceName + "'>Headers 3</a>")
                head4_link = ("<a href='http://" + host + "/headers4/"
                                + resourceName + "'>Headers 4</a>")

                httpBody = (origHttp[:pos+1] + "<p><h1>" + orig_link + " | "
                            + reload_link + " | " + cache_link + " | "
                            + head1_link + " | " + head2_link + " | "
                            + head3_link + " | " + head4_link + "</h1></p>"
                            + origHttp[pos+1:])

                #Store in cache
                self.cache[resourceName] = httpBody

                #Store headers
                self.headers[resourceName] = headers
            else:
                try:
                    if resourceName.split('/')[0] == "cache":
                        httpCode = "200 OK"
                        httpBody = self.cache[resourceName.split('/')[1]]
                    elif resourceName.split('/')[0] == "headers1" or "headers2":
                        #Client petition headers
                        #Same as app-to-server headers
                        httpCode = "200 OK"
                        httpBody = ("<body><p>" 
                                + str(self.headers[resourceName.split('/')[1]])
                                + "</p></body>")
                    elif resourceName.split('/')[0] == "headers3" or "headers4":
                        httpCode = "200 OK"
                        httpBody = ("<body><p>" + self.srv_headers
                                + "</p></body>")
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
