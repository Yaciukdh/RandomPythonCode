#lesson 3: pokemon battles with classes global variables.
from random import *


name = "Ditto"

class Pokemon:

    #internal variables
    Pname     = "default"
    Pattack   = 0.0
    Paccuracy = 0.0
    Phealth   = 1.0

    def __init__(self):
        W = 0

    def setStuff(self, name, attack, accuracy, health):
        self.Pname     = name
        self.Pattack   = attack
        self.Paccuracy = accuracy
        self.Phealth   = health

    def getAttack(self):
        attack = self.Pattack
        return attack

    def getAccuracy(self):
        accuracy = self.Paccuracy
        return accuracy

    def getName(self):
        name = self.Pname
        return name

    def getHealth(self):
        health = self.Phealth
        return health

    def takeHit(self, injury):
        self.Phealth = self.Phealth - injury
        if self.Phealth < 0:
            self.Phealth = 0

#        health = self.Phealth

    def showoff(self):
        global name
        print("All pokemon are just " + name)

class Battle:

    pokemon1 = Pokemon()
    pokemon2 = Pokemon()

    def __init__(self, pokemonA, pokemonB):
        self.pokemon1 = pokemonA
        self.pokemon2 = pokemonB

    def attack(self, pokemonA, pokemonB):

        acc = pokemonA.getAccuracy()
        num = random()

        if num < acc:
            pokemonB.takeHit(pokemonA.getAttack())
        else:
            print(pokemonA.getName() + " missed!")

    def STARTBATTLE(self):

        print("It's " + self.pokemon1.getName() + " versus " + self.pokemon2.getName())

        while self.pokemon1.getHealth() != 0 and self.pokemon2.getHealth() != 0:

            print(self.pokemon1.getName() + " is trying to hit " + self.pokemon2.getName() + " for " + str(self.pokemon1.getAttack()))
            self.attack(self.pokemon1, self.pokemon2)
            print(self.pokemon2.getName() + " is trying to hit " + self.pokemon1.getName() + " for " + str(self.pokemon2.getAttack()))
            self.attack(self.pokemon2, self.pokemon1)

        if self.pokemon1.getHealth() == 0:
            print(self.pokemon1.getName() + " has fainted!")
        else:
            print(self.pokemon2.getName() + " has fainted!")

        print("The battle has ended and we shall forget the fallen.")
        print("")
        self.pokemon1.showoff()


print("")
print("Welcome to Pokemon Battle!")
print("I am using this as an example for OOP, or Object Oriented Programming.")
print("You will be prompted for a name, attack, accuracy, and health for 2 pokemon. ")
print("(Notice the raw input function :] ) ")
name1 = raw_input("Please enter the first name: ")
name2 = raw_input("Please enter the second name: ")

a1 = raw_input("Please enter the first attack stat: ")
a2 = raw_input("Please enter the second attack stat: ")

ac1 = raw_input("Please enter the first accuracy between 0 and 1: ")
ac2 = raw_input("Please enter the second accuracy between 0 and 1: ")

h1 = raw_input("Please enter the first health: ")
h2 = raw_input("Please enter the second health: ")

print("Battle starting...")

poke1 = Pokemon()
poke1.setStuff(name1, float(a1), float(ac1), float(h1))
poke2 = Pokemon()
poke2.setStuff(name2, float(a2), float(ac2), float(h2))
Battle(poke1, poke2).STARTBATTLE()

print("")
print("you might be looking at this and saying wtf, but it's pretty easy once you know.")
print("Pokemon is a class, which is just a collection of variables and functions with some")
print("structure that serves some function.")
print("This is about organization of thoughts mostly. We have some pokemon with")
print("some stats being stored, some setters and getters are written to get and set the values,")
print("also some augmentation functions to keep track of the health")
print("")
print("Battle is just an attack function and a loop that will continue until one of the pokemon")
print("faints.")
print("")
print("Oh! also look up the difference between global and local variables.")
print("I've made the mistake of reusing names and it's really tricky to catch if you are unaware.")
print("")
print("One last thing. the self.stuff command is for variable access within an object. ")
print("the __init__ stuff is what you need to initialize the object.")
print("self.stuff() would indicate a function being called on the data structure object. ")
print("The are either called functions or methods depending on the language you are using.")
print("There is a lot of other stuff in OOP, like abstract classes and inheritance, but this is the basics.")
print("")
print("There is a ton you can do with this.")
print("Make some sorting data structure or some binary tree thing")
print("Make a fake store that lets you stock it and sell shit at a profit, track how much you make")
print("Make a hash table data structure")
print("Simulate some OS scheduling or memory management algorithm")
print("")
print("Happy Coding!")
print("")
print(name)
