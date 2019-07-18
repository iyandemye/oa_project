
import pandas as pd
import numpy as np
import csv
import sys
import os
import ast
import scipy
from scipy.stats import chisqprob
import codecs
import nltk
from nltk.corpus import stopwords

# importing data
batch_size = 1000 # should be the same batch-size used to retrieve pubmed records
out_file_index =  "result_file" # same index used for creating pubmed records
df = pd.DataFrame()
start = 0
current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
while True:
    try:
        file_string = (str(current_dir)+"/source_files/" + out_file_index + str("_") + str(start) + str("-") + str(start + batch_size) + ".csv")

        new_file = pd.read_csv(file_string)
        print(file_string)
        print(len(new_file))
        df = pd.concat([df, new_file], ignore_index=True)
        start = start + batch_size
    except FileNotFoundError:
        print("Exiting at file name: " + ascii(file_string))
        break

# clean oa data
clean_oa_status = []
for res in df["is_oa"]:
    if res == 'TRUE':
        clean_oa_status.append(True)
    elif res == "FALSE":
        clean_oa_status.append(False)
    elif res == True:
        clean_oa_status.append(True)
    elif res == False:
        clean_oa_status.append(False)
    else:
        clean_oa_status.append(None)
df["is_oa"] = clean_oa_status

# segment OA and non OA terms
OA_terms = df[df["is_oa"] == True]
print("Total OA terms: ", len(OA_terms))
NOA_terms = df[df["is_oa"] == False]
print("Total NOA terms: ",len(NOA_terms))

# create a csv file for results
fields = ["word", "OA_frequency", "NOA_frequency"]
f = csv.writer(open('{}.csv'.format("full_term_frequency"), 'w'))
f.writerow(fields)

oa_mesh_terms = [ast.literal_eval(term) for term in OA_terms["mesh_terms"]]
noa_mesh_terms = [ast.literal_eval(term) for term in NOA_terms["mesh_terms"]]

OA_words = []
NOA_words = []

for terms in oa_mesh_terms:
    OA_words.extend(terms)
for terms in noa_mesh_terms:
    NOA_words.extend(terms)
print(OA_words[:100])


all_words = OA_words + NOA_words
all_words = list(set(all_words))
print("Size of all unique words: ", len(all_words))

print("Finding word frequencies...")
# count word frequency
i = 0
for word in all_words:
	i = i + 1
	print(i, word)
	OA_frequency = OA_words.count(word)
	NOA_frequency = NOA_words.count(word)
	f.writerow([word, OA_frequency, NOA_frequency])
print("Done Creating term frequency file ")

df = pd.read_csv("./full_term_frequency.csv")
total_oa = sum(df.OA_frequency)
total_noa = sum(df.NOA_frequency)
pr_oa = total_oa/(total_oa + total_noa)
pr_noa = total_noa/(total_oa + total_noa)
df["oa_noa"] = df["OA_frequency"] + df["NOA_frequency"]
df["expected_oa"] = df["oa_noa"] * pr_oa
df["expected_noa"] = df["oa_noa"] * pr_noa
#df["oa_noa"] = df["expected_oa"] + df["expected_noa"]
df["chi_square"] = ((df.OA_frequency - df.expected_oa)**2)/df.expected_oa + ((df.NOA_frequency - df.expected_noa)**2)/df.expected_noa
df["p_value"] = chisqprob(df.chi_square, 1)
df["depletion_rate"] = (df["OA_frequency"]/(df["OA_frequency"] + df["NOA_frequency"]))/(total_oa/(total_oa + total_noa))
#df["enrichment_rate"] = (df["OA_frequency"]/df["NOA_frequency"])/(total_oa/total_noa)s
df.to_csv("full_term_depletion_data.csv")
