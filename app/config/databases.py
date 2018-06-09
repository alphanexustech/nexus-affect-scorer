from app import app
from flask_pymongo import PyMongo
from . import configurations

# File processing
import os
import csv
import sys

app.config['AFFECTCORPUS_DBNAME'] = 'affect-corpus'
affect_corpus = PyMongo(app, config_prefix='AFFECTCORPUS')

'''
Iniitlaize the application context with hash tables from mongo
'''
def common_set_affects(flaskResponse=None):
    with app.app_context():
        #
        # Manually pruned data from CSV
        #

        if sys.version_info[0] == 2:  # Not named on 2.6
            kwargs = {}
        else:
            kwargs ={
                'encoding': 'utf8',
                'newline': ''
                }

        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = "..\\..\\data\\meta_alternative_name_list.csv"
        if os.name == 'posix': # If on linux system
            rel_path = "../../data/meta_alternative_name_list.csv"
        abs_file_path = os.path.join(script_dir, rel_path)
        affects = {};

        with open(abs_file_path, **kwargs) as csvfile:
            data = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in data:
                if row[2] == '1':
                    if row[1] != '':
                        affects[row[0]] = row[1]
                    else:
                        affects[row[0]] = row[0]

        csvfile.close();

        return affects

# This dict is useful for getting just the commons set
app.common_set_affects = common_set_affects()

def get_frequency_distribution():
    with app.app_context():
        rcd_cursor = affect_corpus.db[configurations.freq_dist_collection].find({});
        frequency_distribution = {}
        for i in rcd_cursor:
            affects = list(set(i['affects']))
            common_affects = []
            for r in affects:
                if r in app.common_set_affects:
                    common_affects.append(app.common_set_affects[r])
            if len(common_affects) > 0:
                frequency_distribution[i['word']] = common_affects
        return frequency_distribution

def get_bucketed_frequency_distribution():
    with app.app_context():
        rcd_cursor = affect_corpus.db[configurations.freq_dist_collection].find({});
        frequency_distribution = {}
        for i in rcd_cursor:
            affects = list(set(i['affects']))
            common_affects = []
            for r in affects:
                if r in app.common_set_affects:
                    common_affects.append(app.common_set_affects[r])
            if len(common_affects) > 0:
                if len(common_affects) not in frequency_distribution:
                    frequency_distribution[len(common_affects)] = [i['word']]
                else:
                    frequency_distribution[len(common_affects)].append(i['word'])
        return frequency_distribution

def get_affect_stop_words():
    with app.app_context():
        data = get_bucketed_frequency_distribution()
        buckets = data
        stopwords = []
        # Add words that show up in over half of the affects.
        for bucket in buckets:
            if bucket > 300:
                stopwords += buckets[bucket]
        # Add words that show up in just once.
        stopwords += buckets[1]
        return stopwords

def get_member_distribution():
    with app.app_context():
        rcd_cursor = affect_corpus.db[configurations.membership_collection].find({});
        member_distribution = {}
        for i in rcd_cursor:
            if i['affect'] in app.common_set_affects:
                member_distribution[app.common_set_affects[i['affect']]] = i['data']
        return member_distribution

def get_bucketed_member_distribution():
    with app.app_context():
        rcd_cursor = affect_corpus.db[configurations.membership_collection].find({});
        member_distribution = {}
        for i in rcd_cursor:
            if i['affect'] in app.common_set_affects:
                if len(i['data']) not in member_distribution:
                    member_distribution[len(i['data'])] = [app.common_set_affects[i['affect']]]
                else:
                    member_distribution[len(i['data'])].append(app.common_set_affects[i['affect']])
        return member_distribution

# Iniitlaized hashtables
app.frequency_distribution = get_frequency_distribution()
app.bucketed_frequency_distribution = get_bucketed_frequency_distribution()
app.affect_stop_words = get_affect_stop_words()
app.member_distribution = get_member_distribution()
app.bucketed_member_distribution = get_bucketed_member_distribution()
