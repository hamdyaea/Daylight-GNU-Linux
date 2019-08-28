# Developer : Hamdy Abou El Anein
# This card game is made in Python 3 with the easygui library
# You play against the computer and the first without card lose the game


from easygui import *
import random
import sys

picwin = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/winner.gif"
piclose = "/usr/share/daylight/Battle-Cards-with-GUI//Pictures/gameover.gif"
Pic2carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/2Carreaux.gif"
Pic2coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/2Coeur.gif"
Pic2piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/2Piques.gif"  # trop petite image
Pic2treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/2treffles.gif"
Pic3carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/3Carreaux.gif"
Pic3coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/3Coeur.gif"
Pic3piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/3Piques.gif"
Pic3treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/3treffles.gif"
Pic4carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/4Carreaux.gif"
Pic4coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/4Coeur.gif"
Pic4piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/4Piques.gif"
Pic4treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/4treffles.gif"
Pic5carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/5Carreaux.gif"
Pic5coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/5coeur.gif"
Pic5piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/5Piques.gif"
Pic5treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/5treffles.gif"
Pic6carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/6Carreaux.gif"
Pic6coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/6Coeur.gif"
Pic6piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/6Piques.gif"
Pic6treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/6treffles.gif"
Pic7carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/7Carreaux.gif"
Pic7coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/7Coeur.gif"
Pic7piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/7Piques.gif"
Pic7treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/7treffles.gif"
Pic8carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/8Carreaux.gif"
Pic8coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/8Coeur.gif"
Pic8piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/8Piques.gif"
Pic8treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/8treffles.gif"
Pic9carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/9Carreaux.gif"
Pic9coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/9Coeur.gif"
Pic9piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/9Piques.gif"
Pic9treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/9treffles.gif"
Pic10carreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/10Carreaux.gif"
Pic10coeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/10Coeur.gif"
Pic10piques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/10Piques.gif"
Pic10treffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/10treffles.gif"
AsCarreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/AsDeCaraux.gif"
AsCoeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/AsDeCoeur.gif"
AsPiques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/AsDePique.gif"
AsTreffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/AsDeTreffles.gif"
ReineCarreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ReineCarreaux.gif"
ReineCoeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ReineCoeur.gif"
ReinePiques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ReinePiques.gif"
ReineTreffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ReineTreffles.gif"
RoiCarreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/RoiCarreaux.gif"
RoiCoeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/RoiCoeur.gif"
RoiPiques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/RoiPiques.gif"
RoiTreffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/RoiTreffles.gif"
ValetCarreaux = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ValetCarreaux.gif"
ValetCoeur = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ValetCoeur.gif"
ValetPiques = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ValetPiques.gif"
ValetTreffles = "/usr/share/daylight/Battle-Cards-with-GUI/Pictures/ValetTreffles.gif"
image1 = ""
image2 = ""

battleList = []

CardList = {'Card2carreaux': 2, 'Card2coeur': 2, 'Card2piques': 2, 'Card2treffles': 2, 'Card3carreaux': 3,'Card3coeur': 3, 'Card3piques': 3, 'Card3treffles': 3, 'Card4carreaux': 4, 'Card4coeur': 4,'Card4piques': 4, 'Card4treffles': 4, 'Card5carreaux': 5, 'Card5coeur': 5, 'Card5piques': 5,'Card5treffles': 5, 'Card6carreaux': 6, 'Card6coeur': 6, 'Card6treffles': 6, 'Card7carreaux': 7,'Card6piques': 6, 'Card7coeur': 7, 'Card7piques': 7, 'Card7treffles': 7, 'Card8carreaux': 8,'Card8coeur': 8, 'Card8piques': 8, 'Card8treffles': 8, 'Card9carreaux': 9, 'Card9coeur': 9,'Card9piques': 9, 'Card9treffles': 9, 'Card10carreaux': 10, 'Card10coeur': 10, 'Card10piques': 10,'Card10treffles': 10, 'CardAsCarreaux': 15, 'CardAsCoeur': 15, 'CardAsPiques': 15, 'CardAsTreffles': 15,'CardReineCarreaux': 13, 'CardReineCoeur': 13, 'CardReinePiques': 13, 'CardReineTreffles': 13,'CardRoiCarreaux': 14, 'CardRoiCoeur': 14, 'CardRoiPiques': 14, 'CardRoiTreffles': 14,'CardValetCarreaux': 12, 'CardValetCoeur': 12, 'CardValetPiques': 12, 'CardValetTreffles': 12}
Cards2play = ['Card2carreaux', 'Card2coeur', 'Card2piques', 'Card2treffles', 'Card3carreaux', 'Card3coeur','Card3piques', 'Card3treffles', 'Card4carreaux', 'Card4coeur', 'Card4piques', 'Card4treffles','Card5carreaux', 'Card5coeur', 'Card5piques', 'Card5treffles', 'Card6carreaux', 'Card6coeur','Card6treffles', 'Card7carreaux', 'Card6piques', 'Card7coeur', 'Card7piques', 'Card7treffles','Card8carreaux', 'Card8coeur', 'Card8piques', 'Card8treffles', 'Card9carreaux', 'Card9coeur','Card9piques', 'Card9treffles', 'Card10carreaux', 'Card10coeur', 'Card10piques', 'Card10treffles','CardAsCarreaux', 'CardAsCoeur', 'CardAsPiques', 'CardAsTreffles', 'CardReineCarreaux', 'CardReineCoeur','CardReinePiques', 'CardReineTreffles', 'CardRoiCarreaux', 'CardRoiCoeur', 'CardRoiPiques','CardRoiTreffles', 'CardValetCarreaux', 'CardValetCoeur', 'CardValetPiques', 'CardValetTreffles']


def mixCards():
    global cpuCards, usrCards, Cards2play, CardList

    random.shuffle(Cards2play)
    usrCards = Cards2play[:26]
    cpuCards = Cards2play[26:]

    Game()

