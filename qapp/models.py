from django.db import models
import hashlib

class Student(models.Model):
	roll_id = models.IntegerField()
	uname = models.TextField()
	psk = models.TextField()
	hos_code = models.CharField(max_length = 2)
	mail_id = models.TextField()
	contact = models.TextField()

	def publish(self):
		self.psk = hashlib.sha256(self.psk).hexdigest()
		self.save()

	def __str__(self):
		return str(self.roll_id)

class Menu_item(models.Model):
	restaurant_id = models.IntegerField()
	item_id = models.TextField()
	price = models.IntegerField()
	item_name = models.TextField()

	def publish(self):
		if int((self.item_id).split('_')[0]) == self.restaurant_id:
			self.save()
			return True
		else:
			return False

	def __str__(self):
		return self.item_id + ': ' + self.item_name + ': ' + str(self.price)

class Restaurant(models.Model):
	restaurant_name = models.TextField()
	min_order_val = models.IntegerField()
	contact = models.IntegerField()
	psk = models.TextField()

	def publish(self):
		self.psk = hashlib.sha256(self.psk).hexdigest()
		self.save()

	def __str__(self):
		return self.restaurant_name