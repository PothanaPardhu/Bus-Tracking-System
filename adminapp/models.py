from django.db import models
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files import File
import qrcode
import random
import os

# Create your models here.
class ChildModels(models.Model):
    c_id=models.AutoField(primary_key=True)
    children_rollnum=models.CharField(help_text='children_rollnum',max_length=50,null=True)
    children_name=models.CharField(help_text='collector_name',max_length=50)
    children_mothername=models.CharField(help_text='children_mothername',max_length=50)
    children_fathername=models.CharField(help_text='collector_fathername',max_length=50)
    children_contact=models.CharField(help_text='children_contact',max_length=50,null=True)
    children_email=models.EmailField(help_text='children_email')
    children_password=models.CharField(help_text='children_password',max_length=50,null=True)
    children_address=models.TextField(help_text='children_address')
    children_class=models.CharField(help_text='children_class',max_length=50)
    children_image=models.ImageField(help_text='children_image',null=True,upload_to='media/')
    children_status1=models.CharField(help_text='children_status',default='pending',max_length=50)
    children_status2=models.CharField(help_text='children_status',default='pending',max_length=50)
    children_qrcode=models.ImageField(blank=True,upload_to='media/',null=True)
  

    class Meta:
        db_table='childrens_data'


class DelayModel(models.Model):
    delay_status=models.TextField(help_text='delay_status')


    class Meta:
        db_table='bus_delay_details'

 
            