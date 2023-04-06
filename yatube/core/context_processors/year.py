from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': timezone.now().year
    }
