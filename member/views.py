from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
# from django.shortcuts import pyrebase
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import forms
from firebase_admin import firestore
from rest_framework import authentication, serializers
from rest_framework.permissions import AllowAny
# from .forms import CreateInDiscussion, PersonForm, UserUpdateForm
from rest_framework.parsers import JSONParser
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from workshop.models import Booking, Workshop
from group.models import Group, GroupMember, GroupSharing
from .models import Person
from member.models import Member
from sharing.models import Feed
from rest_framework.permissions import AllowAny
from member.serializers import MyTokenObtainPairSerializer, UsersSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import requests
#from member.models import Users 
from .serializers import UsersSerializer 
#from rest_framework import viewsets
# def encryptPassword(Pwd):
#         key = Fernet.generate_key()
#         fernet = Fernet(key)
#         encrypted = fernet.encrypt(Pwd.encode())
#         return encrypted

# def deryptPassword(Pwd):
#         key = Fernet.generate_key()
#         fernet = Fernet(key)
#         decrypted = fernet.decrypt(Pwd).decode()
#         return decrypted
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore

# cred = credentials.Certificate('D:\IGROW_V-main\member\serviceAccountKey.json')

# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://i-grow-kmma.firebaseio.com'
# })

def user_list(request):

    if request.method == 'GET':
        person = Person.objects.all()
        serializer = UsersSerializer(person, many=True)
        return JsonResponse(serializers.data, safe=False)

    else:
        request.method == 'POST'
        data = JSONParser().parse(request)
        serializer = UsersSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status = 201)
        return JsonResponse(serializer.errors, status=400)




def Indexpage(request):
    return render(request, 'index.html')

def homepage(request):
    person = Person.objects.filter(Email=request.session['Email'])
    return render(request, 'homepage.html',{'person': person })

def homepageAdmin(request):
    person = Person.objects.filter(Email=request.session['Email'])
    return render(request, 'homepageAdmin.html',{'person': person })


#user registration
def UserReg(request):
    if request.method=='POST':
        Email=request.POST['Email']
        Pwd=request.POST['Pwd']
        Username=request.POST.get('Username')
        Name=request.POST.get('Name')
        DateOfBirth=request.POST.get('DateOfBirth')
        Age=request.POST['Age']
        District=request.POST['District']
        State=request.POST['State']
        Occupation=request.POST['Occupation']
        About=request.POST['About']
        Gen=request.POST.get('Gender')
        MaritalStatus=request.POST.get('MaritalStatus')
        UserLevel = request.POST.get("UserLevel")
        Photo = request.POST.get('Photo')
        #resume = request.POST.get('resume')
        # Person(Email=Email,Password=Pwd,Username=Username,Name=Name,DateOfBirth=DateOfBirth,Age=Age,District=District,State=State,
        #     Occupation=Occupation,About=About,Gender=Gen,MaritalStatus=MaritalStatus,UserLevel=UserLevel,Photo=Photo).save(),

        db = firestore.client()

        db.collection('users').add({'username':Username, 'age':'20'})

        #ranking = request.POST.get('ranking')
        
        #Users(Person, ranking=ranking)
        #Users.upload_photo(Person, photo)
        #Users.upload_file(Person, resume)

        #cuba
        # FarmingPerson(Email=Email,Password=Pwd,Username=Username,Name=Name,DateOfBirth=DateOfBirth,Age=Age,District=District,State=State,
        #     Occupation=Occupation,About=About,Gender=Gen,MaritalStatus=MaritalStatus).save(),
        # FarmingPerson(Email=Email,Password=Pwd,Username=Username,Name=Name,DateOfBirth=DateOfBirth,Age=Age,District=District,State=State,
            # Occupation=Occupation,About=About,Gender=Gen,MaritalStatus=MaritalStatus),
        messages.success(request,'The new user ' + request.POST['Username'] + " is save succesfully..!")
        return render(request,'registration.html')
    else :
        return render(request,'registration.html')



