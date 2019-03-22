# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

from django.shortcuts import render
from django.shortcuts import redirect

from main.models import Facilities
from main.models import FacOverview
from main.models import Users
from main.models import AccountMoney

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.hashers import make_password, check_password
import hashlib
import re
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import transaction

from datetime import datetime
from django.contrib import messages

date_today = datetime.today().date()
time_now = datetime.now()

def rounder(t):
    if t.hour == 6 :
        return t.replace(minute=0, hour=6)
    elif t.hour == 7:
        return t.replace(minute=0, hour=8)
    elif t.hour == 8:
        return t.replace(minute=0, hour=8)
    elif t.hour == 9:
        return t.replace(minute=0, hour=10)
    elif t.hour == 10:
        return t.replace(minute=0, hour=10)
    elif t.hour == 11:
        return t.replace(minute=0, hour=12)
    elif t.hour == 12:
        return t.replace(minute=0, hour=12)
    elif t.hour == 13:
        return t.replace(minute=0, hour=14)
    elif t.hour == 14:
        return t.replace(minute=0, hour=14)
    elif t.hour == 15:
        return t.replace(minute=0, hour=16)
    elif t.hour == 16:
        return t.replace(minute=0, hour=16)
    elif t.hour == 17:
        return t.replace(minute=0, hour=18)
    elif t.hour == 18:
        return t.replace(minute=0, hour=18)
    else:
        return t.replace(minute=0, hour=18)

@csrf_exempt
def login(request):
    login_page = True
    if "fog" in request.COOKIES.keys():
        cookie_value = request.COOKIES['fog']
        user_id = re.sub(r"[?<=/]\w*","",cookie_value)
        user_value = re.sub(r"\w*[?<=/]","",cookie_value)
        users = Users.objects.filter(id_users=user_id)

        for i in users:
            user_id = i.id_users
            if user_value ==  hashlib.sha1(i.username).hexdigest():
                return redirect('/user/'+str(user_id)+'/')

    if request.method == 'POST': # POST - to update error row list
        username = request.POST['username']
        password = request.POST['password']
        users = Users.objects.filter(username=username)

        if not users:
            messages.info(request,'failed', extra_tags='login_username_invalid')
            # return HttpResponse("Invalid Username/Password")
            return redirect('/login/')
        else:

            for i in users:
                user_id = i.id_users
                user_username = i.username
                pwd = i.password
                if password == pwd :
                    hex_dig = hashlib.sha1(user_username).hexdigest()
                    # response = render(request, 'main/login.html')
                    if user_id == 0:
                        response = redirect('/admin/')
                    else:
                        response = redirect('/user/'+str(user_id)+'/')

                    response.set_cookie(key='fog',value= str(user_id) + "/" + str(hex_dig), max_age=86400)
                    # response.cookies['dashboard']['expires'] = datetime.datetime.today() + datetime.timedelta(days=2) #Expire the above 1 day from today.
                    return response
                else:
                    messages.info(request,'failed', extra_tags='login_pwd_invalid')
                    # return HttpResponse("Invalid Username/Password")
                    return redirect('/login/')
            
        
    context = {
        "login_page":login_page
    }

    return render(request, "main/login.html", context)


