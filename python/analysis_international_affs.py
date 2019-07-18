# Import all of the packages required to run the code

from config import *
import pandas as pd
import ast
import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import math
from scipy.stats.stats import pearsonr
sns.set_style("white")

plotly.tools.set_credentials_file(username= PLOTLY_USER_NAME, api_key= PLOTLY_API_KEY)

# # Collecting and merging source files

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


# cleaning strings (reading strings as arrays of strings)

country = []
for c in df.country:
    country.append(np.unique(ast.literal_eval(c))) # unique country per ro


mesh_terms = []
for m in df.mesh_terms:
    mesh_terms.append(ast.literal_eval(m))

df["country"] = country
df["mesh_terms"] = mesh_terms

#selecting only the necessary columns
df = df[["pmid", "mesh_terms", "country", "is_oa"]]


# # Cleaning Country Names

def clean_country(c):
    if c in ["United States", "United States of America", "USA"]:
        return "United States"
    elif c in ["Vietnam", "Viet Nam"]:
        return "Vietnam"
    elif c in ["The Netherlands", "Netherlands"]:
        return "Netherlands"
    elif c in ["D.R.", "Democratic Republic of the Congo", "Democratic Republic Of Congo", "Congo", "Drc"]:
        return "Congo, Dem. Rep."
    elif c in ["Czech Republic", "Czech", "Czechia"]:
        return "Czech Republic"
    elif c in ["[\"CÃ´te dIvoire\"]", "Ivory Coast", "Côte d'Ivoire", "CÃ´te d'Ivoire", "Côte d’Ivoire", "C?te d'Ivoire","C?te d?Ivoire","C??te d'Ivoire"]:
        return "Cote d'Ivoire"
    elif c in ["\"Peoples Republic of China\"]", "[\"Peoples Republic of China",
               "[\"Peoples Republic of China\"]", "China", "\"Peoples Republic of China\"",
               "[\"Peoples Republic of China\"", "PRC", "People's Republic of China"]:
        return "China"
    elif c in ["Virgin Islands", "U.S. Virgin Islands"]:
        return "Virgin Islands (U.S.)"
    elif c in ["Cabo Verde", "Cape Verde"]:
        return "Cabo Verde"
    elif c in ["RÃ©union", "Reunion", "Réunion", "R?union"]:
        return "Reunion"
    elif c in ["SÃ£o TomÃ© and PrÃ\xadncipe", "Sao Tome and Principe", "São Tomé and Príncipe"]:
        return "Sao Tome and Principe"
    elif c in ["Hong Kong"]:
        return "Hong Kong SAR, China"
    elif c in ["South Korea"]:
        return "Korea, Rep."
    elif c in ["Iran"]:
        return "Iran, Islamic Rep."
    elif c in ["Laos"]:
        return "Lao PDR"
    elif c in ["Egypt"]:
        return "Egypt, Arab Rep."
    elif c in ["Russia"]:
        return 'Russian Federation'
    elif c in ["Slovakia"]:
        return 'Slovak Republic'
    elif c in ["Syria"]:
        return "Syrian Arab Republic"
    elif c in ["Gambia", "The Gambia"]:
        return "Gambia, The"
    elif c in ["Micronesia", "Federated States of Micronesia"]:
        return "Micronesia, Fed. Sts."
    elif c in ["Macedonia"]:
        return "Macedonia, FYR"
    elif c in ["Yemen"]:
        return "Yemen, Rep."
    elif c in ["Brunei"]:
        return "Brunei Darussalam"
    elif c in ["Macao", "Macau"]:
        return "Macao SAR, China"
    elif c in ["Venezuela"]:
        return "Venezuela, RB"
    elif c in ["Saint Kitts and Nevis", "St. Kitts & Nevis"]:
        return "St. Kitts and Nevis"
    elif c in ["Independent Papua New Guinea"]:
        return "Papua New Guinea"
    elif c in ["Bahamas"]:
        return "Bahamas, The"
    elif c in ["Republic of Ireland"]:
        return "Ireland"
    elif c in ["Saint Martin"]:
        return "St. Martin (French part)"
    elif c in ["North Korea"]:
        return "Korea, Dem. People’s Rep."
    elif c in ["Saint Lucia"]:
        return "St. Lucia"
    elif c in ["Curaçao", "Cura?ao"]:
        return "Curacao"
    elif c in ["East Timor"]:
        return "Timor-Leste"
    elif c in ["Saint Vincent and the Grenadines"]:
        return "St. Vincent and the Grenadines"
    elif c in ["Trinidad and Tobago", "Trinidad & Tobago"]:
        return "Trinidad and Tobago"
    elif c in ["Bosnia & Herzegovina"]:
        return "Bosnia and Herzegovina"
    elif c in ["Sint Maarten"]:
        return "Sint Maarten (Dutch part)"
    else:
        return c


