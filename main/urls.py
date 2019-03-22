from django.conf.urls import url, include
from . import views

urlpatterns = [

	url(r'^$', views.index, name="main-index"), # should be here, if not cvannot access any page. Maybe can use this for check cookies login.
	url(r'^user/(?P<userReceiver>[\d]+)/', views.index, name="main-index"),
	url(r'^facility/(?P<facilityId>[\d]+)/$', views.facility, name="main-facility"),
	url(r'^account/$', views.account, name="main-account"),
	url(r'^transactions/$', views.transactions, name="main-transactions"),
	url(r'^admin/$', views.admin, name="main-admin"),
	# url(r'^admin/facility/$', views.admin, name="main-admin"),
	# url(r'^admin/transaction/$', views.admin, name="main-admin"),

	# url(r'user/(?P<userReceiver>[\d]+)/$', views.user, name="main-user"),
	url(r'^login/$', views.login, name="main-login"),

	# url(r'^testScan/$', views.testScan, name="main-testScan"),

	# for test since cannot use mobile at home.
	url(r"^scan/(?P<userReceiver>[\d]+)/$", views.scan, name="main-scan")
    
]
