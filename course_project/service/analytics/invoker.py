import logging
import subprocess
import re

from time import sleep, time
from random import random


logger = logging.getLogger(__name__)

class Model:
    def __init__(self, genre):
        self.genre = genre.upper()
        self.final_score = 0
        self.scores = []
        self.result = ''
        self.created = time()

    def process(self):
        if self.genre not in Genres():
            result = False
            message = 'Genre "%s" is not presented, sorry' % self.genre
            return result, message

        sleep(1)
        self.final_score = round(random() * 100)
        self.scores = [
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
        ]
        self.result = 'January 17, 2018'

        result = True
        message = ''

        return result, message
    
    def valid(self):
        return time() - self.created < 1000*60*60


def Genres():
    stdout, stderr = run_R_script('all')
    if len(stderr) > 0:
        logger.error(stderr)
        logger.info(stdout)
        return ['FAILED TO LOAD GENRES']
    genre_value = re.compile(r'"(\w+)"')
    return genre_value.findall(stdout)

def run_R_script(genre):
    proc = subprocess.Popen(
        ['Rscript', '--vanilla', '../model.R', '--genre=%s' % genre],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    stdout, stderr = proc.communicate()
    return str(stdout, 'utf-8'), str(stderr, 'utf-8')
