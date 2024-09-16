from wakemeup import MatchData

PATH="/home/ubuntu/dexter/wakemeup-server/data/"
url="https://www.cricbuzz.com/live-cricket-scores/94514/indw-vs-rsaw-one-off-test-south-africa-women-tour-of-india-2024"
m=MatchData(url,PATH)			
m.get_match_info()
m.current_status()
m.get_current_batsmen_scores()
m.print()