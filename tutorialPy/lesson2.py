# Lesson two: libraries and functions
import time

def func1():
    print("This function prints some lines")
    print("Functions are reusable pieces of code")
    print("Sometimes they make code more readable")


def sumasafunction(begin, end, timeStep):

    sum = 0
    for x in range(begin, end, timeStep):
        sum = sum+x

    return sum


def weirdprint(printable):

    print("You are in weird print! A weird print you can pass stuff to!")

    if type(printable) is int:
        print("You entered a integer!")
        print("printable is equal to: " + str(printable))

    elif type(printable) is str:
        print("You entered a string!")
        print("printable is equal to: " + printable)

    else:
        print("wtf ya doin? Passing a non int or string? what am I, a mind reader? getcho shit together mane.")
    print("")


print("")
time.sleep(1)

print("import statements brings libraries into the program that you can use")
time.sleep(1)
print("time.wait() lets the program wait for a specified amount of time")
print("")
time.sleep(1)
print("the program waited 1 second to print!")
print("")
time.sleep(1)

print("Now we get to functions.")

#FUNCTIONS
time.sleep(1)

func1()

print("You don't need input for a function.")
cool = sumasafunction(0, 5, 1)
print("You can return a result!")
print(cool)
print("You can reuse code as necessary!")
cool = sumasafunction(0, 7, 2)
print(cool)

print("You can do crazier things too.")
print("")
weirdprint("Bagel.")
weirdprint(sumasafunction(0, 5, 1))
weirdprint(1.1)
time.sleep(1)

#IF, ELSE IF. ELSE

print("type() is for type checking, you can run functions inside functions so you're not storing anything in a var,")
print("and elif means else if. The chain is if, then elif until else which handles weird cases.")
print("")
time.sleep(2)
print("Stuff is dope. Wait until classes.")
time.sleep(3)
