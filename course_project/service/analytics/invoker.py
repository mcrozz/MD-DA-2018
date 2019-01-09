import logging
import subprocess
import re

from time import sleep, time, ctime
from datetime import datetime
from random import random


logger = logging.getLogger(__name__)

class Model:
    def __init__(self, genre):
        self.genre = genre.upper()
        self.final_score = 0
        self.scores = []
        self.dates = []
        self.created = time()

    def process(self):
        if self.genre not in Genres():
            result = False
            message = 'Genre "%s" is not presented, sorry' % self.genre
            return result, message

        stdout, stderr = run_R_script(self.genre)
        if len(stderr) > 0:
            logger.error(stderr)

        self._process_script_result(stdout)
        self._process_final_score()

        result = True
        message = ''
        return result, message
    
    def valid(self):
        return time() - self.created < 1000*60*60

    def _process_script_result(self, stdout):
        control_seq = re.compile(r'"\!\&(\w+)"')
        command = None
        read_lines = 0
        vector_values = re.compile(r'(\d+)')

        accuracy_description = {
            'ME': 'Mean Error',
            'RMSE': 'Root Mean Squared Error',
            'MAE': 'Mean Absolute Error',
            'MPE': 'Mean Percentage Error',
            'MAPE': 'Mean Absolute Scaled Error',
            'MASE': 'Mean Absolute Scaled Error',
            'ACF1': 'Autocorrelation of errors at lag 1',
        }

        for line in stdout.split('\n'):
            if command is None:
                seq = control_seq.findall(line)
                if len(seq) > 0:
                    command = seq[0]
                    read_lines = 0
                continue

            if line[0] == '[':
                line = line[line.index(']') + 1:]

            if command == 'dates':
                dates = vector_values.findall(line)
                beginning = datetime(datetime.now().year, 1, 1).timestamp()
                for date in dates:
                    self.dates.append(datetime.fromtimestamp(beginning + int(date)*24*60*60))

                command = None
            elif command in accuracy_description.keys() and read_lines == 1:
                values = vector_values.findall(line)
                training_set = int(values[0])
                test_set = int(values[1])
                value, rating, raw = self._calculate_rating(training_set, test_set)
                self.scores.append({
                    'name': command,
                    'value': value,
                    'help': accuracy_description[command],
                    'rating': rating,
                    '_raw': raw,
                    '_training_set': training_set,
                    '_test_set': test_set
                })
                command = None

            read_lines = read_lines + 1

    def _process_final_score(self):
        final_score = 0
        total = len(self.scores)
        if total == 0:
            self.final_score = 0
            return

        per_score = 1 / total
        for score in self.scores:
            logger.error(score)
            final_score = final_score + (score['_raw'] * per_score)

        final_score = round(final_score * 100)
        self.final_score = final_score

    def _calculate_rating(self, training_set, test_set):
        value = test_set

        val1 = training_set if training_set > test_set else test_set
        val2 = training_set if training_set < test_set else test_set

        if val1 == 0:
            return test_set, '***', 0

        frac = val2 / val1
        if frac < 0.5 and frac > -0.5:
            rating = '***'
        if frac < 1.5 and frac >- 1.5:
            rating= '**'
        if frac < 3.0 and frac > -3.0:
            rating = '*'

        return value, rating, frac


def Genres():
    stdout, stderr = run_R_script('all')
    if len(stderr) > 0:
        logger.error(stderr)
        # logger.info(stdout)
        # return ['FAILED TO LOAD GENRES']
    genre_value = re.compile(r'"(\w+)"')
    return genre_value.findall(stdout)

def run_R_script(genre):
    proc = subprocess.Popen(
        ['Rscript', '--vanilla', '../model.R', '--genre=%s' % genre],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    stdout, stderr = proc.communicate()
    return str(stdout, 'utf-8'), str(stderr, 'utf-8')
