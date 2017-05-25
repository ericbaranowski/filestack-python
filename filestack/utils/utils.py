from filestack.config import CDN_URL, HEADERS

import requests


def get_url(base, handle=None, path=None, security=None):
    url_components = [base]

    if path:
        url_components.append(path)

    if security:
        url_components.append('security=policy:{policy},signature:{signature}'.format(
            policy=security['policy'], signature=security['signature'])
        )
    if handle:
        url_components.append(handle)

    return '/'.join(url_components)


def get_transform_url(tasks, external_url=None, handle=None, security=None, apikey=None):
        url_components = [CDN_URL]
        if external_url:
            url_components.append(apikey)
        if security:
            url_components.append('security=policy:{},signature:{}'.format(
                security['policy'], security['signature'])
            )
        if 'debug' in tasks:
            index = tasks.index('debug')
            tasks.pop(index)
            tasks.insert(0, 'debug')

        url_components.append('/'.join(tasks))
        url_components.append(handle or external_url)

        return '/'.join(url_components)


def make_call(base, action, handle=None, path=None, params=None, data=None, files=None, security=None, transform_url=None):
    request_func = getattr(requests, action)
    if transform_url:
        return request_func(transform_url, params=params, headers=HEADERS, data=data, files=files)

    if security:
        url = get_url(base, path=path, handle=handle, security=security)
    else:
        url = get_url(base, path=path, handle=handle)

    return request_func(url, params=params, headers=HEADERS, data=data, files=files)


def return_transform_task(transformation, params):
    transform_tasks = []

    for k, v in params.items():

        if type(v) == list:
            v = str(v).replace("'", "").replace('"', '').replace(" ", "")
        if type(v) == bool:
            v = str(v).lower()

        transform_tasks.append('{}:{}'.format(k, v))

    transform_tasks = sorted(transform_tasks)

    if len(transform_tasks) > 0:
        transformation_url = '{}={}'.format(transformation, ','.join(transform_tasks))
    else:
        transformation_url = transformation

    return transformation_url
