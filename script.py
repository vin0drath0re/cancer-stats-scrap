import requests
from bs4 import BeautifulSoup
import json
import csv 


def scrape_tables(url):
    # to send a request to the URL and get a response
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all('table')
        if not tables:
            print("No tables found on the page.")
            return []

        all_tables_data = []

        for table in tables:

            # to extract the data from the tables
            table_data = []
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_data.append(row_data)

            all_tables_data.append(table_data)
            
            # to remove the tables we dont need
            all_tables_data = [table for table in all_tables_data if len(table) == 187] 

        return all_tables_data

    except requests.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return []


def write_to_txt(data, filename):
    # to write the data to a clean_data.txt file in a readable format
    with open(filename, 'w') as file:
        for table in data:
            for row in table:
                file.write(str(row)+"\n")
            file.write("\n\n")    
    

def data_cleanup(all_tables_data):
    # to clean the data and structure it to be able to structure to a JSON format
    for table in all_tables_data:
        table.pop(0)
        for row in table:
            for cell in row:
                cell.replace(",", "")

    for table in all_tables_data:

        for row in table:

            for i in range(1, len(row)):
                # to remove commas, non-breaking spaces, and spaces from the numerical values
                cell = row[i].replace(",", "").replace(u'\xa0', "").replace(" ", "")
                row[i] = cell

            # to make the country names consistent, so that they can be matched across the tables
            if row[0].lower().strip() == "korea, north":
                row[0] = "North Korea"
            if row[0].lower().strip() == "korea, south":
                row[0] = "South Korea"
            if row[0].lower().strip() == "total":
                row[0] = "World"
            if row[0].lower().strip() == "the netherlands":
                row[0] = "Netherlands"

    for table in all_tables_data:
        # to sort the tables by country name
        world_row = table.pop(0)
        table.sort(key=lambda x: x[0])
        table.insert(0, world_row)  

    return all_tables_data


def structure_data(clean_data):
    # to structure the data in a JSON format
    structured_data = {
        "with_nmsc": {
            "both": {
                "population": {},
                "asr": {},
                "mortality": {}
            },
            "men": {
                "population": {},
                "mortality": {}
            },
            "women": {
                "population": {},
                "mortality": {}
            }
        },

        "without_nmsc": {
            "both": {
                "population": {},
                "asr": {},
                "mortality": {}
            },
            "men": {
                "population": {},
                "mortality": {}
            },
            "women": {
                "population": {},
                "mortality": {}
            }
        }
    }

    countries = [clean_data[0][index][0] for index in range(len(clean_data[0]))]

    for i in range(len(countries)):
        # inserting the data into the structured format
        structured_data["with_nmsc"]["both"]["population"][countries[i]] = int(clean_data[0][i][1])
        structured_data["with_nmsc"]["both"]["asr"][countries[i]] = float(clean_data[0][i][2])
        structured_data["with_nmsc"]["both"]["mortality"][countries[i]] = int(clean_data[6][i][1])

        structured_data["with_nmsc"]["men"]["population"][countries[i]] = int(clean_data[2][i][1])
        structured_data["with_nmsc"]["men"]["mortality"][countries[i]] = int(clean_data[8][i][1])

        structured_data["with_nmsc"]["women"]["population"][countries[i]] = int(clean_data[4][i][1])
        structured_data["with_nmsc"]["women"]["mortality"][countries[i]] = int(clean_data[10][i][1])


        structured_data["without_nmsc"]["both"]["population"][countries[i]] = int(clean_data[1][i][1])
        structured_data["without_nmsc"]["both"]["asr"][countries[i]] = float(clean_data[1][i][2])
        structured_data["without_nmsc"]["both"]["mortality"][countries[i]] = int(clean_data[7][i][1])

        structured_data["without_nmsc"]["men"]["population"][countries[i]] = int(clean_data[3][i][1])
        structured_data["without_nmsc"]["men"]["mortality"][countries[i]] = int(clean_data[9][i][1])

        structured_data["without_nmsc"]["women"]["population"][countries[i]] = int(clean_data[5][i][1])
        structured_data["without_nmsc"]["women"]["mortality"][countries[i]] = int(clean_data[11][i][1])

    return structured_data


def write_to_json(data, filename):
    # to write the data to a JSON file
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def write_to_csv(data, filename):
    # to write the data to a CSV file 
    with open(filename, 'w') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Country", 
                             "With NMSC : Both Sexes : Population", "With NMSC : Both Sexes : ASR", "With NMSC : Both Sexes : Mortality", 
                             "With NMSC : Men : Population", "With NMSC : Men : Mortality", 
                             "With NMSC : Women : Population", "With NMSC : Women : Mortality", 
                             "Without NMSC : Both Sexes : Population", "Without NMSC : Both Sexes : ASR", "Without NMSC : Both Sexes : Mortality", 
                             "Without NMSC : Men : Population", "Without NMSC : Men : Mortality", 
                             "Without NMSC : Women : Population", "Without NMSC : Women : Mortality"])

                             
        for country in data["with_nmsc"]["both"]["population"]:
            # using the dictionary keys to write the data to the CSV file
            csv_writer.writerow([country, 
                                 data["with_nmsc"]["both"]["population"][country], data["with_nmsc"]["both"]["asr"][country], data["with_nmsc"]["both"]["mortality"][country], 
                                 data["with_nmsc"]["men"]["population"][country], data["with_nmsc"]["men"]["mortality"][country], 
                                 data["with_nmsc"]["women"]["population"][country], data["with_nmsc"]["women"]["mortality"][country], 
                                 data["without_nmsc"]["both"]["population"][country], data["without_nmsc"]["both"]["asr"][country], data["without_nmsc"]["both"]["mortality"][country], 
                                 data["without_nmsc"]["men"]["population"][country], data["without_nmsc"]["men"]["mortality"][country], 
                                 data["without_nmsc"]["women"]["population"][country], data["without_nmsc"]["women"]["mortality"][country]])


# source URL
url = 'https://www.wcrf.org/preventing-cancer/cancer-statistics/global-cancer-data-by-country/'

all_tables_data = scrape_tables(url)

with open('raw_data.txt', 'w') as file:
    file.write(str(all_tables_data))

clean_data = data_cleanup(all_tables_data)

write_to_txt(clean_data, 'clean_data.txt')

structured_data = structure_data(clean_data)

write_to_json(structured_data, 'structured_data.json')

write_to_csv(structured_data, 'structured_data.csv')