# # importing gpd, region and income level data (from the World Bank)

# Open files for regions, income groups, and GDP
economies = pd.read_csv(str(parent_dir)+"/raw_data/WB_economies.csv", encoding = "ISO-8859-1")

# 2015 gdp per capita data
gdp_data = pd.read_csv(str(parent_dir)+"/raw_data/gdp_data.csv", encoding = "ISO-8859-1")

gdp_data.columns = ["country_name", "Code", "gdp"]
economies = pd.merge(economies, gdp_data, on = "Code", how = 'left')
economies.set_index('country_name', inplace=True)
summary_data = economies.to_dict("index")
summary_data["Taiwan"] = {'Code': 'TWN', 'Economy': 'Taiwan, China', 'Income group': 'High income',
    'Region': 'East Asia & Pacific','gdp': 22374.00 }
summary_data["Swaziland"] = {'Code': 'SWZ', 'Economy': 'Swaziland', 'Income group': 'Lower middle income',
    'Region': 'Sub-Saharan Africa','gdp': 3047.95 }



# merging gdp, region and income level data with OA data
cleaned_country = []
region = []
n_regions = []
income_level = []
n_countries = []
n_income_levels = []
for this_row in range(len(df)):
    row_regions = []
    row_countries = []
    row_income_levels = []
    for c in df.country[this_row]:
        #removing countries whose region and gdp data we don't have
        clean_c = clean_country(c)
        if clean_c not in ["[]", "", "No_country", 'Guadeloupe', 'Tokelau', "Reunion", "Palestine", "Kyrgyzstan", 'French Guiana',
                     "Jersey", "Bonaire", "Falkland Islands", "Christmas Island", "Wallis and Futuna", "Antarctica",
                     "Guernsey", "United States Minor Outlying Islands", "Mayotte", "Martinique", "Svalbard and Jan Mayen",
                     "South Georgia and South Sandwich Islands", "Montserrat", "Anguilla", "Western Sahara",
                     "Vatican City", "Cook Islands", "Caribbean Netherlands"]:
            try:
                row_countries.append(clean_c)
                row_regions.append(summary_data[clean_c]['Region'])
                row_income_levels.append(summary_data[clean_c]['Income group'])
            except KeyError:
                print(clean_c)
                continue
    cleaned_country.append(row_countries)
    region.append(np.unique(row_regions))
    n_regions.append(len(np.unique(row_regions)))
    income_level.append(np.unique(row_income_levels))
    n_income_levels.append(len(np.unique(row_income_levels)))
    n_countries.append(len(np.unique(row_countries)))


df['clean_country'] = cleaned_country
df['region'] = region
df['number_of_regions'] = n_regions
df['income_group'] = income_level
df['number_of_income_groups'] = n_income_levels
df['number_of_countries'] = n_countries
# play with this to change the number of affiliated countries
df_international_affs = df[df["number_of_countries"] > 1]
#print("Papers authored by authors in countries within the same region", len(df_same_region))
df = df_international_affs
print(df.head())

# # Country level analysis
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

# # Country level analysis


countries_oa = df.groupby(["is_oa"]).agg({'clean_country': lambda x: list(x)}).reset_index()
country = []
for big_array in countries_oa.clean_country:
    falses = []
    for c in big_array:
        falses.extend(c)
    country.append(falses)
countries_oa.clean_country = country



all_countries = []
for big_c in countries_oa.clean_country:
    for c in big_c:
        all_countries.append(c)

seen = ["[]"]
frequency_oa = []
frequency_noa = []
countries = []
regions = []
income_levels = []
gdps = []
loggdps = []
for c in all_countries:
    if (c not in seen) and (c != "Cook Islands"):
        oa_counts = 0
        noa_counts = 0
        seen.append(c)
        countries.append(c)
        oa_counts = countries_oa.clean_country[1].count(c)
        noa_counts = countries_oa.clean_country[0].count(c)
        frequency_oa.append(oa_counts)
        frequency_noa.append(noa_counts)
        regions.append(summary_data[c]["Region"])
        income_levels.append(summary_data[c]["Income group"])
        gdps.append(summary_data[c]["gdp"])
        loggdps.append(math.log(summary_data[c]["gdp"],10))


