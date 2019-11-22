# Lesson one

print("This is the print command.")
print("Put character data between quotes and it will print to the terminal below.")
print("This might vary depending on which version of python you're running.")
print("One character is typically called a char, while multiple char's concatenated is a string.")
print("print is a weird function. Most languages only print stuff on a new line when specified.")
print("For python, you would need to either build a string or import a function to print on the same line.")
print("This is ok, but remember going forward that it's not typical.")
print("Oh! # are comment characters, meaning that lines with #'s won't get executed by compiler or interpreter.")
# print("see?");
print("Python doesn't require explict type declaration. It's typically inferred.")

integer1 = 11
integer2 = 4
integer3 = integer1 + integer2

print("Here is the result:")
print(integer3)
print("Note that Python automatically turns the integer to a string and when you print a variable like integer3,")
print("there is no quotes. You can put variables and text data together in a print using a + symbol and str converter")
print("Explict typing is nice most of the time, but sometimes it fucks you up.")
print("watch this: " + str(integer1) + "/" + str(integer2))

intDivide = integer1/integer2

print(intDivide)
print("D:")
print("Back in the day people wanted integer division to ignore the remainder to keep the ints as ints.")
print("you can recover the remainder using the mod operator(%) like so:")

intMod = integer1 % integer2

print(intMod)
print("You can translate ints into floats by adding a decimal point or by adding .0 to the number before the operation.")

float1 = (integer1+.0)/integer2
print(float1)
print("now division works like you would expect.")
print(" ")
print("Now the fun stuff happens")
print("This is a for loop. Python enforces good practices, so you have to use tabs to execute things in the loop.")
print("It's nice, but also aggravating if you mis-tab a loop")

begin = 0
end = 4
timeStep = 1

for x in range(begin, end, timeStep):
    print(x)    # since there isn't anything tabbed, this line is executed multiple times.

print("This adds 1 to x until x=4, at which point the code exits the loop.")
print("If you wanted to add 2, you would change the timeStep variable, while the begin and end control the range.")
print("You might design a loop and it will run to infinity. It sucks, but it's easy to find using prints.")
print("Let's make a sum of numbers using a different loop style!")

i = begin;
sum = 0;

while i < end:
    sum = sum + i;
    i = i + 1  # equivalently you could write i+=1

print(sum)
print("Nice! 0 + 1 + 2 + 3 = 6. A common loop that professors ask students to write is factorial. Look it up :p")
print("If statements are cool too. They are like loops with specific conditions. Here:")

end = 900
timeStep = 100

for x in range(begin, end, timeStep):
    if x % 300 == 0:
        print(x)    # double tabbed due to the if statement and loop.

print("Notice how 900 isn't included. if you want it to be included, then make begin 901")
