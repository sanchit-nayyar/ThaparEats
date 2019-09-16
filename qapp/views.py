from django.shortcuts import render
from selenium import webdriver
from pyvirtualdisplay import Display
from qapp.models import *
import hashlib, MySQLdb, traceback

def check_val(restaurant_id, roll_number):
	hostel = (Student.objects.get(roll_id = roll_number)).hos_code
	min_order = (Restaurant.objects.get(id = restaurant_id)).min_order_val
	current_order_total = 0
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'SELECT amount, user_id, order_id FROM Order_Details WHERE delivery_status = "ORDERED" AND restaurant_id = ' + str(restaurant_id) + ';'
	print query
	c.execute(query)
	results = c.fetchall()
	match_students = []
	for row in results:
		if (Student.objects.get(roll_id = row[1])).hos_code == hostel:
			current_order_total += int(row[0])
			match_students.append(row[2])
	print len(match_students)
	if current_order_total >= min_order:
		for sdnt in match_students:
			try:
				print 'rng'
				qry = 'UPDATE Order_Details SET delivery_status = "RECIEVED" WHERE order_id = ' + str(sdnt)
				print qry
				c.execute(qry)
				db.commit()
			except:
				db.rollback()
	db.close()


def next_value():
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'SELECT MAX(order_id) FROM Order_Details'
	c.execute(query)
	try:
		nextval = int(c.fetchone()[0])
	except:
		nextval = 0
	return nextval + 1
	db.close()

def attempt_kiosk_login(roll, pwd):
	display = Display(visible=0, size=(1366, 768))
	display.start()
	ffx = webdriver.Firefox()
	ffx.get('https://webkiosk.thapar.edu/index.jsp?_ga=2.47888167.1679932621.1542041253-847389414.1540468662')
	ffx.find_element_by_name('MemberCode').send_keys(roll)
	ffx.find_element_by_name('Password').send_keys(pwd)
	ffx.find_element_by_name('BTNSubmit').click()
	url = ffx.current_url
	ffx.close()
	display.stop()
	return url == 'https://webkiosk.thapar.edu/StudentFiles/StudentPage.jsp'

def kiosk_running():
	return attempt_kiosk_login('101603302', '101601857')
# Create your views here.

def home(request):
	return render(request, 'qapp/index.html', {})

def register(request):
	if kiosk_running():
		return render(request, 'qapp/register.html', {})
	return render(request, 'qapp/index.html', {'eMsg': 'Thapar service for registration is not running. Please try again later'})

def fpwd(request):
	if kiosk_running():
		return render(request, 'qapp/forgotpassword.html', {})
	return render(request, 'qapp/index.html', {'eMsg': 'Thapar service for Password Reset is not running. Please try again later'})