COUNTRY = pd.DataFrame()
COUNTRY["Economy"] = countries
COUNTRY["Region"] = regions
COUNTRY["income_group"] = income_levels
COUNTRY["gdp"] = gdps
COUNTRY["loggdp"] = loggdps
COUNTRY["oa_frequency"] = frequency_oa
COUNTRY["noa_frequency"] = frequency_noa
COUNTRY["overall_frequency"] = COUNTRY["oa_frequency"] + COUNTRY["noa_frequency"]
COUNTRY["oa_status"] = (COUNTRY["oa_frequency"]/COUNTRY["overall_frequency"])*100
COUNTRY["log_frequency"] = np.log2(COUNTRY.overall_frequency)
COUNTRY.to_csv("oa_by_country_2_or_more_countries.csv")

# Get correlation coefficient and p-value
#country_subset = COUNTRY[COUNTRY["gdp"].notna()]
#coeffic = pearsonr(country_subset["loggdp"], country_subset["oa_status"])
#print(coeffic)

# # Create a gapminder..ish bubble plot.

country_data = COUNTRY
country_data = country_data.sort_values(['Region', 'Economy'])
slope = 2.666051223553066e-05
hover_text = []
bubble_size = []

for index, row in country_data.iterrows():
    hover_text.append(('Country: {country}<br>'+
                      'Open Access Publications (Percentage) : {oa_status}<br>'+
                      'GDP per capita: {gdp}<br>'+
                      'Log Publications: {overall_frequency}<br>'
                      ).format(country=row['Economy'],
                                            oa_status=row['oa_status'],
                                            gdp=row['gdp'],
                                            overall_frequency=row['log_frequency']))
    bubble_size.append(row['log_frequency'])

country_data['text'] = hover_text
country_data['size'] = bubble_size
sizeref = 0.1


trace0 = go.Scatter(
    x=country_data['gdp'][country_data['Region'] == 'Sub-Saharan Africa'],
    y=country_data['oa_status'][country_data['Region'] == 'Sub-Saharan Africa'],
    mode='markers',
    name='Sub-Saharan Africa',
    text=country_data['text'][country_data['Region'] == 'Sub-Saharan Africa'],
    marker=dict(
        symbol='circle',
        color = 'rgb(224,243,219)',
        sizemode='area',
        sizeref=sizeref,
        size=country_data['size'][country_data['Region'] == 'Sub-Saharan Africa'],
        line=dict(
            width=2
        ),
    )
)
trace1 = go.Scatter(
    x=country_data['gdp'][country_data['Region'] == 'Latin America & Caribbean'],
    y=country_data['oa_status'][country_data['Region'] == 'Latin America & Caribbean'],
    mode='markers',
    name='Latin America & Caribbean',
    text=country_data['text'][country_data['Region'] == 'Latin America & Caribbean'],
    marker=dict(
        sizemode='area',
        color = 'rgb(204,235,197)',
        sizeref=sizeref,
        size=country_data['size'][country_data['Region'] == 'Latin America & Caribbean'],
        line=dict(
            width=2
        ),
    )
)
trace2 = go.Scatter(
    x=country_data['gdp'][country_data['Region'] == 'Europe & Central Asia'],
    y=country_data['oa_status'][country_data['Region'] == 'Europe & Central Asia'],
    mode='markers',
    name='Europe & Central Asia',
    text=country_data['text'][country_data['Region'] == 'Europe & Central Asia'],
    marker=dict(

        sizemode='area',
        color = 'rgb(168,221,181)',
        sizeref=sizeref,
        size=country_data['size'][country_data['Region'] == 'Europe & Central Asia'],
        line=dict(
            width=2
        ),
    )
)
trace3 = go.Scatter(
    x=country_data['gdp'][country_data['Region'] == 'East Asia & Pacific'],
    y=country_data['oa_status'][country_data['Region'] == 'East Asia & Pacific'],
    mode='markers',
    name='East Asia & Pacific',
    text=country_data['text'][country_data['Region'] == 'East Asia & Pacific'],
    marker=dict(
        sizemode='area',
        color = 'rgb(123,204,196)',
        sizeref=sizeref,
        size=country_data['size'][country_data['Region'] == 'East Asia & Pacific'],
        line=dict(
            width=2
        ),
    )
)
trace4 = go.Scatter(
    x=country_data['gdp'][country_data['Region'] == 'Middle East & North Africa'],
    y=country_data['oa_status'][country_data['Region'] == 'Middle East & North Africa'],
    mode='markers',
    name='Middle East & North Africa',
    text=country_data['text'][country_data['Region'] == 'Middle East & North Africa'],
    marker=dict(
        sizemode='area',
        color = 'rgb(78,179,211)',
        sizeref=sizeref,
        size=country_data['size'][country_data['Region'] == 'Middle East & North Africa'],
        line=dict(
            width=2
        ),
    )
)
trace5 = go.Scatter(
    x=country_data['gdp'][country_data['Region'] == 'South Asia'],
    y=country_data['oa_status'][country_data['Region'] == 'South Asia'],
    mode='markers',
    name='South Asia',
    text=country_data['text'][country_data['Region'] == 'South Asia'],
    marker=dict(
        sizemode='area',
        color = 'rgb(43,140,190)',
        sizeref=sizeref,
        size=country_data['size'][country_data['Region'] == 'South Asia'],
        line=dict(
            width=2
        ),
    )
)


