import firebase_admin
from firebase_admin import credentials, db, messaging
from logger_config import logger  # Import centralized logger

class AlertService:
    def __init__(self, firebase_key_path, database_url):
        # Initialize Firebase Admin SDK
        # cred = credentials.Certificate(firebase_key_path)
        # firebase_admin.initialize_app(cred, {
        #     'databaseURL': database_url
        # })
        self.score_buffer = 3  # Buffer for score alerts
        self.score_reached = False

    # Main logic to check alerts and send notifications
    def check_alerts(self):
        ref = db.reference('alerts')
        alerts = ref.get()
        match_ref = db.reference('OngoingMatchesList')
        matches = match_ref.get()

        if not alerts or not matches:
            logger.info('No alerts or matches to process')
            return

        for user_id, user_alerts in alerts.items():
            for alert_key, each_alert in user_alerts.items():
                logger.info(f"Processing alert {alert_key} for user {user_id}")
                match_title = each_alert.get('matchTitle')
                team = each_alert.get('team')
                player = each_alert.get('player').split('(')[0].strip()
                score = int(each_alert.get('score'))

                match_data = matches.get(match_title)
                if match_data:
                    player_data = match_data['MatchData']['CurrentBatsmanScore'].get(player)
                    if player_data and int(player_data['Runs']) + self.score_buffer >= score:
                        if score >= int(player_data['Runs']):
                            self.score_reached = True
                        else:
                            self.score_reached = False
                        logger.info(f'Alert triggered for user {user_id} - Player {player} scored {score} runs')
                        self.send_notification_with_data(user_id, each_alert)

                        # Remove the alert after it's triggered
                        self.remove_alert(user_id, alert_key)

    # Function to send data notification
    def send_notification_with_data(self, user_id, alert):
        # Retrieve the user's FCM token from the database
        token_ref = db.reference(f'users/{user_id}/token')
        token = token_ref.get()

        if token:
            if self.score_reached:
                body = f'{alert["player"]} has scored {alert["score"]} runs!'
            else:
                body = f'{alert["player"]} is nearing {alert["score"]} runs!'

            message = messaging.Message(
                data={
                    'title': 'Score Alert!',
                    'body': body,
                    'trigger_alarm': 'true'  # Custom data to trigger the alarm
                },
                token=token
            )
            try:
                response = messaging.send(message)
                logger.info(f'Successfully sent message: {response}')
            except Exception as e:
                logger.error(f'Failed to send message: {e}')
        else:
            logger.warning(f'No token found for user {user_id}')

    # Function to send notification without data (optional)
    def send_notification(self, user_id, alert):
        # Retrieve the user's FCM token from the database
        token_ref = db.reference(f'users/{user_id}/token')
        token = token_ref.get()

        if token:
            message = messaging.Message(
                notification=messaging.Notification(
                    title='Score Alert!',
                    body=f'{alert["player"]} has scored {alert["score"]} runs!'
                ),
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        channel_id='high_importance_channel'  # Replace with your actual channel ID
                    )
                ),
                token=token
            )
            try:
                response = messaging.send(message)
                logger.info(f'Successfully sent message: {response}')
            except Exception as e:
                logger.error(f'Failed to send message: {e}')
        else:
            logger.warning(f'No token found for user {user_id}')

    # Function to remove alert from Firebase
    def remove_alert(self, user_id, alert_key):
        """Remove the alert from Firebase after it has been triggered."""
        alert_ref = db.reference(f'alerts/{user_id}/{alert_key}')
        try:
            alert_ref.delete()
            logger.info(f'Removed alert {alert_key} for user {user_id}')
        except Exception as e:
            logger.error(f'Failed to remove alert {alert_key} for user {user_id}: {e}')

# Entry point for script execution
if __name__ == '__main__':
    # Initialize the AlertService
    firebase_key_path = 'firebasekey.json'
    database_url = 'https://wakemeup-82e70-default-rtdb.firebaseio.com/'
    alert_service = AlertService(firebase_key_path, database_url)

    # Call the check_alerts method to process alerts
    alert_service.check_alerts()
