""" Hold and manage all kinds of messages to the user, 
with levels of importance, flexible formatting, etc.
Usage via class MessageCue
"""
import os
import datetime
import time
import colorizer
from colorizer import FancyObject as fcy


class MessageCue():
    def __init__(self, maxLength=500):
        self.cue = []
        self.maxLength = maxLength
        
    def add(self, content, level, pause=False):
        """ Pause: Whether to pause and wait for acknowledgement
        when outputting the message
        Levels(In ascending order of chatty-ness):
        Error, Warning, Status, Verbose, Debug
        (0)     (1)     (2)     (3)     (4)
        """
        self.cue.append(Message(content, level, pause))
        if len(self.cue) > self.maxLength:
            self.cue.pop(0)
        
    def print_window(self, outerWidth, outerHeight, border='', 
                     levelFormat='long', printTime=True, printLevel='Debug'):
        """ levelFormat either 'short' for number, 'long' for word or
        False for not at all
        """
        levels = {'Error'   :   0,
                  'Warning' :   1,
                  'Status'  :   2,
                  'Verbose' :   3,
                  'Debug'   :   4,
                  }
        levelsReversed = {}
        # Automatically populate levelsReversed
        for item in levels.items():
            levelsReversed.setdefault(item[1], item[0])
        
        # Determine space on inside
        if border != '':
            innerHeight = outerHeight - 2
            innerWidth = outerWidth
            print(outerWidth * border)
        else:
            innerHeight = outerHeight
            innerWidth = outerWidth
        # cue shorter than height of message window?
        #  skip some lines so it aligns with bottom
        if len(self.cue) < innerHeight:
            difference = innerHeight - len(self.cue)
            print(difference * '\n', end='')
            index = len(self.cue)
        else:
            index = innerHeight
        # The index tells how many messages will fit
        # Traverse list in reverse, 
        #  append only entries w/ low enough lvl
        outCue = []
        reverseDummy = self.cue.copy()
        reverseDummy.reverse()
        for msg in reverseDummy:
            if msg.level <= levels[printLevel]:
                outCue.append(msg)
                index -= 1
            if index == 0:
                break
        # Finally, print the now-filtered messages
        outCue.reverse()
        for msg in outCue:
            msg.out(innerWidth, levelFormat, printTime)
            print()
        # Lower border
        if border != '':
            print(outerWidth * border)
        


class Message():
    levels = {'Error'   :   0,
              'Warning' :   1,
              'Status'  :   2,
              'Verbose' :   3,
              'Debug'   :   4,
              }
    levelsReversed = {}
    # Automatically populate levelsReversed
    for item in levels.items():
        levelsReversed.setdefault(item[1], item[0])

    def __init__(self, content, level, pause):
        self.content = content
        self.level = self.levels[level.capitalize()]
        self.pause = pause
        self.timeStamp = datetime.datetime.now().ctime()[11:19]
        
    def out(self, maxLength, levelFormat, printTime):
        def snip_string(content, targetLength):
            sign = '[...]'
            overhang = len(content) + len(sign) - targetLength
            # Split into two halves, add sign in middle
            split = [content[:int(len(content)/2)],
                     sign,
                     content[int(len(content)/2):]]
            # Start snipping
            #  Alternates popping from right and left
            #   (1) this is kind of a crude way to do it
            i = 1
            while overhang > 0:
                # Always pop from right half first,
                #  this is expected to be longer if uneven,
                #   and less important even if not
                if i % 2 != 0:
                    split[2] = split[2][1:]
                else:
                    split[0] = split[0][:-1]
                overhang -= 1
                i += 1
            return split[0] + split[1] + split[2]
        # Build a string for the level
        if levelFormat:
            levelFormat = levelFormat.lower()
            if levelFormat == 'short':
                levelString = f'{self.level}'
            elif levelFormat == 'long':
                levelString = f'{self.levelsReversed[self.level]}'
            # Colorize level string, add brackets
            match self.levelsReversed[self.level]:
                case 'Error':
                    levelString = fcy(levelString, colorizer.color.red,
                                      colorizer.effects.bold,
                                      colorizer.effects.underline)
                case 'Warning':
                    levelString = fcy(levelString, colorizer.color.red)
                case 'Debug':
                    levelString = fcy(levelString, colorizer.color.brightGreen)
            levelString = f'[{levelString}]'
        else:
            levelString = ''
        # Build a string for the timestamp
        if printTime:
            timeString = f'|{self.timeStamp}'
        else:
            timeString = ''
        # Does message length exceed allotted space?
        maxMessageLength = maxLength - len(levelString) - len(timeString)
        if len(self.content) <= maxMessageLength:
            print(levelString + self.content + timeString, end='')
        else:
            shortenedContent = snip_string(self.content, maxMessageLength)
            print(levelString + shortenedContent + timeString, end='')
        # Pause until user hits return if supposed to
        if self.pause:
            self.pause = False # Mark as read
            input('...')
            # Gets rid of the automatic newline
            CURSOR_UP_ONE = '\x1b[1A'
            print(CURSOR_UP_ONE, end='')
        


        
        




