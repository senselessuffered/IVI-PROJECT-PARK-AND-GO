from django import template

register = template.Library()


@register.filter
def pagination_window(page_obj, paginator):
    current = page_obj.number
    total = paginator.num_pages
    size = 5

    start = max(current - size // 2, 1)
    end = min(start + size - 1, total)
    start = max(end - size + 1, 1)

    return range(start, end + 1)
