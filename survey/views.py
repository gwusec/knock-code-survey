from django.shortcuts import render as render

# Create your views here.

from django.http import HttpResponse,Http404, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
#from django.contrib.staticfiles.templatetags.staticfiles import static
from django.templatetags.static import static

from django.conf import settings

from django import forms

import random
import urllib.parse
import datetime
import base64
import json
from ast import literal_eval

from .models import Participant, Results, Assignment, Blocked_Treatments, Blocked_Scenarios
from .forms import DemographicForm, FinalForm, DeviceForm, ScenarioForm, PostEntryForm, SecurityForm, UsabilityForm
from survey.apps import blacklist_from_file

#-------------------------------------------------------------------------------
#generate a start or fin code
def gencode(length=8):
    alpha='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    num='0123456789'

    code = []
    for i in range(int(length*3/4+0.5)):
        code.append(alpha[random.randrange(0,len(alpha))])
    for i in range(int(length*1/4)):
        code.append(num[random.randrange(0,len(num))])

    return "".join(code)


def uniquecode(code_l,obj,key):
    while(True):
        code = gencode(code_l)
        try:
            obj.get(**{key:code})
        except Participant.DoesNotExist:
            return code


# This is a shortcut to starting the survey without a passcode and will redirect
# to mturk with the right settings. Most be a settings=rootaccess allowed

def root(request):
    #redirect to main page if no start
    if not settings.ALLOW_ROOT_MTURK_START: return redirect("mturk")
        
    if request.method == "GET":
        #otherwise generate a URL that makes sense for starting
        param = {}
        param["assignmentId"] = uniquecode(10, Participant.objects, "assignmentId")
        param["workerId"] = uniquecode(10, Participant.objects, "workerId")
        param["turkSubmitTo"] = "autogen"
        param["hitId"] = "autogen"
        
        return render(request, "root.html", param)
    else:
        return redirect("mturk") 


# Helper decorator for index() to do some simple error checks
#   1) checks for startcode, and redirects to index if not in the session
#   2) retrieve the participant and result info from the DB, returns Error if not present
#   3) calls the function with additional arguments, func(request,startocode,participant,result)
def add_session_info(func):

    #this function get's called instaead of the one being decorated
    def setup(*args,**kwargs):
        request = args[0] #first argument is the request

        #look up the startcode in the sesion
        startcode = request.session.get('startcode', None)

        #check if mobile --- redirect to no-mobile page
        if not request.user_agent.is_mobile:
            return mobile(request, startcode=startcode)

        if "ios" in request.user_agent.os.family.lower():
            return render(request, "ios_error.html")


        if startcode == None:
            #no startcode, redirect to login view
            return login(request)

        try:
            #get relevant DB information
            participant = Participant.objects.get(startcode=startcode)
            result = Results.objects.get(startcode=startcode)

            #append all relevant arguments, and make the function call
            return func(request,startcode,participant,result)

        except (Participant.DoesNotExist, Results.DoesNotExist) as e:
            # invlaid startcode ... shouldn't really be able to get here
            return HttpResponseServerError("Invalid session info (startcode={}), try clearing your site cookies".format(startcode))
    return setup


#---------------------------------------------------------------------------------


# In this section are views for each page of the survey. Define the order of
# them in the view_order variable above index()


# View that checks startcode, and will redicect to the next page of survey via index() if valid
def login(request):
    request.session.set_expiry(60*60) #expire sessions in 1 hour

    #render page with the startcode if it's part of the URL query string
    if request.method == "GET":
        return render(request, "login.html",{"startcode":request.GET.get("startcode",None)})

    #check the code and begin the survey, or send them to the right page if they are coming back to the survey
    if request.method == "POST":

        startcode = request.POST.get("startcode",None)
        if startcode:
            startcode = startcode.strip().upper()
            
        try:
            #check that the participant exists for that startcode
            participant = Participant.objects.get(startcode=startcode)
            result = Results.objects.get(startcode=startcode)

            #save startcode in session
            request.session["startcode"] = startcode

            #incorrect opt-out, opt them in
            if result.optout:
                result.optout = False
                result.save()

            #first log in, set progres to 1 and mark start time
            if participant.progress == 0:
                participant.start_time=datetime.datetime.now()
                participant.useragent=request.META['HTTP_USER_AGENT']
                participant.progress +=1
                participant.save()

            #redirct to the right page
            return redirect("index")

        except (Participant.DoesNotExist, Results.DoesNotExist) as e:
            return render(request, "login.html", {"invalid":True})