def test():
    baseSpeed = 1
    
    
    os.system('clear')
    msgCue = MessageCue()
    
    test_fill(msgCue, border='*', speed=baseSpeed)
    time.sleep(2)
    os.system('clear')
    msgCue = MessageCue()
    test_fill(msgCue, border='',speed=baseSpeed)
    
    time.sleep(5)
    test_level_and_time_formatting(msgCue, border='*',speed=baseSpeed)
    time.sleep(2)
    os.system('clear')
    test_level_and_time_formatting(msgCue, border='',speed=baseSpeed)
    
    time.sleep(2)
    test_window_height_and_width(msgCue, border='*',speed=baseSpeed / 3)
    time.sleep(2)
    os.system('clear')
    test_window_height_and_width(msgCue, border='',speed=baseSpeed / 3)
    
    time.sleep(2)
    test_hide_levels(msgCue, border='*',speed=baseSpeed)
    time.sleep(3)
    os.system('clear')
    test_hide_levels(msgCue, border='',speed=baseSpeed)
    
    time.sleep(2)
    os.system('clear')
    test_maxLength(speed=baseSpeed / 2)
    
    time.sleep(5)
    os.system('clear')
    test_pause(speed=3)
    
    
    
    
def test_fill(msgCue, border, speed):
    letters = ['A', 'b', 'C', 'd', 'E', 'f', 'G', 'h', 'I', 'j', 'K', 'l', 'M', 'n', 'O', 'p', 'Q', 'r', 'S', 't', 'U', 'v', 'W', 'x', 'Y', 'z']
    levels = {'Error'   :   0,
              'Warning' :   1,
              'Status'  :   2,
              'Verbose' :   3,
              'Debug'   :   4,
              }
    levelsReversed = {}
    # Automatically populate levelsReversed
    for item in levels.items():
        levelsReversed.setdefault(item[1], item[0])
        
    speed = speed * 0.1
        
    thisLevel = 0
    for i in range(len(letters)):
        # Construct line to add
        thisLine = ''
        for j in range(i+1):
            thisLine += letters[j]
        msgCue.add(thisLine, levelsReversed[thisLevel])
        thisLevel += 1
        if thisLevel == 5:
            thisLevel = 0
        # Output
        os.system('clear')
        msgCue.print_window(len(letters), len(letters)+2, border=border,
                            levelFormat='long')
        time.sleep(speed * 1)
        
