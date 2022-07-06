from django.core.paginator import Paginator


def paginator(request, posts, posts_per_page):
    """Функция-паджинатор. Разбивает список постов на несколько страниц"""
    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
