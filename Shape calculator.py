#Import
import math
from colorama import Fore, Back, Style
import webbrowser
import time

#Defines
radius = 1
area = 1
length = 1
height = 1
width = 1
base = 1
side = 1

#List
values = [radius, area, length, height, width, base, side]

#Just for fun storing the name of the characters
fighter = ""

#The fun begins
print("==================")
print("Welcome to Mortal Kombat Area Calculator 📐")
print("==================")

print("CHOOSE YOUR SHAPE FIGHTER!!!")

print(Fore.GREEN + "1. Johnny Circle")
print(Fore.WHITE + Back.BLUE + "2. Sub - Square")
print(Fore.BLACK + Back.GREEN + "3. Reptangle")
print(Fore.RED + Back.YELLOW + "4. Tri angle" + Style.RESET_ALL)
print("5. Exit")

shape = int(input("Enter the number of your champion: "))

print(f"So you have chosen {shape}")

#Conditions

#Conditions for all of my math values
for value in values:
    if value <= 0:
        print("Your stats cannot be 0 or negative! Your character is a superhero!")

#Circle
if shape == 1:
    fighter = "Johnny Circle"
    radius = int(input("Enter the stats (radius) of your champion: "))
    area = math.pi * radius**2
    print(f"Your area is: {area} ")
#Square
elif shape == 2:
    fighter = "Sub - Square"
    side = int(input("Enter the stats (side) of your champion: "))
    area = side**2
    print(f"Your area is: {area} ")
#Rectangle
elif shape == 3:
    fighter = "Reptangle"
    length = int(input("Length. Enter the stats of your champion: "))
    width = int(input("Width. Enter the stats of your champion: "))
    area = length * width
    print(f"Your area is: {area} ")
#Triangle
elif shape == 4:
    fighter = "Tri angle"
    height = int(input("Height. Enter the stats of your champion: "))
    base = int(input("Base. Enter the stats of your champion: "))
    area = (height * base)/2
    print(f"Your area is: {area} ")
else:
    print("Oh no! Something went terribly wrong. You are clearly too strong for this universe!")


#End message    
print(Back.BLACK + Style.BRIGHT + f"{fighter} wins!")
print(Back.BLACK + Style.BRIGHT + "FLAWLESS VICTORY!")

#TOASTY
def play_youtube_audio(url):
    webbrowser.open(url)
time.sleep(5)
play_youtube_audio("https://youtu.be/oyTwBLLAmNA")