#view that displays the informed consent page
def informed(request,startcode,participant,result):

    #redner the the page normally
    if request.method == "GET":
        return render(request,  "informed.html",{"invalid":False,
                                                 "progress":int(participant.progress*100/(tot_views-1)),
                                                 "currentPagenumber": int(participant.progress),
                                                 "totalPagenumber": int(tot_views)-1})

    #ccheck result
    if request.method == "POST":
        consent = request.POST.get("consent",None)

        #notify that they have to answer
        if consent == None :
            return render(request, "informed.html",{"invalid":True,
                                                    "progress":int(participant.progress*100/(tot_views-1)),
                                                    "currentPagenumber": int(participant.progress),
                                                    "totalPagenumber": int(tot_views)-1})

        #if no, redirect to optout
        if consent == "no": #does not cosent, opt them out
            return redirect("/optout")
        elif consent == "yes":
            ## consent them and move them along
            result.consent=True
            participant.progress+=1
            result.save()
            participant.save()
            return redirect("index")


#demographic questoin page
def demo(request,startcode,participant,result):

    #render normal page for get with the appropriate Form
    if request.method == "GET":
        form = DemographicForm()
        return render(request,"demo.html",{'form':form,
                                           "total":tot_views,
                                           "progress":int(participant.progress*100/(tot_views-1)),
                                           "currentPagenumber": int(participant.progress),
                                           "totalPagenumber": int(tot_views)-1})

    #posting back, get valid data and save it in results
    if request.method == "POST":
        form = DemographicForm(request.POST)
        if form.is_valid():
            #set the results
            result.demo_age=form.cleaned_data["age"]
            result.demo_gender=form.cleaned_data["gender"]
            result.demo_handed=form.cleaned_data["handed"]
            result.demo_locale=form.cleaned_data["locale"]
            result.demo_edu=form.cleaned_data["education"]
            result.demo_tech=form.cleaned_data["tech"]
            result.demo_attention=form.cleaned_data["attention"]
            result.save()

            #move forward the progress and redirect back to index() to get the next page
            participant.progress+=1
            participant.save()
            return redirect("index")
        else:
            #invalid data, takes them back to the form with appropriate error messaging
            return render(request,"demo.html",{'form':form,
                                               "total":tot_views,
                                               "progress":int(participant.progress*100/(tot_views-1)),
                                               "currentPagenumber": int(participant.progress),
                                               "totalPagenumber": int(tot_views)-1})



#demographic questoin page
def device(request,startcode,participant,result):

    #render normal page for get with the appropriate Form
    if request.method == "GET":
        form = DeviceForm()
        return render(request,"device.html",{'form':form,
                                             "progress":int(participant.progress*100/(tot_views-1)),
                                             "currentPagenumber": int(participant.progress),
                                             "totalPagenumber": int(tot_views)-1})

    #posting back, get valid data and save it in results
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            #set the results
            result.device_num=form.cleaned_data["num"]
            result.device_brand=form.cleaned_data["brand"]
            result.device_no=form.cleaned_data["no"]
            #result.device_usage=form.cleaned_data["usage"]
            result.device_curlock=form.cleaned_data["curlock"]

            result.save()

            #move forward the progress and redirect back to index() to get the next page
            participant.progress+=1
            participant.save()
            return redirect("index")
        else:
            #invalid data, takes them back to the form with appropriate error messaging
            return render(request,"device.html",{'form':form,
                                                 "progress":int(participant.progress*100/(tot_views-1)),
                                                 "currentPagenumber": int(participant.progress),
                                                 "totalPagenumber": int(tot_views)-1})



