from django.shortcuts import render,redirect
from adminapp.models import *
from . import views
from django.contrib import messages
import requests
# import numpy as np
import math, random
# import qrcode
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files import File

from userapp.models import *

# from .models import QrCode
# import qrcode.image.svg

 
# Create your views here.
def admin_index(request):
    children=ChildModels.objects.all().count()
    # feedback=UserFeedbackModel.objects.all().count()
    # delay=DelayModel.objects.all().count()
    return render(request,'admin/admin-index.html',{'children':children})

def admin_addnewstudent(request):
 
    if request.method=='POST' and request.FILES['image']:

        name=request.POST.get('name')
        childclass=request.POST.get('class')
        mothername=request.POST.get('mothername')
        fathername=request.POST.get('fathername')
        email=request.POST.get('email')
        contact=request.POST.get('contact')
        address=request.POST.get('address')
        childid=request.POST.get('childid')
        image=request.FILES['image']
        
        print(name,childclass,mothername,fathername,contact,address,childid,image)
        children= ChildModels.objects.create(children_name=name,children_class=childclass,children_rollnum=childid,children_mothername=mothername,children_fathername=fathername,children_email=email,children_contact=contact,children_address=address,children_image=image)
        print('created')
        messages.info(request,'Student Details Added Successfully.')
        string = '0123456789'
        OTP = ""
        length = len(string)

        for i in range(6) :
            OTP += string[math.floor(random.random() * length)]
        print(OTP)

        # url = "https://www.fast2sms.com/dev/bulkV2"
        # message = ' Dear {}. Welcome to Reveal. Here is your One Time Validation {}.'.format(name,OTP)
        # numbers = contact
        # payload = f'sender_id=FTWSMS&message={message}&language=english&route=v3&numbers={numbers}'
        # headers = {
        #         'authorization': "BHDFHdnBtRXSrBTvu6hYEHPoocj3TwmCk7hQlL1Y31AnHYwE78DWDpbtbV07",
        #         'Content-Type': "application/json",
        #         'Cache-Control': "no-cache",
        #         }
        # response = requests.request("POST", url, data=payload, headers=headers)
        # print(response.text,'heloooooo')
         
        # # password=ChildModels.objects.get(children_rollnum=childid)
        # children.children_password=OTP
        # # password.save(update_fields=['children_password'])
        # children.save()
        
        # url = "https://www.fast2sms.com/dev/bulkV2"
        #         # create a dictionary
        # my_data = {'sender_id': 'FSTSMS', 
        #                         'message': 'Dear '+str(children.children_name)+', Your OTP for Login is '+  OTP, 
        #                         'language': 'english', 
        #                         'route': 'q', 
        #                         'numbers':children.children_contact,
        #         }
                    
        #             # create a dictionary
        # headers = {
        #                 'authorization': "BHDFHdnBtRXSrBTvu6hYEHPoocj3TwmCk7hQlL1Y31AnHYwE78DWDpbtbV07",
        #                 'Content-Type': "application/x-www-form-urlencoded",
        #                 'Cache-Control': "no-cache"
        #         }
        #             # make a post request
        # response = requests.request("POST",
        #                                         url,
        #                                         data = my_data,
        #                                         headers = headers)
        # print(response)
        
        password=ChildModels.objects.get(children_rollnum=childid)
        children.children_password=OTP
        password.save(update_fields=['children_password'])
        children.save()
       
        qrcode_img=qrcode.make(children.c_id)
        randnumber = random.randint(0,9999)
        canvas=Image.new("RGB", (300,300),"white")
        draw=ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        buffer=BytesIO()
        canvas.save(buffer,"PNG")
        children.children_qrcode = f'student_{children.children_rollnum}.png'
        children.children_qrcode.save(f'student_{children.children_rollnum}.png',File(buffer),save=False)
        children.save()
        canvas.close()
        return redirect('admin_managestudent')
    
    return render(request,'admin/admin-addnewstudent.html')

def admin_busdelay(request):
    if request.method=='POST':
      message=request.POST.get('message')
      delay= DelayModel.objects.create(delay_status=message)
      print(message)

    return render(request,'admin/admin-busdelay.html')


def  admin_managestudent(request):
    
    children=ChildModels.objects.all().order_by('-c_id')
    return render(request,'admin/admin-manage-student.html',{'items':children})

def admin_feedbackanalysis(request):
    data=UserFeedbackModel.objects.all().order_by('-feedback_id')

    return render(request,'admin/admin-feedback-analysis.html',{'data':data})

def admin_sentimentanalysis(request):
    verypositive=UserFeedbackModel.objects.filter(sentiment='Very Positive').count()
    positive=UserFeedbackModel.objects.filter(sentiment='Positive').count()
    verynegative=UserFeedbackModel.objects.filter(sentiment='Very Negative').count()
    negative=UserFeedbackModel.objects.filter(sentiment='Negative').count()
    neutral=UserFeedbackModel.objects.filter(sentiment='Neutral').count()

    return render(request,'admin/admin-sentimentanalysis.html',{'i':verypositive,'j':positive,'k':verynegative,'l':negative,'m':neutral})



# Create your views here.
# def admin_home(request):
#    if request.method=="POST":
#       Url=request.POST['url']
#       QrCode.objects.create(url=Url)

#    qr_code=QrCode.objects.all()
#    return render(request,"admin/admin-home.html",{'qr_code':qr_code})
# def admin_home(request):
#     context = {}
#     if request.method == "POST":
#         factory = qrcode.image.svg.SvgImage
#         img = qrcode.make(request.POST.get("qr_text",""), image_factory=factory, box_size=20)
#         stream = BytesIO()
#         img.save(stream)
#         context["svg"] = stream.getvalue().decode()

#     return render(request, "admin/admin-home.html", context=context)