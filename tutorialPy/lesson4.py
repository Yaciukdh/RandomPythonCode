# lesson 4: reading from files
from pathlib import Path
import json
import sys


encoder = json.JSONEncoder()  # These are global variables
decoder = json.JSONDecoder()  # for encoding and decoding the variables to be written to file


class IdeaChild:

    knowledge = {}
    myName = " "

    def __init__(self):
        self.knowledge = {}
        self.myName = " "

    def initSelf(self, loaded):
        self.knowledge = loaded

    def setName(self, newname):
        self.myName = newname
        f = open("name.txt",'w')
        f.write(encoder.encode(self.myName))

    def getName(self):
        retname = self.myName
        return retname

    def insertAndStore(self, key, value):

        self.knowledge[key] = value
        f = open("knowledge.txt",'w')
        f.write(encoder.encode(self.knowledge))
        f.close()

    def getVal(self, key):
        ret = self.knowledge.get(key)

        if ret is None:
            return "I have no knowledge of that"
        else:
            return ret


if __name__ == "__main__":

    fn = Path("name.txt")  # checks if file exists in working directory
    idea = IdeaChild()

    if fn.exists():  # if file exists, read files and set variables

        f1 = open("name.txt", 'r')
        f2 = open("knowledge.txt", 'r')
        idea.setName(decoder.decode(f1.read()))
        idea.initSelf(decoder.decode(f2.read()))
        print("Hello again! Remember me? I'm " + idea.getName() + "!")
        print("Would you like me to learn? to quiz me? Let me know what you want and I'll get back to you.")

    else:  # if file does not exist, get info and make files

        print("This is an example of reading and writing files using Python.")
        print("Everything is stored in json format in .txt files using encoders and decoders.")
        print("Also, we introduce dictionaries. You give a dictionary a keyword and it will retrieve")
        print("an associated value.")
        print("")
        print("")
        print("")
        print("Hi! I'm a new soul, created from the eather by your fingertips.")
        name = input("What is my name?\n")
        idea.setName(name)
        idea.insertAndStore('0', 'z')
        print("If you want me to learn, type \'learn\' followed by a topic, then what you want me to know")
        print("If you want to quiz me, type \'quiz\', then the topic. Chances are I will remember!")
        print("Maybe you want to know how to improve me and my memory, then type \'improve\'")
        print("then I'll give you suggestions!")
        print("And if you want me to sleep a bit, type sleep and I'll exit gracefully.")

    k = 0

    while k < 1:
        job = input("what would you like to do?\n")

        if job == "learn":

            key = input("On what topic?\n")
            value = input("What information would you like me to know?\n")
            print("Nice! I'll make a note of that.")
            idea.insertAndStore(key, value)

        elif job == "quiz":

            key = input("What topic do you want to quiz me on?\n")
            val = idea.getVal(key)
            print("Here's what I know:")
            print(val)

        elif job == "sleep":

            print("Thank you, I will nap.")
            sys.exit()

        elif job == "improve":

            print("Right now I have the restriction of only knowing one thing about each topic.")
            print("Can you make it so I can know more things if you tell them to me?")
            print("Check the commented code for hints.")

            # It's a pretty straight forward task.
            # you use the list data type as the value associated with the key
            # so you can point to more than one piece of information.
            # Now when you do a dictionary look up, you get a list of info instead of a simple string.
            # formatting is up to you, iterate through array or just print array if lazy.

        else:

            print("I am unfamiliar with that command.")
