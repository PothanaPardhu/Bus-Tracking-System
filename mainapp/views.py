from django.shortcuts import render,redirect
from django.contrib import messages
from adminapp.models import *

from mainapp.models import *

# Create your views here.
def main_index(request):

    return render(request,'main/main-index.html')

def main_about(request):
    return render(request,'main/main-about.html')

def main_contact(request):
    return render(request,'main/main-contact.html')

def main_admin_login(request):
    if request.method=='POST':
        
        username=request.POST.get('username')
        userpassword=request.POST.get('userpassword')
        print(username,userpassword)

        if username =="admin" and userpassword == "admin":
            # print('suceeeee')
            messages.success(request,"admin successfully login")
            return redirect('admin_index')
        else:
            messages.error(request,"invalid credentials")
            return redirect('main_admin_login')
  

        messages.success(request,"invalid credentials")
       
    return render(request,'main/main-admin-login.html')



def main_conductor_login(request):
     if request.method=='POST':
        
        name=request.POST.get('name')
        password=request.POST.get('password')
        print(name,password)

        if name =="conductor" and password == "conductor":
            # print('suceeeee')
            messages.success(request,"successfully login")
            return redirect('conductor_index')
        else:
            messages.error(request,"invalid credentials")
            return redirect('main_conductor_login')
     return render(request,'main/main-conductor-login.html')

def main_parent(request):
     if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)

        try:
            
            # request.session[''] = 
            user = ChildModels.objects.get(
                children_email= email, children_password=password)
            request.session['c_id'] = user.c_id
            messages.success(request,"successfully login")
            return redirect('user_index')
        except:
            messages.error(request,"invalid credentials")
            return redirect('main_parent')
        
    
     return render(request,'main/main-parent-login.html')
