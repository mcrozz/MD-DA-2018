import json

from django.shortcuts import render


def index(request):
    return render(request, 'home.html')

def genre_result(request, genre):
    [slider_x, slider_y] = calculate_gauge_angles(95.0)
    model = {
        'genre': genre,
        'gauge': {
            'score': 95.0,
            'slider_x': slider_x,
            'slider_y': slider_y
        },
        'scores': [
            {
                'name': 'R squared',
                'value': 0.8,
                'rating': '***'
            },
            {
                'name': 'Adj. R sqr.',
                'value': 0.75,
                'rating': '**'
            },
            {
                'name': 'Correlation',
                'value': 0.5,
                'rating': '*'
            }
        ],
        'result': 'January 17, 2018'
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
    radius = 40
    gauge_span_angle = 135 - 45
    angle = (percent * gauge_span_angle) / 100

    rad = radians(angle)
    angle_x = 50 + (radius * cos(rad))
    angle_y = 50 + (radius * sin(rad))

    return [angle_x, angle_y]
    # return [80.94, 23.55]