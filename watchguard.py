import cgi
import datetime
import httplib
import urllib
import webapp2
import jinja2
import os
import logging
import time
import socket

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	
from array import array
from datetime import timedelta, datetime, tzinfo
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import urlfetch

class Device(db.Model):
	"""Models an individual Device with DeviceName, Description, Command, IP, Port."""
	DeviceName = db.StringProperty()
	Description = db.StringProperty(multiline=True)
	Command = db.StringProperty()
	IP = db.StringProperty()
	Port = db.StringProperty()
	
class Command(db.Model):
	"""Models an individual Command with Contact, E-Mail Address, Command Name, """
	Command = db.StringProperty()
	Contact = db.StringProperty()
	EMail = db.StringProperty()
	
class Update(db.Model):
	"""Models an individual Update with Device Name, Status, Note, and Date/Time stamp. """
	Device = db.StringProperty()
	DeviceName = db.StringProperty()
	Status = db.StringProperty()
	Note = db.StringProperty(multiline=True)
	Date = db.DateTimeProperty(auto_now_add=True)


def devicedb_key(devicedb_name=None):
	"""Constructs a Datastore key for a Device entity with devicedb_name."""
	return db.Key.from_path('DeviceStore', devicedb_name or 'default_devicedb')
	
def commanddb_key(commanddb_name=None):
	"""Constructs a Datastore key for a Command entity with devicedb_name."""
	return db.Key.from_path('CommandStore', commanddb_name or 'default_commanddb')
	
def updatedb_key(updatedb_name=None):
	"""Constructs a Datastore key for a Update entity with devicedb_name."""
	return db.Key.from_path('UpdateStore', updatedb_name or 'default_updatedb')


class DeviceHandler(webapp2.RequestHandler):
	def get(self):

		""" This section of code will load the Devices view which is currectly seen as the main page for this project """

		#guestbook_name=self.request.get('guestbook_name')
		#greetings_query = Greeting.all().ancestor(
		#	guestbook_key(guestbook_name)).order('-date')
		#greetings = greetings_query.fetch(10)
		
		devicedb_name=self.request.get('devicedb_name')
		devices_query = Device.all().ancestor(
			devicedb_key(devicedb_name)).order('-DeviceName')
		devices = devices_query.fetch(50)

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'devices': devices,
			'url': url,
			'url_linktext': url_linktext,
		}

		template = jinja_environment.get_template('index.html')
		self.response.out.write(template.render(template_values))

	def post(self):

		# Can Use this to post data to the datastore
		# We set the same parent key on the 'Greeting' to ensure each greeting is in
		# the same entity group. Queries across the single entity group will be
		# consistent. However, the write rate to a single entity group should
		# be limited to ~1/second.

		devicedb_name = self.request.get('devicedb_name')
		device = Device(parent=devicedb_key(devicedb_name))

		#if users.get_current_user():
		  #greeting.author = users.get_current_user().nickname()

		device.DeviceName = self.request.get('DeviceName')
		device.Description = self.request.get('Description')
		device.Command = self.request.get('Command')
		device.IP = self.request.get('IP')
		device.Port = self.request.get('Port')
		device.put()
		
		# Mail construct to test using the api inclusion. Can be used to notify a new device being added currently.
		# More needed to implement notification e-mails when failures occur
		
		mail.send_mail(sender="Robert Augenstein <Robert_Augenstein@usc.salvationarmy.org>",
			to="Rob Augenstein <robaugie@gmail.com>",
			subject="Device Has Been Added",
			body="""
				Dear Robert:

				A new device has been added to the Device list please check it out.
				
				-Robert
				
			""")
						
		self.redirect('/main?' + urllib.urlencode({'devicedb_name': devicedb_name}))
		
class ContactHandler(webapp2.RequestHandler):
	def get(self):

		""" This class holds all structure for the Command Page which will most likely be updated to Contacts in the future """

		commanddb_name=self.request.get('commanddb_name')
		commands_query = Command.all().ancestor(
			commanddb_key(commanddb_name)).order('-Command')
		commands = commands_query.fetch(20)

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'commands': commands,
			'url': url,
			'url_linktext': url_linktext,
		}

		template = jinja_environment.get_template('command.html')
		self.response.out.write(template.render(template_values))

	def post(self):

		# Can Use this to post data to the datastore
		# We set the same parent key on the 'Greeting' to ensure each greeting is in
		# the same entity group. Queries across the single entity group will be
		# consistent. However, the write rate to a single entity group should
		# be limited to ~1/second.

		commanddb_name = self.request.get('commanddb_name')
		command = Command(parent=commanddb_key(commanddb_name))

		command.Command = self.request.get('Command')
		command.Contact = self.request.get('Contact')
		command.EMail = self.request.get('EMail')
		command.put()
		
		# Mail construct to test using the api inclusion. Can be used to notify a new device being added currently.
		# More useful to implement notification e-mails when failures occur
		
		mail.send_mail(sender="Robert Augenstein <Robert_Augenstein@usc.salvationarmy.org>",
			to="Rob Augenstein <robaugie@gmail.com>",
			subject="Device Has Been Added",
			body="""
				Dear Robert:

				A new command has been added to the Command list please check it out.
				
				-Robert
				
			""")
						
		self.redirect('/contacts?' + urllib.urlencode({'commanddb_name': commanddb_name}))

