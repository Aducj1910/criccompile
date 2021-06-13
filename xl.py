import accessDB, convertoxl

def viaDB (data, file, matchTracker, infoRows, update):
	accessDB.addRow(data, 'redoT20', infoRows)

	if(not update):
		accessDB.addNewMatch(file, matchTracker)
	
