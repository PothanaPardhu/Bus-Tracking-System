from django.db import models
from adminapp.models import *

# Create your models here.
class UserFeedbackModel(models.Model):
    feedback_id=models.AutoField(primary_key=True)
    userfeedback=models.ForeignKey(ChildModels,models.CASCADE,null=True,related_name='userfeedback')
    rating=models.CharField(help_text='rating3',max_length=200,null=True)
    text=models.CharField(help_text='text',max_length=200,null=True)
    sentiment=models.CharField(help_text='sentiment',max_length=700,null=True)
    class Meta:
        db_table='user_feedback'