from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='lgn'),
    url(r'^register/$', views.register, name='rgstr'),
    url(r'^fpwd/$', views.fpwd, name='fpwd'),
    url(r'^register_submit/$', views.rgstr, name='rgstr_sbt'),
    url(r'^fpd_submit/$', views.forgotpd, name='fpd_sbt'),
    url(r'^login/$', views.login, name='login'),
    url(r'^login/fetchOrder/$', views.fetchOrder, name='fetchOrder'),
    url(r'^login/fetchOrder/placeOrder/$', views.placeOrder, name='placeOrder'),
    url(r'^login/trackOrders/$', views.trackOrders, name='trackOrder'),
    url(r'^login/prevOrders/$', views.prevOrders, name='showOrderHistory'),
    url(r'^markPaid/$', views.markPaid, name='markPaid'),
    url(r'^markDispatched/$', views.markDispatched, name='markDispatched'),
    url(r'^markDelivered/$', views.markDelivered, name='markDelivered'),
    url(r'^orderDetails/$', views.orderDetails, name='orderDetails'),
]