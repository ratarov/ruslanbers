from django.conf import settings
from django.core.paginator import Paginator


def get_posts_context(queryset, request):
    paginator = Paginator(queryset, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


def get_authors_context(queryset, request):
    paginator = Paginator(queryset, settings.AUTHORS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }
