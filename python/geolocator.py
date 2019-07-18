

import rpy2
from rpy2.robjects import *
from rpy2.robjects.packages import importr
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
import http
from r_helper import *

# finds a country from author affiliation
states = [ 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
          'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
          'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
          'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
          'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
          'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
          'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee',
          'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

# All state codes except "WA", which conflicts with "Western Australia"
state_codes = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WV", "WI", "WY"]

all_countries = ['Aruba', 'Afghanistan', 'Angola', 'Anguilla', 'Åland Islands', 'Albania', 'Andorra', 'United Arab Emirates',
'Argentina', 'Armenia', 'American Samoa', 'Antarctica', 'French Southern Territories',
'Antigua and Barbuda', 'Australia', 'Austria', 'Azerbaijan', 'Burundi', 'Belgium', 'Benin',
'Bonaire', 'Burkina Faso', 'Bangladesh', 'Bulgaria', 'Bahrain', 'Bahamas',
'Bosnia and Herzegovina', 'Saint Barthélemy', 'Belarus', 'Belize', 'Bermuda', 'Bolivia',
'Brazil', 'Barbados', 'Brunei Darussalam', 'Bhutan', 'Bouvet Island', 'Botswana', 'Central African Republic',
'Canada', 'Cocos (Keeling) Islands', 'Switzerland', 'Chile', 'China', "Côte d'Ivoire", 'Cameroon',
'Drc', 'Democratic Republic Of Congo', 'Congo', 'Cook Islands', 'Colombia', 'Comoros', 'Cabo Verde',
'Costa Rica', 'Cuba', 'Curaçao', 'Christmas Island', 'Cayman Islands', 'Cyprus', 'Czech', 'Germany',
'Djibouti', 'Dominica', 'Denmark', 'Dominican Republic', 'Algeria', 'Ecuador', 'Egypt', 'Eritrea',
'Western Sahara', 'Spain', 'Estonia', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)',
'France', 'Faroe Islands', 'Micronesia', 'Gabon', 'United Kingdom', 'Georgia',
'Guernsey', 'Ghana', 'Gibraltar', 'Guinea', 'Guadeloupe', 'Gambia', 'Guinea-Bissau', 'Equatorial Guinea',
'Greece', 'Grenada', 'Greenland', 'Guatemala', 'French Guiana', 'Guam', 'Guyana', 'Hong Kong',
'Heard Island and McDonald Islands', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia',
'Isle of Man', 'India', 'British Indian Ocean Territory', 'Ireland', 'Iran',
'Iraq', 'Iceland', 'Israel', 'Italy', 'Jamaica', 'Jersey', 'Jordan', 'Japan', 'Kazakhstan', 'Kenya',
'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Saint Kitts and Nevis', 'Korea', 'Kuwait',
"Lao", 'Lebanon', 'Liberia', 'Libya', 'Saint Lucia', 'Liechtenstein',
'Sri Lanka', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Macao', 'Saint Martin',
'Morocco', 'Monaco', 'Moldova', 'Madagascar', 'Maldives', 'Mexico', 'Marshall Islands',
'Macedonia, Republic of', 'Mali', 'Malta', 'Myanmar', 'Montenegro', 'Mongolia', 'Northern Mariana Islands',
'Mozambique', 'Mauritania', 'Montserrat', 'Martinique', 'Mauritius', 'Malawi', 'Malaysia', 'Mayotte', 'Namibia',
'New Caledonia', 'Niger', 'Norfolk Island', 'Nigeria', 'Nicaragua', 'Niue', 'Netherlands', 'Norway', 'Nepal',
'Nauru', 'New Zealand', 'Oman', 'Pakistan', 'Panama', 'Pitcairn', 'Peru', 'Philippines', 'Palau', 'Papua New Guinea',
'Poland', 'Puerto Rico', "Korea", 'Portugal', 'Paraguay', 'Palestine',
'French Polynesia', 'Qatar', 'Réunion', 'Romania', 'Russian Federation', 'Rwanda', 'Saudi Arabia', 'Sudan', 'Senegal',
'Singapore', 'South Georgia and the South Sandwich Islands', 'Saint Helena, Ascension and Tristan da Cunha',
'Svalbard and Jan Mayen', 'Solomon Islands', 'Sierra Leone', 'El Salvador', 'San Marino', 'Somalia',
'Saint Pierre and Miquelon', 'Serbia', 'South Sudan', 'Sao Tome and Principe', 'Suriname', 'Slovakia',
'Slovenia', 'Sweden', 'Swaziland', 'Sint Maarten (Dutch part)', 'Seychelles', 'Syrian Arab Republic', 'Syria',
'Turks and Caicos Islands', 'Chad', 'Togo', 'Thailand', 'Tajikistan', 'Tokelau', 'Turkmenistan',
'Timor-Leste', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Tuvalu', 'Taiwan',
'Tanzania', 'Uganda', 'Ukraine', 'United States Minor Outlying Islands', 'Uruguay',
'United States', 'Uzbekistan', 'Holy See', 'Vatican City', 'Saint Vincent and the Grenadines',
'Venezuela', 'Virgin Islands, U.S.', 'Virgin Islands', 'Viet Nam', 'Vanuatu',
'Wallis and Futuna', 'Samoa', 'Yemen', 'South Africa', 'Zambia', 'Zimbabwe']

