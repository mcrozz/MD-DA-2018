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
        p_pattern = re.compile(r'p-value\s[=<>]\s(.+)$')

        ha_value = 0

        accuracy_description = {
            'ME': 'Mean Error',
            'RMSE': 'Root Mean Squared Error',
            'MAE': 'Mean Absolute Error',
            'MPE': 'Mean Percentage Error',
            'MAPE': 'Mean Absolute Scaled Error',
            'MASE': 'Mean Absolute Scaled Error',
            'ACF1': 'Autocorrelation of errors at lag 1',
            'Q': 'Ljung-Box test',
            'p-value': 'From Ljung-Box test',
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
                line = line.strip()
                space_index = line.index(' ')
                training_set = float(line[:space_index])
                test_set = float(line[space_index:])
                raw, rating = self._calculate_rating(command, training_set)
                self.scores.append({
                    'name': command,
                    'value': training_set,
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
                            'help': accuracy_description['Q'],
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
                            'help': accuracy_description['p-value'],
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
        if len(self.scores) == 0:
            self.final_score = 0
            return

        weight_distribution = {
            'ME': 0.03,
            'RMSE': 0.03,
            'MAE': 0.03,
            'MPE': 0.03,
            'MAPE': 0.03,
            'MASE': 0.03,
            'ACF1': 0.03,
            'Q': 0.70,
            'p-value': 0.11,
        }

        for score in self.scores:
            per_score = weight_distribution[score['name']]
            score_weighted = score['_raw'] * per_score
            score_weighted = per_score if score_weighted > per_score else score_weighted
            final_score = final_score + score_weighted

        final_score = round(final_score * 100)
        self.final_score = final_score

    def _calculate_rating(self, name, training_set):
        score_system = {
            'ME': (0.5, 1.5),
            'RMSE': (1.0, 2.5),
            'MAE': (1.0, 2.5),
            'MPE': (1.0, 2.5),
            'MAPE': (4.0, 10.0),
            'MASE': (1.0, 2.0),
            'ACF1': (0.05, 0.5),
        }

        upper_limit = score_system[name]
        value = abs(training_set)
        if value == 0:
            return 0, '***'
        if value < upper_limit[0]:
            rating = '***'
        elif value < upper_limit[1]:
            rating= '**'
        else:
            rating = '*'

        return value, rating

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
