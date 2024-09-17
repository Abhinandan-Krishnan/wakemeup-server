from wakemeup import MatchData
from get_match_list import GetMatchList
import requests
from bs4 import BeautifulSoup
from utils import *
from logger_config import logger
from alert_service import AlertService

# Initialize AlertService
firebase_key_path = '/home/ubuntu/dexter/wakemeup-server/scripts/firebasekey.json'
database_url = 'https://wakemeup-82e70-default-rtdb.firebaseio.com/'


cred = credentials.Certificate('/home/ubuntu/dexter/wakemeup-server/wakemeup-firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://wakemeup-82e70-default-rtdb.firebaseio.com'
})

if __name__ == "__main__":
    PATH = "/home/ubuntu/dexter/wakemeup-server/data/"
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    uploaded = False
    existing_matches = fetch_from_firebase()
    match_list_fetcher = GetMatchList(url)
    alert_service = AlertService(firebase_key_path, database_url)

    ongoing_matches = match_list_fetcher.get_matches()
    current_matches = list(ongoing_matches.keys())
    logger.info(f"Current matches fetched: {current_matches}")

    for match in ongoing_matches.keys():
        logger.info(f"Extracting info for: {match}")
        m = MatchData(ongoing_matches[match]['link'], PATH)
        m.get_match_info()
        current_state = m.current_status()
        batsmen_score = m.get_current_batsmen_scores()

        if m.match["MatchStatus"]["Status"] == 'complete' or m.match["MatchStatus"]["Status"] == 'N/A':
            logger.info(f"Skipping match {match} as it is complete or status is N/A")
            continue

        ongoing_matches[match]['MatchData'] = m.match

        if match in existing_matches:
            existing_matches.remove(match)
            logger.info(f"Updating existing match {match} in Firebase")
            upload_current_batsman_score_to_firebase(match, batsmen_score)
            upload_match_status_to_firebase(match, current_state)
        else:
            logger.info(f"Uploading new match {match} to Firebase")
            upload_to_firebase(ongoing_matches[match], match)

    if existing_matches:
        logger.info(f"Removing old entries from Firebase: {existing_matches}")
        for match in existing_matches:
            delete_match_from_firebase(match)
            delete_alerts_from_firebase(match)

    alert_service.check_alerts()