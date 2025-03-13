from django.shortcuts import render, HttpResponse, redirect
from AudioText2SignLangApp.models import Contact
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
import nltk
import contractions
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from django.contrib import messages


# Create your views here.
# home view
def home(request):
    return render(request, 'home.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/animation')
        else:
            messages.warning(request, 'Invalid username or password.')
            return redirect('/login')
        
    return render(request, 'login.html')

# About View
def about(request):
    return render(request, 'about.html')

# Contact view
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        # print(name, phone, email, desc)
        contact = Contact(name=name, phone=phone, email=email,
                          desc=desc, date=datetime.today())
        contact.save()

        # this is for dismishal message
        messages.success(request, 'submitted successfully!')
        return redirect('/contact')
        # till this
    return render(request, 'contact.html')


contraction_map = {
    "you're": "you are", "I'm": "I am", "he's": "he is", "she's": "she is", 
    "it's": "it is", "we're": "we are", "they're": "they are", "that's": "that is",
    "isn't": "is not", "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "haven't": "have not", "hasn't": "has not", "hadn't": "had not", "won't": "will not",
    "wouldn't": "would not", "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "can't": "cannot", "couldn't": "could not", "shouldn't": "should not", 
    "mightn't": "might not", "mustn't": "must not"
}

def expand_contractions(text):
    words = text.split()
    expanded_words = []
    
    for word in words:
        if word.lower() in contraction_map:
            expanded_words.extend(contraction_map[word.lower()].split())  # Ensure all parts are added
        else:
            expanded_words.append(word)
    
    return " ".join(expanded_words)



# @login_required(login_url='/login/')

def animation(request):
    if request.method == 'POST':
        text = request.POST.get('sentence').strip()

        # Case 1: Check if input text directly matches a video title
        video_path = text + ".mp4"
        video_file = finders.find(video_path)

        # if not finders.find(video_path):
        #     return HttpResponse("Error: Video file not found.", status=404)


        if video_file:
            return render(request, 'animation.html', {'words': [text], 'text': text})
        # else:
        #     messages.error(request, f"Video file '{video_path}' not found. Please try another input.")
    

        # Case 2: Apply preprocessing (expansion, contraction, tokenization) if no exact match is found
        expanded_text = expand_contractions(text).lower()
        words = word_tokenize(expanded_text)

        tagged = nltk.pos_tag(words)
        stop_words = set(stopwords.words('english')) - {"my", "your", "you", "i"}
        lr = WordNetLemmatizer()
        filtered_text = [lr.lemmatize(w) for w in words if w not in stop_words]

        # Look for individual word videos
        animated_words = []
        for word in filtered_text:
            word_path = word + ".mp4"
            word_file = finders.find(word_path)
            if word_file:
                animated_words.append(word)
            else:
                animated_words.extend(list(word))  # Fallback to letter-based animation

        return render(request, 'animation.html', {'words': animated_words, 'text': text})
    
    else:
        if request.user.is_authenticated:
            return render(request, 'animation.html')
        else:
            messages.info(request, 'Login Required')
            return redirect('/login')



# Signup view
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("firstname")
        last_name = request.POST.get("lastname")
        print(username, email, password)
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username is already taken.')
            return redirect('/signup')
        
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Use correct email.')
            return redirect('/signup')
        
        # Create the user
        # user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()

        messages.success(request, 'Successfully Signing Up!.')
        
        # Authenticate and login the user
        authenticated_user = authenticate(request=request, username=username, password=password)
        if authenticated_user is not None:
            login(request, user)
            return redirect('/animation')
        else:
            messages.info(request, 'Invalid username or password.')
            return redirect('/signup')
    return render(request, 'signup.html')


# logout view
def logout_view(request):
    logout(request)
    return redirect('/')
    


def profile_view(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html')
    else:
        messages.info(request, 'Login Required')
        return redirect('/login') 