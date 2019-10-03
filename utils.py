import typing as _t

from yarl import URL


def transform_to_paginated_response(
        data: list,
        page: int,
        page_size: int,
        total_pages: int,
        total_items: int,
        has_next: bool,
        has_prev: bool,
        url_for: _t.Callable,
        request_url: URL,
        **kwargs) -> dict:
    """
    Transform paginated data to json-api-like format

    :param data: items list
    :param page: page number
    :param page_size: page size
    :param total_pages: total pages count
    :param total_items: total items count
    :param has_next: has next page
    :param has_prev: has previous page
    :param url_for: url_for method for url resolution
    :param request_url: original request.url to get the host
    :param kwargs: extra keyword arguments for url query
    :return: dict
    """
    data = {
        'data': data,
        'meta': {
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'total_items': total_items
        },
        'links': {
            'self': str(
                request_url.join(
                    url_for().with_query(
                        page=page,
                        page_size=page_size,
                        **kwargs
                    )
                )
            ),
            'next': str(
                request_url.join(
                    url_for().with_query(
                        page=page + 1,
                        page_size=page_size,
                        **kwargs
                    )
                )
            ) if has_next else None,
            'prev': str(
                request_url.join(
                    url_for().with_query(
                        page=page - 1,
                        page_size=page_size,
                        **kwargs
                    )
                )
            ) if has_prev else None
        }
    }
    return data
