from django.db import models

# Create your models here.

class Assignment(models.Model):
    TREATMENTS = (
        ('con', 'control'),
        ('bla', 'blacklist'),
        ('big', 'big')
    )
    SCENARIOS = (
        ('bank', 'bank'),
        ('shop', 'blacklist')
    )
    startcode = models.CharField(max_length=8,primary_key=True)
    treatment = models.CharField(max_length=3,choices=TREATMENTS,blank=True,null=True)
    scenario = models.CharField(max_length=4,choices=SCENARIOS,blank=True,null=True)
    completed = models.BooleanField(default=False)

class Blocked_Treatments(models.Model):
    TREATMENTS = (
        ('con', 'control'),
        ('bla', 'blacklist'),
        ('big', 'big')
    )
    name = models.CharField(max_length=3,choices=TREATMENTS,blank=True,null=True)
    blocked = models.BooleanField(default=False)

class Blocked_Scenarios(models.Model):
    SCENARIOS = (
        ('bank', 'bank'),
        ('shop', 'blacklist')
    )
    name = models.CharField(max_length=4,choices=SCENARIOS,blank=True,null=True)
    blocked = models.BooleanField(default=False)

#This model is to represent the participant
class Participant(models.Model):
    startcode = models.CharField(max_length=8,primary_key=True,default=None) #this will be our unique identifier
    fincode = models.CharField(max_length=12,blank=True,unique=True,null=True,default=None) #this will be assigned at the end of the survey
    assignmentId=models.CharField(max_length=256,default="ASSIGNMENT_ID_NOT_AVAILABLE") #assignmentID
    hitId=models.CharField(max_length=128,default=None) # the hit this was accepted
    workerId=models.CharField(max_length=128,default=None) #the worker who accepted
    turkSubmitTo=models.CharField(max_length=256,default=None) #where we submit to at the end
    submitted=models.BooleanField(default=False) #finished and submitted
    progress=models.IntegerField(default=0) #at beginning
    treatment=models.IntegerField(default=0) 
    scenario=models.IntegerField(default=0) 
    entry=models.IntegerField(default=0) #entry counter
    recall=models.IntegerField(default=0) #recall counter
    start_time=models.DateTimeField(default=None,null=True,blank=True)
    end_time=models.DateTimeField(default=None,null=True,blank=True)
    useragent = models.TextField(default="",blank=True)
    otherExempt= models.BooleanField(default=False)

#This model is for tracking the results
class Results(models.Model):
    startcode = models.CharField(max_length=8,primary_key=True)
    optout = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)

    demo_age= models.CharField(max_length=10,default="")
    demo_gender= models.CharField(max_length=1,default="")
    demo_handed= models.CharField(max_length=1,default="")
    demo_locale= models.CharField(max_length=1,default="")
    demo_edu = models.CharField(max_length=16,default="")
    demo_tech= models.CharField(max_length=16,default="")
    demo_attention = models.CharField(max_length=16,default="")

    device_num = models.CharField(max_length=1,default="")
    device_brand = models.CharField(max_length=512,default="")
    device_no = models.CharField(max_length=1,default="")
    #device_usage = models.CharField(max_length=512,default="")
    device_curlock = models.CharField(max_length=512,default="")

    #store the practice code, in case it is interesting
    pract_code = models.CharField(max_length=128,default="")
    pract_time = models.CharField(max_length=128,default="")
    pract_taps = models.CharField(max_length=128,default="")

    entry_0_code = models.TextField(max_length=128,default="")
    entry_0_time = models.TextField(max_length=128,default="")
    entry_0_type = models.TextField(max_length=128,default="")
    entry_0_taps = models.TextField(max_length=128,default="")
    entry_0_hitblacklist = models.TextField(max_length=128,default="")

    confirm_0_code = models.TextField(max_length=128,default="")
    confirm_0_time = models.TextField(max_length=128,default="")
    confirm_0_type = models.TextField(max_length=128,default="")
    confirm_0_taps = models.TextField(max_length=128,default="")

    post_0_secure =  models.CharField(max_length=16,default="")
    post_0_difficult =  models.CharField(max_length=16,default="")
    post_0_strat_secure = models.CharField(max_length=512,default="")
    post_0_strat_remember = models.CharField(max_length=512,default="")

    # post_0_strat_secure =  models.CharField(max_length=512,default="")
    # post_0_strat_remember =  models.CharField(max_length=512,default="")

    entry_1_code = models.TextField(max_length=128,default="")
    entry_1_time = models.TextField(max_length=128,default="")
    entry_1_type = models.TextField(max_length=128,default="")
    entry_1_taps = models.TextField(max_length=128,default="")

    confirm_1_code = models.TextField(max_length=128,default="")
    confirm_1_time = models.TextField(max_length=128,default="")
    confirm_1_type = models.TextField(max_length=128,default="")
    confirm_1_taps = models.TextField(max_length=128,default="")

    post_1_secure =  models.CharField(max_length=16,default="")
    post_1_difficult =  models.CharField(max_length=16,default="")
    post_1_strat_secure = models.CharField(max_length=512,default="")
    post_1_strat_remember = models.CharField(max_length=512,default="")

    # post_1_strat_secure =  models.CharField(max_length=512,default="")
    # post_1_strat_remember =  models.CharField(max_length=512,default="")

    security_secure = models.CharField(max_length=16,default="")
    security_pin = models.CharField(max_length=16,default="")
    security_password = models.CharField(max_length=16,default="")
    security_pattern = models.CharField(max_length=16,default="")
    security_likes = models.CharField(max_length=512,default="")
    security_dislikes = models.CharField(max_length=512,default="")

    usability_frequency = models.CharField(max_length=16,default="")
    usability_complx = models.CharField(max_length=16,default="")
    usability_easyuse = models.CharField(max_length=16,default="")
    usability_techsupport = models.CharField(max_length=16,default="")
    usability_integration = models.CharField(max_length=16,default="")
    usability_insonsistent = models.CharField(max_length=16,default="")
    usability_learn = models.CharField(max_length=16,default="")
    usability_attention = models.CharField(max_length=16,default="")
    usability_cumbersome = models.CharField(max_length=16,default="")
    usability_confident = models.CharField(max_length=16,default="")
    usability_requirements = models.CharField(max_length=16,default="")

    recall_0_attempts =  models.TextField(max_length=1024,default="")
    recall_0_forgot =  models.BooleanField(default=False)
    recall_0_time = models.TextField(max_length=128,default="")
    recall_0_taps = models.TextField(max_length=128,default="")

    recall_1_attempts =  models.TextField(max_length=1024,default="")
    recall_1_forgot =  models.BooleanField(default=False)
    recall_1_time = models.TextField(max_length=128,default="")
    recall_1_taps = models.TextField(max_length=128,default="")


    honest=models.BooleanField(default=False)
    #add more fields as we add more questions
