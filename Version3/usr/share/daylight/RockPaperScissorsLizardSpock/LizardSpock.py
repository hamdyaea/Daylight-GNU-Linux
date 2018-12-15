# Developer : Hamdy Abou El Anein

import tkinter as tk
import tkinter
from tkinter import messagebox
import random


top = tk.Tk()
top.title("Rock - Paper - Scissors - Lizard - Spock")

ciseaux_tk = tk.PhotoImage(file="/usr/share/daylight/RockPaperScissorsLizardSpock/images/scissors.gif")
caillou_tk = tk.PhotoImage(file="/usr/share/daylight/RockPaperScissorsLizardSpock/images/rock.gif")
feuille_tk = tk.PhotoImage(file="/usr/share/daylight/RockPaperScissorsLizardSpock/images/paper.gif")
lizard_tk = tk.PhotoImage(file="/usr/share/daylight/RockPaperScissorsLizardSpock/images/lizard.gif")
spock_tk = tk.PhotoImage(file="/usr/share/daylight/RockPaperScissorsLizardSpock/images/spock.gif")


user_score = 0
sheldon_score = 0


def Rock():
    global user_score, sheldon_score

    comp = random.randint(1, 5)

    if comp == 3:
        comp = "Scissors"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nRock crushes Scissors \n" + "Your Choice:Rock\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 1:
        comp = "Rock"
        messagebox.showinfo("Same choice!",
                            "EGUALITY!\n" + "Your Choice:Rock\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 2:
        comp = "Lizard"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nRock crushes Lizard \n" + "Your Choice:Rock\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 4:
        comp = "Spock"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE! \nSpock vaporizes Rock \n" + "Your Choice:Rock\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


    else:
        comp = "Paper"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nPaper covers Rock \n" + "Your Choice:Rock\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


def paper():
    global user_score, sheldon_score

    comp = random.randint(1, 5)

    if comp == 1:
        comp = "Rock"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nPaper covers Rock \n" + "Your Choice: Paper\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 2:
        comp = "Paper"
        messagebox.showinfo("Same choice!",
                            "EGUALITY!\n" + "Your Choice: Paper\n" + "\nSheldon's Choice:" + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 3:
        comp = "Lizard"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nLizard eats Paper\n" + "Your Choice: Paper\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 4:
        comp = "Spock"
        sheldon_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nPaper disproves Spock \n" + "Your Choice: Paper\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


    else:
        comp = "Scissors"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nScissors cuts Paper \n" + "Your Choice: Paper\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


def scissors():
    global user_score, sheldon_score

    comp = random.randint(1, 5)

    if comp == 2:
        comp = "Paper"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nScissors cuts Paper \nYour Choice: Scissors\n" + "\nSheldon's choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 3:
        comp = "Scissors"
        messagebox.showinfo("Same choice!",
                            "EGUALITY!\nYour Choice: Scissors\n" + "\nSheldon's choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


    elif comp == 1:
        comp = "Lizard"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nScissors decapitates Lizard \n" + "Your Choice:Scissors\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 4:
        comp = "Spock"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nSpock smashes Scissors \n" + "Your Choice:Scissors\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


    else:
        comp = "Rock"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nRock crushes Scissors \nYour Choice: Scissors\n" + "\nSheldon's choice:" + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

def lizard():
    global user_score, sheldon_score

    comp = random.randint(1, 5)

    if comp == 2:
        comp = "Paper"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nLizard eats Paper \nYour Choice: Lizard\n" + "\nSheldon's choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 3:
        comp = "Scissors"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nScissors decapitates Lizard \nYour Choice: Lizard\n" + "\nSheldon's choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


    elif comp == 1:
        comp = "Lizard"
        messagebox.showinfo("Same choice!",
                            "EGUALITY!\n" + "Your Choice: Lizard\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 4:
        comp = "Spock"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nLizard poisons Spock \n" + "Your Choice:Lizard\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))



    else:
        comp = "Rock"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nRock crushes Lizard \nYour Choice: Lizard\n" + "\nSheldon's choice:" + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

def spock():
    global user_score, sheldon_score

    comp = random.randint(1, 5)

    if comp == 2:
        comp = "Paper"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nPaper disproves Spock \nYour Choice: Spock\n" + "\nSheldon's choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


    elif comp == 3:
        comp = "Scissors"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN !\nSpock smashes Scissors \nYour Choice: Spock\n" + "\nSheldon's choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 1:
        comp = "Lizard"
        sheldon_score += 1
        messagebox.showinfo("Unlucky!",
                            "YOU LOOSE!\nLizard poisons Spock \n" + "Your Choice: Spock\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))

    elif comp == 4:
        comp = "Spock"
        messagebox.showinfo("Same choice!",
                            "EGUALITY!\n" + "Your Choice: Spock\n" + "\nSheldon's Choice: " + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


    else:
        comp = "Rock"
        user_score += 1
        messagebox.showinfo("Congratulation!",
                            "YOU WIN!\nSpock vaporizes Rock \nYour Choice: Spock\n" + "\nSheldon's choice:" + comp + "\nYour Score: " + str(
                                user_score) + "\nSheldon's Score: " + str(sheldon_score))


B1 = tkinter.Button(top, image=caillou_tk, height="300", width="280", command=Rock)
B2 = tkinter.Button(top, image=feuille_tk, height="300", width="280", command=paper)
B3 = tkinter.Button(top, image=ciseaux_tk, height="300", width="280", command=scissors)
B4 = tkinter.Button(top, image=lizard_tk, height="300", width="280", command=lizard)
B5 = tkinter.Button(top, image=spock_tk, height="300", width="280", command=spock)

B1.pack(side='left')
B2.pack(side='left')
B3.pack(side='left')
B4.pack(side='left')
B5.pack(side='left')

top.mainloop()

