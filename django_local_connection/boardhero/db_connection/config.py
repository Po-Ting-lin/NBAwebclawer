from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def pagination(request, data, num=30):
    paginator = Paginator(data, num)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except Exception:
        items = paginator.page(1)
    return items
