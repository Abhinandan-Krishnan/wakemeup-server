import requests
import bs4
import re
import json
from collections import defaultdict
import os
import traceback
import time
from logger_config import logger



class MatchData:
    def __init__(self, url, PATH):
        self.score_url = url
        self.score_res = requests.get(self.score_url)
        self.score_dump = bs4.BeautifulSoup(self.score_res.text, 'lxml')
        self.PATH = PATH
        self.card_url = url.replace('scores', 'scorecard')
        self.card_res = requests.get(self.card_url)
        self.card_dump = bs4.BeautifulSoup(self.card_res.text, 'html.parser')
        self.match = defaultdict(dict)
        self.names = {}

        self.PATH = PATH

    def extract_data(self, pattern, string):
        extract = re.search(pattern, string)
        if extract:
            res = extract.groups()
        else:
            res = "Not found."
        return res

    def get_match_info(self):
        try:
            data = self.card_dump.select('.cb-col .cb-col-100 .cb-font-13')[-1].getText()
            header = self.card_dump.select('.cb-nav-hdr.cb-font-18')[0].getText()
            team1, team2 = self.extract_data(r'\b([A-Z]+)\s+vs\s+([A-Z]+)\b', data)
            full_team1, full_team2 = self.extract_data(r'([A-Za-z\s]+)\s+vs\s+([A-Za-z\s]+),', header)

            self.names[team1] = full_team1
            self.names[team2] = full_team2

            self.match['MatchInfo']['Teams'] = [team1, team2]

            # Extract Toss
            toss = self.extract_data(r"Toss\s\s(.*?)\swon the toss and opt to (bowl|bat)", data)
            self.match['MatchInfo']['Toss'] = [toss[0], toss[1]]

            # Extract Player names
            team1_players = self.extract_data(r"{}\sSquad  Playing(.*?)Bench".format(self.names[team1]), data)[0].split(',')
            team2_players = self.extract_data(r"{}\sSquad  Playing(.*?)Bench".format(self.names[team2]), data)[0].split(',')
            self.match['MatchInfo']['Players'] = {
                team1: [player.strip() for player in team1_players],
                team2: [player.strip() for player in team2_players]
            }

            # Extract Match Type
            if "ODI" in data:
                match_type = "ODI"
            elif "T20" in data or "Bash" in data or "IPL" in data or "Ford" in data:
                match_type = "T20"
            else:
                match_type = "Test"

            self.match['MatchInfo']['Format'] = match_type
            logger.info(f"Match info extracted: {self.match['MatchInfo']}")
        except Exception as e:
            logger.error(f"Error extracting match info: {e}")
            traceback.print_exc()

    def current_status(self):
        current_state = defaultdict(dict)
        classes = [value for element in self.score_dump.find_all(class_=True) for value in element["class"]]
        if 'cb-text-complete' in classes:
            result = self.score_dump.select('.cb-text-complete')
            status = 'complete'
        elif 'cb-text-inprogress' in classes:
            result = self.score_dump.select('.cb-text-inprogress')
            status = 'inprogress'
        elif 'cb-text-stumps' in classes:
            result = self.score_dump.select('.cb-text-stumps')
            status = 'stumps'
        else:
            result = 'N/A'
            status = 'N/A'

        try:
            current_state = {"Status": status, "Description": result[-1].getText()}
            self.match["MatchStatus"] = current_state
        except:
            current_state = {"Status": status, "Description": result}
            self.match["MatchStatus"] = current_state
        logger.info(f"Current match status: {self.match['MatchStatus']}")
        return current_state

    def get_player_scores(self):
        pass

    def get_current_scores(self):
        if self.match["MatchStatus"]["Status"] == "inprogress" or self.match["MatchStatus"]["Status"] == "stumps":
            data = self.score_dump.select('.cb-col .cb-col-100 .cb-col-scores')[0].getText()
            res = re.search(r'\b([A-Z]{2,4})(.*?)([A-Z]{2,4})(.*?)\)', data)
            scores = res.groups()
            current_state = {scores[0]: {"Score": scores[1]}, scores[2]: {"Score": scores[3]}}
            self.match["Scores"] = current_state
            logger.info(f"Current scores: {self.match['Scores']}")
        else:
            self.match["Scores"] = "Match not in Progress"
            logger.info("No scores, match not in progress.")

    def get_current_batsmen_scores(self):
        current_scores = defaultdict(dict)
        if self.match["MatchStatus"]["Status"] == "inprogress" or self.match["MatchStatus"]["Status"] == "stumps":
            data = self.score_dump.find("div", class_='cb-col-67 cb-col').find("div", class_='cb-min-inf cb-col-100').find_all("div", class_='cb-col cb-col-100 cb-min-itm-rw')
            for batsman in data: 
                info = []
                for div in batsman.find_all("div", class_="cb-col"):
                    info.append(div.text.strip())
                current_scores[info[0]] = {"Runs": info[1], "Balls": info[2], "4s": info[3], "6s": info[4]}
                self.match["CurrentBatsmanScore"] = current_scores
            logger.info(f"Current batsmen scores: {self.match['CurrentBatsmanScore']}")
        else:
            self.match["CurrentBatsmanScore"] = "Match not in Progress"
            logger.info("No batsmen scores, match not in progress.")
        return current_scores

    def print(self):
        try:
            j = json.dumps(self.match, indent=4)
            with open(os.path.join(self.PATH, "match_data.json"), 'w') as f:
                json.dump(self.match, f, indent=4)
            logger.info("Match data saved to match_data.json")
        except Exception as e:
            logger.error(f"Error saving match data to file: {e}")
            traceback.print_exc()
