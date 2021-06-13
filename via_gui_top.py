import intlSuper

def main(_type):
	update = True

	if(_type == "odi"):
		return intlSuper.main('https://stats.espncricinfo.com/ci/content/records/307851.html', 'matchTrackerODI', 'infoRowsODI', {'matchType': "ODI", "overs": 50}, update, _type)

	if(_type == "test"):
		return intlSuper.main('https://stats.espncricinfo.com/ci/content/records/307847.html', 'matchTrackerTest', 'infoRowsTest', {'matchType': "Test", "overs": "unlimited"}, update, _type)

	if(_type == "t20"):
		return intlSuper.main('https://stats.espncricinfo.com/ci/content/records/307852.html', 'matchTracker', 'infoRows', {'matchType': "T20", "overs": 20}, update, _type)