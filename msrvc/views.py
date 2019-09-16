from __future__ import unicode_literals
from django.shortcuts import render
import MySQLdb as sql

class sqlConnect:
	host = '127.0.0.1'
	username = 'root'
	passkey = 'password'
	dbname = 'Software'
	connector = None
	cursor = None
	def __init__(self):
		self.connector = sql.connect(self.host, self.username, self.passkey, self.dbname)
		self.cursor = self.connector.cursor()
	def __del__(self):
		(self.connector).close()
	def execQuery(self, query, writeNeed):
		try:
			rval = self.cursor.execute(query)
			if not writeNeed:
				rval = self.cursor.fetchall()
		except:
			return "False000"
		if writeNeed:
			try:
				self.cursor.commit()
			except:
				return False
		return rval

def encrypt(key):
	import hashlib
	return str(hashlib.sha256(str(hashlib.sha256(key).hexdigest())).hexdigest())

dbHandle = sqlConnect()

def home(request):
	hosNames = dbHandle.execQuery('SELECT hostelName from Hostel ORDER BY hostelName ASC;', False)
	return render(request, 'msrvc/index.html', {'hName': [i[0] for i in hosNames]})

def register(request):
	if request.method != 'POST':
		return render(request, 'msrvc/errPage.html')
	# Get User Data
	roll = request.POST['rno']
	name = request.POST['nm']
	phone = request.POST['cno']
	hostel = request.POST['hostel']
	passkey = encrypt("tiet@" + str(roll))
	response = dbHandle.execQuery('INSERT INTO STUDENT (RollNo, Name, secureKey, contactNumber, hostel) VALUES (' + str(roll) + ', "' + str(name) + '", "' + str(passkey) + '", ' + str(phone) + ', "' + str(hostel) + '")', True)
	return render(request, 'msrvc/index.html', {'execCode': response})