#user login
def loginpage(request):
    if request.method == "POST":
        try:
            #UserLevel = Person.objects.get(Userlevel = request.POST['UserLevel'])
            Userdetails = Person.objects.get(Email = request.POST['Email'], Password = (request.POST['Pwd']))
            UserLevel = (request.POST.get('UserLevel'))
            print("Username", Userdetails)
            request.session['Email'] = Userdetails.Email
            person = Person.objects.filter(Email = request.POST['Email'])
            request.session['UserLevel'] = Userdetails.UserLevel
            if request.session['UserLevel'] == 'user':
            #user = Person.objects.filter(UserLevel = request.Post['UserLevel'])
                return render(request,'homepage.html',{'person' : person})
            else:
                return render(request,'homepageAdmin.html',{'person' : person})
        except Person.DoesNotExist as e:
            messages.success(request,'Username/Password Invalid..!')
    return render(request,'login.html')

#user logout
def logout(request):
    try:
        del request.session['Email']
    except:
        return render(request,'index.html')
    return render(request,'index.html')

#profile
def view(request):
    person = Person.objects.filter(Email=request.session['Email'])
    if request.method=='POST':
       t = Person.objects.get(Email=request.session['Email'])
       t.Password=request.POST['Password']
       t.Username=request.POST.get('Username')
       t.Name=request.POST.get('Name')
       t.DateOfBirth=request.POST.get('DateOfBirth')
       t.Age=request.POST['Age']
       t.District=request.POST['District']
       t.State=request.POST['State']
       t.Occupation=request.POST['Occupation']
       t.About=request.POST['About']
       t.Gen=request.POST.get('Gender')
       t.MaritalStatus=request.POST.get('MaritalStatus')
       t.photo=request.POST.get('photo')
       t.save()

       return render(request,'homepage.html')
    else:
        return render(request, 'profile.html',{'person': person})  

#list of user for admin view
def UserList(request):
    person = Person.objects.all()
    return render(request, 'UserList.html',{'person': person})  

#sharing
def mainSharing(request):
    try:
        feed=Feed.objects.all()
        return render(request,'MainSharing.html',{'feed':feed})
    except Feed.DoesNotExist:
        raise Http404('Data does not exist')

def sharing(request):
    if request.method=='POST':
        Title=request.POST.get('Title')
        Message=request.POST.get('Message')
        Photo=request.POST.get('Photo')
        Video=request.POST.get('Video')
        Graph=request.POST.get('Graph')
        Feed(Title=Title,Message=Message,Photo=Photo,Video=Video,Graph=Graph).save(),
        messages.success(request,'The new feed is save succesfully..!')
        return render(request,'sharing.html')
    else :
        return render(request,'sharing.html')

def viewSharing(request):
    feed = Feed.objects.all()
    return render(request,'ViewSharing.html',{'feed':feed})  

def updateSharing(request):
    feed = Feed.objects.get(Title=request.session['Title'])
    if request.method=='POST':
       f = Feed.objects.get(Title=request.session['Title'])
       f.Title=request.POST['Title']
       f.Message=request.POST.get('Message')
       f.Photo=request.POST.get('Photo')
       f.Video=request.POST.get('Video')
       f.Graph=request.POST['Graph']
       f.save()
       return render(request,'ViewSharing.html',{'feed':feed})
    else:
        return render(request, 'homepage.html', {'feed':feed})

def deleteSharing(request,id):
    sharing = get_object_or_404(sharing, id=id)
    if request.method=='POST':
        sharing.delete()
        return redirect('homepage.html')
    context = {
        "object" : sharing
    }
    return render(request, 'deleteSharing.html', {'object':sharing})

    #feed_id = int(feed_id)
    #try:
    #    feed_sel = Feed.objects.get(id = feed_id)
    #except Feed.DoesNotExist:
    #    return redirect('index')
    #feed_sel.delete()
    #return redirect('index')