def test_level_and_time_formatting(msgCue, border, speed):
    letters = ['A', 'b', 'C', 'd', 'E', 'f', 'G', 'h', 'I', 'j', 'K', 'l', 'M', 'n', 'O', 'p', 'Q', 'r', 'S', 't', 'U', 'v', 'W', 'x', 'Y', 'z']
    levels = {'Error'   :   0,
              'Warning' :   1,
              'Status'  :   2,
              'Verbose' :   3,
              'Debug'   :   4,
              }
    levelsReversed = {}
    # Automatically populate levelsReversed
    for item in levels.items():
        levelsReversed.setdefault(item[1], item[0])
        
    speed = speed * 0.5
        
    os.system('clear')
    msgCue.print_window(len(letters), len(letters)+2, levelFormat='Long',
                        border=border)
    time.sleep(speed * 3)
    os.system('clear')
    msgCue.print_window(len(letters), len(letters)+2, levelFormat='short',
                        border=border)
    time.sleep(speed * 3)
    os.system('clear')
    msgCue.print_window(len(letters), len(letters)+2, levelFormat=False,
                        border=border)
    time.sleep(speed * 3)
    os.system('clear')
    msgCue.print_window(len(letters), len(letters)+2, levelFormat=False,
                        border=border, printTime=False)
    time.sleep(speed * 3)
    os.system('clear')
    msgCue.print_window(len(letters), len(letters)+2, levelFormat='short',
                        border=border, printTime=False)
    time.sleep(speed * 3)
    os.system('clear')
    msgCue.print_window(len(letters), len(letters)+2, levelFormat='long',
                        border=border, printTime=False)
    time.sleep(speed * 3)
    os.system('clear')
    msgCue.print_window(len(letters), len(letters)+2, levelFormat='long',
                        border=border, printTime=True)
    
def test_maxLength(speed):
    msgCue = MessageCue(maxLength=10)
    for i in range(msgCue.maxLength + 20):
        thisLine = str(i)
        msgCue.add(thisLine, level='status')
        os.system('clear')
        msgCue.print_window(30, msgCue.maxLength + 2)
        time.sleep(speed * 1.5)        
    
def test_pause(speed):
    import random
    msgCue = MessageCue()
    for i in range(100):
        toss = random.randint(1, 10)
        if toss == 10:
            msgCue.add('Oooo', 'status', pause=True)
        else:
            msgCue.add('Whatever', 'status')
    os.system('clear')
    msgCue.print_window(30, 102)
    
def test_window_height_and_width(msgCue, border, speed):
    letters = ['A', 'b', 'C', 'd', 'E', 'f', 'G', 'h', 'I', 'j', 'K', 'l', 'M', 'n', 'O', 'p', 'Q', 'r', 'S', 't', 'U', 'v', 'W', 'x', 'Y', 'z']
    
    height = len(letters) + 2
    width = len(letters)
    heightBuffer = 0
    
    while height >= 2:
        os.system('clear')
        print(heightBuffer * '\n', end='')
        msgCue.print_window(outerWidth=width, outerHeight=height, border=border, levelFormat='long')
        height -= 1
        heightBuffer += 1
        time.sleep(speed * 1.5)
    while height <= len(letters) + 2:
        os.system('clear')
        print(heightBuffer * '\n', end='')
        msgCue.print_window(outerWidth=width, outerHeight=height, border=border, levelFormat='long')
        height += 1
        heightBuffer -= 1
        time.sleep(speed * 1.5)
    while width > 0:
        os.system('clear')
        msgCue.print_window(outerWidth=width, outerHeight=height, border=border, levelFormat='long')
        width -= 1
        time.sleep(speed * 1.5)
    while width <= len(letters):
        os.system('clear')
        msgCue.print_window(outerWidth=width, outerHeight=height, border=border, levelFormat='long')
        width += 1
        
def test_hide_levels(msgCue, border, speed):
    levels = {'Error'   :   0,
              'Warning' :   1,
              'Status'  :   2,
              'Verbose' :   3,
              'Debug'   :   4,
              }
    levelsReversed = {}
    # Automatically populate levelsReversed
    for item in levels.items():
        levelsReversed.setdefault(item[1], item[0])
    
    speed = speed * 1
    
    for i in range(5):
        os.system('clear')
        thisLevel = levelsReversed[i]
        msgCue.print_window(26, 26, border=border, levelFormat='long', 
                            printLevel=thisLevel)
        time.sleep(speed * 1)
    for i in range(4, -1, -1):
        os.system('clear')
        thisLevel = levelsReversed[i]
        msgCue.print_window(26, 26, border=border, levelFormat='long', 
                            printLevel=thisLevel)
        time.sleep(speed * 1)


if __name__ == '__main__':
    test()