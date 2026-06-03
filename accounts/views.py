from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.utils.http import url_has_allowed_host_and_scheme
from .admin import CustomUserCreationForm
from django.contrib import messages
from reviews.models import Review

# Create your views here.

def register(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':    
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Account created successfully')
            return redirect('all_books')

        else:
            print(form.errors)
    
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    next_url = request.POST.get('next') or request.GET.get('next')

    if request.user.is_authenticated:
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('home')

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            User = get_user_model()
            user_by_email = User.objects.filter(email__iexact=username_or_email).first()
            if user_by_email is not None:
                user = authenticate(request, username=user_by_email.username, password=password)

        if user is not None:
            auth_login(request, user)
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            
    return render(request, 'registration/login.html', {'next': next_url})


def password_reset_form(request):
    return render(request, 'registration/password_reset_form.html')


def perfil(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Voce precisa esta logado para fazer essa ação")
        return redirect('login')
    
    user_reviews = Review.objects.filter(autor=request.user).order_by('-created_at')

    return render(request, 'registration/perfil.html', {'reviews': user_reviews})
