from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from reviews.models import Review
from .models import Books

REVIEWS_PER_PAGE = 10

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
    reviews = (
        Review.objects
        .filter(book=book)
        .select_related("autor")
        .order_by("-created_at")
    )
    paginator = Paginator(reviews, REVIEWS_PER_PAGE)
    reviews_page = paginator.get_page(request.GET.get("page"))
    reviews_page_range = paginator.get_elided_page_range(
        number=reviews_page.number,
        on_each_side=1,
        on_ends=1,
    )

    return render(
        request,
        'detalhes.html',
        {
            'book': book,
            'reviews_page': reviews_page,
            'reviews_count': paginator.count,
            'reviews_page_range': reviews_page_range,
        },
    )
