from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect, render
from .forms import LoginForm,RegisterForm
from django.contrib.auth.models import User

# Create your views here.
def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
        except Exception:
            user = None
        
        if user!=None:
            # request.user == user
            login(request,user)
            return render(request,'/')
        else:
            # attempts = request.session.get('attempts') or 0
            # request.session['attempts'] = attempts + 1
            request.session['registration_error'] = 1
            return render(request,'login.html',{"form":form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("masuk pengecekan "+ str(username)+" "+ str(password))
        user = authenticate(request,username=username,password=password)
        if user!=None:
            print('User : '+user.username)
            # request.user == user
            login(request,user)
            request.session['user'] = user.username
            return redirect('index')
        else:
            return render(request,'login.html')
    else:
        return render(request,'login.html')

def logout_view(request):
    logout(request)
    return redirect("/login")