class StatusHandler(webapp2.RequestHandler):
	def get(self):

		""" This class contains the structure for the Status Page """
		
		newupdates = []

		updatedb_name=self.request.get('updatedb_name')
		updates_query = Update.all().ancestor(
			updatedb_key(updatedb_name)).order('-Date')
		updates = updates_query.fetch(24)
		thecount = updates_query.count()
		
		update = Update(parent=updatedb_key(updatedb_name))

		#Using each value from Devices

		devicedb_name=self.request.get('devicedb_name')
		devices_query = Device.all().ancestor(
			devicedb_key(devicedb_name)).order('DeviceName')
		devices = devices_query.fetch(50)

		""" Iterates through the devices datastore and uses each value to filter the updates datastore before ordering it
			and fetching the first entry so that we can get the most current update data for each specific device """

		for xstatus, ystatus in enumerate(devices):

			UpdateTest = Update.all()
			UpdateTest.filter("DeviceName =", devices[xstatus].DeviceName)
			UpdateTest.order("-Date")

			UpdateResult = UpdateTest.fetch(1)
			for x,y in enumerate(UpdateResult):
				#logging.info(UpdateResult[x].Date.__str__())
				#logging.info(UpdateResult[x].Date.toordinal())
				#UpdateResult[x].Date = UpdateResult[x].Date.__str__()
				#logging.info(UpdateResult[x].Date.replace(tzinfo=gmt1))
				#logging.info(time.mktime(UpdateResult[x].Date.timetuple())*1000.0)
				#logging.info(UpdateResult[x].Date.strftime('%Y%m%d%H%M%S%f'))
				#UpdateResult[x].ModDate = UpdateResult[x].Date.ctime()
				UpdateResult[x].ModDate = time.mktime(UpdateResult[x].Date.timetuple())*1000.0
				#logging.info(UpdateResult[x].ModDate)
				newupdates.append(UpdateResult[x])

		logging.info(thecount)

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'updates': newupdates,
			'url': url,
			'url_linktext': url_linktext,
			'newupdates': newupdates,
		}

		template = jinja_environment.get_template('status - Copy.html')
		self.response.out.write(template.render(template_values))

	def post(self):

		#Using each value from Devices
		devicedb_name=self.request.get('devicedb_name')
		devices_query = Device.all().ancestor(
			devicedb_key(devicedb_name)).order('DeviceName')
		devices = devices_query.fetch(50)

		#for x, y in DeviceList
		for x, y in enumerate(devices):
		
			updatedb_name = self.request.get('updatedb_name')
			update = Update(parent=updatedb_key(updatedb_name))

			if(int(devices[x].Port)==4110):
				url = "http://" + devices[x].IP + ":" + devices[x].Port
				
			else:
				url = "https://" + devices[x].IP + ":" + devices[x].Port
					
			update.Device = devices[x].Command + " " + devices[x].Description
			update.DeviceName = devices[x].DeviceName
			
			try:
				result = urlfetch.fetch(url,validate_certificate=False)
				
			except Exception as urlfail:
				logging.info(urlfail)
				update.Note = str(urlfail)
				update.Status = "Down"
				
			else:
				if result.status_code == 200:
					update.Status = "Up"
				else:
					update.Status = "Down"
			
			update.put()
			
		self.redirect('/status?' + urllib.urlencode({'updatedb_name': updatedb_name}))

class UpdateStore(webapp2.RequestHandler):
	def post(self):

		# Can Use this to post data to the datastore
		# We set the same parent key on the 'Greeting' to ensure each greeting is in
		# the same entity group. Queries across the single entity group will be
		# consistent. However, the write rate to a single entity group should
		# be limited to ~1/second.

		updatedb_name = self.request.get('updatedb_name')
		update = Update(parent=updatedb_key(updatedb_name))

		update.Device = self.request.get('Device')
		update.DeviceName = self.request.get('DeviceName')
		update.Status = self.request.get('Status')
		update.Note = self.request.get('Note')
		update.put()
							
		#self.redirect('/command?' + urllib.urlencode({'commanddb_name': commanddb_name}))
		
class DeviceRemove(webapp2.RequestHandler):
	def post(self):
		# Can Use this to remove data from the datastore
		devicedb_name = self.request.get('devicedb_name')
		device = Device(parent=devicedb_key(devicedb_name))
		
		ToRemove = self.request.get('ToRemove')
		logging.info("The record to be deleted is %s", str(ToRemove))
		
		remove = device.gql("WHERE DeviceName = :Device", Device=ToRemove )
		
		"""remove = db.GqlQuery("SELECT * "
						"FROM Device "
						"WHERE ANCESTOR IS :1 "
						"WHERE DeviceName = :2 "
						"ORDER BY date DESC LIMIT 10",
						devicedb_key(devicedb_name),
						ToRemove)"""
						
		db.delete(remove)
		
		self.redirect('/main?' + urllib.urlencode({'devicedb_name': devicedb_name}))
		
