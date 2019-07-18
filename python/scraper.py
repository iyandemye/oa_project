
from config import *
from Bio import Entrez
import pandas as pd
import requests
import csv
import json
import time
import multiprocessing
from multiprocessing import Pool
import xml.etree.ElementTree as ET
from geolocator import *
from r_helper import *

""" Uses the Pubmed Entrez API to extract articles xml files """
def fetch_xml(id_list):
    ids = ','.join(id_list)
    Entrez.email = EMAIL
    handle = Entrez.efetch(db='pubmed',retmode='xml', id=ids)
    try:
        tree = ET.parse(handle)
        papers = tree.findall('./PubmedArticle')
    except (http.client.IncompleteRead) as e:
        tree = e.partial
        papers = tree.findall('./PubmedArticle')
    return papers

def find_elem_text(root, xpath_string):
    elem = root.find(xpath_string)
    return None if elem is None else elem.text

""" Function gets all the paper details we need """
def get_paper_details(article):
    pmid = find_elem_text(article, 'MedlineCitation/PMID')
    #print("paper id:", pmid)
    doi = find_elem_text(article, 'MedlineCitation/Article/ELocationID[@EIdType="doi"][@ValidYN="Y"]')
    if doi is None:
        doi = find_elem_text(article, './/ArticleId[@IdType="doi"]')
    title = find_elem_text(article,'MedlineCitation/Article/ArticleTitle')
    author_elems = article.findall('MedlineCitation/Article/AuthorList/Author/LastName')
    author_names = None if author_elems is None \
                        else [au.text for au in author_elems]
    affiliation_elems = article.findall('MedlineCitation/Article/AuthorList/Author/AffiliationInfo/Affiliation')
    affiliations = None if affiliation_elems is None \
                        else [aff.text for aff in affiliation_elems]
    mesh_terms_elems = article.findall('MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName')
    mesh_terms = None if mesh_terms_elems is None \
                        else [mt.text for mt in mesh_terms_elems]
    try:
        is_oa = unpaywall_data[pmid]["is_oa"]
    except KeyError:
        is_oa = None
        print(pmid)
    affils_tosave = []
    all_affils = []
    for af in affiliations:
        short_affiliations = r_script.handler(af)
        all_affils.append(short_affiliations)
        affils_tosave.append(af)

    red_affils = r_script.set_strings(all_affils)
    for each_affil in red_affils:
        try:
            [brute_force_country,method] = find_country(each_affil) #get country from the affiliation
        except TypeError:
            brute_force_country = [None]
            method = [None]
        try:
            return {"pmid": pmid,
                    "doi": doi,
                    "full_affiliations": ascii(affils_tosave),
                    "short_affiliations": each_affil,
                    "country": clean_country(brute_force_country),
                    "country_finder": method,
                    "mesh_terms":mesh_terms,
                    "is_oa": is_oa}
        except UnicodeEncodeError:
            continue

""" apply multiprocessing to improve data retrieval """
def mp_handler(data):
    p = multiprocessing.Pool(20)
    results = p.map(get_paper_details, data)
    p.terminate()
    p.join()
    return results

if __name__ == '__main__':
    start_time = time.time()
    # text file with the pmids we want to pull
    with open('biomed_results.txt', 'r') as file:
        Idlist = file.readlines()
    # json file with the OA status for each paper
    with open("./unpaywall_data_final.json") as f:
        unpaywall_data = json.load(f)
    batch_size = 1000  # use same batch size while reading in files for analysis
    output_file_index =  "result_file" # use same name index while reading in files for analysis
    number_of_rounds = len(Idlist)/batch_size + (len(Idlist) % batch_size > 0)
    print("%i rounds of queries with %i papers per round." % (number_of_rounds, batch_size))

    for i in range(int(number_of_rounds)):
        results = []
        start = i*batch_size
        end = (i+1)*batch_size
        output_filename = output_file_index + "_"  + str(start) + "-" + str(end) + ".csv"
        try:
            pd.read_csv(output_filename)
        except FileNotFoundError:
            print("writing file ", output_filename)
            try:
                res = mp_handler(fetch_xml(Idlist[start:end]))
                for row in res:
                    results.append(row)
                file_out = pd.DataFrame(results)
                file_out.to_csv(output_filename)
            # throw every http related error in here.
            except (http.client.IncompleteRead, AttributeError) as e:
                res = mp_handler(fetch_xml(Idlist[start:end]))
                for row in res:
                    results.append(row)
                file_out = pd.DataFrame(results)
                file_out.to_csv(output_filename)
    end_time = time.time()
    print(end_time - start_time)
