class SafePaginationMixin:

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        raw = self.kwargs.get(self.page_kwarg) or self.request.GET.get(self.page_kwarg) or 1
        try:
            page_number = int(raw)
        except (TypeError, ValueError):
            page_number = paginator.num_pages if raw == 'last' else 1
        page_number = min(max(page_number, 1), paginator.num_pages)
        page = paginator.page(page_number)
        return paginator, page, page.object_list, page.has_other_pages()
