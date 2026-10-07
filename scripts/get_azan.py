import os
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Union
from tqdm import tqdm
import json


class Azan:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        }
        self.session.headers.update(self.headers)
        self.download_dir = "islamic_data/adhan/"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        
        self.temp_list = []
            

    def get(self, url: str) -> Union[requests.Response, requests.exceptions.RequestException]:
        """Fetch content from a URL."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as error:
            return error

    def extract_content_from_url(self, response: requests.Response) -> BeautifulSoup:
        """Parse HTML content into BeautifulSoup object."""
        return BeautifulSoup(response.text, "lxml")

    def extract_titles(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extracts titles and URLs from the soup.
        Returns a dict mapping url -> title.
        """
        ul = soup.find("ul", {"id": "ul-play-list"})
        titles: Dict[str, str] = {}

        if not ul:
            return titles

        for a_tag in ul.find_all('a', {"rel": "nofollow", "class": "link-media never"}):
            url = a_tag.get("href", "")
            title = a_tag.find("span").get_text(
                strip=True) if a_tag.find("span") else "Unknown"
            titles[url] = re.sub(r'\s+', ' ', title.replace('-', '')).strip()

        return titles

    def get_azan_combined(self, url_ar: str, url_en: str) -> List[Dict[str, str]]:
        """Fetch Arabic and English titles and combine them by URL."""
        response_ar = self.get(url_ar)
        response_en = self.get(url_en)

        if not isinstance(response_ar, requests.Response):
            print(f"Error fetching Arabic URL: {response_ar}")
            return []

        if not isinstance(response_en, requests.Response):
            print(f"Error fetching English URL: {response_en}")
            return []

        soup_ar = self.extract_content_from_url(response_ar)
        soup_en = self.extract_content_from_url(response_en)

        titles_ar = self.extract_titles(soup_ar)
        titles_en = self.extract_titles(soup_en)

        combined: List[Dict[str, str]] = []
        for url, title_ar in titles_ar.items():
            title_en = titles_en.get(url, "Unknown")
            combined.append(
                {"title_ar": title_ar, "title_en": title_en, "url": url})

        return combined

    def save_as_json(self, data: List[Dict[str, str]], filename: str):
        """Save the combined Adhan list as a JSON file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

    def download_azan(self, url: str, filename: str):
        """
            Download the Adhan audio file from the given URL.
            progress bar using tqdm to show download progress.

        """
        filename = re.sub(r'[\\/*?:"<>|]', "_", filename).lower().replace(" ", "_")  # Sanitize filename
        # check if the directory exists, if not create it

        path = f"{self.download_dir}/{filename}"
        # Create the directory if it doesn't exist
        # add each title on seprated folder
        # there something title it may be same but the diff is "fajr" i want to add same title like "Yaseen Al Aassaf Adhan Al Fajr, Al Iraq.mp3" and "Yaseen Al Aassaf Adhan, Al Iraq.mp3" in same folder and keep names

        title_folder = os.path.splitext(filename)[0]

        path = f"{self.download_dir}/{title_folder}/{filename}"
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            with open(path, "wb") as f:
                for chunk in tqdm(response.iter_content(chunk_size=8192), total=total_size//8192 + 1, desc=f"Downloading {path}"):
                    f.write(chunk)
            print(f"Downloaded: {path}")
        except requests.exceptions.RequestException as error:
            print(f"Error downloading {url}: {error}")
    



    def __del__(self):
        self.session.close()

    def __str__(self):
        return f"Azan Scraper with session: {self.session}"

    def __repr__(self):
        return f"Azan()"

    def __len__(self):
        return 1  # Just a placeholder, as this class doesn't have a length concept


if __name__ == "__main__":
    url_ar = "https://ar.assabile.com/adhan-call-prayer"
    url_en = "https://assabile.com/adhan-call-prayer"

    azan = Azan()
    adhan_list = azan.get_azan_combined(url_ar, url_en)

    # Print the combined list
    for adhan in adhan_list:
        # print(adhan)
        azan.download_azan(adhan["url"], f"{adhan['title_en']}.mp3")

    # Save as JSON
    azan.save_as_json(adhan_list, "adhan.json")