#provide some training
def training(request,startcode,participant,result):

    #render normal page for get with the appropriate Form
    if request.method == "GET":
        return render(request,"training.html",{"treatment": Assignment.objects.get(startcode=startcode).treatment,
                                               "progress":int(participant.progress*100/(tot_views-1)),
                                               "currentPagenumber": int(participant.progress),
                                               "totalPagenumber": int(tot_views)-1})

    #posting back, get valid data and save it in results
    if request.method == "POST":
        participant.progress+=1
        participant.save()
        return redirect("index")

#allow users to practice
def practice(request,startcode,participant,result):
    #render normal page for get with the appropriate Form
    if request.method == "GET":
        treatment = Assignment.objects.get(startcode=startcode).treatment
        scenario_text = "<u>Practice</u> making a Knock Code. <br>The Knock Code must be at least 6 taps and at least 3 different regions."
        return render(request,"practice.html",{"prefix": "practice_",
                                               "scenario": scenario_text,
                                               "next_text": "Tap Next when done.",
                                               "dynamic_instruction": "true",
                                               "treatment": treatment,
                                               "progress":int(participant.progress*100/(tot_views-1)),
                                               "currentPagenumber": int(participant.progress),
                                               "totalPagenumber": int(tot_views)-1})

    #posting back, get valid data and save it in results
    if request.method == "POST":
        code = request.POST.get('code',None)
        time = request.POST.get('time',None)
        taps = request.POST.get('taps',None)

        if code == None :
            redirect("index") #shouldn't happen, right?

        result.pract_code = code
        result.pract_time = time 
        result.pract_taps = taps
        result.save()

        participant.progress+=1
        participant.save()

        return redirect("index")

#instructions for the scenarios to follow
def scenarios(request,startcode,participant,result):
    #render normal page for get with the appropriate Form
    if request.method == "GET":
        form = ScenarioForm()
        scenario = Assignment.objects.get(startcode=startcode).scenario
        print(scenario)
        return render(request,"scenarios.html",{"scenario":scenario, 
                                                "form":form,
                                                "progress":int(participant.progress*100/(tot_views-1)),
                                                "currentPagenumber": int(participant.progress),
                                                "totalPagenumber": int(tot_views)-1})

    #posting back, get valid data and save it in results
    if request.method == "POST":
        form = ScenarioForm(request.POST)
        if form.is_valid():
            aid = form.cleaned_data["aid"]
            scene = form.cleaned_data["scene"]

            #opt them out if they can't answer yes to these questions
            if aid == "N" or scene == "N":
                return redirect("/optout")

            participant.progress+=1
            participant.save()
            return redirect("index")
        else:
            return render(request,"scenarios.html",{"form":form,
                                                    "progress":int(participant.progress*100/(tot_views-1)),
                                                    "currentPagenumber": int(participant.progress),
                                                    "totalPagenumber": int(tot_views)-1})


def entry(request,startcode,participant,result):
    fmt = "Select a Knock Code <br> for <u>{}</u>"
    scenarios = [(static("/survey/images/unlock.svg"), "Device Unlock"),
                 (static("/survey/images/briefcase.svg"), "Banking App."),
                 (static("/survey/images/shopping-cart.svg"), "Shopping Cart")]

    assignment = Assignment.objects.get(startcode=startcode)
    treatment = assignment.treatment #determine the treatment
    if participant.entry == 0:
        scenario = "unlock"
    else:
        scenario = assignment.scenario

    scenarios = {"unlock": [static("/survey/images/unlock.svg"), "Device Unlock"],
                 "bank": [static("/survey/images/briefcase.svg"), "Banking App."],
                 "shop": [static("/survey/images/shopping-cart.svg"), "Shopping Cart"]}

    if assignment.treatment == "bla":
        blacklist = blacklist_from_file
    else:
        blacklist = []

    if request.method == "GET":
        form = ScenarioForm()
        return render(request,"entry.html",{"blacklist": base64.b64encode(json.dumps(blacklist).encode()).decode("utf-8"),
                                            "dynamic_instruction": "true",
                                            "icon": scenarios[scenario][0],
                                            "next_text": "Tap Next when done.",
                                            "prefix": "entry_{}_".format(participant.entry),
                                            "progress": int(participant.progress*100/(tot_views-1)),
        									"scenario": fmt.format(scenarios[scenario][1]),
                                            "scenario_short": scenarios[scenario][1],
                                            "treatment": assignment.treatment,
                                            "currentPagenumber": int(participant.progress),
                                            "totalPagenumber": int(tot_views)-1})

    if request.method == "POST":
        code = request.POST.get('code',None)
        time = request.POST.get('time',None)
        taps = request.POST.get('taps',None)
        hitblacklist = request.POST.get('hitblacklist',False)

        if code == None :
            redirect("index") #shouldn't happen, right?

        setattr(result,"entry_{}_code".format(participant.entry), code)
        setattr(result,"entry_{}_type".format(participant.entry), scenarios[scenario][1])
        setattr(result,"entry_{}_time".format(participant.entry), time)
        setattr(result,"entry_{}_taps".format(participant.entry), taps)
        setattr(result,"entry_{}_hitblacklist".format(participant.entry), hitblacklist)
        result.save()

        participant.progress+=1
        participant.save()

        return redirect("index")

