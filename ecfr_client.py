import requests

class ECFRClient:
    @staticmethod
    def get_part_11_text():
        """Fetches 21 CFR Part 11 from the eCFR API."""
        # Querying Title 21 (Food and Drugs), Part 11
        url = "https://www.ecfr.gov/api/versioner/v1/full/2024-02-01/title-21.xml?part=11"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        raise Exception(f"Failed to fetch eCFR data: {response.status_code}")