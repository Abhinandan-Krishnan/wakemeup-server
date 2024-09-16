import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, db

class GetMatchList:
    def __init__(self, url):
        self.url = url
    
    def fetch_html(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return None
    
    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        matches = {}

        match_containers = soup.find_all('div', class_='cb-mtch-lst cb-col cb-col-100 cb-tms-itm')
        for container in match_containers:
            match_header = container.find('h3', class_='cb-lv-scr-mtch-hdr inline-block')
            if match_header:
                match_link_tag = match_header.find('a', class_='text-hvr-underline text-bold')
                if match_link_tag and match_link_tag.get('title') and match_link_tag.get('href'):
                    title = match_link_tag['title']
                    link = 'https://www.cricbuzz.com' + match_link_tag['href']

                    match_status=self.get_match_status(container)

                    completed = container.find('div', class_='cb-text-complete') is not None
                    if not completed:
                        matches[title] = {
                            'link': link,
                            'completed': completed
                        }
        
        return matches
    
    def get_match_status(self,classes):
        if 'cb-text-complete' in classes:
            result = self.score_dump.select('.cb-text-complete')
            status='complete'
        elif 'cb-text-inprogress' in classes:
            result = self.score_dump.select('.cb-text-inprogress')
            status='inprogress'
        elif 'cb-text-stumps' in classes:
            result = self.score_dump.select('.cb-text-stumps')
            status='stumps'
        else:
            result='N/A'
            status='N/A'
        return status
    
    def get_matches(self):
        html = self.fetch_html()
        if html:
            matches = self.parse_html(html)
            return matches
        return {}