class CommandRemove(webapp2.RequestHandler):
	def post(self):
		# Can Use this to remove data from the datastore
		commanddb_name = self.request.get('commanddb_name')
		command = Command(parent=commanddb_key(commanddb_name))
		
		ToRemove = self.request.get('ToRemove')
		logging.info("The record to be deleted is %s", str(ToRemove))
		
		remove = command.gql("WHERE Command = :Command", Command=ToRemove )
		
		db.delete(remove)
		
		self.redirect('/command?' + urllib.urlencode({'commanddb_name': commanddb_name}))

class CronStatusHandler(webapp2.RequestHandler):
	def get(self):

		#Using each value from Devices
		devicedb_name=self.request.get('devicedb_name')
		devices_query = Device.all().ancestor(
			devicedb_key(devicedb_name)).order('DeviceName')
		devices = devices_query.fetch(50)

		#for x, y in DeviceList
		for x, y in enumerate(devices):
		
			updatedb_name = self.request.get('updatedb_name')
			update = Update(parent=updatedb_key(updatedb_name))

			if(int(devices[x].Port)==4110):
				url = "http://" + devices[x].IP + ":" + devices[x].Port
				
			else:
				url = "https://" + devices[x].IP + ":" + devices[x].Port
					
			update.Device = devices[x].Command + " " + devices[x].Description
			update.DeviceName = devices[x].DeviceName
			
			try:
				result = urlfetch.fetch(url,validate_certificate=False)
				
			except Exception as urlfail:
				logging.info(urlfail)
				update.Note = str(urlfail)
				update.Status = "Down"
				
			else:
				if result.status_code == 200:
					update.Status = "Up"
				else:
					update.Status = "Down"
			
			update.put()
			

class LoginHandler(webapp2.RequestHandler):
	def get(self):
	
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'url': url,
			'url_linktext': url_linktext,
		}

		template = jinja_environment.get_template('login.html')
		self.response.out.write(template.render(template_values))

class PurgeDataStore(webapp2.RequestHandler):
	def get(self):

		updatedb_name = self.request.get('updatedb_name')
		update = Update(parent=updatedb_key(updatedb_name))
		UpdatePurge = Update.all()

		logging.info('Entered the Purge')

		"""
		for x,y in enumerate(UpdatePurge):
			delta = datetime.today() - UpdatePurge[x].Date
			
			if((UpdatePurge[x].Status == 'Up') and (delta.days <= 1)):
				logging.info(UpdatePurge[x].Status)
				#db.delete(UpdatePurge[x])
				Update.delete(UpdatePurge[x])

		
		"""
		delta = datetime.today() - timedelta(minutes=+20)
		logging.info(delta)
		remove = update.gql("WHERE Date <= :Date AND Status = :Status", Date=delta, Status='Up')
		db.delete(remove)
		
		logging.info('The purge has ended')



class DeviceInformation(webapp2.RequestHandler):
	def post(self):
		devicedb_name = self.request.get('devicedb_name')
		device = Device(parent=devicedb_key(devicedb_name))

		DeviceInfo = self.request.get('DeviceName')
		logging.info("The record to be deleted is %s", str(DeviceInfo))

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'url': url,
			'url_linktext': url_linktext,
		}

		template = jinja_environment.get_template('test.html')
		self.response.out.write(template.render(template_values))

	def get(self, DeviceInfoName):

		#logging.info(DeviceInfoName)
		devicehistory = []

		UpdateTest = Update.all()
		UpdateTest.filter("DeviceName =", DeviceInfoName)
		UpdateTest.order("-Date")

		for x,y in enumerate(UpdateTest):
			UpdateTest[x].ModDate = time.mktime(UpdateTest[x].Date.timetuple())*1000.0
			devicehistory.append(UpdateTest[x])

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'updates': devicehistory,
			'url': url,
			'url_linktext': url_linktext,
		}

		template = jinja_environment.get_template('individualstatus.html')
		self.response.out.write(template.render(template_values))
		

app = webapp2.WSGIApplication([('/', StatusHandler),
							   ('/main', DeviceHandler),
		                       ('/store', DeviceHandler),
							   ('/contacts', ContactHandler),
   							   ('/contactstore', ContactHandler),
							   ('/status', StatusHandler),
   							   ('/updater', StatusHandler),
   							   ('/cronupdater', CronStatusHandler),
							   ('/updatestore', UpdateStore),
							   ('/remove', DeviceRemove),
							   ('/contactremove', CommandRemove),
							   ('/login', LoginHandler),
							   ('/purgeupdates', PurgeDataStore),
							   (r'/deviceinfo/(.*)', DeviceInformation)],
                              debug=True)