def confirm(request, startcode, participant, result):
    fmt = "Confirm the Knock Code <br> for <u>{}</u>"
    scenarios = [(static("/survey/images/unlock.svg"), "Device Unlock"),
                 (static("/survey/images/briefcase.svg"), "Banking App."),
                 (static("/survey/images/shopping-cart.svg"), "Shopping Cart")]

    assignment = Assignment.objects.get(startcode=startcode)
    treatment = assignment.treatment #determine the treatment
    if participant.entry == 0:
        scenario = "unlock"
    else:
        scenario = assignment.scenario

    scenarios = {"unlock": [static("/survey/images/unlock.svg"), "Device Unlock"],
                 "bank": [static("/survey/images/briefcase.svg"), "Banking App."],
                 "shop": [static("/survey/images/shopping-cart.svg"), "Shopping Cart"]}

    if request.method == "GET":
        return render(request,"confirm.html",{"dynamic_instruction": "false",
                                              "icon": scenarios[scenario][0],
                                              "knockcode": literal_eval(getattr(result,"entry_{}_code".format(participant.entry)))[-1],
                                              "next_text": "Tap Confirm when done.",
                                              "prefix": "confirm_{}_".format(participant.entry),
                                              "progress": int(participant.progress*100/(tot_views-1)),
                                              "scenario": fmt.format(scenarios[scenario][1]),
                                              "scenario_short": scenarios[scenario][1],
                                              "treatment": assignment.treatment,
                                              "currentPagenumber": int(participant.progress),
                                              "totalPagenumber": int(tot_views)-1})

    if request.method == "POST":
        code = request.POST.get('code',None)
        confirmed = request.POST.get('confirmed',None)
        time = request.POST.get('time',None)
        taps = request.POST.get('taps',None)

        if code == None :
            redirect("index") #shouldn't happen, right?

        setattr(result,"confirm_{}_code".format(participant.entry), code)
        setattr(result,"confirm_{}_type".format(participant.entry), scenarios[scenario][1])
        setattr(result,"confirm_{}_time".format(participant.entry), time)
        setattr(result,"confirm_{}_taps".format(participant.entry), taps)
        result.save()
        if confirmed == "1":
            participant.progress += 1
        elif confirmed == "0":
            participant.progress -= 1
        participant.save()

        return redirect("index")



def post(request,startcode,participant,result):

    #render normal page for get with the appropriate Form
    if request.method == "GET":
        form = PostEntryForm()
        return render(request,"post.html",{"form":form,
                                           "progress":int(participant.progress*100/(tot_views-1)),
                                           "currentPagenumber": int(participant.progress),
                                           "totalPagenumber": int(tot_views)-1})

    #posting back, get valid data and save it in results
    if request.method == "POST":
        form = PostEntryForm(request.POST)
        if form.is_valid():
            #set the results
            setattr(result,"post_{}_secure".format(participant.entry),form.cleaned_data["security"])
            setattr(result,"post_{}_difficult".format(participant.entry),form.cleaned_data["difficulty"])
            setattr(result,"post_{}_strat_secure".format(participant.entry),form.cleaned_data["strat_secure"])
            setattr(result,"post_{}_strat_remember".format(participant.entry),form.cleaned_data["strat_remember"])
            result.save()

            participant.entry += 1 #also increment entry number for next entry

            #move forward the progress and redirect back to index() to get the next page

            participant.progress+=1
            participant.save()
            return redirect("index")
        else:
            #invalid data, takes them back to the form with appropriate error messaging
            return render(request,"post.html",{"form":form,
                                               "progress":int(participant.progress*100/(tot_views-1)),
                                               "currentPagenumber": int(participant.progress),
                                               "totalPagenumber": int(tot_views)-1})

