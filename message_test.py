import praw

r = praw.Reddit("bot message test")
r.login("WhoWouldWinBot", "Reaper29")

messages = list(r.get_inbox(limit=1))

for message in messages:
	if message.author.name == "BJ2094":
		print "hey"