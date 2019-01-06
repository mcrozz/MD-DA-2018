import json

from django.shortcuts import render
from django.http import HttpResponse


def ping(request):
    status = {
        'running': False
    }
    json_data = json.dumps(status)
    return HttpResponse(json_data, content_type='application/json')

def run(request):
    status = {
        'running': False
    }
    json_data = json.dumps(status)
    return HttpResponse(json_data, content_type='application/json')