import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from analytics.invoker import Model, Genres
from time import time


genres = Genres()

def index(request):
    return render(request, 'home.html', { 'genres': genres })

ceche = dict()

def genre_result(request, genre):
    global ceche
    genre = genre.upper() if genre is not None else ''
    if request.method == 'PUT':
        if genre is None or len(genre) == 0:
            result = {
                'ok': False,
                'message': 'Invalid genre, please try again'
            }
            result_json = json.dumps(result)
            return HttpResponse(result_json, content_type='application/json')

        if genre in ceche.keys():
            processed_model = ceche[genre]
            if processed_model.valid():
                result = {
                    'ok': True,
                    'message': ''
                }
                result_json = json.dumps(result)
                return HttpResponse(result_json, content_type='application/json')

        model = Model(genre)
        ok, message = model.process()
        if ok:
            ceche[genre] = model

        result = {
            'ok': ok,
            'message': message
        }
        result_json = json.dumps(result)
        return HttpResponse(result_json, content_type='application/json')
    if request.method != 'GET':
        return HttpResponse('FAIL', content_type='application/text')

    if genre not in ceche.keys():
        return redirect('/wait?redirect=/result/' + genre, permanent=True)

    processed_model = ceche[genre]
    if not processed_model.valid():
        # Model expired, recreate
        return redirect('/wait?redirect=/result/' + genre, permanent=True)

    [slider_x, slider_y] = calculate_gauge_angles(processed_model.final_score)
    model = {
        'genre': processed_model.genre,
        'gauge': {
            'score': processed_model.final_score,
            'slider_x': slider_x,
            'slider_y': slider_y
        },
        'scores': processed_model.scores,
        'result': processed_model.result
    }
    return render(request, 'result.html', {
        'model': model
    })

def wait(request):
    redirect = request.GET.get('redirect')
    return render(request, 'wait.html', {
        'redirect_url': redirect
    })

from math import cos, sin, pi, radians
def calculate_gauge_angles(percent):
    radius = 40.0
    gauge_span_angle = 135.0 - 45.0
    angle = (percent * gauge_span_angle) / 100.0

    rad = radians(angle)
    angle_x = 50.0 + (radius * cos(rad))
    angle_y = 50.0 + (radius * sin(rad))

    return [angle_x, angle_y]
    # return [80.94, 23.55]