def security(request,startcode,participant,result):
    #render normal page for get with the appropriate Form
    if request.method == "GET":
        form = SecurityForm()
        return render(request,"secure.html",{"form":form,
                                             "progress":int(participant.progress*100/(tot_views-1)),
                                             "currentPagenumber": int(participant.progress),
                                             "totalPagenumber": int(tot_views)-1})

    if request.method == "POST":
        form = SecurityForm(request.POST)
        if form.is_valid():
            #set the results
            result.security_secure = form.cleaned_data["secure"]
            result.security_pin = form.cleaned_data["pin"]
            result.security_password = form.cleaned_data["password"]
            result.security_pattern = form.cleaned_data["pattern"]
            result.security_likes = form.cleaned_data["likes"]
            result.security_dislikes = form.cleaned_data["dislikes"]
            result.save()

            #move forward the progress and redirect back to index() to get the next page

            participant.progress+=1
            participant.save()
            return redirect("index")
        else:
            #invalid data, takes them back to the form with appropriate error messaging
            return render(request,"secure.html",{"form":form,
                                                 "progress":int(participant.progress*100/(tot_views-1)),
                                                 "currentPagenumber": int(participant.progress),
                                                 "totalPagenumber": int(tot_views)-1})


def usability(request,startcode,participant,result):
    #render normal page for get with the appropriate Form
    if request.method == "GET":
        form = UsabilityForm()
        return render(request,"usable.html",{'form':form,
                                             "progress":int(participant.progress*100/(tot_views-1)),
                                             "currentPagenumber": int(participant.progress),
                                             "totalPagenumber": int(tot_views)-1})

    if request.method == "POST":
        form = UsabilityForm(request.POST)
        if form.is_valid():
            #set the results
            result.usability_frequency = form.cleaned_data["frequency"]
            result.usability_complx = form.cleaned_data["complx"]
            result.usability_easyuse = form.cleaned_data["easyuse"]
            result.usability_techsupport = form.cleaned_data["techsupport"]
            result.usability_integration = form.cleaned_data["integration"]
            result.usability_insonsistent = form.cleaned_data["inconsistent"]
            result.usability_learn = form.cleaned_data["learn"]
            result.usability_attention = form.cleaned_data["attention"]
            result.usability_cumbersome = form.cleaned_data["cumbersome"]
            result.usability_confident = form.cleaned_data["confident"]
            result.usability_requirements = form.cleaned_data["requirements"]

            result.save()

            #move forward the progress and redirect back to index() to get the next page

            participant.progress+=1
            participant.save()
            return redirect("index")
        else:
            #invalid data, takes them back to the form with appropriate error messaging
            return render(request,"usable.html",{"form":form,
                                                 "progress":int(participant.progress*100/(tot_views-1)),
                                                 "currentPagenumber": int(participant.progress),
                                                 "totalPagenumber": int(tot_views)-1})

