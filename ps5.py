# 6.00 Problem Set 5
# RSS Feed Filter

import feedparser
import string
import time
from project_util import translate_html
from news_gui import Popup

#-----------------------------------------------------------------------
#
# Problem Set 5

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        summary = translate_html(entry.summary)
        try:
            subject = translate_html(entry.tags[0]['term'])
        except AttributeError:
            subject = ""
        newsStory = NewsStory(guid, title, subject, summary, link)
        ret.append(newsStory)
    return ret

#======================
# Part 1
# Data structure design
#======================

# Problem 1

# TODO: NewsStory

class NewsStory(object):
    def __init__(self, guid, title, subject, summary, link):
        self.guid = guid
        self.title = title
        self.subject = subject
        self.summary = summary
        self.link = link

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_subject(self):
        return self.subject

    def get_summary(self):
        return self.summary

    def get_link(self):
        return self.link

#======================
# Part 2
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError

# Whole Word Triggers
# Problems 2-5

# TODO: WordTrigger

class WordTrigger(Trigger):
    ##looking ahead to "Phrase Triggers" shows that what i built WordTrigger out beyond spec
    ##(or not to spec) -- is_word_in shouldn't work for 'New York City' or any "word" with a space in it
    
    def find_start_indices(self, text, word):
        """
        Outputs a list with the starting indices of all the instances of word in string -- this is to cover cases like "Microsoft is soft," which, if you look at
        just the first instance of soft, you're going to return false for is_word_in. Doesn't assume that string or word is uncapitalized
        """
        locIndices = []
        endOfLastWord = 0
        while (True):
            try:
                index = text.index(word, endOfLastWord)
                locIndices.append(index)
                endOfLastWord = index + 1 ##if add len(word), doesn't cover scenarios like finding all the "woowoo"s in "woowoowoowoowoo"
            except ValueError: ## gets raised when index method doesn't find word
                break
        return locIndices
            
    def is_word_in(self, text, word):
        """
        Returns True if word is in string -- e.g. "soft" in, "That dude is soft." or "Soft, that dude is." but not "Microsoft was founded by Bill Gates."
        """
        import string
        text = text.lower()
        word = word.lower()
        locIndices = self.find_start_indices(text, word)
        for i in locIndices:
            if (i == 0) or (text[i - 1] in string.punctuation) or (text[i - 1] == " "):
                if (i + len(word) == len(text)) or (text[i + len(word)] in string.punctuation) or (text[i + len(word)] == " "):
                    return True
        return False
        

# TODO: TitleTrigger

class TitleTrigger(WordTrigger):
    """
    takes a string as an input
    """
    def __init__(self, word):
        self.word = word
    def evaluate(self, story):
        return self.is_word_in(story.get_title(), self.word)
        


# TODO: SubjectTrigger

class SubjectTrigger(WordTrigger):
    def __init__(self, word):
        self.word = word
    def evaluate(self, story):
        return self.is_word_in(story.get_subject(), self.word)
    
# TODO: SummaryTrigger

class SummaryTrigger(WordTrigger):
    def __init__(self, word):
        self.word = word
    def evaluate(self, story):
        return self.is_word_in(story.get_summary(), self.word)


# Composite Triggers
# Problems 6-8

# TODO: NotTrigger

class NotTrigger(Trigger):
    def __init__(self, triggerOne):
        self.triggerOne = triggerOne
    def evaluate(self, story):
        return not(self.triggerOne.evaluate(story))
    
# TODO: AndTrigger

class AndTrigger(Trigger):
    def __init__(self, triggerOne, triggerTwo):
        self.triggerOne = triggerOne
        self.triggerTwo = triggerTwo
    def evaluate(self, story):
        return self.triggerOne.evaluate(story) and self.triggerTwo.evaluate(story)
    
# TODO: OrTrigger

class OrTrigger(Trigger):
    def __init__(self, triggerOne, triggerTwo):
        self.triggerOne = triggerOne
        self.triggerTwo = triggerTwo
    def evaluate(self, story):
        return self.triggerOne.evaluate(story) or self.triggerTwo.evaluate(story)
# Phrase Trigger
# Question 9

# TODO: PhraseTrigger

class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        self.phrase = phrase
    def evaluate(self, story):
        return (
             (self.phrase in story.get_subject()) or
             (self.phrase in story.get_title()) or
             (self.phrase in story.get_summary())
             )


#======================
# Part 3
# Filtering
#======================

def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory-s.
    Returns only those stories for whom
    a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    filteredStories = []
    for i in stories:
        for j in triggerlist:
            if j.evaluate(i):
                filteredStories.append(i)
                break
    return stories

#======================
# Part 4
# User-Specified Triggers
#======================