#group
def mainGroup(request):
    try:
        group=Group.objects.all()
        person = Person.objects.all()
        #Gsharing = GroupSharing.objects.all()
        sharing = Feed.objects.all()
        return render(request,'MainGroup.html',{'group':group, 'person':person, 'sharing':sharing})
    except Group.DoesNotExist:
        raise Http404('Data does not exist')

def GroupAdmin(request):
    try:
        group=Group.objects.all()
        return render(request,'CreategroupAdmin.html',{'group':group})
    except Group.DoesNotExist:
        raise Http404('Data does not exist')

def group(request):
    #person_fk = Person.objects.filter()
    if request.method=='POST':
        GName=request.POST.get('GName')
        GAbout=request.POST.get('GAbout')
        GMedia=request.POST.get('GMedia')
        Group(GName=GName,GAbout=GAbout,GMedia=GMedia).save(),
        messages.success(request,'The new group ' + request.POST['GName'] + " is create succesfully..!")
        return render(request,'group.html',)

    else :
        return render(request,'group.html')

def myGroup(request):
    try:
        group = Group.objects.all()
        Gmember = GroupMember.objects.all()
        return render(request,'MyGroup.html',{'group':group, 'Gmember':Gmember})
    except Group.DoesNotExist:
       raise Http404('Data does not exist')

def updateGroup(request, fk1, fk):
    #group = Group.objects.filter(Name=request.session['GName'])
    p = Person.objects.filter(Email=request.session['Email'])
    group = Group.objects.get(pk=fk1)
    person = Person.objects.filter(Email=request.session['Email'])
    gmember = GroupMember.objects.all()
    if request.method=='POST':
        t = Group.objects.get(pk=fk1)
        f = Person.objects.get(pk=fk)
        #GUsername = request.POST.get('Username')
        GroupMember(Username=f.Username, Group_fk=t, Person_fk=f).save(),
        #messages.success(request,"Your username is successfully added")
        return render(request,'EditGroup.html', {'group':group, 'person':person, 'gmember':gmember})

    else:
        return render(request, 'EditGroup.html', {'group':group, 'person':person})

def GSharing(request, fk1,fk3):
    group = Group.objects.get(pk=fk3)
    person = Person.objects.filter(Email=request.session['Email'])
    g = Group.objects.get(pk=fk3)
    p = Person.objects.get(pk=fk1)
    if request.method=='POST':
        GTitle=request.POST.get('GTitle')
        GMessage=request.POST.get('GMessage')
        GPhoto=request.POST.get('GPhoto')
        GVideo=request.POST.get('GVideo')
        GGraph=request.POST.get('GGraph')
        GroupSharing(GTitle=GTitle,GMessage=GMessage,GPhoto=GPhoto,GVideo=GVideo,GGraph=GGraph,Person_fk=p,Group_fk=g).save(),
        #messages.success(request,'The new feed' + request.POST['GTitle'] + "is save succesfully..!")
        return render(request,'GSharing.html')
    else :
        return render(request,'GSharing.html')

def AddGroupSharing(request):
    try:
        group=Group.objects.all()
        person = Person.objects.filter(Email=request.session['Email'])
        #Gsharing = GroupSharing.objects.all()
        sharing = Feed.objects.all()
        return render(request,'AddGroupSharing.html',{'group':group, 'person':person, 'sharing':sharing})
    except Group.DoesNotExist:
        raise Http404('Data does not exist')

def ViewGroupSharing(request):
    person = Person.objects.filter(Email=request.session['Email'])
    feed = GroupSharing.objects.all()
    return render(request,'ViewGroupSharing.html',{'feed':feed, 'person':person})  







#member
def mainMember(request):
    try:
        member = Member.objects.all()
        return render(request,'MainMember.html',{'member':member})
    except Member.DoesNotExist:
        raise Http404('Data does not exist')

