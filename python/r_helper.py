    
import rpy2
from rpy2.robjects import *
from rpy2.robjects.packages import importr
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
import http
from config import *

#import httplib

# R Helper Code:
#----------------
"""
utils = importr('utils')
utils.chooseCRANmirror(ind=1)
utils.install_packages("readr")
utils.install_packages("yaml")
utils.install_packages("XML")
utils.install_packages("XML")
utils.install_packages("XML")
utils.install_packages("countrycode")
utils.install_packages("data.table")
utils.install_packages("jsonlite")
utils.install_packages("stringr")
utils.install_packages("RCurl")
utils.install_packages("readr")
utils.install_packages("data.table")
utils.install_packages("dplyr")
utils.install_packages("purrr")
utils.install_packages("forcats")
"""
string = """


warn.conflicts = FALSE
library(jsonlite)
library(RCurl)
library(stringr)
library(readr)

# The API keys here must be entered for google (ga)
api_key_ga = GOOGLE_API_KEY

# Function to remove emails from affiliations, using regex
split_strings = function(in_string){
  # Strip out email addresses
  in_string = gsub("\\\\s*Electronic address.*[a-z0-9\\\\.\\\\_\\\\-]+\\\\@[a-z0-9\\\\.\\\\-\\\\_]+",
                   "", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("\\\\s*e.?mail.*[a-z0-9\\\\.\\\\_\\\\-]+\\\\@[a-z0-9\\\\.\\\\-\\\\_]+",
                   "", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("\\\\s*[a-z0-9\\\\.\\\\_\\\\-]+\\\\@[a-z0-9\\\\.\\\\-\\\\_]+",
                   "", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("\\\\s*Telephone:*[0-9\\\\s\\\\-\\\\+]+",
                   "", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("\\\\s*phone:*[+0-9\\\\s\\\\-\\\\+]+",
                   "", in_string, perl = TRUE, ignore.case = TRUE)

    # Fix PR China, PO Box, and related abbreviations that use a period
  in_string = gsub("P\\\\.O\\\\.|P\\\\. O\\\\.","PO", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("P\\\\.R\\\\.|P\\\\. R\\\\.","PR", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("CO\\\\.|CORP\\\\.","CO", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("No\\\\.","no", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("Rd\\\\.","rd", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("u\\\\.","u", in_string, perl = TRUE, ignore.case = TRUE)
  in_string = gsub("st\\\\.","st", in_string, perl = TRUE, ignore.case = TRUE)


  # Split strings by semicolons
  return_strings = strsplit(in_string, "\\\\s?;\\\\s?")
  return(return_strings[[1]])
}

# Function to split strings by apparent end of sentence
split_sentences = function(in_string){
  # Find matches to the end of a sentence (with a period), excluding PO Boxes
  end_affil = gregexpr("[A-Za-z0-9 ]+, [A-Za-z0-9 ]+(?<!St)\\\\.(?![A-Z]\\\\.)", in_string, perl = TRUE)

  # Get the position of each match in the string
  affil_match = end_affil[[1]]
  affil_lengths = attributes(end_affil[[1]])$match.length
  affil_split = affil_match + affil_lengths
  if(!is.na(affil_split[[1]])){
    return_strings = c()
    affil_split = c("1", affil_split)
    if ((nchar(in_string)+1)>as.integer(affil_split[length(affil_split)])){
      affil_split = c(affil_split, (nchar(in_string)+1))
    }
    for (i in 1:(length(affil_split)-1)){
      return_strings = c(return_strings, (substring(in_string,affil_split[[i]], affil_split[[i+1]])))
    }
  }
  else{
    return_strings = in_string
  }
  return(return_strings)
}

set_strings = function(in_list){
  return(list(unique(unlist(in_list))))
}

# This is a  "handler" that breaks up the strings and removes text like division, department, etc.
handler = function(instring){
  if(!is.na(instring)){
    int_out = split_strings(instring)
    output = c()
    for (elem in int_out){
      output = c(output, split_sentences(elem))
    }
    return_string = c()
    for (elem in output){
      rem_dept = gsub("^[0-9 ]{1,2}|[^,]*Department[^,\\\\.]*(,| at| in )|[^,]*Division[^,\\\\.]*(,| at| in )|.Co.first author.", "", elem, ignore.case = TRUE)
      rem_dept = tolower(rem_dept)
      rem_dept = gsub("^[^a-zA-Z]", "", rem_dept)
      rem_dept = gsub("[^a-z]+$", "", rem_dept, ignore.case = TRUE)
      if (nchar(rem_dept)>6){
        return_string = c(return_string, rem_dept)
      }
    }
  } else{
    return_string = instring
  }
  return(unique(return_string))
}

# First trim to first 1,2, or 3 "phrases"
trimmer = function(input_string, return_length){
  val = regexpr("\\\\s?[0-9a-z' \\\\.]+,\\\\s?[0-9a-z' \\\\.]+,\\\\s?[0-9a-z' \\\\.]+$",
                    input_string, perl = TRUE, ignore.case = TRUE)
  match = val[1]
  # If no match or if the match is to the beginning of the string
  if (abs(match) ==1 | return_length == 2){
    val = regexpr("\\\\s?[0-9a-z' \\\\.]+,\\\\s?[0-9a-z' \\\\.]+$",
                    input_string, perl = TRUE, ignore.case = TRUE)
    match = val[1]
  }
  if (abs(match) ==1 | return_length == 1){
    val = regexpr("\\\\s?[0-9a-z' \\\\.]+$",
                    input_string, perl = TRUE, ignore.case = TRUE)
    match = val[1]
  }
  # If the match is to a new substring
  if (match >1 & match + 4 < nchar(input_string)){
    return_string = substring(input_string, match, nchar(input_string))
  } else {
    return_string = NA
  }
  return(return_string)
}

getcountry = function(address){
  country = "No_country"
  numel = length(address$results$address_components[[1]]$types)
  if (numel > 0){
    for (i in 1:numel){
      if(address$results$address_components[[1]]$types[i][[1]][1] == "country"){
        country = address$results$address_components[[1]]$long_name[i][[1]][1]
      }
    }
  }
  return(country)
}

# Check shorter strings to ensure they have identifiable information in them
citystring = read_file("../raw_data/citynames.txt")
countrystring = read_file("../raw_data/countrynames.txt")
geochecker = function(input_string){
  if(grepl(countrystring, input_string, ignore.case = TRUE)){
    proceed = TRUE
  } else if(grepl(citystring, input_string, ignore.case = TRUE)){
    proceed = TRUE
  } else {
    proceed = FALSE
  }
  return(proceed)
}

URLquery = function(address){
  url_start = "https://maps.googleapis.com/maps/api/geocode/json?address="
  request_url = URLencode(paste(url_start,
                              address,"&key=",api_key_ga, sep = ""))
  response = getURL(request_url)
  dat = fromJSON(response)
  return(dat)
}

find_country_via_google_api = function(address){
  out = ""
  out$status = "NA"
  if (is.na(address)){
  }
  else if (geochecker(address)){
    out = URLquery(address)
    # If doesn't return, or address has lots of components...
    if (out$status != "OK"| length(out$results$address_components) >2){
      newstring = trimmer(address, 3)
      if (!is.na(newstring)){
        out = URLquery(newstring)
        if (out$status != "OK"| length(out$results$address_components) >2){
          newstring = trimmer(address, 2)
          if (!is.na(newstring)){
            out = URLquery(newstring)
            if (out$status != "OK"| length(out$results$address_components) >2){
              newstring = trimmer(address, 1)
              if (!is.na(newstring)){
                out = URLquery(newstring)
              }
            }
          }
        }
      }
    }
 }
if (out$status == "OK" & length(out$results$address_components) <4){
    country = getcountry(out)
    return(country)
    }
}

"""

string = string.replace("GOOGLE_API_KEY", '"' + GOOGLE_API_KEY + '"')

# Reads in the R code
r_script = SignatureTranslatedAnonymousPackage(string, "r_script")