# Capital lookup.
cities = {'Andorra la Vella': 'Andorra', 'Kabul': 'Afghanistan', "St. John's": 'Antigua and Barbuda', 'Tirana': 'Albania',
'Yerevan': 'Armenia', 'Luanda': 'Angola', 'Buenos Aires': 'Argentina', 'Vienna': 'Austria', 'Canberra': 'Australia',
'Baku': 'Azerbaijan', 'Bridgetown': 'Barbados', 'Dhaka': 'Bangladesh', 'Brussels': 'Belgium', 'Ouagadougou': 'Burkina Faso',
'Sofia': 'Bulgaria', 'Manama': 'Bahrain', 'Bujumbura': 'Burundi', 'Porto-Novo': 'Benin', 'Bandar Seri Begawan': 'Brunei Darussalam',
'Sucre': 'Bolivia', 'Brasilia': 'Brazil', 'Nassau': 'Bahamas', 'Thimphu': 'Bhutan', 'Gaborone': 'Botswana',
'Minsk': 'Belarus', 'Belmopan': 'Belize', 'Ottawa': 'Canada', 'Kinshasa': 'Democratic Republic of the Congo',
'Brazzaville': 'Republic of the Congo', 'Yamoussoukro': "CÃ´te d'Ivoire", 'Santiago': 'Chile', 'YaoundÃ©': 'Cameroon',
'Beijing': "People's Republic of China", 'BogotÃ¡': 'Colombia', 'San JosÃ©': 'Costa Rica', 'Havana': 'Cuba',
'Praia': 'Cape Verde', 'Nicosia': 'Cyprus', 'Prague': 'Czech Republic', 'Berlin': 'Germany', 'Djibouti City': 'Djibouti',
'Copenhagen': 'Denmark', 'Roseau': 'Dominica', 'Santo Domingo': 'Dominican Republic', 'Quito': 'Ecuador', 'Tallinn': 'Estonia',
'Cairo': 'Egypt', 'Asmara': 'Eritrea', 'Addis Ababa': 'Ethiopia', 'Helsinki': 'Finland', 'Suva': 'Fiji', 'Paris': 'France',
 'Libreville': 'Gabon', 'Tbilisi': 'Georgia', 'Accra': 'Ghana', 'Banjul': 'The Gambia', 'Conakry': 'Guinea', 'Athens': 'Greece',
 'Guatemala City': 'Guatemala', 'Port-au-Prince': 'Haiti', 'Bissau': 'Guinea-Bissau',
 'Tegucigalpa': 'Honduras', 'Budapest': 'Hungary', 'Jakarta': 'Indonesia', 'Dublin': 'Republic of Ireland',
 'Jerusalem': 'Israel', 'New Delhi': 'India', 'Baghdad': 'Iraq', 'Tehran': 'Iran', 'ReykjavÃk': 'Iceland',
 'Rome': 'Italy', 'Kingston': 'Jamaica', 'Amman': 'Jordan', 'Tokyo': 'Japan', 'Nairobi': 'Kenya',
 'Bishkek': 'Kyrgyzstan', 'Tarawa': 'Kiribati', 'Pyongyang': 'North Korea', 'Seoul': 'South Korea',
 'Kuwait City': 'Kuwait', 'Beirut': 'Lebanon', 'Vaduz': 'Liechtenstein', 'Monrovia': 'Liberia', 'Maseru': 'Lesotho',
 'Vilnius': 'Lithuania', 'Luxembourg City': 'Luxembourg', 'Riga': 'Latvia', 'Tripoli': 'Libya', 'Antananarivo': 'Madagascar',
 'Majuro': 'Marshall Islands', 'Skopje': 'Macedonia', 'Bamako': 'Mali', 'Naypyidaw': 'Myanmar', 'Ulaanbaatar': 'Mongolia',
 'Nouakchott': 'Mauritania', 'Valletta': 'Malta', 'Port Louis': 'Mauritius', 'MalÃ©': 'Maldives', 'Lilongwe': 'Malawi',
 'Mexico City': 'Mexico', 'Kuala Lumpur': 'Malaysia', 'Maputo': 'Mozambique', 'Windhoek': 'Namibia', 'Niamey': 'Niger',
 'Abuja': 'Nigeria', 'Managua': 'Nicaragua', 'Amsterdam': 'The Netherlands', 'Oslo': 'Norway', 'Kathmandu': 'Nepal',
  'Yaren': 'Nauru', 'Wellington': 'New Zealand', 'Muscat': 'Oman', 'Panama City': 'Panama', 'Lima': 'Peru',
  'Port Moresby': 'Papua New Guinea', 'Manila': 'Philippines', 'Islamabad': 'Pakistan', 'Warsaw': 'Poland', 'Lisbon': 'Portugal',
   'Ngerulmud': 'Palau', 'AsunciÃ³n': 'Paraguay', 'Doha': 'Qatar', 'Bucharest': 'Romania', 'Moscow': 'Russia',
   'Kigali': 'Rwanda', 'Riyadh': 'Saudi Arabia', 'Honiara': 'Solomon Islands', 'Khartoum': 'Sudan',
   'Stockholm': 'Sweden', 'Singapore': 'Singapore', 'Ljubljana': 'Slovenia', 'Bratislava': 'Slovakia', 'Freetown': 'Sierra Leone',
    'San Marino': 'San Marino', 'Dakar': 'Senegal', 'Mogadishu': 'Somalia', 'Paramaribo': 'Suriname', 'Sao Tome': 'Sao Tome and Principe',
    'Damascus': 'Syria', 'LomÃ©': 'Togo', 'Bangkok': 'Thailand', 'Dushanbe': 'Tajikistan', 'Ashgabat': 'Turkmenistan',
    'Tunis': 'Tunisia', 'NukuÊ»alofa': 'Tonga', 'Ankara': 'Turkey', 'Port of Spain': 'Trinidad and Tobago', 'Funafuti': 'Tuvalu',
    'Dodoma': 'Tanzania', 'Kiev': 'Ukraine', 'Kampala': 'Uganda', 'Washington, D.C.': 'United States', 'Montevideo': 'Uruguay',
    'Tashkent': 'Uzbekistan', 'Vatican City': 'Vatican City', 'Caracas': 'Venezuela', 'Hanoi': 'Vietnam', 'Port Vila': 'Vanuatu',
    "Sana'a": 'Yemen', 'Lusaka': 'Zambia', 'Harare': 'Zimbabwe', 'Algiers': 'Algeria', 'Sarajevo': 'Bosnia and Herzegovina',
    'Phnom Penh': 'Cambodia', 'Bangui': 'Central African Republic', "N'Djamena": 'Chad', 'Moroni': 'Comoros', 'Zagreb': 'Croatia',
    'Dili': 'East Timor', 'San Salvador': 'El Salvador', 'Malabo': 'Equatorial Guinea', "St. George's": 'Grenada',
    'Astana': 'Kazakhstan', 'Vientiane': 'Laos', 'Palikir': 'Federated States of Micronesia', 'Monaco': 'Monaco',
    'Podgorica': 'Montenegro', 'Rabat': 'Morocco', 'Basseterre': 'Saint Kitts and Nevis', 'Castries': 'Saint Lucia',
    'Kingstown': 'Saint Vincent and the Grenadines', 'Apia': 'Samoa', 'Belgrade': 'Serbia', 'Pretoria': 'South Africa',
    'Madrid': 'Spain', 'Sri Jayewardenepura Kotte': 'Sri Lanka', 'Mbabane': 'Swaziland', 'Bern': 'Switzerland',
    'Abu Dhabi': 'United Arab Emirates', 'London': 'United Kingdom', 'Boston': 'United States', 'San Francisco': 'United States',
    'Chicago' : 'United States', 'Los Angeles' : 'United States', 'Houston' : 'United States', 'Phoenix' : 'United States', 'Shanghai' : 'China',
    'Yokohama' : 'Japan', 'Osaka' : 'Japan', 'Nagoya' : 'Japan', 'Sapporo' : 'Japan', 'Fukuoka' : 'Japan', 'Kobe' : 'Japan',
    'Kawasaki' : 'Japan', 'Kyoto' : 'Japan', 'Melbourne' : 'Australia', 'Brisbane' : 'Australia', 'Perth' : 'Australia',
    'Adelaide': 'Australia', 'Mumbai' : 'India', 'Kolkota' : 'India', 'Bangalore' : 'India', 'Chongqing' : 'China', 'Guangzhou' : 'China',
    'Toronto' : 'Canada', 'Hyderabad' : 'India'}