def recall(request,startcode,participant,result):
    fmt = "Recall your Knock Code <br> for <u>{}</u>"

    assignment = Assignment.objects.get(startcode=startcode)
    treatment = assignment.treatment #determine the treatment
    if participant.recall == 0:
        scenario = "unlock"
    else:
        scenario = assignment.scenario

    scenarios = {"unlock": [static("/survey/images/unlock.svg"), "Device Unlock"],
                 "bank": [static("/survey/images/briefcase.svg"), "Banking App."],
                 "shop": [static("/survey/images/shopping-cart.svg"), "Shopping Cart"]}

    if request.method == "GET":
        return render(request,"recall.html",{"dynamic_instruction": "false",
                                             "icon": scenarios[scenario][0],
                                             "knockcode":literal_eval(getattr(result,"entry_{}_code".format(participant.recall)))[-1],
                                             "next_text": "Tap OK when done.",
                                             "prefix": "recall_{}_".format(participant.recall),
                                             "progress":int(participant.progress*100/(tot_views-1)),
                                             "scenario":fmt.format(scenarios[scenario][1]),
                                             "scenario_short":scenarios[scenario][1],
                                             "treatment": assignment.treatment,
                                             "currentPagenumber": int(participant.progress),
                                             "totalPagenumber": int(tot_views)-1})

    if request.method == "POST":
        attempts = request.POST.get('attempts',None)
        forgot = request.POST.get('forgot',None)
        time = request.POST.get('time',None)
        taps = request.POST.get('taps',None)

        print(attempts)
        if attempts == None or forgot == None:
            redirect("index") #shouldn't happen, right?

        setattr(result,"recall_{}_attempts".format(participant.recall), attempts)
        setattr(result,"recall_{}_time".format(participant.recall), time)
        setattr(result,"recall_{}_forgot".format(participant.recall), forgot)
        setattr(result,"recall_{}_taps".format(participant.recall), taps)
        result.save()

        participant.recall+=1
        participant.progress+=1
        participant.save()

        return redirect("index")


#view that displays the final submit page, and honesty question
def submit(request,startcode,participant,result):

    #render the the page normalling with appropriate form
    if request.method == "GET":
        form = FinalForm()
        return render(request,"submit.html",{'form':form,
                                             "progress":int(participant.progress*100/(tot_views-1)),
                                             "currentPagenumber": int(participant.progress),
                                             "totalPagenumber": int(tot_views)-1})

    #posting back, get valid results and save it
    if request.method == "POST":
        form = FinalForm(request.POST)
        if form.is_valid():
            #set the results
            result.honest = True if "Y" == form.cleaned_data["honest"] else False
            result.save()

            #move the progress forward and redirect back to index
            participant.progress+=1
            participant.save()

            return redirect("index")
        else:
            return render(request,"submit.html",{'form':form,
                                                 "progress":int(participant.progress*100/(tot_views-1)),
                                                 "currentPagenumber": int(participant.progress),
                                                 "totalPagenumber": int(tot_views)-1})

#view for the final page, generate a fincode and direct users back to mturk
def finish(request,startcode,participant,result):
    if not participant.fincode:
        assignment = Assignment.objects.get(startcode=startcode)
        assignment.completed = True
        assignment.save(update_fields=['completed'])
        participant.end_time=datetime.datetime.now()
        participant.fincode = gencode(8) #finish code
        participant.save()
    return render(request, "finish.html", {"fincode":participant.fincode,
                                           "progress":participant.progress,
                                           "total":tot_views,
                                           "progress":int(participant.progress*100/(tot_views-1)),
                                           "currentPagenumber": int(participant.progress),
                                           "totalPagenumber": int(tot_views)-1})




#---------------------------------------------------------------------------------------

# view() Defines the order of the views that are called by the index() view. It is
# tracked by the participant.progress field.
#
# Progress ordering is based at 1 indexing, thus the None value. If progress is
# ever 0, redirect occurs ot login() by default, and is handled by the decorator

view_order=[None,informed,device,training,practice,scenarios,entry,confirm,post,entry,confirm,post,security,usability,recall,recall,demo,submit,finish]


tot_views=len(view_order)

# index() is the primary entry point to the survey. The decorator will handle
# common errors, redirect to login() or HTTP errors if needed. Otherwise, the
# decorator fills in the startcode, particiapnt, and result arguments, and
# returns the result of the appropriate view.

@add_session_info
def index(request,startcode,participant,result):
    #check the current progress counter and return the rendering for the right view
    if participant.progress < len(view_order):
        return view_order[participant.progress](request,startcode,participant,result)
    else:
        #out of bounds ... some sort of error, clear session and put them at the beginning
        request.session.flush()
        redirect("index")


# optout view will either redirect users back to login, if they reached this by
# accident and were not previously logged on (via the decorator), otherwise, it
# will set the optout flag, and give the option for users to change their mind
# by relogging in.

