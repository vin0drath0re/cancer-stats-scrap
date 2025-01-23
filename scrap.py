import requests
from bs4 import BeautifulSoup

def scrape_tables(url):
    try:
        # Send an HTTP GET request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP requests that fail

        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all tables in the page
        tables = soup.find_all('table')
        if not tables:
            print("No tables found on the page.")
            return []

        all_tables_data = []

        for table in tables:
            # Extract table headers
            headers = [header.get_text(strip=True) for header in table.find_all('th')]

            # Extract table rows
            rows = []
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                rows.append(row_data)

            table_data = {
                'headers': headers,
                'rows': rows
            }
            all_tables_data.append(table_data)

        return all_tables_data

    except requests.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return []

# Example usage
url = 'https://www.wcrf.org/preventing-cancer/cancer-statistics/global-cancer-data-by-country/'
tables_data = scrape_tables(url)
for table in tables_data:
    print("\n\nHeaders:", table['headers'])
    print("\nRows:")
    for row in table['rows']:
        print(row)
    