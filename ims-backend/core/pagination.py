from django.core.paginator import Paginator, Page

def paginate_queryset(queryset, page_number, items_per_page):
    paginator = Paginator(queryset, items_per_page)
    page_obj = paginator.get_page(page_number)
    return page_obj