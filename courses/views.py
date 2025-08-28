from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Lesson, StudentProgress, ChatHistory, Curriculum, VideoSummary, Course
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect

from django.shortcuts import redirect
from django.http import JsonResponse

import logging

# Set up logging
logger = logging.getLogger(__name__)

def home_redirect(request):
    return redirect('dashboard')



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, 'registration/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'registration/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'registration/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        login(request, user)
        return redirect('dashboard')

    return render(request, 'registration/register.html')



# ----------------------------
# Dashboard View
# ----------------------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    courses = Course.objects.filter(user=request.user)
    progress_reports = []
    for course in courses:
        progress = StudentProgress.objects.filter(user=request.user, course=course).first()
        if progress:
            percent = int((progress.lessons_completed / progress.total_lessons) * 100) if progress.total_lessons else 0
        else:
            percent = 0
        progress_reports.append({
            'title': course.title,
            'description': course.description,
            'progress': percent,
            'completed': progress.completed if progress else False,
        })
    curriculums = Curriculum.objects.filter(user=request.user)
    video_summaries = VideoSummary.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'progress_reports': progress_reports,
        'curriculums': curriculums,
        'video_summaries': video_summaries,
    }
    return render(request, 'dashboard.html', context)


# ----------------------------
# Lesson Detail View
# ----------------------------
from django.shortcuts import get_object_or_404, render
from .models import Lesson

def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, 'lesson_detail.html', {'lesson': lesson})



