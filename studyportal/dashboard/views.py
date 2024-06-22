from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import Notes,Homework,ToDo
from .import models
from .forms import *
from django.views import generic
from django.contrib import messages
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from wikipedia.exceptions import DisambiguationError
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import logout




# Create your views here.
def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method=='POST':
        form=NotesForm(request.POST)
        if form.is_valid():
            notes=Notes(user=request.user,
                        title=request.POST['title'],
                        description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added form {request.user.username} Successfully!")
    else:
        form=NotesForm()
    form=NotesForm()
    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)
@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model=Notes
    
@login_required
def homework(request):
    if request.method=='POST':
        form=HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished=='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            homeworks=Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            homeworks.save()
            messages.success(request,f"Home work added form {request.user.username}!")
    else:
        form=HomeworkForm()
    form=HomeworkForm()
    homework=Homework.objects.filter(user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
    context={
            "homeworks":homework,"homeworks_done":homework_done,"form":form,}
    return render(request,'dashboard/homework.html',context)

# def update_homework(request,pk=None):
#     homework=Homework.objects.get(id=pk)
#     if homework.is_finished==True:
#         homework.is_finished=False
#     else:
#         homework.is_finished=True
#     homework.save()
#     return redirect("homework")
@login_required
def update_homework(request, pk=None):
    homework = get_object_or_404(Homework, id=pk)
    homework.is_finished = not homework.is_finished
    homework.save()
    return redirect("homework")

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

class HomeworksDetailView(generic.DetailView):
    model=Homework

def youtube(request):
    if request.method=='POST':
        form=DashboardForm(request.POST)
        text=request.POST['text']
        vedio=VideosSearch(text,limit=10)
        result_list=[]
        for i in vedio.result()['result']:
            result_dict={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']  
            }
            desc=''
            if['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc +=j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form=DashboardForm()
    context={"form":form}
    return render(request,'dashboard/youtube.html',context)

# def todo(request):
    # if request.method=='POST':
    #     form=ToDoForm(request.POST)
    #     if form.is_valid():
    #         try:
    #             finished=request.POST['is_finished']
    #             if finished=='on':
    #                 finished=True
    #             else:
    #                 finished=False
    #         except:
    #             finished=False
    #         todos=ToDo(
    #             user=request.user,
    #             title=request.POST['title'],
    #             is_finished=finished
    #         )
    #         todos.save()
    #         messages.success(request,f"To Do added form {request.user.username}!")
    # else:
    #     form=ToDoForm()
    # form=ToDoForm()
    # todo=ToDo.objects.filter(user=request.user)
    # if len(todo)==0:
    #     todos_done=True
    # else:
    #     todos_done=False
# @login_required
# def todo(request):
#     if request.method=='POST':
#         form=ToDoForm(request.POST)
#         if form.is_valid():
#             try:
#                 finished=request.POST['is_finished']
#                 if finished=='on':
#                     finished=True
#                 else:
#                     finished=False
#             except:
#                 finished=False
#             todos=ToDo(
#                     user=request.user,
#                     title=request.POST['title'],
#                     is_finished=finished)
#             todos.save()
#             messages.success(request,f"ToDo added form {request.user.username}!")
#     else:
#         form=ToDoForm()
#     form=ToDoForm()
#     todo=ToDo.objects.filter(user=request.user)
#     if len(todo)==0:
#         todos_done=True
#     else:
#         todos_done=False
#     context={
#         'form':form,
#         'todos':todo,
#         'todos_done':todos_done
#         }
#     return render(request,'dashboard/todo.html',context)

@login_required
def todo(request):
    if request.method == 'POST':
        form = ToDoForm(request.POST)
        if form.is_valid():
            # Get title safely using .get() method
            title = request.POST.get('title', '')
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except KeyError:
                finished = False
            
            todos = ToDo(
                user=request.user,
                title=title,
                is_finished=finished
            )
            todos.save()
            messages.success(request, f"ToDo added for {request.user.username}!")
    else:
        form = ToDoForm()
    
    todos = ToDo.objects.filter(user=request.user)
    todos_done = len(todos) == 0
    
    context = {
        'form': form,
        'todos': todos,
        'todos_done': todos_done
    }
    return render(request, 'dashboard/todo.html', context)

@login_required
def update_todo(request,pk=None):
    todo=get_object_or_404(ToDo,pk=pk)
    todo.is_finished=not todo.is_finished
    todo.save()
    return redirect("todo") 
# def update_todo(request, pk):
#     if request.method == "POST":
#         todo = get_object_or_404(ToDo, pk=pk)
#         todo.is_finished = not todo.is_finished
#         todo.save()
#         return redirect("todo")
@login_required
def delete_todo(request,pk=None):
    ToDo.objects.get(id=pk).delete()
    return redirect("todo") 

def books(request):
    if request.method=='POST':
        form=DashboardForm(request.POST)
        text=request.POST['text']
        url="https://www.googleapis.com/books/v1/volumes?q="+text
        r=requests.get(url)
        answer=r.json()
        result_list=[]
        for i in range(10):
            result_dict={
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink'),

            }
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/books.html',context)
    else:
        form=DashboardForm()
    context={"form":form}
    return render(request,'dashboard/books.html',context)

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        
        try:
            r = requests.get(url)
            r.raise_for_status()
            answer = r.json()

            phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'No phonetics found.')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
            meanings = answer[0].get('meanings', [{}])[0]
            definitions = meanings.get('definitions', [{}])[0]

            definition = definitions.get('definition', 'No definition found.')
            example = definitions.get('example', 'No example found.')
            synonyms = definitions.get('synonyms', [])

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except requests.exceptions.HTTPError as e:
            # Check if the error is a 404 Not Found
            if e.response.status_code == 404:
                context = {
                    'form': form,
                    'input': text,
                    'error': "Word not found. Please try another word.",
                }
            else:
                context = {
                    'form': form,
                    'input': text,
                    'error': "There was a problem retrieving the data.",
                }
        except (IndexError, KeyError) as e:
            # Log the error (Optional: import logging and configure it)
            print(f"JSON parsing failed: {e}")
            context = {
                'form': form,
                'input': text,
                'error': "Error in parsing the response data.",
            }
        
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
        context = {
            'form': form,
        }
    return render(request, 'dashboard/dictionary.html', context)

# def dictionary(request):
#     if request.method=="POST":
#         form=DashboardForm(request.POST)
#         text=request.POST['text']
#         url="https://api.dictionaryapi.dev/api/v2/entries/en_Us/"+text
#         r=requests.get(url)
#         answer=r.json()
#         result_list=[]
#         try:
#             phonetics=answer[0].get['phonetics'][0].get['text']
#             audio=answer[0].get['phonetics'][0].get['audio']
#             definition=answer[0].get['meanings'].get[0].get['definitions'][0].get['definition']
#             example=answer[0].get['meanings'][0].get['definitions'][0].get['example']
#             synonyms=answer[0].get['meanings'][0].get['definitions'][0].get['synonyms']
#             context={
#                 'form':form,
#                 'input':text,
#                 'phonetics':phonetics,
#                 'audio':audio,
#                 'definition':definition,
#                 'example':example,
#                 'synonyms':synonyms
#             }
#         except:
#             context={
#                 'form':form,
#                 'input':''
#                 }
#         return render(request,'dashboard/dictionary.html',context)
#     else:
#         form=DashboardForm()
#         context={
#             'form':form
#             }
#     return render(request,'dashboard/dictionary.html',context)


def wiki(request):
    if request.method=='POST':
        text=request.POST['text']
        form=DashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form=DashboardForm()
        context={'form':form}
    return render(request,'dashboard/wiki.html',context)

def conversion(request):
    if request.method=='POST':
        form=ConversionForm(request.POST)
        if request.POST['measurement']=='length':
            measurement_form=ConversionLengthForm()
            context={
                'form':form,
                'm_form':measurement_form,
                'input':True
                }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input) >=0:
                    if first=='yard' and second=='foot':
                        answer=f'{input} yard={int(input)*3} foot'
                    if first=='foot' and second=='yard':
                        answer=f'{input} foot={int(input)/3} yard'
                    context={
                        'form':form,
                        'm_form':measurement_form,
                        'input':True,
                        'answer':answer
                        }
        else:
            if request.POST['measurement']=='mass':
                measurement_form=ConversionMassForm()
            context={
                'form':form,
                'm_form':measurement_form,
                'input':True
                }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input) >=0:
                    if first=='pound' and second=='kilogram':
                        answer=f'{input} pound={int(input)*0.453592} kilogram'
                    if first=='kilogram' and second=='pound':
                        answer=f'{input} kilogram={int(input)*2.20462} pound'
                    context={
                        'form':form,
                        'm_form':measurement_form,
                        'input':True,
                        'answer':answer
                        }
    else:
        form=ConversionForm()
        context={
        'form':form,
        'Input':False
    }
    return render(request,'dashboard/conversion.html',context)

def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f'Account Created for {username}!!')
            return redirect("login")
    else:
        form=UserRegistrationForm()
    context={
        'form':form
        }
    return render(request,'dashboard/register.html',context)

@login_required
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=ToDo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todos_done=True
    else:
        todos_done=False
    context={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done
        }
    return render(request,"dashboard/profile.html",context)

@login_required
def logout(request):
    if request.method == 'POST':
        pass
    else:
        auth_logout(request)
        return redirect('home')