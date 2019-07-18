# coding: utf-8
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from os import path
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
#get_ipython().magic('matplotlib inline')
import warnings
warnings.filterwarnings("ignore")


current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
# change the dataset name if you're using tokenized mesh terms
df = pd.read_csv( str(current_dir)+ "/output_files/full_term_depletion_data.csv")
# Set the directory so it saves in the right place
os.chdir(str(current_dir)+"/output_files")

"""
GENERATING WORDCLOUD IMAGES FOR DEPLETED AND ENRICHED TERMS
  * A cutoff of 33.3% to get enrichment terms
  * Cutoffs: 1.333 or more for ernchiment or 0.666 or less for depletion)
  * make the size of the terms proportional to enrichment (or depletion)
"""

# If you don't use the full terms, change 500 to 2000
strong_df = df[df.oa_noa >= 500].reset_index()
print(len(strong_df))

# Enriched terms
text = {}
for word, i in zip(strong_df.word, range(0, len(strong_df.word))):
    if (strong_df.depletion_rate[i] >= 1.3333):
        text[word] = strong_df.depletion_rate[i]
print("The total number of terms considered:", len(text))

def grey_color_func(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl(319,100%%, %d%%)" % np.random.randint(0,5))

# Create and generate a wordcloud image
# The larger the terms, the more enriched they are in open access papers.
wordcloud = WordCloud(width=1600, height=800, max_words=2500,relative_scaling=1,normalize_plurals=False,
                      color_func = grey_color_func, background_color='white',
                      max_font_size=135, min_font_size=45).generate_from_frequencies(text)
plt.figure( figsize=(20,10))
plt.imshow(wordcloud)
plt.savefig("enriched_full_term_wordcloud")

# Depleted terms
text = {}
for word, i in zip(strong_df.word, range(0, len(strong_df.word))):
    if (strong_df.depletion_rate[i] <= 0.6666):
        if type(word) != float:
            text[word] = 1.0/(strong_df.depletion_rate[i])
def grey_color_func(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl(319,100%%, %d%%)" % np.random.randint(0,5))

# Create and generate a wordcloud image
# The larger the words the more depleted they are in OA papers.
wordcloud = WordCloud(width=1600, height=800, max_words=2500,relative_scaling=1,normalize_plurals=False,
                      color_func = grey_color_func, background_color='white',
                      max_font_size=180, min_font_size=60).generate_from_frequencies(text)
plt.figure( figsize=(20,10))
plt.imshow(wordcloud)
plt.savefig("depleted_full_term_wordcloud")
