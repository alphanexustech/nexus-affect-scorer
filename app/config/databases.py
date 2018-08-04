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

def get_frequency_distribution():
    with app.app_context():
        rcd_cursor = affect_corpus.db[configurations.freq_dist_collection].find({});
        frequency_distribution = {}
        for i in rcd_cursor:
            affects = list(set(i['affects']))
            if len(affects) > 0:
                frequency_distribution[i['word']] = affects
        return frequency_distribution

def get_bucketed_frequency_distribution():
    with app.app_context():
        rcd_cursor = affect_corpus.db[configurations.freq_dist_collection].find({});
        frequency_distribution = {}
        for i in rcd_cursor:
            affects = list(set(i['affects']))
            if len(affects) > 0:
                if len(affects) not in frequency_distribution:
                    frequency_distribution[len(affects)] = [i['word']]
                else:
                    frequency_distribution[len(affects)].append(i['word'])
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
            member_distribution[i['affect']] = i['data']
        return member_distribution

def get_bucketed_member_distribution():
    with app.app_context():
        rcd_cursor = affect_corpus.db[configurations.membership_collection].find({});
        member_distribution = {}
        for i in rcd_cursor:
            if len(i['data']) not in member_distribution:
                member_distribution[len(i['data'])] = [i['affect']]
            else:
                member_distribution[len(i['data'])].append(i['affect'])
        return member_distribution

# Iniitlaized hashtables
app.frequency_distribution = get_frequency_distribution()
app.bucketed_frequency_distribution = get_bucketed_frequency_distribution()
app.affect_stop_words = get_affect_stop_words()
app.member_distribution = get_member_distribution()
app.bucketed_member_distribution = get_bucketed_member_distribution()