# views.py
from django.shortcuts import render, redirect
from .models import Course
from .forms import CourseForm
@login_required
def course_list(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            return redirect('course_list')
    else:
        form = CourseForm()

    courses = Course.objects.filter(user=request.user)

    return render(request, 'courses/courses.html', {
        'form': form,
        'courses': courses
    })




from django.shortcuts import render, get_object_or_404
from .models import Course, ChatHistory
from django.views.decorators.csrf import csrf_exempt  # Only if you're handling this via JS (not recommended for forms)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
@login_required
def lesson_chatbot(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    session_key = f'chat_history_course_{course_id}'

    # Get curriculum for this course if exists
    # Try to find curriculum by topic matching course title
    curriculum = Curriculum.objects.filter(user=request.user, topic__icontains=course.title).first()
    # If not found, get the most recent curriculum for this user
    if not curriculum:
        curriculum = Curriculum.objects.filter(user=request.user).order_by('-created_at').first()
    
    curriculum_text = curriculum.curriculum_text if curriculum else "No curriculum available for this course."

    # Initialize chat history for this course if not present
    if session_key not in request.session:
        # Get previous chat history from database
        previous_chats = ChatHistory.objects.filter(
            user=request.user, 
            course=course
        ).order_by('timestamp')
        
        # Initialize session history with system message including curriculum
        session_history = [
            {'type': 'system', 'content': f"You are a tutor for the course: {course.title}. The course curriculum is: {curriculum_text}. Teach and answer questions about this subject. Remember our previous conversations to provide context for your answers."}
        ]
        
        # Add previous chat history to session
        for chat in previous_chats:
            session_history.append({
                'type': chat.message_type,
                'content': chat.content
            })
        
        request.session[session_key] = session_history

    # Convert session history to LangChain message objects
    history_objs = []
    for msg in request.session[session_key]:
        if msg['type'] == 'system':
            history_objs.append(SystemMessage(content=msg['content']))
        elif msg['type'] == 'human':
            history_objs.append(HumanMessage(content=msg['content']))
        elif msg['type'] == 'ai':
            history_objs.append(AIMessage(content=msg['content']))

    if request.method == "POST":
        user_message = request.POST.get("message", "")
        
        # Add the user message to history objects
        history_objs.append(HumanMessage(content=user_message))

        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.9,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        result = model.invoke(history_objs)
        history_objs.append(AIMessage(content=result.content))

        # Save back to session as dicts
        session_history = []
        for msg in history_objs:
            if isinstance(msg, SystemMessage):
                session_history.append({'type': 'system', 'content': msg.content})
            elif isinstance(msg, HumanMessage):
                session_history.append({'type': 'human', 'content': msg.content})
            elif isinstance(msg, AIMessage):
                session_history.append({'type': 'ai', 'content': msg.content})

        request.session[session_key] = session_history
        request.session.modified = True

        # Save user message and AI response to DB
        ChatHistory.objects.create(
            user=request.user,
            course=course,
            message_type='human',
            content=user_message
        )
        ChatHistory.objects.create(
            user=request.user,
            course=course,
            message_type='ai',
            content=result.content
        )

        display_history = [
            {'user': m['content']} if m['type'] == 'human' else {'ai': m['content']}
            for m in session_history if m['type'] in ['human', 'ai']
        ]

        return JsonResponse({"reply": result.content, "history": display_history})

    # For initial page load
    display_history = [
        {'user': m['content']} if m['type'] == 'human' else {'ai': m['content']}
        for m in request.session[session_key] if m['type'] in ['human', 'ai']
    ]

    return render(request, 'courses/lesson_chatbot.html', {
        "course": course,
        "chat_history": display_history
    })


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
# At the top of your views.py or settings.py
from dotenv import load_dotenv
load_dotenv()

@csrf_exempt
@login_required
def global_chatbot(request):
    # Initialize chat history in session if not present
    if 'chat_history' not in request.session:
        # Store as list of dicts for serialization
        request.session['chat_history'] = [
            {'type': 'system', 'content': "You are a helpful assistant."}
        ]

    # Convert session history to LangChain message objects
    history_objs = []
    for msg in request.session['chat_history']:
        if msg['type'] == 'system':
            history_objs.append(SystemMessage(content=msg['content']))
        elif msg['type'] == 'human':
            history_objs.append(HumanMessage(content=msg['content']))
        elif msg['type'] == 'ai':
            history_objs.append(AIMessage(content=msg['content']))

    if request.method == "POST":
        user_message = request.POST.get("message", "")
        history_objs.append(HumanMessage(content=user_message))

        # ✅ FIXED: Include the API key properly
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.9,
            max_tokens=100,
            google_api_key=os.getenv("GOOGLE_API_KEY")  # <-- This is essential
        )

        result = model.invoke(history_objs)
        history_objs.append(AIMessage(content=result.content))

        # Save back to session as dicts
        session_history = []
        for msg in history_objs:
            if isinstance(msg, SystemMessage):
                session_history.append({'type': 'system', 'content': msg.content})
            elif isinstance(msg, HumanMessage):
                session_history.append({'type': 'human', 'content': msg.content})
            elif isinstance(msg, AIMessage):
                session_history.append({'type': 'ai', 'content': msg.content})

        request.session['chat_history'] = session_history
        request.session.modified = True

        # For frontend display
        display_history = [
            {'user': m['content']} if m['type'] == 'human' else {'ai': m['content']}
            for m in session_history if m['type'] in ['human', 'ai']
        ]

        return JsonResponse({"reply": result.content, "history": display_history})

    # For initial page load
    display_history = [
        {'user': m['content']} if m['type'] == 'human' else {'ai': m['content']}
        for m in request.session['chat_history'] if m['type'] in ['human', 'ai']
    ]

    return render(request, "global_chatbot.html", {"chat_history": display_history})  # ✅ FIXED: removed stray quote




@login_required
def curriculum(request):
    if request.method == "POST":
        topic = request.POST.get("topic")
        # Generate curriculum using chatbot
        prompt = f"Create a detailed curriculum for learning about '{topic}'."
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=500,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        result = model.invoke([HumanMessage(content=prompt)])
        Curriculum.objects.create(
            user=request.user,
            topic=topic,
            curriculum_text=result.content
        )
        messages.success(request, "Curriculum generated and saved!")
        return redirect('dashboard')
    return render(request, 'curriculum.html')


@login_required
def video_summarize(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url", "")
        title = request.POST.get("title")
        content = request.POST.get("content")
        
        # Improved prompt for summarizing provided content
        prompt = (
            f"Please provide a comprehensive and detailed summary of the following video content. "
            f"Video Title: {title}\n"
            f"Content to summarize:\n{content}\n\n"
            "Please create a well-structured summary that covers all key points, important details, and main ideas presented in the content. "
            "Organize the summary in a clear, logical manner with appropriate sections if needed. "
            "The summary should be approximately 300-500 words."
        )
        
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=1500,  # Increased to allow longer output
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        result = model.invoke([HumanMessage(content=prompt)])
        
        VideoSummary.objects.create(
            user=request.user,
            title=title,
            video_url=video_url,
            summary=result.content
        )
        messages.success(request, "Video summary generated and saved!")
        return redirect('dashboard')
    return render(request, 'video_summarize.html')


@login_required
def quiz(request):
    if request.method == "POST":
        topic = request.POST.get("topic")
        difficulty = request.POST.get("difficulty")
        
        # Create a prompt for generating a quiz with a specific format
        prompt = f"""Generate a quiz with 5 questions on the topic '{topic}' at '{difficulty}' difficulty level. 
        Each question should have 4 options (A, B, C, D) and indicate the correct answer.
        Please format the output EXACTLY as follows:
        
        Q1: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct Answer: [A/B/C/D]
        
        Q2: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct Answer: [A/B/C/D]
        
        (Continue for all 5 questions)
        """
        
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=1000,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        result = model.invoke([HumanMessage(content=prompt)])
        
        # Pass the generated quiz to the template
        return render(request, 'quiz.html', {
            'quiz_content': result.content,
            'topic': topic,
            'difficulty': difficulty
        })
    
    return render(request, 'quiz.html')
