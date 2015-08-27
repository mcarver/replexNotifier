import json, time, urllib2
from xml.etree import ElementTree

#misc
version = "v0.1"
L = None #last loop

print "\nReplex Notifier "+version+"\n"

#read config file
with open('config.json') as config_file:
	config = json.load(config_file)

#check config file
if (
	'serverIp' not in config or
	'serverPort' not in config or
	'pushbulletAccessToken' not in config or
	'checkInterval' not in config
	):
	print "ERROR: Configurations are missing in config.json"
	exit()
if config["serverIp"] == "<Plex Server IP>":
	print "ERROR: Please set your Plex Server IP in the config.json file."
	exit()
if config["pushbulletAccessToken"] == "<Pushbullet Access Token>":
	print "ERROR: Please set your PushBullet access token in the config.json file."
	exit()
if 'notifyOnPlay' not in config: config['notifyOnPlay'] = True
if 'notifyOnStop' not in config: config['notifyOnStop'] = False
if config['notifyOnPlay'] is False and config['notifyOnStop'] is False:
	print "ERROR: No notifications are active in config.json...  Exitting."
	exit()

#list comparison function
def compare(a, b):
	return sorted(a) == sorted(b)

#push function
def push(session):
	if session["videoGrandparentTitle"] is None:
		#movie
		if session["playerState"] == "playing":
			pushText = "%s started %s %s on %s" % (
				session["userTitle"], session["playerState"], session["videoTitle"], session["playerTitle"])
		else:
			pushText = "%s %s %s on %s" % (
				session["userTitle"], session["playerState"], session["videoTitle"], session["playerTitle"])
	else:
		#tv
		if session["playerState"] == "playing":
			pushText = "%s started %s %s - %s on %s" % (
				session["userTitle"], session["playerState"], session["videoGrandparentTitle"], session["videoTitle"], session["playerTitle"])
		else:
			pushText = "%s %s %s - %s on %s" % (
				session["userTitle"], session["playerState"], session["videoGrandparentTitle"], session["videoTitle"], session["playerTitle"])

	push = {}
	push['type'] = "note"
	push['title'] = "Replex - Activity"
	push['body'] = pushText

	print pushText

	req = urllib2.Request('https://api.pushbullet.com/v2/pushes')
	req.add_header('Content-Type', 'application/json')
	req.add_header('Access-Token',config["pushbulletAccessToken"])
	resp = urllib2.urlopen(req, json.dumps(push))

#main loop
print "Listening for sessions..."
while True:
	#get sessions xml
	try:
		response = urllib2.urlopen("http://%s:%d/status/sessions" % (
			config["serverIp"], config["serverPort"]))
	except urllib2.URLError, e:
		print "ERROR: Could not contact Plex server at: "+config["serverIp"]+". Retrying in 60 seconds."
		L = None
		time.sleep(60)
		continue

	tree = ElementTree.parse(response)
	videos = tree.findall("Video")

	C = list() #current loop

	#parse the xml
	for video in videos:
		session = {}
		user = video.find("User")
		player = video.find("Player")
		transcodeSession = video.find("TranscodeSession")

		#values
		session["videoGrandparentTitle"] = video.get("grandparentTitle")
		session["videoTitle"] = video.get("title")
		session["userTitle"] = user.get("title") if len(user) > 0 else "Unknown"
		session["playerState"] = player.get("state")
		session["playerTitle"] = player.get("title")

		C.append(session)

	#if current and last sessions are different
	if L is not None and compare(C, L) is False:
		#get the new sessions
		N = [item for item in C if item not in L]
		for session in N:
			if session["playerState"] == "playing":
				tempSession = dict(session)
				tempSession["playerState"] = "paused"
				if tempSession not in L:
					if config["notifyOnPlay"] is True: push(session)
		#get the old sessions
		O = [item for item in L if item not in C]
		for session in O[:]:
			if session["playerState"] == "playing" or session["playerState"] == "paused":
				tempSession = dict(session)
				tempSession["playerState"] = "playing"
				if tempSession not in C:
					tempSession["playerState"] = "paused"
					if tempSession not in C:
						session["playerState"] = "stopped"
						if config["notifyOnStop"] is True: push(session)

	#make a copy of the current sessions
	L = list(C);

	time.sleep(config["checkInterval"])
