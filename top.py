import intlSuper, super

_type = "T20"
update = True

if(_type == "ODI"):
	intlSuper.main('https://stats.espncricinfo.com/ci/content/records/307851.html', 'matchTrackerODI', 'infoRowsODI', {'matchType': "ODI", "overs": 50}, update)

if(_type == "Test"):
	intlSuper.main('https://stats.espncricinfo.com/ci/content/records/307847.html', 'matchTrackerTest', 'infoRowsTest', {'matchType': "Test", "overs": "unlimited"}, update)

if(_type == "T20i"):
	intlSuper.main('https://stats.espncricinfo.com/ci/content/records/307852.html', 'matchTracker', 'infoRows', {'matchType': "T20", "overs": 20}, update)

if(_type == "BBL"):
	super.main('https://stats.espncricinfo.com/ci/engine/records/team/match_results_season.html?id=158;type=trophy', 'matchTrackerBBL', 'infoRowsBBL', {'matchType': 'T20', 'overs': 20}, update)
