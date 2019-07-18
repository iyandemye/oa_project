# Project Summary

The goal of this project is to understand the topical and geographical landscape of open access publications in biomedical research literature in order to identify specific regions and fields of research that should be priority areas for open access advocacy and to better understand the current landscape of open access.   

# Process
This work involved:
 * Searching PubMed to identify a set of papers that matched a specified search criteria (the actual search query is included in the paper),
 * Downloading all of the PubMed IDs returned,
 * Using Entrez e-utilities to extract MeSH terms, digital object identifier (DOI), and affiliation metadata for each paper,
 * Using Unpaywall to identify the OA status of each paper (each DOI),
 * Spliting affiliations and geolocating them using a rule based algorithm that searched for named countries, cities and abbrevations, and using Google Maps Geocoding Api for complex strings,  
 * Using World Bank data on regions, GDP and Income levels to analyse world economies and regions,
 * Splitting Mesh Terms and calculating term frequency to identify enriched and depleted terms/topics.

# Code

Python 3 should be used for this work
* Python packages
    * biopython (for Entrez utilities)
    * beautifulsoup4
    * numpy
    * pandas
    * lxml
    * pycountry
    * rpy2 (The rpy2 package only works with R version 3.3.3 or earlier)
* R libraries
    * jsonlite
    * stringr
    * RCurl
    * readr
* Scipts
    * ```scraper.py```
      * Uses the Pubmed Entrez API to extract articles xml files
      * Collects all paper details needed for analysis
      * Uses multiprocessing to fasten data retrieval and cleanup
      * Creates csv files of data in batches of 1000 papers
    * ```r_helper.py```
      * Runs R code that splits affiliations strings into substrings for geolocation
      * Uses the google API to geolocate substrings that are hard to geolocate otherwise
    * ```geolocator.py```
      * Uses rules-based process of identifying named places in affiliations substrings
      * Calls the ```r_helper.py``` google API geolocation function for strings that are hard to geolocate otherwise
    * ```unpaywallscraper.py```
      * Calls the unpaywall API for the OA status of an article/paper using the article's DOI
      * Uses multiprocessing to improve data retrieval. Without this, every unpaywall call takes almost 1 sec which scales poorly with 600000+ papers.
      * Returns a json file (unpaywall_data.json) with each paper/doi and its OA status
    * ```analysis.py```
      * Collects and merges all source files scraped from PubMed
      * Cleans the merged dataset (country names, etc) for analysis
      * Merges PubMed data with World Bank economies/gdp data
      * Performs OA frequency analysis on country level, regional level, and income level.
      * Creates a gapminder...ish bubble plot of gdb, publications and oa status
    * ```mesh_term_frequency_and_term_depletion.py```
      * Calculates term frequency for tokenized mesh terms
    * ```full_term_frequency_and_term_depletion.py```
      * Calculates full term frequency for non-tokenized/full mesh terms
    * ```enrichment_wordcloud.py```
      * Generates word cloud images for the most enriched and most depleted terms using term frequency in OA vs non-OA
      * Uses tokenized term (not full mesh term) frequency
    * ```enrichment_wordcloud_full_terms.py```
      * Generates word cloud images for the most enriched and most depleted mesh terms using term frequency in OA vs non-OA
      * Uses full mesh term frequency
    * ```analysis_international_affs.py```
      * Performs OA analysis on papers whose authors were from 2 or more countries
    * ```analysis_within_income_group.py```
      * Performs OA analysis on papers whose authors were from the same income group (no collaboration across income groups)
    * ```analysis_within_regions.py```
      * Performs OA analysis on papers whose authors were from 2 or more income groups
    * ```biomed_results.txt```
      * Contains downloaded PubMed Ideas from our search
    * ```config.py```
      * Contains api keys and email
    * ```output_files```
      * Contains all files created for analysis
    * ```source_files```
      * Contains all csv files containing scraped data for each pubMed Id.

  For questions or feedback, please reach out to j.iyandemye@ughe.org
