import json

from django.shortcuts import render, redirect
from django.http import HttpResponse


def ping(request):
    status = {
        'running': False
    }
    json_data = json.dumps(status)
    return HttpResponse(json_data, content_type='application/json')

def run(request):
    if request.method == 'POST':
        genre = request.POST.get('genre')
        return redirect('/wait?redirect=/result/' + genre, permanent=True)
    return HttpResponse('Nope', content_type='application/text')


import subprocess
def run_model(genre):
    output = run_R_script(genre)

def run_R_script(genre):
    proc = subprocess.Popen(
        ['R', '--vanilla', '../model.R', '--genre=\'%s\'' % genre],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout