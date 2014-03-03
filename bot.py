""" 
	WhoWouldWinBot identifies character names from the posts in the whowouldwin subreddit
	and posts appropriate links to provide character info.
	Author: Brian Jones
"""

import praw
import time
import sys
	
# Determines if "name" is a subsequence of the words in "title"
	
def is_subsequence(name, title):
	#Replaces all punctuation with spaces, and splits title into words
		
	title = title.replace(".", " ")
	title = title.replace(",", " ")
	title = title.replace("?", " ")
	title = title.replace("<", " ")
	title = title.replace(">", " ")
	title = title.replace("\'", " ")
	title_words = title.split(" ")
		
	temp_string = ""
		
	for i in range(0, len(title_words)):
		temp_string = ""
		for j in range(i, len(title_words)):
			if j != i:
				temp_string += " "
			temp_string += title_words[j]
				
			if temp_string == name:
				return True
					
	return False
	
# Compares two strings, omitting "the" and "The"
# e.g. compare_without_the("Flash", "The Flash") returns true
	
def compare_without_the(s1, s2):
	if "The " in s1:
		s1 = s1.replace("The ", '')
	if "the " in s1:
		s1 = s1.replace("the ", '')
		
	if "The " in s2:
		s2 = s2.replace("The ", '')
	if "the " in s2:
		s2 = s2.replace("the ", '')
	
	if s1 == s2:
		return True
	else:
		return False

# Each character has a name and list of links
		
class Character:
	def __init__(self):
		self.name = "Default Name"
		self.links = []
		
	def display(self):
		print "Name: " + self.name
		print "Links: "
		for link in self.links:
			print link

# Bot class includes all methods needed for bot to run
			
class Bot:
	r = praw.Reddit("WhoWouldWin Info Bot")
	subreddit = r.get_subreddit("whowouldwin")

	def __init__(self, password):
		self.found_characters = []
		self.password = password
		
	def login(self, name, password):
		self.r.login(name, password)
		
	# Posts reply after searching titles
		
	def make_post(self, post):
		comment_text = ""
		for char in self.found_characters:
			comment_text += "**" + char.name + "**\n\n"
			for link in char.links:
				comment_text += link + "\n\n"
			comment_text += "---\n\n"
			
		comment_text += "Was this bot helpful? Please leave a reply, or message /u/BJ2094 [Here](http://www.reddit.com/message/compose/?to=BJ2094)\n\n"
		comment_text += "[Source Code](https://github.com/bjones2094/WhoWouldWinBot)"
			
		post.add_comment(comment_text)
		
	# Posts a reply to comment calling bot when character is found
		
	def make_success_reply(self, comment):
		comment_text = ""
		for char in self.found_characters:
			comment_text += "**" + char.name + "**\n\n"
			for link in char.links:
				comment_text += link + "\n\n"
			comment_text += "---\n\n"
			
		comment_text += "Hey, I can read comments now! Was this bot helpful? Please leave a reply, or message /u/BJ2094 [Here](http://www.reddit.com/message/compose/?to=BJ2094)\n\n"
		comment_text += "[Source Code](https://github.com/bjones2094/WhoWouldWinBot)"
			
		comment.reply(comment_text)
		
	# Posts a reply to comment calling bot when character is not found
		
	def make_negative_reply(self, comment):
		comment.reply("Sorry, I couldn't find the character(s) you were looking for. I have failed you :(")
		
	# Searches titles using is_subsequence method
		
	def search_titles(self, posts):
		used_ids = open("used_post_ids.txt", 'r').read()	# Uses used_post_ids.txt to store and check used post ids so as not to reply to the same post twice
		id_output = open("used_post_ids.txt", 'a')
		
		for post in posts:
			self.found_characters = []
			post_title = post.title.encode('utf-8')
			
			if post.id not in used_ids:		# Checks the used post ids
				id_output.write(post.id + ' ' + post_title + '\n')
				
				self.find_wiki_links(post_title)
				self.find_OBD_links(post_title)
				
				if len(self.found_characters) > 0:
					print "Title: " + post_title
					self.display_characters()
					self.make_post(post)
			
		id_output.close()
		
	# Searches comments using is_subsequence method
		
	def search_comments(self, posts):
		used_ids = open("used_comment_ids.txt", 'r').read()		# Uses used_comment_ids.txt to store and check used comment ids so as not to reply to the same comment twice
		id_output = open("used_comment_ids.txt", 'a')
		
		prompt1 = "/u/whowouldwinbot who is"
		prompt2 = "/u/WhoWouldWinBot who is"
		prompt3 = "/u/whowouldwinbot, who is"
		prompt4 = "/u/WhoWouldWinBot, who is"
		
		for post in posts:
			post_title = post.title.encode('utf-8')
			
			print "Searching comments in " + post_title
			
			post.replace_more_comments(limit = None, threshold = 1)
			comments = praw.helpers.flatten_tree(post.comments)
			for comment in comments:
				self.found_characters = []
				
				if comment.id not in used_ids:
					id_output.write(comment.id + ' ' + post_title + '\n')
					
					if prompt1 in comment.body or prompt2 in comment.body or prompt3 in comment.body or prompt4 in comment.body:
						begin = comment.body.find("who is") + 7
						end = comment.body.find("?", begin)
						if end == -1:
							end == len(comment.body)
						character_name = comment.body[begin:end]
						
						self.find_wiki_links(character_name)
						self.find_OBD_links(character_name)
						
						if len(self.found_characters) > 0:
							self.make_success_reply(comment)
							print "Success Comment Posted!\n"
						else:
							self.make_negative_reply(comment)
							print "Failure Comment Posted :(\n"
							
		id_output.close()
		
	# Run method does all of the bot's searching and posting
		
	def run(self):
		self.login("WhoWouldWinBot", self.password)
		
		new_posts = self.subreddit.get_new(limit = 10)
		
		self.search_titles(new_posts)
		
		hot_posts = self.subreddit.get_hot(limit = 10)
		new_posts = self.subreddit.get_new(limit = 25)
			
		print "Searching new posts\n"
		self.search_comments(new_posts)
		print "Searching hot posts\n"
		self.search_comments(hot_posts)
	
	# Finds links from wiki sites and appends them to found characters list
	
	def find_wiki_links(self, title):
		for i in range(0, 4):
			if i == 0:
				filename = "links/DC_Wiki_links.txt"
				link_prefix = "http://www.dc.wikia.com/wiki/"
			elif i == 1:
				filename = "links/Marvel_Wiki_links.txt"
				link_prefix = "http://www.marvel.wikia.com/wiki/"
			elif i == 2:
				filename = "links/DBZ_Wiki_links.txt"
				link_prefix = "http://www.dragonball.wikia.com/wiki/"
			elif i == 3:
				filename = "links/Starwars_Wiki_links.txt"
				link_prefix = "http://www.starwars.wikia.com/wiki/"
			else:
				print "This shouldn't happen"
				
			links = open(filename, 'r')
					
			for line in links:
				name = line[0:len(line) - 1]
				name = name.replace("_", " ")
				
				if is_subsequence(name, title):
					new_character = Character()
					new_character.name = name
					new_character.links.append(link_prefix + line)
					
					name_is_found = False
				
					for found_char in self.found_characters:
						if name == found_char.name:
							found_char.links.append(link_prefix + line)
							name_is_found = True
							break
						elif compare_without_the(name, found_char.name):
							found_char.links.append(link_prefix + line)
							name_is_found = True
							break
						elif is_subsequence(name, found_char.name):
							name_is_found = True
							break
						elif is_subsequence(found_char.name, name):
							self.found_characters.remove(found_char)
							name_is_found = False
							break
						else:
							name_is_found = False
					
					if not name_is_found:
						self.found_characters.append(new_character)
		
	# Finds links from OBD and appends them to found characters list
		
	def find_OBD_links(self, title):
		for i in range(0, 4):
			if i == 0:
				filename = "links/AE_links.txt"
			elif i == 1:
				filename = "links/FK_links.txt"
			elif i == 2:
				filename = "links/LQ_links.txt"
			elif i == 3:
				filename = "links/RZ_links.txt"
			else:
				print "This shouldn't happen"
				
			links = open(filename, 'r')
				
			for line in links:
				begin = line.find("-") + 2
				temp_name = line[begin:len(line) - 1]
					
				name = temp_name.replace("+", " ")
				name = name.replace("-", " ")
				name = name.replace("%", " ")
				
				if is_subsequence(name, title):
					new_character = Character()
					new_character.name = name
					new_character.links.append(line)
					
					name_is_found = False
				
					for found_char in self.found_characters:
						if name == found_char.name:
							found_char.links.append(line)
							name_is_found = True
							break
						elif compare_without_the(name, found_char.name):
							found_char.links.append(line)
							name_is_found = True
							break
						elif is_subsequence(name, found_char.name):
							name_is_found = True
							break
						elif is_subsequence(found_char.name, name):
							self.found_characters.remove(found_char)
							name_is_found = False
							break
						else:
							name_is_found = False
					
					if not name_is_found:
						self.found_characters.append(new_character)
		
	# Displays characters bot finds (used mostly in testing)
		
	def display_characters(self):
		for char in self.found_characters:
			char.display()
	
bot = Bot(sys.argv[1])	# Bot password must be passed as first parameter

count = 0

while True:
	bot.run()
	count += 1
	print "Sleeping..."
	time.sleep(300)