def GameBattle():
    global image1, image2, battleList

    if CardList[usrCards[0]] == CardList[cpuCards[0]]:
        Image = image1,image2
        msg = "                              Eguality, we continue the battle\n\n\n              "+str("\n\n Your cards : ") + str(len(usrCards)) + str("\n\n\n Computer cards : ") + str(len(cpuCards))+str("\n\n\n           User cards                                    Computer cards")
        choices = ["Continue"]
        result = buttonbox(msg, image=Image, choices=choices)
        if result == "Continue":
            Battle()

    elif CardList[usrCards[0]] < CardList[cpuCards[0]]:
        if usrCards[0] == 'Card2carreaux':
            image1 = Pic2carreaux
            cpuCards.append('Card2carreaux')
            usrCards.remove('Card2carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card2coeur':
            image1 = Pic2coeur
            cpuCards.append('Card2coeur')
            usrCards.remove('Card2coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card2piques':
            image1 = Pic2piques
            cpuCards.append('Card2piques')
            usrCards.remove('Card2piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card2treffles':
            image1 = Pic2treffles
            cpuCards.append('Card2treffles')
            usrCards.remove('Card2treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card3carreaux':
            image1 = Pic3carreaux
            cpuCards.append('Card3carreaux')
            usrCards.remove('Card3carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card3coeur':
            image1 = Pic3coeur
            cpuCards.append('Card3coeur')
            usrCards.remove('Card3coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card3piques':
            image1 = Pic3piques
            cpuCards.append('Card3piques')
            usrCards.remove('Card3piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card3treffles':
            image1 = Pic3treffles
            cpuCards.append('Card3treffles')
            usrCards.remove('Card3treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card4carreaux':
            image1 = Pic4carreaux
            cpuCards.append('Card4carreaux')
            usrCards.remove('Card4carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card4coeur':
            image1 = Pic4coeur
            cpuCards.append('Card4coeur')
            usrCards.remove('Card4coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card4piques':
            image1 = Pic4piques
            cpuCards.append('Card4piques')
            usrCards.remove('Card4piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card4treffles':
            image1 = Pic4treffles
            cpuCards.append('Card4treffles')
            usrCards.remove('Card4treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card5carreaux':
            image1 = Pic5carreaux
            cpuCards.append('Card5carreaux')
            usrCards.remove('Card5carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card5coeur':
            image1 = Pic5coeur
            cpuCards.append('Card5coeur')
            usrCards.remove('Card5coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card5piques':
            image1 = Pic5piques
            cpuCards.append('Card5piques')
            usrCards.remove('Card5piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card5treffles':
            image1 = Pic5treffles
            cpuCards.append('Card5treffles')
            usrCards.remove('Card5treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card6carreaux':
            image1 = Pic6carreaux
            cpuCards.append('Card6carreaux')
            usrCards.remove('Card6carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card6coeur':
            image1 = Pic6coeur
            cpuCards.append('Card6coeur')
            usrCards.remove('Card6coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card6treffles':
            image1 = Pic6treffles
            cpuCards.append('Card6treffles')
            usrCards.remove('Card6treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card6piques':
            image1 = Pic6piques
            cpuCards.append('Card6piques')
            usrCards.remove('Card6piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card7carreaux':
            image1 = Pic7carreaux
            cpuCards.append('Card7carreaux')
            usrCards.remove('Card7carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card7coeur':
            image1 = Pic7coeur
            cpuCards.append('Card7coeur')
            usrCards.remove('Card7coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card7piques':
            image1 = Pic7piques
            cpuCards.append('Card7piques')
            usrCards.remove('Card7piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card7treffles':
            image1 = Pic7treffles
            cpuCards.append('Card7treffles')
            usrCards.remove('Card7treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card8carreaux':
            image1 = Pic8carreaux
            cpuCards.append('Card8carreaux')
            usrCards.remove('Card8carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card8treffles':
            image1 = Pic8treffles
            cpuCards.append('Card8treffles')
            usrCards.remove('Card8treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card8piques':
            image1 = Pic8piques
            cpuCards.append('Card8piques')
            usrCards.remove('Card8piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card8coeur':
            image1 = Pic8coeur
            cpuCards.append('Card8coeur')
            usrCards.remove('Card8coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card9carreaux':
            image1 = Pic9carreaux
            cpuCards.append('Card9carreaux')
            usrCards.remove('Card9carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card9coeur':
            image1 = Pic9coeur
            cpuCards.append('Card9coeur')
            usrCards.remove('Card9coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card9piques':
            image1 = Pic9piques
            cpuCards.append('Card9piques')
            usrCards.remove('Card9piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card9treffles':
            image1 = Pic9treffles
            cpuCards.append('Card9treffles')
            usrCards.remove('Card9treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card10carreaux':
            image1 = Pic10carreaux
            cpuCards.append('Card10carreaux')
            usrCards.remove('Card10carreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card10coeur':
            image1 = Pic10coeur
            cpuCards.append('Card10coeur')
            usrCards.remove('Card10coeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card10piques':
            image1 = Pic10piques
            cpuCards.append('Card10piques')
            usrCards.remove('Card10piques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'Card10treffles':
            image1 = Pic10treffles
            cpuCards.append('Card10treffles')
            usrCards.remove('Card10treffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardAsCarreaux':
            image1 = AsCarreaux
            cpuCards.append('CardAsCarreaux')
            usrCards.remove('CardAsCarreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardAsCoeur':
            image1 = AsCoeur
            cpuCards.append('CardAsCoeur')
            usrCards.remove('CardAsCoeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardAsPiques':
            image1 = AsPiques
            cpuCards.append('CardAsPiques')
            usrCards.remove('CardAsPiques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardAsTreffles':
            image1 = AsTreffles
            cpuCards.append('CardAsTreffles')
            usrCards.remove('CardAsTreffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardReineCarreaux':
            image1 = ReineCarreaux
            cpuCards.append('CardReineCarreaux')
            usrCards.remove('CardReineCarreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardReineCoeur':
            image1 = ReineCoeur
            cpuCards.append('CardReineCoeur')
            usrCards.remove('CardReineCoeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardReinePiques':
            image1 = ReinePiques
            cpuCards.append('CardReinePiques')
            usrCards.remove('CardReinePiques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardReineTreffles':
            image1 = ReineTreffles
            cpuCards.append('CardReineTreffles')
            usrCards.remove('CardReineTreffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardRoiCarreaux':
            image1 = RoiCarreaux
            cpuCards.append('CardRoiCarreaux')
            usrCards.remove('CardRoiCarreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardRoiCoeur':
            image1 = RoiCoeur
            cpuCards.append('CardRoiCoeur')
            usrCards.remove('CardRoiCoeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardRoiPiques':
            image1 = RoiPiques
            cpuCards.append('CardRoiPiques')
            usrCards.remove('CardRoiPiques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardRoiTreffles':
            image1 = RoiTreffles
            cpuCards.append('CardRoiTreffles')
            usrCards.remove('CardRoiTreffles')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardValetCarreaux':
            image1 = ValetCarreaux
            cpuCards.append('CardValetCarreaux')
            usrCards.remove('CardValetCarreaux')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardValetCoeur':
            image1 = ValetCoeur
            cpuCards.append('CardValetCoeur')
            usrCards.remove('CardValetCoeur')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardValetPiques':
            image1 = ValetPiques
            cpuCards.append('CardValetPiques')
            usrCards.remove('CardValetPiques')
            cpuCards.extend(battleList)
        elif usrCards[0] == 'CardValetTreffles':
            image1 = ValetTreffles
            cpuCards.append('CardValetTreffles')
            usrCards.remove('CardValetTreffles')
            cpuCards.extend(battleList)

        if cpuCards[0] == 'Card2carreaux':
            image2 = Pic2carreaux
        elif cpuCards[0] == 'Card2coeur':
            image2 = Pic2coeur
        elif cpuCards[0] == 'Card2piques':
            image2 = Pic2piques
        elif cpuCards[0] == 'Card2treffles':
            image2 = Pic2treffles
        elif cpuCards[0] == 'Card3carreaux':
            image2 = Pic3carreaux
        elif cpuCards[0] == 'Card3coeur':
            image2 = Pic3coeur
        elif cpuCards[0] == 'Card3piques':
            image2 = Pic3piques
        elif cpuCards[0] == 'Card3treffles':
            image2 = Pic3treffles
        elif cpuCards[0] == 'Card4carreaux':
            image2 = Pic4carreaux
        elif cpuCards[0] == 'Card4coeur':
            image2 = Pic4coeur
        elif cpuCards[0] == 'Card4piques':
            image2 = Pic4piques
        elif cpuCards[0] == 'Card4treffles':
            image2 = Pic4treffles
        elif cpuCards[0] == 'Card5carreaux':
            image2 = Pic5carreaux
        elif cpuCards[0] == 'Card5coeur':
            image2 = Pic5coeur
        elif cpuCards[0] == 'Card5piques':
            image2 = Pic5piques
        elif cpuCards[0] == 'Card5treffles':
            image2 = Pic5treffles
        elif cpuCards[0] == 'Card6carreaux':
            image2 = Pic6carreaux
        elif cpuCards[0] == 'Card6coeur':
            image2 = Pic6coeur
        elif cpuCards[0] == 'Card6treffles':
            image2 = Pic6treffles
        elif cpuCards[0] == 'Card6piques':
            image2 = Pic6piques
        elif cpuCards[0] == 'Card7carreaux':
            image2 = Pic7carreaux
        elif cpuCards[0] == 'Card7coeur':
            image2 = Pic7coeur
        elif cpuCards[0] == 'Card7piques':
            image2 = Pic7piques
        elif cpuCards[0] == 'Card7treffles':
            image2 = Pic7treffles
        elif cpuCards[0] == 'Card8carreaux':
            image2 = Pic8carreaux
        elif cpuCards[0] == 'Card8treffles':
            image2 = Pic8treffles
        elif cpuCards[0] == 'Card8piques':
            image2 = Pic8piques
        elif cpuCards[0] == 'Card8coeur':
            image2 = Pic8coeur
        elif cpuCards[0] == 'Card9carreaux':
            image2 = Pic9carreaux
        elif cpuCards[0] == 'Card9coeur':
            image2 = Pic9coeur
        elif cpuCards[0] == 'Card9piques':
            image2 = Pic9piques
        elif cpuCards[0] == 'Card9treffles':
            image2 = Pic9treffles
        elif cpuCards[0] == 'Card10carreaux':
            image2 = Pic10carreaux
        elif cpuCards[0] == 'Card10coeur':
            image2 = Pic10coeur
        elif cpuCards[0] == 'Card10piques':
            image2 = Pic10piques
        elif cpuCards[0] == 'Card10treffles':
            image2 = Pic10treffles
        elif cpuCards[0] == 'CardAsCarreaux':
            image2 = AsCarreaux
        elif cpuCards[0] == 'CardAsCoeur':
            image2 = AsCoeur
        elif cpuCards[0] == 'CardAsPiques':
            image2 = AsPiques
        elif cpuCards[0] == 'CardAsTreffles':
            image2 = AsTreffles
        elif cpuCards[0] == 'CardReineCarreaux':
            image2 = ReineCarreaux
        elif cpuCards[0] == 'CardReineCoeur':
            image2 = ReineCoeur
        elif cpuCards[0] == 'CardReinePiques':
            image2 = ReinePiques
        elif cpuCards[0] == 'CardReineTreffles':
            image2 = ReineTreffles
        elif cpuCards[0] == 'CardRoiCarreaux':
            image2 = RoiCarreaux
        elif cpuCards[0] == 'CardRoiCoeur':
            image2 = RoiCoeur
        elif cpuCards[0] == 'CardRoiPiques':
            image2 = RoiPiques
        elif cpuCards[0] == 'CardRoiTreffles':
            image2 = RoiTreffles
        elif cpuCards[0] == 'CardValetCarreaux':
            image2 = ValetCarreaux
        elif cpuCards[0] == 'CardValetCoeur':
            image2 = ValetCoeur
        elif cpuCards[0] == 'CardValetPiques':
            image2 = ValetPiques
        elif cpuCards[0] == 'CardValetTreffles':
            image2 = ValetTreffles

        battleList.clear()
        Image = image1,image2
        msg = "                    You lose the battle, we continue the game\n\n\n              "+str("\n\n Your cards : ") + str(len(usrCards)) + str("\n\n\n Computer cards : ") + str(len(cpuCards))+str("\n\n\n           User cards                                    Computer cards")
        choices = ["Continue"]
        result = buttonbox(msg, image=Image, choices=choices)
        if result == "Continue":
            Game()

    elif CardList[usrCards[0]] > CardList[cpuCards[0]]:

        if usrCards[0] == 'Card2carreaux':
            image1 = Pic2carreaux
        elif usrCards[0] == 'Card2coeur':
            image1 = Pic2coeur
        elif usrCards[0] == 'Card2piques':
            image1 = Pic2piques
        elif usrCards[0] == 'Card2treffles':
            image1 = Pic2treffles
        elif usrCards[0] == 'Card3carreaux':
            image1 = Pic3carreaux
        elif usrCards[0] == 'Card3coeur':
            image1 = Pic3coeur
        elif usrCards[0] == 'Card3piques':
            image1 = Pic3piques
        elif usrCards[0] == 'Card3treffles':
            image1 = Pic3treffles
        elif usrCards[0] == 'Card4carreaux':
            image1 = Pic4carreaux
        elif usrCards[0] == 'Card4coeur':
            image1 = Pic4coeur
        elif usrCards[0] == 'Card4piques':
            image1 = Pic4piques
        elif usrCards[0] == 'Card4treffles':
            image1 = Pic4treffles
        elif usrCards[0] == 'Card5carreaux':
            image1 = Pic5carreaux
        elif usrCards[0] == 'Card5coeur':
            image1 = Pic5coeur
        elif usrCards[0] == 'Card5piques':
            image1 = Pic5piques
        elif usrCards[0] == 'Card5treffles':
            image1 = Pic5treffles
        elif usrCards[0] == 'Card6carreaux':
            image1 = Pic6carreaux
        elif usrCards[0] == 'Card6coeur':
            image1 = Pic6coeur
        elif usrCards[0] == 'Card6treffles':
            image1 = Pic6treffles
        elif usrCards[0] == 'Card6piques':
            image1 = Pic6piques
        elif usrCards[0] == 'Card7carreaux':
            image1 = Pic7carreaux
        elif usrCards[0] == 'Card7coeur':
            image1 = Pic7coeur
        elif usrCards[0] == 'Card7piques':
            image1 = Pic7piques
        elif usrCards[0] == 'Card7treffles':
            image1 = Pic7treffles
        elif usrCards[0] == 'Card8carreaux':
            image1 = Pic8carreaux
        elif usrCards[0] == 'Card8treffles':
            image1 = Pic8treffles
        elif usrCards[0] == 'Card8piques':
            image1 = Pic8piques
        elif usrCards[0] == 'Card8coeur':
            image1 = Pic8coeur
        elif usrCards[0] == 'Card9carreaux':
            image1 = Pic9carreaux
        elif usrCards[0] == 'Card9coeur':
            image1 = Pic9coeur
        elif usrCards[0] == 'Card9piques':
            image1 = Pic9piques
        elif usrCards[0] == 'Card9treffles':
            image1 = Pic9treffles
        elif usrCards[0] == 'Card10carreaux':
            image1 = Pic10carreaux
        elif usrCards[0] == 'Card10coeur':
            image1 = Pic10coeur
        elif usrCards[0] == 'Card10piques':
            image1 = Pic10piques
        elif usrCards[0] == 'Card10treffles':
            image1 = Pic10treffles
        elif usrCards[0] == 'CardAsCarreaux':
            image1 = AsCarreaux
        elif usrCards[0] == 'CardAsCoeur':
            image1 = AsCoeur
        elif usrCards[0] == 'CardAsPiques':
            image1 = AsPiques
        elif usrCards[0] == 'CardAsTreffles':
            image1 = AsTreffles
        elif usrCards[0] == 'CardReineCarreaux':
            image1 = ReineCarreaux
        elif usrCards[0] == 'CardReineCoeur':
            image1 = ReineCoeur
        elif usrCards[0] == 'CardReinePiques':
            image1 = ReinePiques
        elif usrCards[0] == 'CardReineTreffles':
            image1 = ReineTreffles
        elif usrCards[0] == 'CardRoiCarreaux':
            image1 = RoiCarreaux
        elif usrCards[0] == 'CardRoiCoeur':
            image1 = RoiCoeur
        elif usrCards[0] == 'CardRoiPiques':
            image1 = RoiPiques
        elif usrCards[0] == 'CardRoiTreffles':
            image1 = RoiTreffles
        elif usrCards[0] == 'CardValetCarreaux':
            image1 = ValetCarreaux
        elif usrCards[0] == 'CardValetCoeur':
            image1 = ValetCoeur
        elif usrCards[0] == 'CardValetPiques':
            image1 = ValetPiques
        elif usrCards[0] == 'CardValetTreffles':
            image1 = ValetTreffles

        if cpuCards[0] == 'Card2carreaux':
            image2 = Pic2carreaux
            usrCards.append('Card2carreaux')
            cpuCards.remove('Card2carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card2coeur':
            image2 = Pic2coeur
            usrCards.append('Card2coeur')
            cpuCards.remove('Card2coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card2piques':
            image2 = Pic2piques
            usrCards.append('Card2piques')
            cpuCards.remove('Card2piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card2treffles':
            image2 = Pic2treffles
            usrCards.append('Card2treffles')
            cpuCards.remove('Card2treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card3carreaux':
            image2 = Pic3carreaux
            usrCards.append('Card3carreaux')
            cpuCards.remove('Card3carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card3coeur':
            image2 = Pic3coeur
            usrCards.append('Card3coeur')
            cpuCards.remove('Card3coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card3piques':
            image2 = Pic3piques
            usrCards.append('Card3piques')
            cpuCards.remove('Card3piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card3treffles':
            image2 = Pic3treffles
            usrCards.append('Card3treffles')
            cpuCards.remove('Card3treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card4carreaux':
            image2 = Pic4carreaux
            usrCards.append('Card4carreaux')
            cpuCards.remove('Card4carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card4coeur':
            image2 = Pic4coeur
            usrCards.append('Card4coeur')
            cpuCards.remove('Card4coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card4piques':
            image2 = Pic4piques
            usrCards.append('Card4piques')
            cpuCards.remove('Card4piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card4treffles':
            image2 = Pic4treffles
            usrCards.append('Card4treffles')
            cpuCards.remove('Card4treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card5carreaux':
            image2 = Pic5carreaux
            usrCards.append('Card5carreaux')
            cpuCards.remove('Card5carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card5coeur':
            image2 = Pic5coeur
            usrCards.append('Card5coeur')
            cpuCards.remove('Card5coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card5piques':
            image2 = Pic5piques
            usrCards.append('Card5piques')
            cpuCards.remove('Card5piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card5treffles':
            image2 = Pic5treffles
            usrCards.append('Card5treffles')
            cpuCards.remove('Card5treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card6carreaux':
            image2 = Pic6carreaux
            usrCards.append('Card6carreaux')
            cpuCards.remove('Card6carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card6coeur':
            image2 = Pic6coeur
            usrCards.append('Card6coeur')
            cpuCards.remove('Card6coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card6treffles':
            image2 = Pic6treffles
            usrCards.append('Card6treffles')
            cpuCards.remove('Card6treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card6piques':
            image2 = Pic6piques
            usrCards.append('Card6piques')
            cpuCards.remove('Card6piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card7carreaux':
            image2 = Pic7carreaux
            usrCards.append('Card7carreaux')
            cpuCards.remove('Card7carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card7coeur':
            image2 = Pic7coeur
            usrCards.append('Card7coeur')
            cpuCards.remove('Card7coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card7piques':
            image2 = Pic7piques
            usrCards.append('Card7piques')
            cpuCards.remove('Card7piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card7treffles':
            image2 = Pic7treffles
            usrCards.append('Card7treffles')
            cpuCards.remove('Card7treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card8carreaux':
            image2 = Pic8carreaux
            usrCards.append('Card8carreaux')
            cpuCards.remove('Card8carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card8treffles':
            image2 = Pic8treffles
            usrCards.append('Card8treffles')
            cpuCards.remove('Card8treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card8piques':
            image2 = Pic8piques
            usrCards.append('Card8piques')
            cpuCards.remove('Card8piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card8coeur':
            image2 = Pic8coeur
            usrCards.append('Card8coeur')
            cpuCards.remove('Card8coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card9carreaux':
            image2 = Pic9carreaux
            usrCards.append('Card9carreaux')
            cpuCards.remove('Card9carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card9coeur':
            image2 = Pic9coeur
            usrCards.append('Card9coeur')
            cpuCards.remove('Card9coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card9piques':
            image2 = Pic9piques
            usrCards.append('Card9piques')
            cpuCards.remove('Card9piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card9treffles':
            image2 = Pic9treffles
            usrCards.append('Card9treffles')
            cpuCards.remove('Card9treffle')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card10carreaux':
            image2 = Pic10carreaux
            usrCards.append('Card10carreaux')
            cpuCards.remove('Card10carreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card10coeur':
            image2 = Pic10coeur
            usrCards.append('Card10coeur')
            cpuCards.remove('Card10coeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card10piques':
            image2 = Pic10piques
            usrCards.append('Card10piques')
            cpuCards.remove('Card10piques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'Card10treffles':
            image2 = Pic10treffles
            usrCards.append('Card10treffles')
            cpuCards.remove('Card10treffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardAsCarreaux':
            image2 = AsCarreaux
            usrCards.append('CardAsCarreaux')
            cpuCards.remove('CardAsCarreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardAsCoeur':
            image2 = AsCoeur
            usrCards.append('CardAsCoeur')
            cpuCards.remove('CardAsCoeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardAsPiques':
            image2 = AsPiques
            usrCards.append('CardAsPiques')
            cpuCards.remove('CardAsPiques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardAsTreffles':
            image2 = AsTreffles
            usrCards.append('CardAsTreffles')
            cpuCards.remove('CardAsTreffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardReineCarreaux':
            image2 = ReineCarreaux
            usrCards.append('CardReineCarreaux')
            cpuCards.remove('CardReineCarreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardReineCoeur':
            image2 = ReineCoeur
            usrCards.append('CardReineCoeur')
            cpuCards.remove('CardReineCoeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardReinePiques':
            image2 = ReinePiques
            usrCards.append('CardReinePiques')
            cpuCards.remove('CardReinePiques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardReineTreffles':
            image2 = ReineTreffles
            usrCards.append('CardReineTreffles')
            cpuCards.remove('CardReineTreffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardRoiCarreaux':
            image2 = RoiCarreaux
            usrCards.append('CardRoiCarreaux')
            cpuCards.remove('CardRoiCarreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardRoiCoeur':
            image2 = RoiCoeur
            usrCards.append('CardRoiCoeur')
            cpuCards.remove('CardRoiCoeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardRoiPiques':
            image2 = RoiPiques
            usrCards.append('CardRoiPiques')
            cpuCards.remove('CardRoiPiques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardRoiTreffles':
            image2 = RoiTreffles
            usrCards.append('CardRoiTreffles')
            cpuCards.remove('CardRoiTreffles')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardValetCarreaux':
            image2 = ValetCarreaux
            usrCards.append('CardValetCarreaux')
            cpuCards.remove('CardValetCarreaux')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardValetCoeur':
            image2 = ValetCoeur
            usrCards.append('CardValetCoeur')
            cpuCards.remove('CardValetCoeur')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardValetPiques':
            image2 = ValetPiques
            usrCards.append('CardValetPiques')
            cpuCards.remove('CardValetPiques')
            usrCards.extend(battleList)
        elif cpuCards[0] == 'CardValetTreffles':
            image2 = ValetTreffles
            usrCards.append('CardValetTreffles')
            cpuCards.remove('CardValetTreffles')
            usrCards.extend(battleList)
        battleList.clear()
        Image = image1,image2
        msg = "                    You win the battle, we continue the game\n\n\n              "+str("\n\n Your cards : ") + str(len(usrCards)) + str("\n\n\n Computer cards : ") + str(len(cpuCards))+str("\n\n\n           User cards                                    Computer cards")
        choices = ["Continue"]
        result = buttonbox(msg, image=Image, choices=choices)
        if result == "Continue":
            Game()

def Battle():
    global battleList, Cards2play, CardList, usrCards, cpuCards
    if cpuCards[0] == 'Card2carreaux':
        battleList.append('Card2carreaux')
        cpuCards.remove('Card2carreaux')
    elif cpuCards[0] == 'Card2coeur':
        battleList.append('Card2coeur')
        cpuCards.remove('Card2coeur')
    elif cpuCards[0] == 'Card2piques':
        battleList.append('Card2piques')
        cpuCards.remove('Card2piques')
    elif cpuCards[0] == 'Card2treffles':
        battleList.append('Card2treffles')
        cpuCards.remove('Card2treffles')
    elif cpuCards[0] == 'Card3carreaux':
        battleList.append('Card3carreaux')
        cpuCards.remove('Card3carreaux')
    elif cpuCards[0] == 'Card3coeur':
        battleList.append('Card3coeur')
        cpuCards.remove('Card3coeur')
    elif cpuCards[0] == 'Card3piques':
        battleList.append('Card3piques')
        cpuCards.remove('Card3piques')
    elif cpuCards[0] == 'Card3treffles':
        battleList.append('Card3treffles')
        cpuCards.remove('Card3treffles')
    elif cpuCards[0] == 'Card4carreaux':
        battleList.append('Card4carreaux')
        cpuCards.remove('Card4carreaux')
    elif cpuCards[0] == 'Card4coeur':
        battleList.append('Card4coeur')
        cpuCards.remove('Card4coeur')
    elif cpuCards[0] == 'Card4piques':
        battleList.append('Card4piques')
        cpuCards.remove('Card4piques')
    elif cpuCards[0] == 'Card4treffles':
        battleList.append('Card4treffles')
        cpuCards.remove('Card4treffles')
    elif cpuCards[0] == 'Card5carreaux':
        battleList.append('Card5carreaux')
        cpuCards.remove('Card5carreaux')
    elif cpuCards[0] == 'Card5coeur':
        battleList.append('Card5coeur')
        cpuCards.remove('Card5coeur')
    elif cpuCards[0] == 'Card5piques':
        battleList.append('Card5piques')
        cpuCards.remove('Card5piques')
    elif cpuCards[0] == 'Card5treffles':
        battleList.append('Card5treffles')
        cpuCards.remove('Card5treffles')
    elif cpuCards[0] == 'Card6carreaux':
        battleList.append('Card6carreaux')
        cpuCards.remove('Card6carreaux')
    elif cpuCards[0] == 'Card6coeur':
        battleList.append('Card6coeur')
        cpuCards.remove('Card6coeur')
    elif cpuCards[0] == 'Card6treffles':
        battleList.append('Card6treffles')
        cpuCards.remove('Card6treffles')
    elif cpuCards[0] == 'Card6piques':
        battleList.append('Card6piques')
        cpuCards.remove('Card6piques')
    elif cpuCards[0] == 'Card7carreaux':
        battleList.append('Card7carreaux')
        cpuCards.remove('Card7carreaux')
    elif cpuCards[0] == 'Card7coeur':
        battleList.append('Card7coeur')
        cpuCards.remove('Card7coeur')
    elif cpuCards[0] == 'Card7piques':
        battleList.append('Card7piques')
        cpuCards.remove('Card7piques')
    elif cpuCards[0] == 'Card7treffles':
        battleList.append('Card7treffles')
        cpuCards.remove('Card7treffles')
    elif cpuCards[0] == 'Card8carreaux':
        battleList.append('Card8carreaux')
        cpuCards.remove('Card8carreaux')
    elif cpuCards[0] == 'Card8coeur':
        battleList.append('Card8coeur')
        cpuCards.remove('Card8coeur')
    elif cpuCards[0] == 'Card8piques':
        battleList.append('Card8piques')
        cpuCards.remove('Card8piques')
    elif cpuCards[0] == 'Card8treffles':
        battleList.append('Card8treffles')
        cpuCards.remove('Card8treffles')
    elif cpuCards[0] == 'Card9carreaux':
        battleList.append('Card9carreaux')
        cpuCards.remove('Card9carreaux')
    elif cpuCards[0] == 'Card9coeur':
        battleList.append('Card9coeur')
        cpuCards.remove('Card9coeur')
    elif cpuCards[0] == 'Card9piques':
        battleList.append('Card9piques')
        cpuCards.remove('Card9piques')
    elif cpuCards[0] == 'Card9treffles':
        battleList.append('Card9treffles')
        cpuCards.remove('Card9treffles')
    elif cpuCards[0] == 'Card10carreaux':
        battleList.append('Card10carreaux')
        cpuCards.remove('Card10carreaux')
    elif cpuCards[0] == 'Card10coeur':
        battleList.append('Card10coeur')
        cpuCards.remove('Card10coeur')
    elif cpuCards[0] == 'Card10piques':
        battleList.append('Card10piques')
        cpuCards.remove('Card10piques')
    elif cpuCards[0] == 'Card10treffles':
        battleList.append('Card10treffles')
        cpuCards.remove('Card10treffles')
    elif cpuCards[0] == 'CardAsCarreaux':
        battleList.append('CardAsCarreaux')
        cpuCards.remove('CardAsCarreaux')
    elif cpuCards[0] == 'CardAsCoeur':
        battleList.append('CardAsCoeur')
        cpuCards.remove('CardAsCoeur')
    elif cpuCards[0] == 'CardAsPiques':
        battleList.append('CardAsPiques')
        cpuCards.remove('CardAsPiques')
    elif cpuCards[0] == 'CardAsTreffles':
        battleList.append('CardAsTreffles')
        cpuCards.remove('CardAsTreffles')
    elif cpuCards[0] == 'CardReineCarreaux':
        battleList.append('CardReineCarreaux')
        cpuCards.remove('CardReineCarreaux')
    elif cpuCards[0] == 'CardReineCoeur':
        battleList.append('CardReineCoeur')
        cpuCards.remove('CardReineCoeur')
    elif cpuCards[0] == 'CardReinePiques':
        battleList.append('CardReinePiques')
        cpuCards.remove('CardReinePiques')
    elif cpuCards[0] == 'CardReineTreffles':
        battleList.append('CardReineTreffles')
        cpuCards.remove('CardReineTreffles')
    elif cpuCards[0] == 'CardRoiCarreaux':
        battleList.append('CardRoiCarreaux')
        cpuCards.remove('CardRoiCarreaux')
    elif cpuCards[0] == 'CardRoiCoeur':
        battleList.append('CardRoiCoeur')
        cpuCards.remove('CardRoiCoeur')
    elif cpuCards[0] == 'CardRoiPiques':
        battleList.append('CardRoiPiques')
        cpuCards.remove('CardRoiPiques')
    elif cpuCards[0] == 'CardRoiTreffles':
        battleList.append('CardRoiTreffles')
        cpuCards.remove('CardRoiTreffles')
    elif cpuCards[0] == 'CardValetCarreaux':
        battleList.append('CardValetCarreaux')
        cpuCards.remove('CardValetCarreaux')
    elif cpuCards[0] == 'CardValetCoeur':
        battleList.append('CardValetCoeur')
        cpuCards.remove('CardValetCoeur')
    elif cpuCards[0] == 'CardValetPiques':
        battleList.append('CardValetPiques')
        cpuCards.remove('CardValetPiques')
    elif cpuCards[0] == 'CardValetTreffles':
        battleList.append('CardValetTreffles')
        cpuCards.remove('CardValetTreffles')
    if usrCards[0] == 'Card2carreaux':
        battleList.append('Card2carreaux')
        usrCards.remove('Card2carreaux')
    elif usrCards[0] == 'Card2coeur':
        battleList.append('Card2coeur')
        usrCards.remove('Card2coeur')
    elif usrCards[0] == 'Card2piques':
        battleList.append('Card2piques')
        usrCards.remove('Card2piques')
    elif usrCards[0] == 'Card2treffles':
        battleList.append('Card2treffles')
        usrCards.remove('Card2treffles')
    elif usrCards[0] == 'Card3carreaux':
        battleList.append('Card3carreaux')
        usrCards.remove('Card3carreaux')
    elif usrCards[0] == 'Card3coeur':
        battleList.append('Card3coeur')
        usrCards.remove('Card3coeur')
    elif usrCards[0] == 'Card3piques':
        battleList.append('Card3piques')
        usrCards.remove('Card3piques')
    elif usrCards[0] == 'Card3treffles':
        battleList.append('Card3treffles')
        usrCards.remove('Card3treffles')
    elif usrCards[0] == 'Card4carreaux':
        battleList.append('Card4carreaux')
        usrCards.remove('Card4carreaux')
    elif usrCards[0] == 'Card4coeur':
        battleList.append('Card4coeur')
        usrCards.remove('Card4coeur')
    elif usrCards[0] == 'Card4piques':
        battleList.append('Card4piques')
        usrCards.remove('Card4piques')
    elif usrCards[0] == 'Card4treffles':
        battleList.append('Card4treffles')
        usrCards.remove('Card4treffles')
    elif usrCards[0] == 'Card5carreaux':
        battleList.append('Card5carreaux')
        usrCards.remove('Card5carreaux')
    elif usrCards[0] == 'Card5coeur':
        battleList.append('Card5coeur')
        usrCards.remove('Card5coeur')
    elif usrCards[0] == 'Card5piques':
        battleList.append('Card5piques')
        usrCards.remove('Card5piques')
    elif usrCards[0] == 'Card5treffles':
        battleList.append('Card5treffles')
        usrCards.remove('Card5treffles')
    elif usrCards[0] == 'Card6carreaux':
        battleList.append('Card6carreaux')
        usrCards.remove('Card6carreaux')
    elif usrCards[0] == 'Card6coeur':
        battleList.append('Card6coeur')
        usrCards.remove('Card6coeur')
    elif usrCards[0] == 'Card6treffles':
        battleList.append('Card6treffles')
        usrCards.remove('Card6treffles')
    elif usrCards[0] == 'Card6piques':
        battleList.append('Card6piques')
        usrCards.remove('Card6piques')
    elif usrCards[0] == 'Card7carreaux':
        battleList.append('Card7carreaux')
        usrCards.remove('Card7carreaux')
    elif usrCards[0] == 'Card7coeur':
        battleList.append('Card7coeur')
        usrCards.remove('Card7coeur')
    elif usrCards[0] == 'Card7piques':
        battleList.append('Card7piques')
        usrCards.remove('Card7piques')
    elif usrCards[0] == 'Card7treffles':
        battleList.append('Card7treffles')
        usrCards.remove('Card7treffles')
    elif usrCards[0] == 'Card8carreaux':
        battleList.append('Card8carreaux')
        usrCards.remove('Card8carreaux')
    elif usrCards[0] == 'Card8coeur':
        battleList.append('Card8coeur')
        usrCards.remove('Card8coeur')
    elif usrCards[0] == 'Card8piques':
        battleList.append('Card8piques')
        usrCards.remove('Card8piques')
    elif usrCards[0] == 'Card8treffles':
        battleList.append('Card8treffles')
        usrCards.remove('Card8treffles')
    elif usrCards[0] == 'Card9carreaux':
        battleList.append('Card9carreaux')
        usrCards.remove('Card9carreaux')
    elif usrCards[0] == 'Card9coeur':
        battleList.append('Card9coeur')
        usrCards.remove('Card9coeur')
    elif usrCards[0] == 'Card9piques':
        battleList.append('Card9piques')
        usrCards.remove('Card9piques')
    elif usrCards[0] == 'Card9treffles':
        battleList.append('Card9treffles')
        usrCards.remove('Card9treffles')
    elif usrCards[0] == 'Card10carreaux':
        battleList.append('Card10carreaux')
        usrCards.remove('Card10carreaux')
    elif usrCards[0] == 'Card10coeur':
        battleList.append('Card10coeur')
        usrCards.remove('Card10coeur')
    elif usrCards[0] == 'Card10piques':
        battleList.append('Card10piques')
        usrCards.remove('Card10piques')
    elif usrCards[0] == 'Card10treffles':
        battleList.append('Card10treffles')
        usrCards.remove('Card10treffles')
    elif usrCards[0] == 'CardAsCarreaux':
        battleList.append('CardAsCarreaux')
        usrCards.remove('CardAsCarreaux')
    elif usrCards[0] == 'CardAsCoeur':
        battleList.append('CardAsCoeur')
        usrCards.remove('CardAsCoeur')
    elif usrCards[0] == 'CardAsPiques':
        battleList.append('CardAsPiques')
        usrCards.remove('CardAsPiques')
    elif usrCards[0] == 'CardAsTreffles':
        battleList.append('CardAsTreffles')
        usrCards.remove('CardAsTreffles')
    elif usrCards[0] == 'CardReineCarreaux':
        battleList.append('CardReineCarreaux')
        usrCards.remove('CardReineCarreaux')
    elif usrCards[0] == 'CardReineCoeur':
        battleList.append('CardReineCoeur')
        usrCards.remove('CardReineCoeur')
    elif usrCards[0] == 'CardReinePiques':
        battleList.append('CardReinePiques')
        usrCards.remove('CardReinePiques')
    elif usrCards[0] == 'CardReineTreffles':
        battleList.append('CardReineTreffles')
        usrCards.remove('CardReineTreffles')
    elif usrCards[0] == 'CardRoiCarreaux':
        battleList.append('CardRoiCarreaux')
        usrCards.remove('CardRoiCarreaux')
    elif usrCards[0] == 'CardRoiCoeur':
        battleList.append('CardRoiCoeur')
        usrCards.remove('CardRoiCoeur')
    elif usrCards[0] == 'CardRoiPiques':
        battleList.append('CardRoiPiques')
        usrCards.remove('CardRoiPiques')
    elif usrCards[0] == 'CardRoiTreffles':
        battleList.append('CardRoiTreffles')
        usrCards.remove('CardRoiTreffles')
    elif usrCards[0] == 'CardValetCarreaux':
        battleList.append('CardValetCarreaux')
        usrCards.remove('CardValetCarreaux')
    elif usrCards[0] == 'CardValetCoeur':
        battleList.append('CardValetCoeur')
        usrCards.remove('CardValetCoeur')
    elif usrCards[0] == 'CardValetPiques':
        battleList.append('CardValetPiques')
        usrCards.remove('CardValetPiques')
    elif usrCards[0] == 'CardValetTreffles':
        battleList.append('CardValetTreffles')
        usrCards.remove('CardValetTreffles')
    GameBattle()



def Game():
    global usrCards, cpuCards, battleList, CardList, Cards2play, image1, image2
    random.shuffle(cpuCards)
    random.shuffle(usrCards)

    if len(usrCards) == 0:
        msg = "\n\n\n                   You lose ! The computer have all your cards !"
        choices = ["OK"]
        result = buttonbox(msg, image=piclose, choices=choices)
        if result == "OK":
            sys.exit(0)
        else:
            sys.exit(0)

    elif len(cpuCards) == 0:
        msg = "\n\n\n                   You win ! the computer don't have any card !"
        choices = ["OK"]
        result = buttonbox(msg, image=picwin, choices=choices)
        if result == "OK":
            sys.exit(0)
        else:
            sys.exit(0)


    if CardList[usrCards[0]] < CardList[cpuCards[0]]:
        print("usrCard = " + str(usrCards[0]))
        print("cpuCard = " + str(cpuCards[0]))

        if usrCards[0] == 'Card2carreaux':
            image1 = Pic2carreaux
            cpuCards.append('Card2carreaux')
            usrCards.remove('Card2carreaux')
        elif usrCards[0] == 'Card2coeur':
            image1 = Pic2coeur
            cpuCards.append('Card2coeur')

            usrCards.remove('Card2coeur')
        elif usrCards[0] == 'Card2piques':
            image1 = Pic2piques
            cpuCards.append('Card2piques')

            usrCards.remove('Card2piques')
        elif usrCards[0] == 'Card2treffles':
            image1 = Pic2treffles
            cpuCards.append('Card2treffles')

            usrCards.remove('Card2treffles')
        elif usrCards[0] == 'Card3carreaux':
            image1 = Pic3carreaux
            cpuCards.append('Card3carreaux')

            usrCards.remove('Card3carreaux')
        elif usrCards[0] == 'Card3coeur':
            image1 = Pic3coeur
            cpuCards.append('Card3coeur')

            usrCards.remove('Card3coeur')
        elif usrCards[0] == 'Card3piques':
            image1 = Pic3piques
            cpuCards.append('Card3piques')

            usrCards.remove('Card3piques')
        elif usrCards[0] == 'Card3treffles':
            image1 = Pic3treffles
            cpuCards.append('Card3treffles')

            usrCards.remove('Card3treffles')
        elif usrCards[0] == 'Card4carreaux':
            image1 = Pic4carreaux
            cpuCards.append('Card4carreaux')

            usrCards.remove('Card4carreaux')
        elif usrCards[0] == 'Card4coeur':
            image1 = Pic4coeur
            cpuCards.append('Card4coeur')

            usrCards.remove('Card4coeur')
        elif usrCards[0] == 'Card4piques':
            image1 = Pic4piques
            cpuCards.append('Card4piques')

            usrCards.remove('Card4piques')
        elif usrCards[0] == 'Card4treffles':
            image1 = Pic4treffles
            cpuCards.append('Card4treffles')

            usrCards.remove('Card4treffles')
        elif usrCards[0] == 'Card5carreaux':
            image1 = Pic5carreaux
            cpuCards.append('Card5carreaux')
            usrCards.remove('Card5carreaux')
        elif usrCards[0] == 'Card5coeur':
            image1 = Pic5coeur
            cpuCards.append('Card5coeur')

            usrCards.remove('Card5coeur')
        elif usrCards[0] == 'Card5piques':
            image1 = Pic5piques
            cpuCards.append('Card5piques')
            usrCards.remove('Card5piques')
        elif usrCards[0] == 'Card5treffles':
            image1 = Pic5treffles
            cpuCards.append('Card5treffles')

            usrCards.remove('Card5treffles')
        elif usrCards[0] == 'Card6carreaux':
            image1 = Pic6carreaux
            cpuCards.append('Card6carreaux')

            usrCards.remove('Card6carreaux')
        elif usrCards[0] == 'Card6coeur':
            image1 = Pic6coeur
            cpuCards.append('Card6coeur')

            usrCards.remove('Card6coeur')
        elif usrCards[0] == 'Card6treffles':
            image1 = Pic6treffles
            cpuCards.append('Card6treffles')

            usrCards.remove('Card6treffles')
        elif usrCards[0] == 'Card6piques':
            image1 = Pic6piques
            cpuCards.append('Card6piques')

            usrCards.remove('Card6piques')
        elif usrCards[0] == 'Card7carreaux':
            image1 = Pic7carreaux
            cpuCards.append('Card7carreaux')
            usrCards.remove('Card7carreaux')
        elif usrCards[0] == 'Card7coeur':
            image1 = Pic7coeur
            cpuCards.append('Card7coeur')

            usrCards.remove('Card7coeur')
        elif usrCards[0] == 'Card7piques':
            image1 = Pic7piques
            cpuCards.append('Card7piques')

            usrCards.remove('Card7piques')
        elif usrCards[0] == 'Card7treffles':
            image1 = Pic7treffles
            cpuCards.append('Card7treffles')

            usrCards.remove('Card7treffles')
        elif usrCards[0] == 'Card8carreaux':
            image1 = Pic8carreaux
            cpuCards.append('Card8carreaux')

            usrCards.remove('Card8carreaux')
        elif usrCards[0] == 'Card8treffles':
            image1 = Pic8treffles
            cpuCards.append('Card8treffles')

            usrCards.remove('Card8treffles')
        elif usrCards[0] == 'Card8piques':
            image1 = Pic8piques
            cpuCards.append('Card8piques')

            usrCards.remove('Card8piques')
        elif usrCards[0] == 'Card8coeur':
            image1 = Pic8coeur
            cpuCards.append('Card8coeur')

            usrCards.remove('Card8coeur')
        elif usrCards[0] == 'Card9carreaux':
            image1 = Pic9carreaux
            cpuCards.append('Card9carreaux')

            usrCards.remove('Card9carreaux')
        elif usrCards[0] == 'Card9coeur':
            image1 = Pic9coeur
            cpuCards.append('Card9coeur')
            usrCards.remove('Card9coeur')
        elif usrCards[0] == 'Card9piques':
            image1 = Pic9piques
            cpuCards.append('Card9piques')

            usrCards.remove('Card9piques')
        elif usrCards[0] == 'Card9treffles':
            image1 = Pic9treffles
            cpuCards.append('Card9treffles')

            usrCards.remove('Card9treffles')
        elif usrCards[0] == 'Card10carreaux':
            image1 = Pic10carreaux
            cpuCards.append('Card10carreaux')

            usrCards.remove('Card10carreaux')
        elif usrCards[0] == 'Card10coeur':
            image1 = Pic10coeur
            cpuCards.append('Card10coeur')

            usrCards.remove('Card10coeur')
        elif usrCards[0] == 'Card10piques':
            image1 = Pic10piques
            cpuCards.append('Card10piques')

            usrCards.remove('Card10piques')
        elif usrCards[0] == 'Card10treffles':
            image1 = Pic10treffles
            cpuCards.append('Card10treffles')

            usrCards.remove('Card10treffles')
        elif usrCards[0] == 'CardAsCarreaux':
            image1 = AsCarreaux
            cpuCards.append('CardAsCarreaux')

            usrCards.remove('CardAsCarreaux')
        elif usrCards[0] == 'CardAsCoeur':
            image1 = AsCoeur
            cpuCards.append('CardAsCoeur')

            usrCards.remove('CardAsCoeur')
        elif usrCards[0] == 'CardAsPiques':
            image1 = AsPiques
            cpuCards.append('CardAsPiques')

            usrCards.remove('CardAsPiques')
        elif usrCards[0] == 'CardAsTreffles':
            image1 = AsTreffles
            cpuCards.append('CardAsTreffles')

            usrCards.remove('CardAsTreffles')
        elif usrCards[0] == 'CardReineCarreaux':
            image1 = ReineCarreaux
            cpuCards.append('CardReineCarreaux')

            usrCards.remove('CardReineCarreaux')
        elif usrCards[0] == 'CardReineCoeur':
            image1 = ReineCoeur
            cpuCards.append('CardReineCoeur')

            usrCards.remove('CardReineCoeur')
        elif usrCards[0] == 'CardReinePiques':
            image1 = ReinePiques
            cpuCards.append('CardReinePiques')

            usrCards.remove('CardReinePiques')
        elif usrCards[0] == 'CardReineTreffles':
            image1 = ReineTreffles
            cpuCards.append('CardReineTreffles')

            usrCards.remove('CardReineTreffles')
        elif usrCards[0] == 'CardRoiCarreaux':
            image1 = RoiCarreaux
            cpuCards.append('CardRoiCarreaux')

            usrCards.remove('CardRoiCarreaux')
        elif usrCards[0] == 'CardRoiCoeur':
            image1 = RoiCoeur
            cpuCards.append('CardRoiCoeur')
            usrCards.remove('CardRoiCoeur')
        elif usrCards[0] == 'CardRoiPiques':
            image1 = RoiPiques
            cpuCards.append('CardRoiPiques')

            usrCards.remove('CardRoiPiques')
        elif usrCards[0] == 'CardRoiTreffles':
            image1 = RoiTreffles
            cpuCards.append('CardRoiTreffles')
            usrCards.remove('CardRoiTreffles')
        elif usrCards[0] == 'CardValetCarreaux':
            image1 = ValetCarreaux
            cpuCards.append('CardValetCarreaux')
            usrCards.remove('CardValetCarreaux')
        elif usrCards[0] == 'CardValetCoeur':
            image1 = ValetCoeur
            cpuCards.append('CardValetCoeur')

            usrCards.remove('CardValetCoeur')
        elif usrCards[0] == 'CardValetPiques':
            image1 = ValetPiques
            cpuCards.append('CardValetPiques')

            usrCards.remove('CardValetPiques')
        elif usrCards[0] == 'CardValetTreffles':
            image1 = ValetTreffles
            cpuCards.append('CardValetTreffles')

            usrCards.remove('CardValetTreffles')

        if cpuCards[0] == 'Card2carreaux':
            image2 = Pic2carreaux
        elif cpuCards[0] == 'Card2coeur':
            image2 = Pic2coeur
        elif cpuCards[0] == 'Card2piques':
            image2 = Pic2piques
        elif cpuCards[0] == 'Card2treffles':
            image2 = Pic2treffles
        elif cpuCards[0] == 'Card3carreaux':
            image2 = Pic3carreaux
        elif cpuCards[0] == 'Card3coeur':
            image2 = Pic3coeur
        elif cpuCards[0] == 'Card3piques':
            image2 = Pic3piques
        elif cpuCards[0] == 'Card3treffles':
            image2 = Pic3treffles
        elif cpuCards[0] == 'Card4carreaux':
            image2 = Pic4carreaux
        elif cpuCards[0] == 'Card4coeur':
            image2 = Pic4coeur
        elif cpuCards[0] == 'Card4piques':
            image2 = Pic4piques
        elif cpuCards[0] == 'Card4treffles':
            image2 = Pic4treffles
        elif cpuCards[0] == 'Card5carreaux':
            image2 = Pic5carreaux
        elif cpuCards[0] == 'Card5coeur':
            image2 = Pic5coeur
        elif cpuCards[0] == 'Card5piques':
            image2 = Pic5piques
        elif cpuCards[0] == 'Card5treffles':
            image2 = Pic5treffles
        elif cpuCards[0] == 'Card6carreaux':
            image2 = Pic6carreaux
        elif cpuCards[0] == 'Card6coeur':
            image2 = Pic6coeur
        elif cpuCards[0] == 'Card6treffles':
            image2 = Pic6treffles
        elif cpuCards[0] == 'Card6piques':
            image2 = Pic6piques
        elif cpuCards[0] == 'Card7carreaux':
            image2 = Pic7carreaux
        elif cpuCards[0] == 'Card7coeur':
            image2 = Pic7coeur
        elif cpuCards[0] == 'Card7piques':
            image2 = Pic7piques
        elif cpuCards[0] == 'Card7treffles':
            image2 = Pic7treffles
        elif cpuCards[0] == 'Card8carreaux':
            image2 = Pic8carreaux
        elif cpuCards[0] == 'Card8treffles':
            image2 = Pic8treffles
        elif cpuCards[0] == 'Card8piques':
            image2 = Pic8piques
        elif cpuCards[0] == 'Card8coeur':
            image2 = Pic8coeur
        elif cpuCards[0] == 'Card9carreaux':
            image2 = Pic9carreaux
        elif cpuCards[0] == 'Card9coeur':
            image2 = Pic9coeur
        elif cpuCards[0] == 'Card9piques':
            image2 = Pic9piques
        elif cpuCards[0] == 'Card9treffles':
            image2 = Pic9treffles
        elif cpuCards[0] == 'Card10carreaux':
            image2 = Pic10carreaux
        elif cpuCards[0] == 'Card10coeur':
            image2 = Pic10coeur
        elif cpuCards[0] == 'Card10piques':
            image2 = Pic10piques
        elif cpuCards[0] == 'Card10treffles':
            image2 = Pic10treffles
        elif cpuCards[0] == 'CardAsCarreaux':
            image2 = AsCarreaux
        elif cpuCards[0] == 'CardAsCoeur':
            image2 = AsCoeur
        elif cpuCards[0] == 'CardAsPiques':
            image2 = AsPiques
        elif cpuCards[0] == 'CardAsTreffles':
            image2 = AsTreffles
        elif cpuCards[0] == 'CardReineCarreaux':
            image2 = ReineCarreaux
        elif cpuCards[0] == 'CardReineCoeur':
            image2 = ReineCoeur
        elif cpuCards[0] == 'CardReinePiques':
            image2 = ReinePiques
        elif cpuCards[0] == 'CardReineTreffles':
            image2 = ReineTreffles
        elif cpuCards[0] == 'CardRoiCarreaux':
            image2 = RoiCarreaux
        elif cpuCards[0] == 'CardRoiCoeur':
            image2 = RoiCoeur
        elif cpuCards[0] == 'CardRoiPiques':
            image2 = RoiPiques
        elif cpuCards[0] == 'CardRoiTreffles':
            image2 = RoiTreffles
        elif cpuCards[0] == 'CardValetCarreaux':
            image2 = ValetCarreaux
        elif cpuCards[0] == 'CardValetCoeur':
            image2 = ValetCoeur
        elif cpuCards[0] == 'CardValetPiques':
            image2 = ValetPiques
        elif cpuCards[0] == 'CardValetTreffles':
            image2 = ValetTreffles


        Image = image1,image2
        msg =  msg = "                              You lose\n\n\n              "+str("\n\n Your cards : ") + str(len(usrCards)) + str("\n\n\n Computer cards : ") + str(len(cpuCards))+str("\n\n\n           User cards                                    Computer cards")
        choices = ["Continue"]
        result = buttonbox(msg, image=Image, choices=choices)
        if result == "Continue":
            Game()

    elif CardList[usrCards[0]] > CardList[cpuCards[0]]:
        print("usrCard = " + str(usrCards[0]))
        print("cpuCard = " + str(cpuCards[0]))

        if usrCards[0] == 'Card2carreaux':
            image1 = Pic2carreaux
        elif usrCards[0] == 'Card2coeur':
            image1 = Pic2coeur
        elif usrCards[0] == 'Card2piques':
            image1 = Pic2piques
        elif usrCards[0] == 'Card2treffles':
            image1 = Pic2treffles
        elif usrCards[0] == 'Card3carreaux':
            image1 = Pic3carreaux
        elif usrCards[0] == 'Card3coeur':
            image1 = Pic3coeur
        elif usrCards[0] == 'Card3piques':
            image1 = Pic3piques
        elif usrCards[0] == 'Card3treffles':
            image1 = Pic3treffles
        elif usrCards[0] == 'Card4carreaux':
            image1 = Pic4carreaux
        elif usrCards[0] == 'Card4coeur':
            image1 = Pic4coeur
        elif usrCards[0] == 'Card4piques':
            image1 = Pic4piques
        elif usrCards[0] == 'Card4treffles':
            image1 = Pic4treffles
        elif usrCards[0] == 'Card5carreaux':
            image1 = Pic5carreaux
        elif usrCards[0] == 'Card5coeur':
            image1 = Pic5coeur
        elif usrCards[0] == 'Card5piques':
            image1 = Pic5piques
        elif usrCards[0] == 'Card5treffles':
            image1 = Pic5treffles
        elif usrCards[0] == 'Card6carreaux':
            image1 = Pic6carreaux
        elif usrCards[0] == 'Card6coeur':
            image1 = Pic6coeur
        elif usrCards[0] == 'Card6treffles':
            image1 = Pic6treffles
        elif usrCards[0] == 'Card6piques':
            image1 = Pic6piques
        elif usrCards[0] == 'Card7carreaux':
            image1 = Pic7carreaux
        elif usrCards[0] == 'Card7coeur':
            image1 = Pic7coeur
        elif usrCards[0] == 'Card7piques':
            image1 = Pic7piques
        elif usrCards[0] == 'Card7treffles':
            image1 = Pic7treffles
        elif usrCards[0] == 'Card8carreaux':
            image1 = Pic8carreaux
        elif usrCards[0] == 'Card8treffles':
            image1 = Pic8treffles
        elif usrCards[0] == 'Card8piques':
            image1 = Pic8piques
        elif usrCards[0] == 'Card8coeur':
            image1 = Pic8coeur
        elif usrCards[0] == 'Card9carreaux':
            image1 = Pic9carreaux
        elif usrCards[0] == 'Card9coeur':
            image1 = Pic9coeur
        elif usrCards[0] == 'Card9piques':
            image1 = Pic9piques
        elif usrCards[0] == 'Card9treffles':
            image1 = Pic9treffles
        elif usrCards[0] == 'Card10carreaux':
            image1 = Pic10carreaux
        elif usrCards[0] == 'Card10coeur':
            image1 = Pic10coeur
        elif usrCards[0] == 'Card10piques':
            image1 = Pic10piques
        elif usrCards[0] == 'Card10treffles':
            image1 = Pic10treffles
        elif usrCards[0] == 'CardAsCarreaux':
            image1 = AsCarreaux
        elif usrCards[0] == 'CardAsCoeur':
            image1 = AsCoeur
        elif usrCards[0] == 'CardAsPiques':
            image1 = AsPiques
        elif usrCards[0] == 'CardAsTreffles':
            image1 = AsTreffles
        elif usrCards[0] == 'CardReineCarreaux':
            image1 = ReineCarreaux
        elif usrCards[0] == 'CardReineCoeur':
            image1 = ReineCoeur
        elif usrCards[0] == 'CardReinePiques':
            image1 = ReinePiques
        elif usrCards[0] == 'CardReineTreffles':
            image1 = ReineTreffles
        elif usrCards[0] == 'CardRoiCarreaux':
            image1 = RoiCarreaux
        elif usrCards[0] == 'CardRoiCoeur':
            image1 = RoiCoeur
        elif usrCards[0] == 'CardRoiPiques':
            image1 = RoiPiques
        elif usrCards[0] == 'CardRoiTreffles':
            image1 = RoiTreffles
        elif usrCards[0] == 'CardValetCarreaux':
            image1 = ValetCarreaux
        elif usrCards[0] == 'CardValetCoeur':
            image1 = ValetCoeur
        elif usrCards[0] == 'CardValetPiques':
            image1 = ValetPiques
        elif usrCards[0] == 'CardValetTreffles':
            image1 = ValetTreffles

        if cpuCards[0] == 'Card2carreaux':
            image2 = Pic2carreaux
            usrCards.append('Card2carreaux')
            cpuCards.remove('Card2carreaux')
        elif cpuCards[0] == 'Card2coeur':
            image2 = Pic2coeur
            usrCards.append('Card2coeur')
            cpuCards.remove('Card2coeur')
        elif cpuCards[0] == 'Card2piques':
            image2 = Pic2piques
            usrCards.append('Card2piques')
            cpuCards.remove('Card2piques')
        elif cpuCards[0] == 'Card2treffles':
            image2 = Pic2treffles
            usrCards.append('Card2treffles')
            cpuCards.remove('Card2treffles')
        elif cpuCards[0] == 'Card3carreaux':
            image2 = Pic3carreaux
            usrCards.append('Card3carreaux')
            cpuCards.remove('Card3carreaux')
        elif cpuCards[0] == 'Card3coeur':
            image2 = Pic3coeur
            usrCards.append('Card3coeur')
            cpuCards.remove('Card3coeur')
        elif cpuCards[0] == 'Card3piques':
            image2 = Pic3piques
            usrCards.append('Card3piques')
            cpuCards.remove('Card3piques')
        elif cpuCards[0] == 'Card3treffles':
            image2 = Pic3treffles
            usrCards.append('Card3treffles')
            cpuCards.remove('Card3treffles')
        elif cpuCards[0] == 'Card4carreaux':
            image2 = Pic4carreaux
            usrCards.append('Card4carreaux')
            cpuCards.remove('Card4carreaux')
        elif cpuCards[0] == 'Card4coeur':
            image2 = Pic4coeur
            usrCards.append('Card4coeur')
            cpuCards.remove('Card4coeur')
        elif cpuCards[0] == 'Card4piques':
            image2 = Pic4piques
            usrCards.append('Card4piques')
            cpuCards.remove('Card4piques')
        elif cpuCards[0] == 'Card4treffles':
            image2 = Pic4treffles
            usrCards.append('Card4treffles')
            cpuCards.remove('Card4treffles')
        elif cpuCards[0] == 'Card5carreaux':
            image2 = Pic5carreaux
            usrCards.append('Card5carreaux')
            cpuCards.remove('Card5carreaux')
        elif cpuCards[0] == 'Card5coeur':
            image2 = Pic5coeur
            usrCards.append('Card5coeur')
            cpuCards.remove('Card5coeur')
        elif cpuCards[0] == 'Card5piques':
            image2 = Pic5piques
            usrCards.append('Card5piques')
            cpuCards.remove('Card5piques')
        elif cpuCards[0] == 'Card5treffles':
            image2 = Pic5treffles
            usrCards.append('Card5treffles')
            cpuCards.remove('Card5treffles')
        elif cpuCards[0] == 'Card6carreaux':
            image2 = Pic6carreaux
            usrCards.append('Card6carreaux')
            cpuCards.remove('Card6carreaux')
        elif cpuCards[0] == 'Card6coeur':
            image2 = Pic6coeur
            usrCards.append('Card6coeur')
            cpuCards.remove('Card6coeur')
        elif cpuCards[0] == 'Card6treffles':
            image2 = Pic6treffles
            usrCards.append('Card6treffles')
            cpuCards.remove('Card6treffles')
        elif cpuCards[0] == 'Card6piques':
            image2 = Pic6piques
            usrCards.append('Card6piques')
            cpuCards.remove('Card6piques')
        elif cpuCards[0] == 'Card7carreaux':
            image2 = Pic7carreaux
            usrCards.append('Card7carreaux')
            cpuCards.remove('Card7carreaux')
        elif cpuCards[0] == 'Card7coeur':
            image2 = Pic7coeur
            usrCards.append('Card7coeur')
            cpuCards.remove('Card7coeur')
        elif cpuCards[0] == 'Card7piques':
            image2 = Pic7piques
            usrCards.append('Card7piques')
            cpuCards.remove('Card7piques')
        elif cpuCards[0] == 'Card7treffles':
            image2 = Pic7treffles
            usrCards.append('Card7treffles')
            cpuCards.remove('Card7treffles')
        elif cpuCards[0] == 'Card8carreaux':
            image2 = Pic8carreaux
            usrCards.append('Card8carreaux')
            cpuCards.remove('Card8carreaux')
        elif cpuCards[0] == 'Card8treffles':
            image2 = Pic8treffles
            usrCards.append('Card8treffles')
            cpuCards.remove('Card8treffles')
        elif cpuCards[0] == 'Card8piques':
            image2 = Pic8piques
            usrCards.append('Card8piques')
            cpuCards.remove('Card8piques')
        elif cpuCards[0] == 'Card8coeur':
            image2 = Pic8coeur
            usrCards.append('Card8coeur')
            cpuCards.remove('Card8coeur')
        elif cpuCards[0] == 'Card9carreaux':
            image2 = Pic9carreaux
            usrCards.append('Card9carreaux')
            cpuCards.remove('Card9carreaux')
        elif cpuCards[0] == 'Card9coeur':
            image2 = Pic9coeur
            usrCards.append('Card9coeur')
            cpuCards.remove('Card9coeur')
        elif cpuCards[0] == 'Card9piques':
            image2 = Pic9piques
            usrCards.append('Card9piques')
            cpuCards.remove('Card9piques')
        elif cpuCards[0] == 'Card9treffles':
            image2 = Pic9treffles
            usrCards.append('Card9treffles')
            cpuCards.remove('Card9treffles')
        elif cpuCards[0] == 'Card10carreaux':
            image2 = Pic10carreaux
            usrCards.append('Card10carreaux')
            cpuCards.remove('Card10carreaux')
        elif cpuCards[0] == 'Card10coeur':
            image2 = Pic10coeur
            usrCards.append('Card10coeur')
            cpuCards.remove('Card10coeur')
        elif cpuCards[0] == 'Card10piques':
            image2 = Pic10piques
            usrCards.append('Card10piques')
            cpuCards.remove('Card10piques')
        elif cpuCards[0] == 'Card10treffles':
            image2 = Pic10treffles
            usrCards.append('Card10treffles')
            cpuCards.remove('Card10treffles')
        elif cpuCards[0] == 'CardAsCarreaux':
            image2 = AsCarreaux
            usrCards.append('CardAsCarreaux')
            cpuCards.remove('CardAsCarreaux')
        elif cpuCards[0] == 'CardAsCoeur':
            image2 = AsCoeur
            usrCards.append('CardAsCoeur')
            cpuCards.remove('CardAsCoeur')
        elif cpuCards[0] == 'CardAsPiques':
            image2 = AsPiques
            usrCards.append('CardAsPiques')
            cpuCards.remove('CardAsPiques')
        elif cpuCards[0] == 'CardAsTreffles':
            image2 = AsTreffles
            usrCards.append('CardAsTreffles')
            cpuCards.remove('CardAsTreffles')
        elif cpuCards[0] == 'CardReineCarreaux':
            image2 = ReineCarreaux
            usrCards.append('CardReineCarreaux')
            cpuCards.remove('CardReineCarreaux')
        elif cpuCards[0] == 'CardReineCoeur':
            image2 = ReineCoeur
            usrCards.append('CardReineCoeur')
            cpuCards.remove('CardReineCoeur')
        elif cpuCards[0] == 'CardReinePiques':
            image2 = ReinePiques
            usrCards.append('CardReinePiques')
            cpuCards.remove('CardReinePiques')
        elif cpuCards[0] == 'CardReineTreffles':
            image2 = ReineTreffles
            usrCards.append('CardReineTreffles')
            cpuCards.remove('CardReineTreffles')
        elif cpuCards[0] == 'CardRoiCarreaux':
            image2 = RoiCarreaux
            usrCards.append('CardRoiCarreaux')
            cpuCards.remove('CardRoiCarreaux')
        elif cpuCards[0] == 'CardRoiCoeur':
            image2 = RoiCoeur
            usrCards.append('CardRoiCoeur')
            cpuCards.remove('CardRoiCoeur')
        elif cpuCards[0] == 'CardRoiPiques':
            image2 = RoiPiques
            usrCards.append('CardRoiPiques')
            cpuCards.remove('CardRoiPiques')
        elif cpuCards[0] == 'CardRoiTreffles':
            image2 = RoiTreffles
            usrCards.append('CardRoiTreffles')
            cpuCards.remove('CardRoiTreffles')
        elif cpuCards[0] == 'CardValetCarreaux':
            image2 = ValetCarreaux
            usrCards.append('CardValetCarreaux')
            cpuCards.remove('CardValetCarreaux')
        elif cpuCards[0] == 'CardValetCoeur':
            image2 = ValetCoeur
            usrCards.append('CardValetCoeur')
            cpuCards.remove('CardValetCoeur')
        elif cpuCards[0] == 'CardValetPiques':
            image2 = ValetPiques
            usrCards.append('CardValetPiques')
            cpuCards.remove('CardValetPiques')
        elif cpuCards[0] == 'CardValetTreffles':
            image2 = ValetTreffles
            usrCards.append('CardValetTreffles')
            cpuCards.remove('CardValetTreffles')

        Image = image1,image2
        msg = "                              You win\n\n\n              "+str("\n\n Your cards : ") + str(len(usrCards)) + str("\n\n\n Computer cards : ") + str(len(cpuCards))+str("\n\n\n           User cards                                    Computer cards")
        choices = ["Continue"]
        result = buttonbox(msg, image=Image, choices=choices)

        if result == "Continue":
            Game()

    elif CardList[usrCards[0]] == CardList[cpuCards[0]]:
        print("usrCard = " + str(usrCards[0]))
        print("cpuCard = " + str(cpuCards[0]))
        if usrCards[0] == 'Card2carreaux':
            image1 = Pic2carreaux
        elif usrCards[0] == 'Card2coeur':
            image1 = Pic2coeur
        elif usrCards[0] == 'Card2piques':
            image1 = Pic2piques
        elif usrCards[0] == 'Card2treffles':
            image1 = Pic2treffles
        elif usrCards[0] == 'Card3carreaux':
            image1 = Pic3carreaux
        elif usrCards[0] == 'Card3coeur':
            image1 = Pic3coeur
        elif usrCards[0] == 'Card3piques':
            image1 = Pic3piques
        elif usrCards[0] == 'Card3treffles':
            image1 = Pic3treffles
        elif usrCards[0] == 'Card4carreaux':
            image1 = Pic4carreaux
        elif usrCards[0] == 'Card4coeur':
            image1 = Pic4coeur
        elif usrCards[0] == 'Card4piques':
            image1 = Pic4piques
        elif usrCards[0] == 'Card4treffles':
            image1 = Pic4treffles
        elif usrCards[0] == 'Card5carreaux':
            image1 = Pic5carreaux
        elif usrCards[0] == 'Card5coeur':
            image1 = Pic5coeur
        elif usrCards[0] == 'Card5piques':
            image1 = Pic5piques
        elif usrCards[0] == 'Card5treffles':
            image1 = Pic5treffles
        elif usrCards[0] == 'Card6carreaux':
            image1 = Pic6carreaux
        elif usrCards[0] == 'Card6coeur':
            image1 = Pic6coeur
        elif usrCards[0] == 'Card6treffles':
            image1 = Pic6treffles
        elif usrCards[0] == 'Card6piques':
            image1 = Pic6piques
        elif usrCards[0] == 'Card7carreaux':
            image1 = Pic7carreaux
        elif usrCards[0] == 'Card7coeur':
            image1 = Pic7coeur
        elif usrCards[0] == 'Card7piques':
            image1 = Pic7piques
        elif usrCards[0] == 'Card7treffles':
            image1 = Pic7treffles
        elif usrCards[0] == 'Card8carreaux':
            image1 = Pic8carreaux
        elif usrCards[0] == 'Card8treffles':
            image1 = Pic8treffles
        elif usrCards[0] == 'Card8piques':
            image1 = Pic8piques
        elif usrCards[0] == 'Card8coeur':
            image1 = Pic8coeur
        elif usrCards[0] == 'Card9carreaux':
            image1 = Pic9carreaux
        elif usrCards[0] == 'Card9coeur':
            image1 = Pic9coeur
        elif usrCards[0] == 'Card9piques':
            image1 = Pic9piques
        elif usrCards[0] == 'Card9treffles':
            image1 = Pic9treffles
        elif usrCards[0] == 'Card10carreaux':
            image1 = Pic10carreaux
        elif usrCards[0] == 'Card10coeur':
            image1 = Pic10coeur
        elif usrCards[0] == 'Card10piques':
            image1 = Pic10piques
        elif usrCards[0] == 'Card10treffles':
            image1 = Pic10treffles
        elif usrCards[0] == 'CardAsCarreaux':
            image1 = AsCarreaux
        elif usrCards[0] == 'CardAsCoeur':
            image1 = AsCoeur
        elif usrCards[0] == 'CardAsPiques':
            image1 = AsPiques
        elif usrCards[0] == 'CardAsTreffles':
            image1 = AsTreffles
        elif usrCards[0] == 'CardReineCarreaux':
            image1 = ReineCarreaux
        elif usrCards[0] == 'CardReineCoeur':
            image1 = ReineCoeur
        elif usrCards[0] == 'CardReinePiques':
            image1 = ReinePiques
        elif usrCards[0] == 'CardReineTreffles':
            image1 = ReineTreffles
        elif usrCards[0] == 'CardRoiCarreaux':
            image1 = RoiCarreaux
        elif usrCards[0] == 'CardRoiCoeur':
            image1 = RoiCoeur
        elif usrCards[0] == 'CardRoiPiques':
            image1 = RoiPiques
        elif usrCards[0] == 'CardRoiTreffles':
            image1 = RoiTreffles
        elif usrCards[0] == 'CardValetCarreaux':
            image1 = ValetCarreaux
        elif usrCards[0] == 'CardValetCoeur':
            image1 = ValetCoeur
        elif usrCards[0] == 'CardValetPiques':
            image1 = ValetPiques
        elif usrCards[0] == 'CardValetTreffles':
            image1 = ValetTreffles

        if cpuCards[0] == 'Card2carreaux':
            image2 = Pic2carreaux
        elif cpuCards[0] == 'Card2coeur':
            image2 = Pic2coeur
        elif cpuCards[0] == 'Card2piques':
            image2 = Pic2piques
        elif cpuCards[0] == 'Card2treffles':
            image2 = Pic2treffles
        elif cpuCards[0] == 'Card3carreaux':
            image2 = Pic3carreaux
        elif cpuCards[0] == 'Card3coeur':
            image2 = Pic3coeur
        elif cpuCards[0] == 'Card3piques':
            image2 = Pic3piques
        elif cpuCards[0] == 'Card3treffles':
            image2 = Pic3treffles
        elif cpuCards[0] == 'Card4carreaux':
            image2 = Pic4carreaux
        elif cpuCards[0] == 'Card4coeur':
            image2 = Pic4coeur
        elif cpuCards[0] == 'Card4piques':
            image2 = Pic4piques
        elif cpuCards[0] == 'Card4treffles':
            image2 = Pic4treffles
        elif cpuCards[0] == 'Card5carreaux':
            image2 = Pic5carreaux
        elif cpuCards[0] == 'Card5coeur':
            image2 = Pic5coeur
        elif cpuCards[0] == 'Card5piques':
            image2 = Pic5piques
        elif cpuCards[0] == 'Card5treffles':
            image2 = Pic5treffles
        elif cpuCards[0] == 'Card6carreaux':
            image2 = Pic6carreaux
        elif cpuCards[0] == 'Card6coeur':
            image2 = Pic6coeur
        elif cpuCards[0] == 'Card6treffles':
            image2 = Pic6treffles
        elif cpuCards[0] == 'Card6piques':
            image2 = Pic6piques
        elif cpuCards[0] == 'Card7carreaux':
            image2 = Pic7carreaux
        elif cpuCards[0] == 'Card7coeur':
            image2 = Pic7coeur
        elif cpuCards[0] == 'Card7piques':
            image2 = Pic7piques
        elif cpuCards[0] == 'Card7treffles':
            image2 = Pic7treffles
        elif cpuCards[0] == 'Card8carreaux':
            image2 = Pic8carreaux
        elif cpuCards[0] == 'Card8treffles':
            image2 = Pic8treffles
        elif cpuCards[0] == 'Card8piques':
            image2 = Pic8piques
        elif cpuCards[0] == 'Card8coeur':
            image2 = Pic8coeur
        elif cpuCards[0] == 'Card9carreaux':
            image2 = Pic9carreaux
        elif cpuCards[0] == 'Card9coeur':
            image2 = Pic9coeur
        elif cpuCards[0] == 'Card9piques':
            image2 = Pic9piques
        elif cpuCards[0] == 'Card9treffles':
            image2 = Pic9treffles
        elif cpuCards[0] == 'Card10carreaux':
            image2 = Pic10carreaux
        elif cpuCards[0] == 'Card10coeur':
            image2 = Pic10coeur
        elif cpuCards[0] == 'Card10piques':
            image2 = Pic10piques
        elif cpuCards[0] == 'Card10treffles':
            image2 = Pic10treffles
        elif cpuCards[0] == 'CardAsCarreaux':
            image2 = AsCarreaux
        elif cpuCards[0] == 'CardAsCoeu':
            image2 = AsCoeur
        elif cpuCards[0] == 'CardAsPiques':
            image2 = AsPiques
        elif cpuCards[0] == 'CardAsTreffles':
            image2 = AsTreffles
        elif cpuCards[0] == 'CardReineCarreaux':
            image2 = ReineCarreaux
        elif cpuCards[0] == 'CardReineCoeur':
            image2 = ReineCoeur
        elif cpuCards[0] == 'CardReinePiques':
            image2 = ReinePiques
        elif cpuCards[0] == 'CardReineTreffles':
            image2 = ReineTreffles
        elif cpuCards[0] == 'CardRoiCarreaux':
            image2 = RoiCarreaux
        elif cpuCards[0] == 'CardRoiCoeur':
            image2 = RoiCoeur
        elif cpuCards[0] == 'CardRoiPiques':
            image2 = RoiPiques
        elif cpuCards[0] == 'CardRoiTreffles':
            image2 = RoiTreffles
        elif cpuCards[0] == 'CardValetCarreaux':
            image2 = ValetCarreaux
        elif cpuCards[0] == 'CardValetCoeur':
            image2 = ValetCoeur
        elif cpuCards[0] == 'CardValetPiques':
            image2 = ValetPiques
        elif cpuCards[0] == 'CardValetTreffles':
            image2 = ValetTreffles
        else:
            print("error 0")

        Image = image1,image2
        msg = "                              Eguality, Battle !\n\n\n              "+str("\n\n Your cards : ") + str(len(usrCards)) + str("\n\n\n Computer cards : ") + str(len(cpuCards))+str("\n\n\n           User cards                                    Computer cards")
        choices = ["Continue"]
        result = buttonbox(msg, image=Image, choices=choices)
        if result == "Continue":
            Battle()

mixCards()
