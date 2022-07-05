from django.core.paginator import Paginator


def paginator(request, post_list, POSTS_PER_PAGE):
    """Функция-паджинатор. Разбивает список постов на несколько страниц"""
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