def rgstr(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	un = request.POST['uname']
	rn = request.POST['roll']
	pd = request.POST['psk']
	try:
		Student.objects.get(uname = un)
		return render(request, 'qapp/index.html', {'eMsg': 'Username not available'})
	except:
		pass

	try:
		Student.objects.get(roll_id = rn)
		return render(request, 'qapp/index.html', {'eMsg': 'Roll Number already registered'})
	except:
		pass
	if pd != request.POST['pskcnf']:
		return render(request, 'qapp/index.html', {'eMsg': 'Passwords do not match'})
	if not attempt_kiosk_login(rn, request.POST['wpd']):
		return render(request, 'qapp/index.html', {'eMsg': 'Incorrect Webkiosk Password. Auth Fail'})
	Student.objects.create(
		roll_id = rn,
		uname = un,
		psk = pd,
		hos_code = request.POST['hoscode'],
		mail_id = request.POST['mail'],
		contact = request.POST['cno']
		).publish()
	return render(request, 'qapp/index.html', {'eMsg': 'User Created!'})

def forgotpd(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	rn = request.POST['roll']
	pd = request.POST['psk']
	if pd != request.POST['pskcnf']:
		return render(request, 'qapp/index.html', {'eMsg': 'Passwords do not match'})
	if not attempt_kiosk_login(rn, request.POST['wpd']):
		return render(request, 'qapp/index.html', {'eMsg': 'Incorrect Webkiosk Password. Auth Fail'})
	s = Student.objects.get(roll_id = rn)
	s.psk = pd
	s.publish()
	return render(request, 'qapp/index.html', {'eMsg': 'Password Reset!'})

def login(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	un = request.POST['uname']
	pd = hashlib.sha256(request.POST['psk']).hexdigest()
	try:
		u = Student.objects.get(uname = un)
		if u.psk == pd:
			return render(request, 'qapp/hpage.html', {'user': u, 'restaurants': Restaurant.objects.all()})
		else:
			return render(request, 'qapp/index.html', {'eMsg': 'Incorrect Password'})
	except:
		return attempt_admin_login(request)

def fetchOrder(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	menu = Menu_item.objects.filter(restaurant_id = request.POST['rstrt'])
	return render(request, 'qapp/fetchOrder.html', {'restaurant_id': request.POST['rstrt'], 'user': Student.objects.get(roll_id = request.POST['user']), 'menu': menu})

def placeOrder(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	u_id = request.POST['user']
	restaurant_id = request.POST['restaurant_id']
	amount = 0
	sql_queries = []
	for item in Menu_item.objects.filter(restaurant_id = restaurant_id):
		amount += item.price * int(request.POST[item.item_id])
		if request.POST[item.item_id] != 0:
			sql_queries.append('INSERT INTO Order_Logs (order_id, item_id, qty) VALUES (' + str(next_value()) + ', "' + item.item_id + '", ' + request.POST[item.item_id] + ');')
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'INSERT INTO Order_Details (user_id, amount, restaurant_id) VALUES (' + str(u_id) + ', ' + str(amount) + ', ' + str(restaurant_id) + ');'
	try:
		if len(sql_queries) != 0:
			c.execute(query)
			db.commit()
			for squery in sql_queries:
				c.execute(squery)
				db.commit()
		check_val(restaurant_id, u_id)
		db.close()
		return render(request, 'qapp/index.html', {'eMsg': 'Order Placed Successfully'})
	except:
		db.rollback()
		db.close()
		return render(request, 'qapp/index.html', {'eMsg': traceback.format_exc()})

def prevOrders(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	order_logs = []
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'SELECT * FROM Order_Details WHERE user_id = ' + request.POST['user']
	c.execute(query)
	results = c.fetchall()
	for row in results:
		if row[5] == 'DELIVERED':
			row = list(row)
			row[3] = (Restaurant.objects.get(id = int(row[3]))).restaurant_name
			order_logs.append(row)
	return render(request, 'qapp/history.html', {'orders': order_logs, 'user': request.POST['user']})

def trackOrders(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	order_logs = []
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'SELECT * FROM Order_Details WHERE user_id = ' + request.POST['user']
	c.execute(query)
	results = c.fetchall()
	for row in results:
		if row[5] != 'DELIVERED':
			row = list(row)
			row[3] = (Restaurant.objects.get(id = int(row[3]))).restaurant_name
			order_logs.append(row)
	return render(request, 'qapp/track.html', {'orders': order_logs, 'user': request.POST['user']})

def attempt_admin_login(request):
	un = request.POST['uname']
	pd = hashlib.sha256(request.POST['psk']).hexdigest()
	try:
		u = Restaurant.objects.get(restaurant_name__iexact = un)
		if u.psk == pd:
			db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
			c = db.cursor()
			query = 'SELECT * FROM Order_Details WHERE restaurant_id = ' + str((Restaurant.objects.get(restaurant_name__iexact = un)).id)
			c.execute(query)
			ordercodes = []
			result = c.fetchall()
			for row in result:
				if row[5] != 'ORDERED' and not (row[5] == 'DELIVERED' and row[4] == 'PAID'):
					ordercodes.append(list(row))
					ordercodes[-1].append(Student.objects.get(roll_id = ordercodes[-1][1]).contact)
					ordercodes[-1][1] = Student.objects.get(roll_id = ordercodes[-1][1]).hos_code
			return render(request, 'qapp/rest_home.html', {'user': u, 'ords': ordercodes})
		else:
			return render(request, 'qapp/index.html', {'eMsg': 'Incorrect Password'})
	except:
		return render(request, 'qapp/index.html', {'eMsg': 'User Not Found'})

def markPaid(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	ordid = request.POST['o_id']
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'UPDATE Order_Details SET payment_status = \'PAID\' WHERE order_id = ' + ordid
	try:
		c.execute(query)
		db.commit()
	except:
		db.rollback()
		print 'UNABLE TO UPDATE'
		print query
	query = 'SELECT restaurant_id FROM Order_Details WHERE order_id = ' + ordid
	c.execute(query)
	restid = c.fetchone()[0]
	u = Restaurant.objects.get(id = restid)
	query = 'SELECT * FROM Order_Details WHERE restaurant_id = ' + str(restid)
	c.execute(query)
	ordercodes = []
	result = c.fetchall()
	for row in result:
		if row[5] != 'ORDERED' and not (row[5] == 'DELIVERED' and row[4] == 'PAID'):
			ordercodes.append(list(row))
			ordercodes[-1].append(Student.objects.get(roll_id = ordercodes[-1][1]).contact)
			ordercodes[-1][1] = Student.objects.get(roll_id = ordercodes[-1][1]).hos_code
	return render(request, 'qapp/rest_home.html', {'user': u, 'ords': ordercodes})

def markDispatched(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	ordid = request.POST['o_id']
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'UPDATE Order_Details SET delivery_status = \'DISPATCHED\' WHERE order_id = ' + ordid
	try:
		c.execute(query)
		db.commit()
	except:
		db.rollback()
		print 'UNABLE TO UPDATE'
		print query
	query = 'SELECT restaurant_id FROM Order_Details WHERE order_id = ' + ordid
	c.execute(query)
	restid = c.fetchone()[0]
	u = Restaurant.objects.get(id = restid)
	query = 'SELECT * FROM Order_Details WHERE restaurant_id = ' + str(restid)
	c.execute(query)
	ordercodes = []
	result = c.fetchall()
	for row in result:
		if row[5] != 'ORDERED' and not (row[5] == 'DELIVERED' and row[4] == 'PAID'):
			ordercodes.append(list(row))
			ordercodes[-1].append(Student.objects.get(roll_id = ordercodes[-1][1]).contact)
			ordercodes[-1][1] = Student.objects.get(roll_id = ordercodes[-1][1]).hos_code
	return render(request, 'qapp/rest_home.html', {'user': u, 'ords': ordercodes})

def markDelivered(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	ordid = request.POST['o_id']
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'UPDATE Order_Details SET delivery_status = \'DELIVERED\' WHERE order_id = ' + ordid
	try:
		c.execute(query)
		db.commit()
	except:
		db.rollback()
		print 'UNABLE TO UPDATE'
		print query
	query = 'SELECT restaurant_id FROM Order_Details WHERE order_id = ' + ordid
	c.execute(query)
	restid = c.fetchone()[0]
	u = Restaurant.objects.get(id = restid)
	query = 'SELECT * FROM Order_Details WHERE restaurant_id = ' + str(restid)
	c.execute(query)
	ordercodes = []
	result = c.fetchall()
	for row in result:
		if row[5] != 'ORDERED' and not (row[5] == 'DELIVERED' and row[4] == 'PAID'):
			ordercodes.append(list(row))
			ordercodes[-1].append(Student.objects.get(roll_id = ordercodes[-1][1]).contact)
			ordercodes[-1][1] = Student.objects.get(roll_id = ordercodes[-1][1]).hos_code
	return render(request, 'qapp/rest_home.html', {'user': u, 'ords': ordercodes})

def orderDetails(request):
	if request.method != 'POST':
		return render(request, 'qapp/index.html', {'eMsg': 'Cannot load page'})
	ordid = request.POST['o_id']
	db = MySQLdb.connect('localhost', 'root', 'password', 'QAPP')
	c = db.cursor()
	query = 'SELECT * FROM Order_Logs WHERE order_id = ' + ordid
	c.execute(query)
	orderDets = []
	result = c.fetchall()
	for row in result:
		orderDets.append(list(row))
		orderDets[-1][1] = Menu_item.objects.get(item_id = orderDets[-1][1]).item_name
	return render(request, 'qapp/orderDets.html', {'odets': orderDets})