# geolocate texts using a rules-based algorithm
def brute_force_geocode(text):
    text = text.title()
    if text.endswith(" Us") or text.endswith(" Usa"):
        return "United States"
    if text.endswith(" Us.") or text.endswith(" Usa.") or text.endswith(" U.S.A.") or text.endswith(" U.S."):
        return "United States"
    elif (" Us " in text) or (" Usa " in text) or (" Us," in text) or (" Usa," in text):
        return "United States"
    elif (" Uk " in text) or (" Uk," in text) or ("Scotland" in text):
        return "United Kingdom"
    elif text.endswith(" Uk") or text.endswith(",Uk") or text.endswith(" Uk.") or text.endswith(",Uk."):
        return "United Kingdom"
    elif "Nigeria" in text:
        return "Nigeria"
    elif "Taiwan" in text:
        return "Taiwan"
    elif "France" in text:
        return "France"
    elif "London" in text and ("Ont." in text or "Ontario" in text):
        return "Canada"
    elif ("Hong Kong" in text):
        return "Hong Kong"
    elif "Korea" in text:
        return "South Korea"
    elif "Russia" in text:
        return "Russia"
    elif "Iran" in text:
        return "Iran"
    elif "Espaã±A" in text:
        return "Spain"
    elif "Mã©Xico" in text:
        return "Mexico"
    elif "Deutschland" in text:
      return "Germany"
    elif "Beth Israel Deaconess" in text:
        return "United States"
    elif "Papua New Guinea" in text:
        return "Papua New Guinea"
    elif "U.S.A" in text:
      return "United States"
    elif "U.S" in text:
      return "United States"
    elif "U.K" in text:
      return "United Kingdom"
    elif "España" in text:
      return "Spain"
    elif "EspaÃ±a".lower().title() in text:
      return "Spain"
    elif  "MÃ©xico".lower().title() in text:
      return "Mexico"
    elif "Brasil" in text:
      return "Brazil"
    elif "England" in text:
      return "United Kingdom"

    for state in states:
        if ((state.lower().title()) in text):
            return "United States"
        elif text.endswith(" " + state.lower().title()):
            return "United States"
        elif text.endswith(" " + state.lower().title() + "."):
            return "United States"

    for country in all_countries:
        if country in text:
          return country

    for city in cities.keys():
      if city in text:
        return cities[city]

    for state_code in state_codes:
        if ((" " + state_code.lower().title() + ",") in text):
            return "United States"
        elif text.endswith(" " + state_code.lower().title()):
            return "United States"
        elif text.endswith(" " + state_code.lower().title() + "."):
            return "United States"