def findWords(lines):
    """
    Returns a list of lists of distinct words (distinct = separated by a space)
    when the input is a list of strings -- not to be used outside this program.
    Assumes for simplicity that no one is going to put in a space at the beginning
    of the line or put two spaces in a row
    """
    linelist = []
    for l in lines:
        wordlist = []
        currentword = ""
        for c in l:
            if len(wordlist) > 1:
                if wordlist[1] == "PHRASE":
                    x = l.find('PHRASE') + len('PHRASE') + 1
                    wordlist.append(l[x:])
                    break
            if c == " ":
                wordlist.append(currentword)
                currentword = ""
            else:
                currentword += c
        if len(currentword) > 0:
            wordlist.append(currentword)
        linelist.append(wordlist)
    return linelist
                
                
             
def readTriggerConfig(filename):
    """
    Returns a list of trigger objects
    that correspond to the rules set
    in the file filename
    """
    # Here's some code that we give you
    # to read in the file and eliminate
    # blank lines and comments
    triggerfile = open(filename, "r")
    all = [ line.rstrip() for line in triggerfile.readlines() ]
    lines = []
    for line in all:
        if len(line) == 0 or line[0] == '#':
            continue
        lines.append(line)
    ##start of my code
    trigdict = dict([('TITLE',TitleTrigger),('PHRASE', PhraseTrigger),
                     ('SUBJECT', SubjectTrigger), ('NOT', NotTrigger),
                     ('SUMMARY', SummaryTrigger), ('AND', AndTrigger),
                     ('OR', OrTrigger)])
    userdict = dict()
    anslist = []             
    linelist = findWords(lines)
    for i in linelist:
        if i[0] == 'ADD':
            try:
                for t in i[1:]:
                    anslist.append(userdict[t])
            except KeyError:
                break
        elif i[1] in ('OR', 'AND'):
            try:
                userdict[i[0]] = trigdict[i[1]](userdict[i[2]],userdict[i[3]])
            except KeyError:
                break
        else:
            userdict[i[0]] = trigdict[i[1]](i[2])
    return anslist


def testConfigImp(lines):
    trigdict = dict([('TITLE',TitleTrigger),('PHRASE', PhraseTrigger),
                     ('SUBJECT', SubjectTrigger), ('NOT', NotTrigger),
                     ('SUMMARY', SummaryTrigger), ('AND', AndTrigger),
                     ('OR', OrTrigger)])
    userdict = dict()
    anslist = []             
    linelist = findWords(lines)
    for i in linelist:
        if i[0] == 'ADD':
            try:
                for t in i[1:]:
                    anslist.append(userdict[t])
            except KeyError:
                break
        elif i[1] in ('OR', 'AND'):
            try:
                userdict[i[0]] = trigdict[i[1]](userdict[i[2]],userdict[i[3]])
            except KeyError:
                break
        else:
            userdict[i[0]] = trigdict[i[1]](i[2])
    return anslist
            
def testConfig():
    lines = ["t1 SUBJECT world", "b TITLE Intel", "c PHRASE New York City", "ADD b c"]
    return testConfigImp(lines)
    
    

    # TODO: Problem 11
    # 'lines' has a list of lines you need to parse
    # Build a set of triggers from it and
    # return the appropriate ones
    
import thread

##def main_thread(p):
##    # A sample trigger list - you'll replace
##    # this with something more configurable in Problem 11
##    #t1 = SubjectTrigger("Obama")
##    #t2 = SummaryTrigger("MIT")
##    #t3 = PhraseTrigger("Supreme Court")
##    #t4 = OrTrigger(t2, t3)
##    #triggerlist = [t1, t4]
##    
##    # TODO: Problem 11
##    # After implementing readTriggerConfig, uncomment this line 
##    triggerlist = readTriggerConfig("triggers.txt")
##
##    guidShown = []
##    
##    while True:
##        print "Polling..."
##
##        # Get stories from Google's Top Stories RSS news feed
##        stories = process("http://news.google.com/?output=rss")
##        # Get stories from Yahoo's Top Stories RSS news feed
##        stories.extend(process("http://rss.news.yahoo.com/rss/topstories"))
##
##        # Only select stories we're interested in
##        stories = filter_stories(stories, triggerlist)
##    
##        # Don't print a story if we have already printed it before
##        newstories = []
##        for story in stories:
##            if story.get_guid() not in guidShown:
##                newstories.append(story)
##        
##        for story in newstories:
##            guidShown.append(story.get_guid())
##            p.newWindow(story)
##
##        print "Sleeping..."
##        time.sleep(SLEEPTIME)
##
##SLEEPTIME = 60 #seconds -- how often we poll
##if __name__ == '__main__':
##    p = Popup()
##    thread.start_new_thread(main_thread, (p,))
##    p.start()
##
##
