
from config import *
from Bio import Entrez
import pandas as pd
import numpy as np
from Bio import Medline
import requests
import csv
import json
import time
import multiprocessing
from multiprocessing import Pool  # This is a thread-based Pool
from multiprocessing import cpu_count

# takes a DOI as input and outputs whether the article is OA
def unpaywall(doi, retry = 0):
    r = requests.get("https://api.unpaywall.org/v2/{}".format(doi), params={"email":EMAIL})
    if r.status_code == 404:
        return "Invalid/unknown DOI"
    if r.status_code == 500:
        if retry < 3:
            return unpaywall(doi, retry+1)
        else:
            print("Retried 3 times and failed. Giving up")
            return "API Failed"
    if  r.json()['is_oa']:
        return "TRUE"
    else:
        return "FALSE"


# Uses the Pubmed Entrez API to extract articles xml files
def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = EMAIL
    handle = Entrez.esummary(db='pubmed',retmode='xml', id=ids)
    results = Entrez.read(handle)
    return results

def get_data(papers):
    data = {}
    try:
        data[papers["Id"]] = {'doi': papers["DOI"], "is_oa":unpaywall(papers["DOI"])}
    except KeyError:
        data[papers["Id"]] = {'doi': None, "is_oa": None}
    return data


def mp_handler(data):
    p = multiprocessing.Pool(100)
    results = p.map(get_data, data)
    p.terminate()
    p.join()
    return results

""" apply multiprocessing to improve data retrieval """

if __name__ == '__main__':
    start_time = time.time()
    Idlist = [line.rstrip('\n') for line in open('./biomed_results.txt')]
    results = {}
    try:
        with open('unpaywall_data_final.json', 'r') as infile:
            results = json.load(infile)
        print("Records in current file: ", len(results.keys()))

        Idlist = set(Idlist) - set(results.keys())
        Idlist = list(Idlist)

    except FileNotFoundError:
        with open('unpaywall_data_final.json', 'w') as outfile:
            json.dump(results, outfile)
        print("Writing a new file")

    nblock = 500
    number_of_rounds = len(Idlist)/nblock + (len(Idlist) % nblock > 0)
    if number_of_rounds > 1:
        print("%i rounds of queries with %i papers per round." % (number_of_rounds, nblock))
        for i in range(int(number_of_rounds)):
            start = i * nblock
            end = (i+1) * nblock

            print ("Fetching round %i..." % (i+1))
            res = mp_handler(fetch_details(Idlist[start:end]))
            for r in res:
                results.update(r)

            with open('unpaywall_data_final.json', 'w') as outfile:
                json.dump(results, outfile)

    print(len(results))
    end_time = time.time()
    print(end_time - start_time)
