from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import AdminBookForm, AdminUserCreateForm, AdminUserUpdateForm, RegisterUserForm
from django.contrib import messages
from book.models import Books
from reviews.models import Review
from laboratory.models import ObjetoLaboratorio

# Create your views here.

def register(request):
    form = RegisterUserForm()
    if request.method == 'POST':    
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
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


def is_system_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_system_admin, login_url='login')
def system_config_home(request):
    return render(request, 'admin_config/home.html', {
        'books_count': Books.objects.count(),
        'users_count': get_user_model().objects.count(),
        'lab_objects_count': ObjetoLaboratorio.objects.count(),
    })


@user_passes_test(is_system_admin, login_url='login')
def manage_books(request):
    action = request.GET.get('action', 'list')
    selected_book = None
    form = AdminBookForm()

    if action in ('edit', 'delete'):
        selected_book = Books.objects.filter(pk=request.GET.get('book')).first()
        if selected_book is None:
            messages.warning(request, 'Selecione um livro valido para continuar.')
            return redirect('admin_books')

    if action == 'edit':
        form = AdminBookForm(instance=selected_book)

    if request.method == 'POST':
        action = request.POST.get('action')
        book_id = request.POST.get('book_id')

        if action == 'create':
            form = AdminBookForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Livro adicionado com sucesso.')
                return redirect('admin_books')

        elif action == 'edit':
            selected_book = Books.objects.filter(pk=book_id).first()
            if selected_book is None:
                messages.warning(request, 'Livro nao encontrado.')
                return redirect('admin_books')

            form = AdminBookForm(request.POST, instance=selected_book)
            if form.is_valid():
                form.save()
                messages.success(request, 'Livro atualizado com sucesso.')
                return redirect('admin_books')

        elif action == 'delete':
            selected_book = Books.objects.filter(pk=book_id).first()
            if selected_book is None:
                messages.warning(request, 'Livro nao encontrado.')
            else:
                selected_book.delete()
                messages.success(request, 'Livro removido com sucesso.')
            return redirect('admin_books')

    return render(request, 'admin_config/manage_books.html', {
        'action': action,
        'books': Books.objects.all().order_by('titulo'),
        'form': form,
        'selected_book': selected_book,
    })


@user_passes_test(is_system_admin, login_url='login')
def manage_users(request):
    User = get_user_model()
    action = request.GET.get('action', 'list')
    selected_user = None
    form = AdminUserCreateForm()

    if action in ('edit', 'delete'):
        selected_user = User.objects.filter(pk=request.GET.get('user')).first()
        if selected_user is None:
            messages.warning(request, 'Selecione um usuario valido para continuar.')
            return redirect('admin_users')

    if action == 'edit':
        form = AdminUserUpdateForm(instance=selected_user)

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == 'create':
            form = AdminUserCreateForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario adicionado com sucesso.')
                return redirect('admin_users')

        elif action == 'edit':
            selected_user = User.objects.filter(pk=user_id).first()
            if selected_user is None:
                messages.warning(request, 'Usuario nao encontrado.')
                return redirect('admin_users')

            form = AdminUserUpdateForm(request.POST, instance=selected_user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario atualizado com sucesso.')
                return redirect('admin_users')

        elif action == 'delete':
            selected_user = User.objects.filter(pk=user_id).first()
            if selected_user is None:
                messages.warning(request, 'Usuario nao encontrado.')
            elif selected_user == request.user:
                messages.warning(request, 'Voce nao pode remover o proprio usuario em uso.')
            else:
                selected_user.delete()
                messages.success(request, 'Usuario removido com sucesso.')
            return redirect('admin_users')

    return render(request, 'admin_config/manage_users.html', {
        'action': action,
        'users': User.objects.select_related('profile').all().order_by('username'),
        'form': form,
        'selected_user': selected_user,
    })