# Create your views here.
def index(request, userReceiver):
    profile=None
    if "fog" not in request.COOKIES.keys():
        return redirect("/login")

    if "fog" in request.COOKIES.keys():
        cookie_value = request.COOKIES['fog']
        user_id = re.sub(r"[?<=/]\w*","",cookie_value)
        # users = Users.objects.filter(id_users=user_id)
        if user_id == userReceiver:
            profile = True
        else:
            profile = False

    users = Users.objects.all()
    acc_money = AccountMoney.objects.all()
    fac_overview = FacOverview.objects.all()
    fac = Facilities.objects.all()

    # Base + Bar Graph
    fac_overview_list = []
    fac_name_list = []
    for i in fac_overview:
        if date_today == i.date:
            if i.time == rounder(time_now).strftime("%H%M"):
                fac_overview_list.append(i.current_occupancy) # [u'20', u'1', u'1', u'10', u'0']
                fac_name = fac.get(facility_id=i.facility_id)
                fac_name_list.append(fac_name) # [<QuerySet [{u'facility_name': u'Library'}]>, <QuerySet [{u'facility_name': u'test'}]>...


    username = users.get(id_users=userReceiver).username
    acc_balance = acc_money.filter(id_account=userReceiver)
    if not acc_balance:
        acc_balance = 0
    else:
        acc_balance = acc_money.filter(id_account=userReceiver).values('balance') # <QuerySet [{u'balance': Decimal('32.00')}]>
        acc_balance = acc_balance[0]['balance']

    qr_image = users.filter(id_users=userReceiver).values('qr_code')
    qr_image = qr_image[0]['qr_code']
    context = {
        #==================== Base ====================
        "fac_overview_list":fac_overview_list,
        "fac_name_list": fac_name_list,
        'user_id': int(user_id),
        #==============================================
        "users":users,
        "username":username,
        "userReceiver":userReceiver,
        "acc_balance":acc_balance,
        "profile":profile,
        "qr_image":qr_image
        
    }

    return render(request, "main/index.html", context)

# def testScan(request):

#     return HttpResponse("Hello World")

def  scan(request, userReceiver):
    # userId : comes from QR image
    # user_id : scanner
    # userReceiver : comes from QR image
    # userScanner : scanner

    userReceiver = userReceiver
    # scanner pov | qrcode : /scan/<id_users>
    # ==========================================
    fac = Facilities.objects.all()
    fac_overview = FacOverview.objects.all()
    user = Users.objects.all()
    time_now = datetime.now()

    if "fog" in request.COOKIES.keys():
        cookie_value = request.COOKIES['fog']
        userScanner = re.sub(r"[?<=/]\w*","",cookie_value)
        user_value = re.sub(r"\w*[?<=/]","",cookie_value)

        # Get facilities_id
        user_fac = user.filter(id_users=userScanner)
        user_cookies = user_fac.values('cookies').filter(id_users=userScanner) # library_cookies = 1

        if user_cookies[0]['cookies'] == None:
            # return HttpResponse("Its a user")

            return redirect('/transactions/?receiver=' + str(userReceiver))

        else:
            # return HttpResponse("Its a facility")
            checkUser = user.filter(id_users=userReceiver).values('location')
            checkUser = checkUser[0]['location']
            if checkUser == None:
                 # checksIn
                time_now = rounder(time_now).strftime("%H%M")
                # fac_name = fac.filter(facility_id=user_cookies).values('facility_name').first()
                # fac_name = fac_name['facility_id']

                facility = fac_overview.filter(facility_id=user_cookies, date=date_today,time=time_now).first() # facility_id = 1
                c_occupancy = int(facility.current_occupancy)
                fac_id = int(facility.facility_id)
                
                # Update Facilities current_occupancy
                fac_update = fac_overview.filter(facility_id=user_cookies, date=date_today,time=time_now).update(current_occupancy=c_occupancy + 1)

                # Update Users location
                userReceiver_update = user.filter(id_users=userReceiver).update(location=facility.facility_id)

                return redirect("/facility/" + str(fac_id) + "/")
            else:
                #checksOut
                time_now = rounder(time_now).strftime("%H%M")

                facility = fac_overview.filter(facility_id=user_cookies, date=date_today,time=time_now).first() # facility_id = 1
                c_occupancy = int(facility.current_occupancy)
                fac_id = int(facility.facility_id)

                # Update Facilities current_occupancy
                fac_update = fac_overview.filter(facility_id=user_cookies, date=date_today,time=time_now).update(current_occupancy=c_occupancy - 1)

                # Update Users location
                userReceiver_update = user.filter(id_users=userReceiver).update(location=None)

                return redirect("/facility/" + str(fac_id) + "/")


    else:
        return HttpResponse("Invalid page")
    # ==========================================

    context = {}

    


