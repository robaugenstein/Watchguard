import cgi
import socket
import subprocess
import smtplib
import time
import urllib
import logging

import entity

from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class UpdateTest(webapp.RequestHandler):
	def post(self):

		end = 0
		url = "localhost:8081/updatestore"

		#def testconnect(address, port, x):
		
		def update(x):
		
			#updatedb_name = self.request.get('updatedb_name')
			update = Update(parent=updatedb_key(updatedb_name))
			
			print('Success')
			
			update.DeviceName = 'Location[x]['Device']'
			update.Status = "Up"
			#update.Note = db.StringProperty(multiline=True)
			update.put()
			
			"""rssStore = entity.Rss(key_name='almightyolive')

			# Elements of our RSS
			rssStore.feed = "almightyolive"
			rssStore.content = content

			# Stores our RSS Feed into the datastore
			rssStore.put()"""
		
		def updatetest(x):
		
			form_fields = {
			"DeviceName": Location[x]['DeviceName'],
			"Status": "Down",
			}
			form_data = urllib.urlencode(form_fields)
			result = urlfetch.fetch(url=url,
													payload=form_data,
													method=urlfetch.POST,
													headers={'Content-Type': 'application/x-www-form-urlencoded'})
		
	
	
					
		def sendmessage(e, x):

			fromaddr = ("THQWANAdmin@usc.org")
			toaddrs  = ('Robert_Augenstein@usc.salvationarmy.org, robaugie@gmail.com')

			msg = "The test of " + Location[x]['Device'] + " has failed " + str(time.ctime()) + " \n "
			msg = msg + str(e)

			server = smtplib.SMTP('10.231.1.10')
			server.set_debuglevel(1)
			server.sendmail(fromaddr, toaddrs, msg)
			server.quit()

		Location= [{"Command":"THQ","Device":"THQ Firewall","IPAddress":"thqwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"THQ","Device":"THQ Watchguard Server","IPAddress":"thqwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"CFO","Device":"CFO Firewall","IPAddress":"67.91.168.98","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"CFO","Device":"CFO Watchguard Server","IPAddress":"67.91.168.98","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"MET","Device":"MET Firewall","IPAddress":"metwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"MET","Device":"MET Watchguard Server","IPAddress":"metwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"HRT","Device":"HRT Firewall","IPAddress":"hrtwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"HRT","Device":"HRT Watchguard Server","IPAddress":"hrtwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"WUM","Device":"WUM Firewall","IPAddress":"wumwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"WUM","Device":"WUM Watchguard Server","IPAddress":"wumwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"NOR","Device":"NOR Firewall","IPAddress":"norwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"NOR","Device":"NOR Watchguard Server","IPAddress":"norwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"WST","Device":"WST Firewall","IPAddress":"wstwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"WST","Device":"WST Watchguard Server","IPAddress":"wstwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"KAN","Device":"KAN Firewall","IPAddress":"kanwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"KAN","Device":"KAN Watchguard Server","IPAddress":"kanwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"MID","Device":"MID Firewall","IPAddress":"midwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"MID","Device":"MID Watchguard Server","IPAddress":"midwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"EMI","Device":"EMI Firewall","IPAddress":"emiwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"EMI","Device":"EMI Watchguard Server","IPAddress":"emiwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"IND","Device":"IND Firewall","IPAddress":"indwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"IND","Device":"IND Watchguard Server","IPAddress":"indwgs","Port":4110,"FailCount":0,"SuccessCount":0},
					{"Command":"WMI","Device":"WMI Firewall","IPAddress":"wmiwgd","Port":8080,"FailCount":0,"SuccessCount":0},
					{"Command":"WMI","Device":"WMI Watchguard Server","IPAddress":"wmiwgs","Port":4110,"FailCount":0,"SuccessCount":0}]

		#while end == 0:

		for x, y in enumerate(Location):
			logging.info("The record to be checked is %s ", Location[x]['DeviceName'])
			update( x )
			#testconnect( x )
			time.sleep( 1 )
				
			#time.sleep( 60 )

application = webapp.WSGIApplication([('/scripts', UpdateTest)],
						 debug=True)

def main():
        wsgiref.handlers.CGIHandler().run(application)
						 
if __name__ == '__main__':
        #run_wsgi_app(application)
        main()