def member(request):
    if request.method=='POST':
        Name=request.POST.get('Name')
        Study=request.POST.get('Study')
        Lives=request.POST.get('Lives')
        Member(Name=Name,Study=Study,Lives=Lives).save(),
        messages.success(request,'The new member ' + request.POST['Name'] + " is create succesfully..!")
        return render(request,'member.html')
    else :
        return render(request,'member.html')
def friendlist(request):
    #try:
    #    member=Member.objects.filter(Name=request.session['Name'])
        return render(request,'friendlist.html')#{'member':member})
    #except Member.DoesNotExist:
     #   raise Http404('Data does not exist')


def myMember(request):
    #try:
    #    member=Member.objects.filter(Name=request.session['Name'])
        return render(request,'MyMember.html')#{'member':member})
    #except Member.DoesNotExist:
     #   raise Http404('Data does not exist')

def MainSearchbar(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        Name = Person.objects.all().filter(Name=search)
        return render(request, 'MainSearchbar.html', {'Name': Name})




#discussion
def viewdiscussion(request):
    if request.method=='POST':
        About=request.POST.get('About')
        Discussion=request.POST.get('Discussion')
        Media=request.POST.get('Media')
        Name=request.POST.get('Name')
        Discussion(About=About,Discussion=Discussion,Name=Name).save(),
        return render(request,'/home.html')
    else :
        return render(request,'discussion.html')

def discussion(request):
    form = CreateInDiscussion()
    if request.method == 'POST':
        form = CreateInDiscussion(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
        context ={'form':form}
    return render(request,'group.html')





#workshop
def workshop(request):
        try:
            data=Workshop.objects.all()
            person = Person.objects.filter(Email=request.session['Email'])
            return render(request,'workshop.html',{'data':data, 'person':person})
        except Workshop.DoesNotExist:
            raise Http404('Data does not exist')

def BookWorkshop(request):
        try:
            data=Workshop.objects.all()
            return render(request,'BookWorkshop.html',{'data':data})
        except Workshop.DoesNotExist:
            raise Http404('Data does not exist')
            
def createWorkshop(request):
    if request.method=='POST':
        ProgrammeName=request.POST.get('ProgrammeName')
        Description=request.POST.get('Description')
        Date=request.POST.get('Date')
        Session=request.POST.get('Session')
        Workshop(ProgrammeName=ProgrammeName,Description=Description,Date=Date,Session=Session).save(),
        messages.success(request,'The ' + request.POST['ProgrammeName'] + " is save succesfully..!")
        return render(request,'CreateWorkshop.html')
    else :
        return render(request,'CreateWorkshop.html')

def booking(request):
    #person = Person.objects.filter(Email=request.session['Email'])
    #return render(request, 'booking.html',{'person': person})

    #try:
    #    data=Workshop.objects.all() #filter(ProgrammeName=request.session['ProgrammeName'])
    #    return render(request,'booking.html',{'data':data})
    #except Workshop.DoesNotExist:
    #    raise Http404('Data does not exist')
    data=Workshop.objects.all()
    person = Person.objects.filter(Email=request.session['Email'])
    if request.method=='POST':
        Name=request.POST.get('Name')
        ProgrammeName=request.POST.get('ProgrammeName')
        Date=request.POST.get('Date')
        Session=request.POST.get('Session')
        Booking(Name=Name,ProgrammeName=ProgrammeName,Date=Date,Session=Session).save(),
        messages.success(request,'The booking of is save succesfully..!')
        return render(request,'workshop.html',{'data':data, 'person':person})
    else :
       return render(request,'workshop.html')

    #data = Workshop.objects.all#filter(ProgrammeName=request.session['ProgrammeName'])
    #return render(request, 'booking.html',{'data': data})

#class Users(viewsets.ModelViewSet):
#    queryset = Users.objects.all() 
#    serializer_class = UsersSerializer

class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    #authentication_class = 
    Email = serializers.CharField(required=False)
    username = Email
    serializers_class = MyTokenObtainPairSerializer
    def get_token(cls, user):
            token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
            token['username'] = user.Email
            return token