def facility(request, facilityId):
    if "fog" in request.COOKIES.keys():
        cookie_value = request.COOKIES['fog']
        user_id = re.sub(r"[?<=/]\w*","",cookie_value)
        user_value = re.sub(r"\w*[?<=/]","",cookie_value)

    time_now = datetime.now()
    time_now = rounder(time_now).strftime("%H%M")

    fac_overview = FacOverview.objects.all()
    fac = Facilities.objects.all()
    facilityId = int(facilityId)

    facility = fac.filter(facility_id=facilityId).first()
    facility_name = facility.facility_name

    facility_overview = fac_overview.filter(facility_id=facilityId, date=date_today, time=time_now).first()
    
    current_occupancy = int(facility_overview.current_occupancy)
    total_occupancy = int(facility_overview.total_occupancy)

    empty_occupancy = total_occupancy - current_occupancy

    try:
        percentage_occupancy = round((current_occupancy/total_occupancy) * 100, 1)
    except ZeroDivisionError:
        percentage_occupancy = 0

    # Base
    fac_overview_list = []
    fac_name_list = []
    for i in fac_overview:
        if date_today == i.date:
            fac_overview_list.append(i.current_occupancy) # [u'20', u'1', u'1', u'10', u'0']
            fac_name = fac.get(facility_id=i.facility_id)
            fac_name_list.append(fac_name) # [<QuerySet [{u'facility_name': u'Library'}]>, <QuerySet [{u'facility_name': u'test'}]>...

    # Line Graph
    fac_overview_line = []
    for i in fac_overview:
        if i.facility_id == facilityId:
            fac_overview_line.append(i)

    context = {
        #==================== Base ====================
        "fac_overview_list":fac_overview_list,
        "fac_name_list": fac_name_list,
        'user_id':user_id,
        #==============================================
        "facility_name": facility_name,
        "current_occupancy": current_occupancy,
        "empty_occupancy":  empty_occupancy,
        "percentage_occupancy":percentage_occupancy,
        "date_today": date_today,
        "fac_overview_line": fac_overview_line

    }

    return render(request, "main/facility.html", context)

def account(request):

    context = {

    }

    return render(request, "main/account.html", context)


@csrf_exempt
def admin(request):
    if "fog" in request.COOKIES.keys():
        cookie_value = request.COOKIES['fog']
        user_id = re.sub(r"[?<=/]\w*","",cookie_value)
        user_value = re.sub(r"\w*[?<=/]","",cookie_value)


    fac = Facilities.objects.all()
    fac_overview = FacOverview.objects.all()

    users = Users.objects.all()
    acc_money = AccountMoney.objects.all()

    date_today = datetime.today().date()
    time_now = datetime.now()
    time_now = rounder(time_now).strftime("%H%M")

    already_exist = None
    invalid_input = None
    if request.method == 'POST': # POST - to update error row list
        if 'fac_id' in request.POST:
            fac_id =  request.POST['fac_id']
            fac_name =  request.POST['fac_name']
            fac_cap =  request.POST['fac_cap']

            try:
                fac_id = int(fac_id)
                fac_name = str(fac_name)
                fac_cap = int(fac_cap)
            except:
                messages.info(request,'failed.', extra_tags='fac_invalid')
                return redirect("/admin/")

            
            fac_exist = fac.filter(facility_id=fac_id).first()
            if fac_exist:
                messages.info(request,'failed.', extra_tags='fac_exist')
            else:
                # Not yet Exist
                fac_add = Facilities(facility_id=fac_id, facility_name=fac_name)
                fac_add.save()