@add_session_info
def optout(request,startcode,participant,result):
    result.optout=True
    result.save()

    request.session.flush()
    return render(request, "optout.html")


# Displayed when a user requests a page using a mobile device 
def mobile(request, **kwargs):
    # render page with the startcode if it's part of the URL query string
    startcode = kwargs.get('startcode', None)
    current_site = str(get_current_site(request))
    url_without_startcode = "https://" + current_site
    if startcode:
        url_with_startcode = "https://" + current_site + "/?startcode=" + startcode
    else:
        startcode = request.GET.get("startcode", None)
        if startcode:
            url_with_startcode = "https://" + current_site + "/?startcode=" + startcode
        else:
            url_with_startcode = "https://" + current_site + "/"
    return render(request, "mobile_error.html", {"urlWithStartcode": url_with_startcode,
                                                 "urlWithoutStartcode": url_without_startcode,
                                                 "startcode":startcode})


# This is the view that manages the mturk display. The decorator ensures that it
# can be loaded within a frame, as needed by MTurk. It can do multiple things,
# depending on the method:
#
#  1) GET: it will display a sample of the page, and if the correct query
#     strings are provided following a HIT acceptance, then it creates a record
#     for that worker and hit and displays a start code.
#
#  2) POST: The partciiapnt finished the survey and has a fincode and clicked
#     the submit button. This will check the code, report an error if there is
#     one, or setup a final submission via the apporpirate external submit URL
#     for MTurk into a hidden form via the mturk_submit.html template. That
#     template has javascript to activate the submission.

#enable this page to load in a FRAME!
@csrf_exempt
@xframe_options_exempt
def mturk(request):
    current_site = str(get_current_site(request))
    qr_code_url = "https://" + current_site

    if request.method == "POST":
        #submitting the data

        #get all relevant posted data
        assignmentId=request.POST.get("assignmentId",None)
        hitId=request.POST.get("hitId",None)
        workerId=request.POST.get("workerId",None)
        turkSubmitTo=request.POST.get("turkSubmitTo",None)
        startcode=request.POST.get("startcode",None)
        fincode=request.POST.get("fincode",None)

        if startcode:
            qr_code_url = "https://" + current_site + "/?startcode=" + startcode

        #manage the template rendering
        render_dict = {
                       'startcode':startcode,
                       'fincode':fincode,
                       "assignmentId":assignmentId,
                       "hitId":hitId,
                       "workerId":workerId,
                       "turkSubmitTo":turkSubmitTo,
                       "qrCodeUrl":qr_code_url}


        # none of these should be None/False
        if  not all((assignmentId,hitId,workerId,turkSubmitTo,startcode,fincode)):
            render_dict["error"] = "None Values"
            return render(request,"error.html",render_dict)

        try:
            #update the record for the participant
            participant = Participant.objects.get(workerId=workerId)

            #notify if theere is an error
            if startcode != participant.startcode or fincode != participant.fincode:
                render_dict["error"] = "Invalid startcode or fincode"
                return render(request,"error.html",render_dict)

            #note that they submitted
            participant.submitted = True
            participant.save()

            #generate apporpriate submission url
            url_vals = list(urllib.parse.urlparse(turkSubmitTo))
            url_vals[2] = "/mturk/externalSubmit"
            url_vals[4] = urllib.parse.urlencode({"assignmentId":assignmentId,
                                                  "startcode":startcode,
                                                  "fincode":fincode,
                                                  "qrCodeUrl":qr_code_url})
            url = urllib.parse.urlunparse(url_vals)

            #render the final form for submission (occurs via JS in that page)
            return render(request, "mturk_submit.html",{"action":url,
                                                        "assignmentId":assignmentId,
                                                        "startcode":startcode,
                                                        "fincode":fincode,
                                                        "qrCodeUrl":qr_code_url})
        except Participant.DoesNotExist:
            render_dict["error"] = "Participant Failure"
            return render(request,"error.html",render_dict)

    if request.method == "GET":

        #These URL query strings are set by MTurk
        assignmentId=request.GET.get("assignmentId",None)
        hitId=request.GET.get("hitId",None)
        workerId=request.GET.get("workerId",None)
        turkSubmitTo=request.GET.get("turkSubmitTo",None)

        #dictionary to drive the template
        render_dict = {'accepted':False,
                       'submitted':False,
                       'startcode':None,
                       'fincode':None,
                       "assignmentId":assignmentId,
                       "hitId":hitId,
                       "workerId":workerId,
                       "turkSubmitTo":turkSubmitTo,
                       "qrCodeUrl":qr_code_url}


        #Check to see if HIT is accepted
        if assignmentId == "ASSIGNMENT_ID_NOT_AVAILABLE" or assignmentId == None:
            return render(request, "mturk.html", render_dict)
        else:
            try:
                participant = Participant.objects.get(workerId=workerId)
            except Participant.DoesNotExist:
                #New participant

                #generate a startcode
                while(True):
                    startcode=gencode()
                    try:
                        participant = Participant.objects.get(startcode=startcode)
                    except Participant.DoesNotExist:
                        break #it's unique

                # assign participant to treatment and scenario
                treatment = assign_treatment()
                scenario = assign_scenario()
                qr_code_url = "https://" + current_site + "/?startcode=" + startcode

                assignment = Assignment.objects.create(
                    startcode = startcode,
                    treatment = treatment,
                    scenario = scenario)
                assignment.save()

                #create an object
                participant = Participant.objects.create(startcode=startcode,
                                                         fincode=None,
                                                         hitId=hitId,
                                                         assignmentId=assignmentId,
                                                         workerId=workerId,
                                                         turkSubmitTo=turkSubmitTo,
                                                         submitted=False,
                                                         progress=0,
                                                         entry=0,
                                                         recall=0,
                                                         start_time=None,
                                                         end_time=None,
                )
                participant.save()

                #create a result object!
                result = Results.objects.create(startcode=startcode)
                result.save()

            #render the page with info
            render_dict['accepted'] = True
            render_dict["fincode"] = participant.fincode if participant.fincode else ""
            render_dict["startcode"] = participant.startcode
            render_dict["submitted"] = participant.submitted
            render_dict["qrCodeUrl"] = qr_code_url
            if participant.hitId != hitId: 
                render_dict["otherHit"] = True
                render_dict["otherExempt"] = participant.otherExempt

            return render(request, "mturk.html", render_dict)

