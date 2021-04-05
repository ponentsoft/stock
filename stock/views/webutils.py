"""

Created by ponentsoft@gmail.com on 2021/4/5
Ponentsoft Technology(c) 2011-2021
"""
import json
from django.http import HttpResponse


def response_json(json_data):
    """返回json数据到客户端
    """
    return HttpResponse(json.dumps(json_data), content_type='application/json')


def get_post(request, name, default=None):
    """POST
    """
    return request.POST.get(name, default) if request.method == 'POST' else None