# time_list = ["0600","0800","1000","1200","1400","1600","1800"]
# for time in time_list:
#     fac_overview_add = FacOverview( date=date_today,time=time,facility_id=7, total_occupancy=20, current_occupancy=0)
#     fac_overview_add.save()
                
                FacOverview.objects.bulk_create([
                    FacOverview( date=date_today,time="0600",facility_id=fac_id, total_occupancy=fac_cap, current_occupancy=0),
                    FacOverview( date=date_today,time="0800",facility_id=fac_id, total_occupancy=fac_cap, current_occupancy=0),
                    FacOverview( date=date_today,time="1000",facility_id=fac_id, total_occupancy=fac_cap, current_occupancy=0),
                    FacOverview( date=date_today,time="1200",facility_id=fac_id, total_occupancy=fac_cap, current_occupancy=0),
                    FacOverview( date=date_today,time="1400",facility_id=fac_id, total_occupancy=fac_cap, current_occupancy=0),
                    FacOverview( date=date_today,time="1600",facility_id=fac_id, total_occupancy=fac_cap, current_occupancy=0),
                    FacOverview( date=date_today,time="1800",facility_id=fac_id, total_occupancy=fac_cap, current_occupancy=0),
                ])
                # run default script for FacOverview. check if else condition.
                messages.success(request,'success', extra_tags='fac_add')

            return redirect("/admin/")

        if 'delete_fac' in request.POST:
            fac_id = int(request.POST['delete_fac']) #{{facility_id}}
            try:
                fac_remove = fac.get(facility_id=fac_id)
                fac_remove.delete()

                fac_overview_remove = fac_overview.filter(facility_id=fac_id)
                fac_overview_remove.delete()

                messages.success(request,'success', extra_tags='fac_remove')
            except:
                messages.info(request,'failed.', extra_tags='fac_remove_fail')
            return redirect("/admin/") # somehow after redirecting, i still cannot unset post request


        if 'fund_acc' in request.POST:
            # if request.POST['fund_acc']
            try:
                fund_user = acc_money.filter(id_account=request.POST['fund_acc'])
                fund_update = fund_user.update(balance=int(fund_user[0].balance) + int(request.POST['fund_amount']))
                
                messages.success(request,'success.', extra_tags='fund_success')
                
            except Exception as e:
                messages.success(request,'success.', extra_tags='fund_fail')

            return redirect("/admin/")

        if 'new_acc' in request.POST:
            try:
                new_user = users.filter(id_users=request.POST['new_acc']).first()
                if new_user == None:
                    new_user_add = Users(id_users=request.POST['new_acc'], username=request.POST['new_username'], password=request.POST['new_password'], email=request.POST['new_email'], qr_code=request.POST['new_qrcode'])
                    # new_user_add = Users(id_users=5, username="asd", password="asdsdd", email="dasfsd", qr_code="asdasdcxv")
                    new_user_add.save()

                    new_balance_add = AccountMoney(id_account=request.POST['new_acc'], balance=0)
                    new_balance_add.save() 

                    messages.success(request,'success.', extra_tags='new_user_success')
                else:
                    messages.info(request,'failed.', extra_tags='new_user_fail')
                
            except Exception as e:
                messages.success(request,'success.', extra_tags='new_user_success')
                
            return redirect("/admin/")

        if 'delete_user' in request.POST:
            del_user_id = int(request.POST['delete_user'])
            try:
                user_remove = users.get(id_users=del_user_id)
                user_remove.delete()

                balance_remove = acc_money.get(id_account=del_user_id)
                balance_remove.delete()

                messages.success(request, 'success.' , extra_tags='del_user_success')
            except:
                messages.info(request,'failed.', extra_tags='del_user_fail')
            return redirect("/admin/") # somehow after redirecting, i still cannot unset post request


        
        return redirect("/admin/")

    # Base 
    fac_overview_list = []
    fac_name_list = []
    for i in fac_overview:
        if date_today == i.date:
            if i.time == time_now:
                fac_overview_list.append(i.current_occupancy) # [u'20', u'1', u'1', u'10', u'0']
                fac_name = fac.get(facility_id=i.facility_id)
                fac_name_list.append(fac_name) # [<QuerySet [{u'facility_name': u'Library'}]>, <QuerySet [{u'facility_name': u'test'}]>...

    # Line Graph
    date_list = []
    c_occ_list = []
    date_distinct = fac_overview.values('date').distinct()
    for i in date_distinct:
        date_list.append(i['date'])

    for i in fac_overview:
        x = 0
        c = fac_overview.filter(facility_id=i.facility_id, date=date_list[x+1]).aggregate(Max('current_occupancy'))
        c_occ_list.append(c)


    context = {
    "fac":fac,
    "fac_overview": fac_overview,
    "users":users,
    #==================== Base ====================
    "fac_overview_list":fac_overview_list,
    "fac_name_list": fac_name_list,
    'user_id':user_id,
    #==============================================
    "already_exist":already_exist,
    "invalid_input": invalid_input,
    "date_today":date_today,
    "time_now":time_now,
    "date_list":date_list,
    "c_occ_list":c_occ_list,
    }

    return render(request, "main/admin.html", context)



