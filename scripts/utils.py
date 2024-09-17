
import firebase_admin
from firebase_admin import credentials, db
from logger_config import logger

# Set up logger
# logger.basicConfig(
#     filename='firebase_operations.log',  # Log to a file
#     level=logger.INFO,                  # Set log level to INFO
#     format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
# )

# cred = credentials.Certificate('/home/ubuntu/dexter/wakemeup-server/wakemeup-firebase-key.json')
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://wakemeup-82e70-default-rtdb.firebaseio.com'
# })

def upload_to_firebase(data, title):
    # Initialize Firebase
    ref = db.reference(f'OngoingMatchesList/{title}')

    # Clear existing matches (optional)
    ref.set({})

    ref.set(data)
    logger.info(f"Uploaded match data for: {title}")

def upload_current_batsman_score_to_firebase(match, data):
    # Initialize Firebase
    ref = db.reference(f'OngoingMatchesList/{match}/MatchData/CurrentBatsmanScore')

    # Retrieve current match status from Firebase
    current_data = ref.get()

    for key,curr_data in current_data.items():
        if curr_data != data[key]:
            curr_ref=db.reference(f'OngoingMatchesList/{match}/MatchData/CurrentBatsmanScore/{key}')
            curr_ref.set(data[key])
            logger.info(f"Updated score for: {key}")
        else:
            logger.info(f"No changes in score for: {key}, skipping update.")

def upload_match_status_to_firebase(match, data):
    # Initialize Firebase reference
    ref = db.reference(f'OngoingMatchesList/{match}/MatchData/MatchStatus')

    # Retrieve current match status from Firebase
    current_data = ref.get()

    for key,curr_data in current_data.items():
        if curr_data != data[key]:
            curr_ref=db.reference(f'OngoingMatchesList/{match}/MatchData/MatchStatus/{key}')
            curr_ref.set(data[key])
            logger.info(f"Updated match status for: {key}")
        else:
            logger.info(f"No changes in match status for: {match}, skipping update.")


def fetch_from_firebase():
    # Initialize Firebase if not already initialized
    ref = db.reference('OngoingMatchesList')
    matches = ref.get()
    titles = []
    if matches:
        for title, data in matches.items():
            titles.append(title)
    logger.info("Fetched matches from Firebase")
    return titles

def delete_match_from_firebase(match):
    ref = db.reference(f'OngoingMatchesList/{match}')
    ref.delete()
    logger.info(f"Match {match} has been removed from Firebase.")


def delete_alerts_from_firebase(match):
    logger.info(f"Deleting alerts for completed matches")
    count=0
    ref = db.reference(f'alerts')
    alerts=ref.get()
    if alerts:
        for user_id, user_alerts in alerts.items():
            for alert_key, each_alert in user_alerts.items():
                match_title = each_alert.get('matchTitle')
                if match_title == match:
                    del_ref = db.reference(f'alerts/{user_id}/{alert_key}')
                    del_ref.delete()
                    count+=1
                    continue
    logger.info(f"Found {count} alerts from previous matches and deleted.")