trace6 = go.Scatter(
    x=country_data['gdp'][country_data['Region'] == 'North America'],
    y=country_data['oa_status'][country_data['Region'] == 'North America'],
    mode='markers',
    name='North America',
    text=country_data['text'][country_data['Region'] == 'North America'],
    marker=dict(
        sizemode='area',
        sizeref=sizeref,
        color = 'rgb(8,88,158)',
        size=country_data['size'][country_data['Region'] == 'North America'],
        line=dict(
            width=2
        ),
    )
)


data = [trace0, trace1, trace2, trace3, trace4, trace5, trace6]
layout = go.Layout(
    title='Percentage of Open Access Publications v. Per Capita GDP, 2015',
    xaxis=dict(
        title='GDP per capita (2015 dollars)',
        gridcolor='rgb(255, 255, 255)',
        range=[2.003297660701705, 5.191505530708712],
        type='log',
        zerolinewidth=1,
        ticklen=5,
        gridwidth=2,
    ),
    yaxis=dict(
        title='Open Access Publications (Percentage)',
        gridcolor='rgb(255, 255, 255)',
        range=[0, 100],
        zerolinewidth=1,
        ticklen=5,
        gridwidth=2,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
)

fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='GDP-OA-NEW-2_or_more_countries')


# # Regional Level Analysis

regions_oa = df.groupby(["is_oa"]).agg({'region': lambda x: list(x)}).reset_index()
region = []
for big_array in regions_oa.region:
    falses = []
    for c in big_array:
        falses.extend(c)
    region.append(falses)
regions_oa.region = region


all_regions = []
for big_c in regions_oa.region:
    for c in big_c:
        all_regions.append(c)

seen = []
frequency_oa = []
frequency_noa = []
regions = []
for c in all_regions:
    if c not in seen:
        oa_counts = 0
        noa_counts = 0
        seen.append(c)
        regions.append(c)
        oa_counts = regions_oa.region[1].count(c)
        noa_counts = regions_oa.region[0].count(c)
        frequency_oa.append(oa_counts)
        frequency_noa.append(noa_counts)


REGION = pd.DataFrame()
REGION["Region"] = regions
REGION["oa_frequency"] = frequency_oa
REGION["noa_frequency"] = frequency_noa
REGION["overall_frequency"] = REGION["oa_frequency"] + REGION["noa_frequency"]
REGION["oa_status"] = (REGION["oa_frequency"]/REGION["overall_frequency"])*100
REGION.to_csv("oa_by_region_2_or_more_countries.csv")


# # Income Group Analysis

levels_oa = df.groupby(["is_oa"]).agg({'income_group': lambda x: list(x)}).reset_index()
level = []
for big_array in levels_oa.income_group:
    falses = []
    for c in big_array:
        falses.extend(c)
    level.append(falses)
levels_oa.income_group = level


all_levels = []
for big_c in levels_oa.income_group:
    for c in big_c:
        all_levels.append(c)

seen = []
frequency_oa = []
frequency_noa = []
levels = []
for c in all_levels:
    if c not in seen:
        oa_counts = 0
        noa_counts = 0
        seen.append(c)
        levels.append(c)
        oa_counts = levels_oa.income_group[1].count(c)
        noa_counts = levels_oa.income_group[0].count(c)
        frequency_oa.append(oa_counts)
        frequency_noa.append(noa_counts)

LEVEL = pd.DataFrame()
LEVEL["income_group"] = levels
LEVEL["oa_frequency"] = frequency_oa
LEVEL["noa_frequency"] = frequency_noa
LEVEL["overall_frequency"] = LEVEL["oa_frequency"] + LEVEL["noa_frequency"]
LEVEL["oa_status"] = (LEVEL["oa_frequency"]/LEVEL["overall_frequency"])*100
LEVEL.to_csv("oa_by_income_group_2_or_more_countries.csv")
print("DONE!")