# def user(request, userId):
#     userId = userId

#     fac = FacOverview.objects.all()

#     library_current = fac.get(facility_id=1)
#     library_current = library_current.current_occupancy
#     library_update = fac.filter(facility_id=1).update(current_occupancy=library_current+1)

#     return redirect("/library") 


@csrf_exempt
def transactions(request):
    # userReceiver : comes from QR image 
    # userScanner : scanner [cookies]
    # use cookies as user and scan qr code as receiver.

    user = Users.objects.all()
    acc_money = AccountMoney.objects.all()
    if "fog" in request.COOKIES.keys():
        cookie_value = request.COOKIES['fog']
        userScanner = re.sub(r"[?<=/]\w*","",cookie_value)
        user_id = userScanner
        user_value = re.sub(r"\w*[?<=/]","",cookie_value)

        userScanner = user.get(id_users=userScanner)
        userScanner = userScanner.id_users
    else:
        redirect('/login')

    try:
        userReceiver = request.GET.get('receiver')
        userReceiver = user.get(id_users=userReceiver)
        userReceiver = userReceiver.id_users
    except ValueError:
        userReceiver = None


    
    invalid_input = None
    invalid_user = None
    userScanner_balance = int(acc_money.get(id_account=userScanner).balance)
    if request.method == 'POST':
        
        userScanner = request.POST['userScanner']
        userReceiver = request.POST['userReceiver']
        amount = request.POST['amount']
        try:
            amount = int(amount)
            reference = request.POST['reference']
            try:
                userScanner_balance = int(acc_money.get(id_account=userScanner).balance)
                if userScanner_balance < amount:
                    messages.info(request,'failed.', extra_tags='transactions_insufficient')
                    return redirect('/transactions/?receiver=' + str(userReceiver))
                userScanner_update = acc_money.filter(id_account=userScanner).update(balance=userScanner_balance - amount)

                userReceiver_balance = int(acc_money.get(id_account=userReceiver).balance)
                userReceiver_update = acc_money.filter(id_account=userReceiver).update(balance=userReceiver_balance + amount)

                messages.success(request,'success.', extra_tags='transactions_success')
                return redirect('/user/'+str(userScanner)+'/')
            except:
                invalid_user = True
        except:
            invalid_input = True
            # context = {
            #     "userReceiver":userReceiver,
            #     "userScanner": userScanner,

            #     "invalid_input":invalid_input

            # }

            # return render(request, "main/transactions.html", context)

    fac = Facilities.objects.all()
    fac_overview = FacOverview.objects.all()
    # Base 
    fac_overview_list = []
    fac_name_list = []
    for i in fac_overview:
        if date_today == i.date:
            if i.time == rounder(time_now).strftime("%H%M"):
                fac_overview_list.append(i.current_occupancy) # [u'20', u'1', u'1', u'10', u'0']
                fac_name = fac.get(facility_id=i.facility_id)
                fac_name_list.append(fac_name) # [<QuerySet [{u'facility_name': u'Library'}]>, <QuerySet [{u'facility_name': u'test'}]>...

    context = {
    "userReceiver":userReceiver,
    "userScanner": userScanner,
    'user_id':user_id,
    "userScanner_balance":userScanner_balance,

    "invalid_input":invalid_input,
    "invalid_user":invalid_user,
    #==================== Base ====================
    "fac_overview_list":fac_overview_list,
    "fac_name_list": fac_name_list,
    #==============================================

    }

    return render(request, "main/transactions.html", context)