# slipt affiliations and geolocate countries in split affiliations
def find_country(full_affiliation):
    #short_affiliations = r_script.handler(full_affiliation)
    country_result = []
    method = []
    try:
        for aff in full_affiliation:
            ct = brute_force_geocode(aff)
            if ct is not None:
                country_result.append(ct)
                method.append("BF")

            else:
                ct = find_country_via_google_api(aff)
                if ct is not None:
                    country_result.append(ct)
                    method.append("GA")

        return country_result, method
    except TypeError:
        return

# geolocate countries using the Google Maps api
def find_country_via_google_api(short_affiliation):
    try:
        country = r_script.find_country_via_google_api(short_affiliation)
        try:
            return country[0]
        except TypeError:
            return
        except IndexError:
            return
    except rpy2.rinterface.RRuntimeError:
        return

# clean the countries that need cleaning
def clean_country(country_array):
    try:
        c = []
        for text in country_array:
            try:
                if "Lao" in text:
                    c.append("Laos")
                elif ("Republic of" in text) and ("Korea" in text):
                    c.append("South Korea")
                elif ("Republic of" in text) or ("Province of" in text):
                    c.append(text.split(",")[0])
                elif 'Macedonia (FYROM)' in text:
                    c.append("Macedonia")
                else:
                    c.append(text)
            except TypeError:
                continue
        return c
    except TypeError:
        return []
