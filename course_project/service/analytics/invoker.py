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
        if 'error' in stderr.lower():
            result = False
            message = stderr
            logger.error(stderr)
            return result, message

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
        q_pattern = re.compile(r'^Q\*\s=\s(\d+\.\d+)')
        p_pattern = re.compile(r'p-value\s=\s(.+)$')

        ha_value = 0

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

            if len(line) > 0 and line[0] == '[':
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
            elif command == 'ljung':
                if read_lines == 4:
                    q_values = q_pattern.findall(line)
                    if len(q_values) == 0:
                        logger.error('Could not parse Q* value')
                    else:
                        q_value = float(q_values[0])
                        raw, rating = self._calculate_rating_for_Q(q_value, ha_value)
                        self.scores.append({
                            'name': 'Q',
                            'value': q_value,
                            'help': 'Ljung-Box test',
                            'rating': rating,
                            '_raw': raw
                        })
                    p_values = p_pattern.findall(line)
                    if len(p_values) == 0:
                        logger.error('Could not parse p-value')
                    else:
                        p_value = float(p_values[0])
                        self.scores.append({
                            'name': 'p-value',
                            'value': p_value,
                            'help': 'From Ljung-Box test',
                            'rating': self._calculate_rating_for_p_value(p_value),
                            '_raw': 1 - p_value
                        })
                    
                    command = None
            elif command == 'hasqr':
                if read_lines == 1:
                    ha_value = float(line)
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
        value = training_set

        training_set = abs(training_set)
        test_set = abs(training_set)

        val1 = training_set if training_set > test_set else test_set
        val2 = training_set if training_set < test_set else test_set

        if val1 == 0:
            return value, '***', 0

        frac = val2 / val1
        if frac < 0.5 and frac > -0.5:
            rating = '***'
        if frac < 1.5 and frac >- 1.5:
            rating= '**'
        if frac < 3.0 and frac > -3.0:
            rating = '*'

        return value, rating, frac

    def _calculate_rating_for_Q(self, q, ha):
        if q > ha:
            return 1, '***'
        return 0, '*'

    def _calculate_rating_for_p_value(self, p):
        if p < 0.95:
            return '***'
        if p < 1.05:
            return '**'
        return '*'


def Genres():
    stdout, stderr = run_R_script('all')
    if len(stderr) > 0:
        logger.error(stderr)
    genre_value = re.compile(r'"(\w+)"')
    return genre_value.findall(stdout)

def run_R_script(genre):
    proc = subprocess.Popen(
        ['Rscript', '--vanilla', '../model.R', '--genre=%s' % genre],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    stdout, stderr = proc.communicate()
    return str(stdout, 'utf-8'), str(stderr, 'utf-8')
