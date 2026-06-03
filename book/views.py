from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Books

# Create your views here.

def all_books(request):
    books = Books.objects.all()
    return render(request, 'all_books.html', {'books': books})


def search_book(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Voce precisa esta logado para fazer essa ação")
        return redirect('login')
    
    query = request.GET.get('q', '').strip()
    if query:
        books = Books.objects.filter(titulo__icontains=query)
    else:
        books = Books.objects.all()
    return render(request, 'search_book.html', {'books': books, 'query': query})


def detalhes(request, id):
    if not request.user.is_authenticated:
        messages.warning(request, "Voce precisa esta logado para fazer essa ação")
        return redirect('login')
    
    book = get_object_or_404(Books, pk=id)
    return render(request, 'detalhes.html', {'book': book})
