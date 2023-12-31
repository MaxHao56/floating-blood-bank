from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate


'''Serializer Imports'''
from .seralizer import RegisterSeralizer
from .seralizer import LoginSeralizer
from .seralizer import SurveySeralizer
from .seralizer import QuestionsSeralizer
from .seralizer import ResponsesSeralizer


from rest_framework.decorators import api_view  # API VIEW FOR DATABASE INTERACTIONS
from rest_framework.response import Response # Rest framwork for response and HTTP status
from rest_framework import status  # Rest Framwork that really took status to diverse options


from django.http import HttpResponse

from django.contrib.auth import login, logout
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session



'''Database Imports'''
from django.contrib.auth.models import User


''' Model Imports'''
from .models import Survey
from .models import Questions
from .models import Responses



'''Form  Imports'''
from .form import Registerform
from .form import LoginForm


@api_view(['POST'])
def register_api(request):

    seralizer = RegisterSeralizer(data=request.data)
    
    if seralizer.is_valid():
        seralizer.save()
        return Response({'message':'Register Sucessfully'}, status=status.HTTP_201_CREATED)
    
    return Response({'message':'seralizer has errors'}, status=status.HTTP_406_NOT_ACCEPTABLE)



# ISSUE === MUTIPLE KEYS AND REPETITIVE SESSION KEY GENERATION #

'''
-> Validates the crediential of login Users

-> Returns session key and infomation of the user
'''
@api_view(['POST'])
def login_api(request):

    seralizer = LoginSeralizer(data=request.data)      

    
          
    session = SessionStore()
    if seralizer.is_valid():
        user = seralizer.validate(request.data)


        if user is not None:
            login(request,user)
            
            
            session['user_id'] = user.id
            session['user_username'] = user.username
            session.create()
       

            return Response({'Message':'Login successful','session_key':session.session_key},status=status.HTTP_200_OK)  
        else:
            return Response({'Message':"User is None"},status=status.HTTP_404_NOT_FOUND) 
    else:
        return Response({'Message':'It is not valid'},status=status.HTTP_400_BAD_REQUEST)
    



'''
-> Authentciated User access through Session Keys
'''

@api_view(['POST'])
def user_profile(request):
    session_key = request.data.get('session_key')

    try:
        session = Session.objects.get(session_key=session_key)
    except Session.DoesNotExist:
        return Response({'Message': 'Invalid session key'}, status=status.HTTP_404_NOT_FOUND)

    session_data = session.get_decoded()
    username = session_data.get('username')

    return Response({'username': username})




'''
-> Returns all Surveys(4)
'''

@api_view(['GET'])
def getSurvey(request):
    surveys = Survey.objects.all()
    seralizer = SurveySeralizer(surveys,many=True)
    return Response(seralizer.data)


'''
-> Returns all Questions
'''

@api_view(['GET'])
def getQuestions(request):
    questions = Questions.objects.all()
    seralizer = QuestionsSeralizer(questions,many=True)
    return Response(seralizer.data)


'''
-> Returns all Responses
'''

@api_view(['GET'])
def getResponse(request):
    response = Responses.objects.all()
    seralizer = QuestionsSeralizer(response,many=True)
    return Response(seralizer.data)





'''
-> Registeration user

-> Redirection
'''

def process_register_form(request):
    if request.method == 'POST':
        form = Registerform(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                email = form.cleaned_data['email'],
                password = form.cleaned_data['password']
            )
            return redirect('home_view')
        else:
            print('User form is not valid')
            print(form.errors)  # Print form errors to see which fields caused validation failure
    else:
        print('request method is not posted')

    return HttpResponse("An error occurred during form processing.")




''' STILL WORKING '''
''' Needs cookies and store in the user's locally to keep session key'''
            
def process_login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            


            if email and password:
                try:
                    user= User.objects.get(email = email)
                    if user.check_password(password):
                        login(request,user)
                        session = SessionStore()
                        session['email'] = user.email
                        session['username'] = user.username
                        session['id'] = user.id
                        session.create()

                        print(session.session_key) # Needs to store the session key in cookies


                except User.DoesNotExist:
                    return Response({'Message':'It is not valid'},status=status.HTTP_400_BAD_REQUEST)

            else: return Response({'Message':"User is None"},status=status.HTTP_404_NOT_FOUND)
   

   
    
    return HttpResponse("An error occurred during form processing.")
    


@api_view(['POST'])
def process_logout(request):
    # if request.method == 'POST':
        logout(request)
        session_key = request.data.get('session_key')

        session = Session.objects.get(session_key=session_key)
        session.expire_date = timezone.now()
        session.save()

        now = timezone.now()
        expired_sessions = Session.objects.filter(expire_date__lt=now)

    # Deleting the expired sessions
        num_deleted, _ = expired_sessions.delete()

        return Response({'message':"done"},status=status.HTTP_200_OK)
        