def assign_treatment():
    treatment_counts = {"con": 0, "bla": 0, "big": 0}
    blocked_treatments = Blocked_Treatments.objects.all()

    for treatment in blocked_treatments:
        if treatment.blocked == True:
            treatment_counts.pop(treatment.name)

    for treatment in treatment_counts:
        treatment_counts[treatment] = Assignment.objects.filter(treatment = treatment, completed = True).count()

    treatment_with_minimal_value = min(treatment_counts, key=treatment_counts.get)
    possible_treatments = [treatment_with_minimal_value]
    for treatment in treatment_counts:
        if treatment != treatment_with_minimal_value and treatment_counts[treatment] == treatment_counts[treatment_with_minimal_value]:
            possible_treatments.append(treatment)
    random.shuffle(possible_treatments)
    chosen_treatment = possible_treatments[0]
    return chosen_treatment



def assign_scenario():
    scenario_counts = {"bank": 0, "shop": 0}
    blocked_scenarios = Blocked_Scenarios.objects.all()

    for scenario in blocked_scenarios:
        if scenario.blocked == True:
            scenario_counts.pop(scenario.name)

    for scenario in scenario_counts:
        scenario_counts[scenario] = Assignment.objects.filter(scenario = scenario, completed = True).count()

    scenario_with_minimal_value = min(scenario_counts, key=scenario_counts.get)
    possible_scenarios = [scenario_with_minimal_value]
    for scenario in scenario_counts:
        if scenario != scenario_with_minimal_value and scenario_counts[scenario] == scenario_counts[scenario_with_minimal_value]:
            possible_scenarios.append(scenario)
    random.shuffle(possible_scenarios)
    chosen_scenario = possible_scenarios[0]
    return chosen_scenario


@csrf_exempt
def mturk_test(request):
    #test view to do local checking
    print(request.GET)
    print(request.POST)
    return HttpResponse("<html>GET:{}<br><br>POST:{}</html>".format(request.GET,request.POST))
