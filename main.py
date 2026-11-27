# -*- coding: utf-8 -*-
"""DraveSpellenkast - spellen voor twee (of alleen), in één kast.
Backgammon, Topografie, Vier op een rij, Zeeslag, Wie ben ik?, Dammen, Schaken, Galgje, Memory en Lingo.
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0.
Donaties: https://paypal.me/roger076 - service@dravenlock.nl
"""
import locale
import math
import os
import random
import sys
import time
import traceback
import webbrowser

HERE = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "DraveSpellenkast-data")
os.makedirs(DATA, exist_ok=True)
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import numpy as np
import pygame

import bg_regels as R
import topo
import vier
import zeeslag
import wiebenik
import dammen
import schaken
import galgje
import memory
import lingo
import sudoku
import puzzel
import pesten
import ganzenbord
import domino
import reversi
import duel
import online
import json
import secrets

VERSIE = "0.18.0"
W, H = 1280, 800


def log_fout(t):
    try:
        with open(os.path.join(DATA, "error.log"), "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S\n") + t + "\n")
    except Exception:
        pass


# ------------------------------------------------------------------ taal
def _taal():
    try:
        t = (locale.getlocale()[0] or "") + (os.environ.get("LANG", ""))
        if not t and sys.platform == "win32":
            import ctypes
            t = locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), "")
        return "nl" if t.lower().startswith(("nl", "dutch")) else "en"
    except Exception:
        return "nl"


TAAL = _taal()
TX = {
    "titel": ("DraveSpellenkast", "DraveSpellenkast"),
    "sub": ("Kies een spel", "Choose a game"),
    "bg": ("Backgammon", "Backgammon"), "bg_sub": ("Dobbelen, zetten, slaan en uitspelen", "Roll, move, hit and bear off"),
    "topo": ("Topografie", "Topography"), "topo_sub": ("Waar ligt het? Steden, gemeentes en provincies", "Where is it? Cities, municipalities, provinces"),
    "vier": ("Vier op een rij", "Connect four"), "vier_sub": ("Wie heeft er eerst vier op een rij?", "Who gets four in a row first?"),
    "zee": ("Zeeslag", "Battleship"), "zee_sub": ("Zoek en laat zijn schepen zinken", "Find and sink his ships"),
    "wie": ("Wie ben ik?", "Guess who?"), "wie_sub": ("Stel vragen en raad wie de ander heeft", "Ask questions and guess who the other has"),
    "dam": ("Dammen", "Draughts"), "dam_sub": ("Het echte Hollandse dambord, 10 bij 10", "The real Dutch board, 10 by 10"),
    "online_dam": ("Dammen online", "Draughts online"),
    "schaak": ("Schaken", "Chess"), "schaak_sub": ("Het koningsspel: zet de koning van de ander mat", "The royal game: checkmate the other king"),
    "online_schaak": ("Schaken online", "Chess online"),
    "galg": ("Galgje", "Hangman"), "galg_sub": ("Raad het woord voordat het poppetje hangt", "Guess the word before the man hangs"),
    "online_galg": ("Galgje online", "Hangman online"),
    "galg_mak": ("Makkelijk: korte woorden", "Easy: short words"), "galg_norm": ("Normaal: middellange woorden", "Normal: medium words"),
    "galg_moeil": ("Moeilijk: lange woorden", "Hard: long words"),
    "galg_online": ("Online: de een bedenkt, de ander raadt", "Online: one thinks of a word, the other guesses"),
    "memo": ("Memory", "Memory"), "memo_sub": ("Draai kaartjes om en zoek de paren", "Turn cards over and find the pairs"),
    "online_memo": ("Memory online", "Memory online"),
    "memo_mak": ("Makkelijk: 12 kaartjes", "Easy: 12 cards"), "memo_norm": ("Normaal: 16 kaartjes", "Normal: 16 cards"),
    "memo_moeil": ("Moeilijk: 24 kaartjes", "Hard: 24 cards"),
    "lingo": ("Lingo", "Lingo"), "lingo_sub": ("Raad het woord van 5 letters, net als op tv", "Guess the 5-letter word, like on TV"),
    "online_lingo": ("Lingo online", "Lingo online"),
    "lingo_alleen": ("Alleen oefenen", "Practise alone"),
    "lingo_c1": ("Om de beurt met de computer - makkelijk", "Take turns with the computer - easy"),
    "lingo_c2": ("Om de beurt met de computer - normaal", "Take turns with the computer - normal"),
    "lingo_c3": ("Om de beurt met de computer - moeilijk", "Take turns with the computer - hard"),
    "rev": ("Reversi", "Reversi"), "rev_sub": ("Sluit zijn schijven in, dan draaien ze om", "Trap his discs and they flip over"),
    "online_rev": ("Reversi online", "Reversi online"),
    "duel": ("DraveDuel", "DraveDuel"), "duel_sub": ("Kaartspel: wezens, spreuken en draken", "Card game: creatures, spells and dragons"),
    "domino": ("Domino", "Dominoes"), "domino_sub": ("Leg aan met hetzelfde aantal ogen", "Match the same number of pips"),
    "online_domino": ("Domino online", "Dominoes online"),
    "kies_muis": ("Wijs een spel aan om te lezen wat het is, klik om te spelen.", "Point at a game to read what it is, click to play."),
    "gans": ("Ganzenbord", "Game of the Goose"), "gans_sub": ("Het oude dobbelspel met de gans en de put", "The old dice game with the goose and the well"),
    "online_gans": ("Ganzenbord online", "Game of the Goose online"),
    "gans_1": ("Tegen 1 computer", "Against 1 computer"), "gans_2": ("Tegen 2 computers", "Against 2 computers"),
    "gans_3": ("Tegen 3 computers", "Against 3 computers"),
    "pest": ("Pesten", "Crazy Eights"), "pest_sub": ("Het kaartspel met de pestkaarten", "The card game with the nasty cards"),
    "online_pest": ("Pesten online", "Crazy Eights online"),
    "pest_1": ("Tegen 1 computer", "Against 1 computer"), "pest_2": ("Tegen 2 computers", "Against 2 computers"),
    "pest_3": ("Tegen 3 computers", "Against 3 computers"),
    "puzzel": ("Puzzel", "Puzzle"), "puzzel_sub": ("Leg de kunst van Roger weer heel", "Put Roger's art back together"),
    "puz_1": ("Makkelijk: 9 stukjes", "Easy: 9 pieces"), "puz_2": ("Normaal: 16 stukjes", "Normal: 16 pieces"),
    "puz_3": ("Moeilijk: 36 stukjes", "Hard: 36 pieces"), "puz_4": ("Schuifpuzzel: 15 stukjes en een gat", "Sliding puzzle: 15 pieces and a gap"),
    "sudoku": ("Sudoku", "Sudoku"), "sudoku_sub": ("Puzzelen met de cijfers 1 tot 9", "Puzzle with the numbers 1 to 9"),
    "sud_1": ("Makkelijk", "Easy"), "sud_2": ("Normaal", "Normal"), "sud_3": ("Moeilijk", "Hard"),
    "leer_schaak": ("Leer schaken: 10 korte lessen", "Learn chess: 10 short lessons"),
    "meer": ("Meer spellen", "More games"), "meer_sub": ("Er komen er nog meer bij", "More are coming"),
    "comp_normaal": ("Computer - normaal", "Computer - normal"), "comp_moeilijk": ("Computer - moeilijk", "Computer - hard"),
    "online_later": ("Online: tegen elkaar (komt eraan)", "Online: against each other (coming soon)"),
    "binnenkort": ("Komt eraan", "Coming soon"),
    "tegen": ("Tegen wie speel je?", "Who do you play against?"),
    "comp_mak": ("Computer - makkelijk", "Computer - easy"), "comp_goed": ("Computer - goed", "Computer - good"),
    "samen": ("Samen op deze pc", "Together on this pc"), "online": ("Online (komt eraan)", "Online (coming soon)"),
    "online_knop": ("Online: op twee pc's", "Online: on two pcs"),
    "online_titel": ("Backgammon online", "Backgammon online"),
    "online_vier": ("Vier op een rij online", "Connect four online"),
    "online_zee": ("Zeeslag online", "Battleship online"),
    "online_wie": ("Wie ben ik? online", "Guess who? online"),
    "server": ("Server", "Server"), "jouw_naam": ("Jouw naam", "Your name"), "code": ("Code van de kamer", "Room code"),
    "maak_kamer": ("Nieuwe kamer maken", "Create a new room"), "meedoen": ("Meedoen", "Join"),
    "online_uitleg": ("Eén maakt een kamer en geeft de code door. De ander typt de code en klikt Meedoen.\n"
                      "Server: laat het adres gewoon staan, dan speel je via internet.\n"
                      "Liever thuis zonder internet? Start de DraveVlag Server en vul het adres in dat dat venster toont.",
                      "One creates a room and passes on the code. The other types the code and clicks Join.\n"
                      "Server: just leave the address as it is, then you play over the internet.\n"
                      "Rather at home without internet? Start the DraveVlag Server and fill in the address it shows."),
    "klik_veld": ("Klik op een vak om te typen.", "Click a field to type."),
    "verbinden": ("Verbinden met de server...", "Connecting to the server..."),
    "geen_server": ("Geen verbinding met de server. Draait de server?", "No connection to the server. Is it running?"),
    "kamer_vol": ("Die kamer is al vol.", "That room is full."),
    "wacht_ander": ("Wacht op je tegenspeler. Geef deze code door: %s", "Waiting for your opponent. Pass on this code: %s"),
    "ander_beurt": ("%s is aan de beurt.", "%s's turn."), "ander_gooit": ("%s gooit...", "%s rolls..."),
    "ander_weg": ("%s is even weg (verbinding).", "%s is away (connection)."),
    "kamer": ("Kamer: %s", "Room: %s"), "tegenspeler": ("Tegenspeler", "Opponent"),
    "versturen": ("Versturen...", "Sending..."),
    "terug": ("Terug", "Back"), "menu": ("Menu", "Menu"),
    "gooi": ("Gooi!", "Roll!"), "klaar": ("Klaar", "Done"), "ongedaan": ("Overnieuw", "Undo"),
    "verder": ("Verder", "Continue"), "nog": ("Nog een potje", "Play again"),
    "wit": ("Wit", "White"), "zwart": ("Zwart", "Black"), "jij": ("Jij", "You"), "computer": ("Computer", "Computer"),
    "speler1": ("Speler 1", "Player 1"), "speler2": ("Speler 2", "Player 2"),
    "beurt": ("Aan de beurt: %s", "Turn: %s"),
    "wiebegint": ("Wie begint? Gooi elk één steen.", "Who starts? Each rolls one die."),
    "begint": ("%s begint met %d-%d!", "%s starts with %d-%d!"), "gelijk": ("Gelijk! Nog een keer.", "A tie! Again."),
    "geslagen": ("Je steen is geslagen! Hij staat op de balk (midden). Breng hem eerst weer in.", "Your checker was hit! It is on the bar (middle). Enter it first."),
    "comp_sloeg": ("De computer sloeg jouw steen! Hij staat nu op de balk.", "The computer hit your checker! It is on the bar now."),
    "balk": ("BALK", "BAR"),
    "comp_oefen": ("Computer - oefenen (heel makkelijk)", "Computer - practice (very easy)"),
    "hulp": ("Hulp", "Help"), "tip": ("Tip", "Tip"),
    "raak": ("Raak! Zijn steen moet naar de balk.", "Hit! His checker goes to the bar."),
    "tip_kop": ("Tip: klik de gouden steen, dan de gouden plek.", "Tip: click the gold checker, then the gold spot."),
    "r_bar": ("Breng eerst je geslagen steen weer in.", "First enter your checker from the bar."),
    "r_uit": ("Speel stenen uit: zo kom je dichter bij winnen.", "Bear off: that brings you closer to winning."),
    "r_sla": ("Sla zijn losse steen: die moet terug naar de balk!", "Hit his lonely checker: it goes back to the bar!"),
    "r_dicht": ("Zet twee stenen samen: dan kunnen ze niet geslagen worden.", "Put two checkers together: then they can't be hit."),
    "r_veilig": ("Zo staan je stenen veiliger: minder losse stenen.", "This keeps your checkers safer: fewer lonely ones."),
    "r_vooruit": ("Zo loop je goed vooruit zonder extra risico.", "Good progress without extra risk."),
    "gevaar_uitleg": ("Rood randje = losse steen die geslagen kan worden", "Red ring = lonely checker that can be hit"),
    "kies_steen": ("Klik op een steen die je wilt zetten", "Click a checker to move"),
    "kies_plek": ("Klik waar hij heen moet (lichte plekken)", "Click where it goes (light spots)"),
    "geen_zet": ("Geen zet mogelijk met %d-%d.", "No move possible with %d-%d."),
    "denkt": ("De computer denkt...", "The computer is thinking..."),
    "wint": ("%s wint!", "%s wins!"), "gammon": ("Gammon! (dubbel)", "Gammon! (double)"),
    "backgammon": ("Backgammon! (drievoudig)", "Backgammon! (triple)"),
    "stand": ("Stand: %s %d - %d %s", "Score: %s %d - %d %s"),
    "pips": ("Nog te lopen: %d", "Pips left: %d"), "uit": ("Uit: %d", "Off: %d"),
    "muziek": ("Muziek", "Music"), "aan": ("aan", "on"), "uitm": ("uit", "off"),
    "info": ("Info", "Info"), "doneer": ("Doneer via PayPal", "Donate via PayPal"),
    "info_tekst": ("DraveSpellenkast %s - gratis van Dravenlock (Roger & Claudio).\nVind je het leuk? Een kleine gift helpt.\nVragen: service@dravenlock.nl",
                   "DraveSpellenkast %s - free from Dravenlock (Roger & Claudio).\nEnjoy it? A small gift helps.\nQuestions: service@dravenlock.nl"),
    "regels": ("Spelregels", "Rules"),
    "regels_tekst": ("BACKGAMMON: Wit loopt tegen de klok in naar rechtsonder, zwart de andere kant op.\n"
                     "Gooi de stenen en zet zoveel ogen als de stenen zeggen. Dubbel = 4 zetten.\n"
                     "Een plek met 2 of meer stenen van de ander is dicht. Staat er 1: dan sla je hem.\n"
                     "Geslagen? Eerst weer inbrengen vanaf de balk.\n"
                     "Staan al je stenen thuis (laatste kwart), dan mag je ze uitspelen.\n"
                     "Wie als eerste alle 15 stenen uit heeft, wint.\n"
                     "VIER OP EEN RIJ: laat om de beurt een schijf in een kolom vallen. Hij valt tot onderaan.\n"
                     "Wie als eerste vier schijven op een rij heeft (liggend, staand of schuin), wint.\n"
                     "Tip-knop: wijst een goede kolom aan. Hulp aan: een rood rondje = daar kan de computer winnen!\n"
                     "ZEESLAG: zet je 5 schepen neer (5, 4, 3, 3 en 2 lang). Ze mogen elkaar niet raken.\n"
                     "Schiet om de beurt op een vakje van de ander. Wit plonsje = mis, vlammetje = raak.\n"
                     "Zijn alle vakjes van een schip raak, dan zinkt het. Wie het eerst alle schepen laat zinken, wint.\n"
                     "Hulp aan: rond een gezonken schip zie je stipjes = daar kan geen schip liggen.\n"
                     "WIE BEN IK?: jij en de ander hebben elk stiekem een figuurtje.\n"
                     "Om de beurt stel je een ja/nee-vraag uit de lijst. Klap om wie het niet kan zijn (Hulp aan: dat gaat vanzelf).\n"
                     "Weet je het? Klik Raden! en dan op het figuurtje. Goed = gewonnen, fout = verloren.\n"
                     "DAMMEN: wit begint. Een schijf loopt schuin vooruit, één vakje per keer, alleen over de donkere vakjes.\n"
                     "Slaan doe je door over een stuk van de ander te springen, ook achteruit. Slaan is verplicht!\n"
                     "Kun je op meer manieren slaan? Dan moet je de manier kiezen waarmee je de meeste stukken slaat.\n"
                     "Kom je op de overkant, dan wordt je schijf een dam (met kroontje). Een dam vliegt over de hele lijn.\n"
                     "Wie geen stukken meer heeft, of niet meer kan zetten, verliest.\n"
                     "Hulp aan: gouden randje = dit stuk kan (moet) slaan, rood kruisje = dat stuk sla je.\n"
                     "SCHAKEN: wit begint. Elk stuk loopt op zijn eigen manier. Koning: één vakje elke kant op. Dame: zo ver je wilt, recht en schuin.\n"
                     "Toren: zo ver je wilt, recht. Loper: zo ver je wilt, schuin. Paard: een L-sprong, en mag over andere stukken springen.\n"
                     "Pion: één vakje vooruit (de eerste keer mag het twee), en slaat schuin vooruit. Op de overkant wordt hij wat je kiest.\n"
                     "Rokeren: koning twee vakjes naar een toren, de toren springt over hem heen (als ze nog niet bewogen hebben).\n"
                     "Staat je koning aangevallen, dan sta je schaak: dat moet je meteen oplossen. Kan dat niet: schaakmat, en je verliest.\n"
                     "Kan niemand zetten zonder schaak te komen: pat (remise). Hulp aan: rood randje = dat stuk kan zomaar geslagen worden.\n"
                     "GALGJE: er is een woord, je ziet alleen streepjes. Klik op een letter (of typ hem).\n"
                     "Zit de letter erin, dan komt hij op zijn plek. Zo niet, dan komt er een stukje van de galg bij.\n"
                     "Raad het hele woord voordat het poppetje hangt (10 fouten). Tip: laat een letter zien, maar kost een fout.\n"
                     "(M is hier een letter, geen muziek.) Hulp aan: je ziet wat voor soort woord het is. Online bedenkt de een een woord en raadt de ander, om de beurt.\n"
                     "MEMORY: alle kaartjes liggen omgekeerd. Draai er om de beurt twee om.\n"
                     "Zelfde plaatje? Dan is het een paar: je houdt ze en je mag nog een keer.\n"
                     "Niet hetzelfde? Dan gaan ze weer dicht en is de ander aan de beurt. Onthoud goed waar ze liggen!\n"
                     "Wie de meeste paren heeft als alles weg is, wint. Tip (met Hulp aan): wijst een paar aan dat je al gezien hebt.\n"
                     "LINGO: raad het woord van 5 letters. De eerste letter krijg je cadeau. Je hebt 6 beurten.\n"
                     "Groen vakje = goede letter op de goede plek. Gele bol = die letter zit erin, maar op een andere plek. Grijs = zit er niet in.\n"
                     "Tegen de computer of online raden jullie om de beurt hetzelfde woord: wie het raadt, wint de ronde.\n"
                     "REVERSI: zwart begint. Zet een schijf zo dat je schijven van de ander insluit (recht of schuin).\n"
                     "Alle ingesloten schijven draaien om naar jouw kleur. Kun je niet zetten, dan pas je vanzelf.\n"
                     "Is het bord vol (of kan niemand meer), dan wint wie de meeste schijven heeft. Hoeken zijn goud waard!\n"
                     "Hulp aan: stipjes = hier mag je zetten, en je ziet hoeveel schijven er omdraaien.\n"
                     "DRAVEDUEL: kies een stok: Woud en Vuur (wezens, aanvallen) of Licht en Water (spreuken, verdediging). Je hebt 20 levens.\n"
                     "Elke beurt krijg je 1 mana meer (tot 8) en trek je 1 kaart. Het blauwe getal op een kaart is wat hij kost.\n"
                     "Klik een kaart om hem te spelen. Een wezen moet 1 beurt wennen; met Haast valt hij meteen aan.\n"
                     "Aanvallen: klik je wezen, dan een vijandelijk wezen of de held. Ze slaan elkaar met hun kracht (geel) van hun leven (rood) af.\n"
                     "Wacht (gouden rand) moet eerst verslagen worden. Wolven worden sterker in een roedel. Breng de ander naar 0: gewonnen!\n"
                     "Hulp aan: groen = dit kan je nu doen. Tip (of de T-toets) wijst de beste zet aan. Muis op een kaart = grote kaart met uitleg.\n"
                     "DOMINO: iedereen krijgt 7 stenen, de rest ligt in de pot. Om de beurt leg je een steen aan een uiteinde.\n"
                     "Het aantal ogen moet gelijk zijn aan het uiteinde. Past geen steen, dan pak je er een uit de pot. Is de pot leeg: passen.\n"
                     "Wie het eerst al zijn stenen kwijt is, wint en krijgt de ogen van de ander als punten. Kan niemand meer: minste ogen wint.\n"
                     "GANZENBORD: gooi om de beurt de twee stenen en loop zoveel vakjes. Wie precies op 63 komt, wint. Te ver? Terug lopen.\n"
                     "Gans: nog een keer zo ver. Brug (6): door naar 12. Herberg (19): beurt overslaan. Put (31) en gevangenis (52): wachten tot een ander er komt.\n"
                     "Doolhof (42): terug naar 39. De dood (58): helemaal terug naar het begin! Eerste worp 6+3: naar 26, 5+4: naar 53.\n"
                     "PESTEN: iedereen krijgt 7 kaarten. Gooi om de beurt een kaart op met dezelfde kleur of hetzelfde getal. Kan het niet: pak er een.\n"
                     "2 = de volgende pakt er 2. Joker = 5 (en past altijd). Wie moet pakken, mag zelf een 2 of joker leggen: dan krijgt de volgende alles.\n"
                     "7 en heer = nog een keer. 8 = de volgende slaat over. Aas = andersom. Boer = past altijd, en jij kiest de kleur.\n"
                     "Wie het eerst geen kaarten meer heeft, wint. Hulp aan: de kaarten die passen krijgen een groen randje.\n"
                     "PUZZEL: een plaatje van Roger is in stukjes geknipt. Klik twee stukjes om ze te verwisselen, tot het plaatje weer klopt.\n"
                     "Een stukje op de goede plek zit vast (groen randje met Hulp aan). Schuifpuzzel: schuif de stukjes naar het lege vakje.\n"
                     "SUDOKU: vul elk leeg vakje met een cijfer van 1 tot 9. In elke rij, elke kolom en elk blok van 3x3 komt elk cijfer precies één keer.\n"
                     "Potlood: kleine cijfertjes als geheugensteuntje. Hulp aan: foute cijfers worden rood en dezelfde cijfers lichten op.\n"
                     "TOPOGRAFIE: kies wat je oefent (provincies, hoofdsteden, steden of gemeentes).\n"
                     "Kies uit 4 namen: welke plek licht goud op? Of klik op de kaart: waar ligt het?\n"
                     "Goed = 10 punten, bijna = 5. Per beurt 10 vragen. Met z'n tweeën om de beurt.",
                     "BACKGAMMON: White moves counter-clockwise to the bottom right, black the other way.\n"
                     "Roll and move as many points as the dice show. Doubles = 4 moves.\n"
                     "A point with 2+ of the other's checkers is blocked. Only 1? Then you hit it.\n"
                     "Hit? First enter again from the bar.\n"
                     "All your checkers home (last quarter)? Then you may bear them off.\n"
                     "First to bear off all 15 wins.\n"
                     "CONNECT FOUR: take turns dropping a disc in a column. It falls to the bottom.\n"
                     "First with four discs in a row (across, up or diagonal) wins.\n"
                     "Tip button: points at a good column. Help on: a red ring = the computer can win there!\n"
                     "BATTLESHIP: place your 5 ships (5, 4, 3, 3 and 2 long). They may not touch.\n"
                     "Take turns shooting at a square of the other. White splash = miss, flame = hit.\n"
                     "All squares of a ship hit? It sinks. First to sink all ships wins.\n"
                     "Help on: dots around a sunk ship = no ship can be there.\n"
                     "GUESS WHO?: you and the other each secretly have a person.\n"
                     "Take turns asking a yes/no question from the list. Flip down who it can't be (Help on: automatic).\n"
                     "Know it? Click Guess! and then the person. Right = you win, wrong = you lose.\n"
                     "DRAUGHTS: white starts. A man moves diagonally forward, one square at a time, only on the dark squares.\n"
                     "You capture by jumping over a piece of the other, also backwards. Capturing is compulsory!\n"
                     "More ways to capture? Then you must take the way that captures the most pieces.\n"
                     "Reach the other side and your man becomes a king (with a crown). A king flies along the whole line.\n"
                     "Whoever has no pieces left, or cannot move, loses.\n"
                     "Help on: gold ring = this piece can (must) capture, red cross = that piece you capture.\n"
                     "CHESS: white starts. Each piece moves its own way. King: one square any way. Queen: as far as you like, straight and diagonal.\n"
                     "Rook: as far as you like, straight. Bishop: as far as you like, diagonal. Knight: an L-jump, and may jump over pieces.\n"
                     "Pawn: one square forward (the first time two), and captures diagonally forward. On the far side it becomes what you choose.\n"
                     "Castling: king two squares towards a rook, the rook jumps over it (if neither has moved yet).\n"
                     "Is your king attacked, you are in check: you must solve that at once. Can't you: checkmate, and you lose.\n"
                     "Nobody can move without getting in check: stalemate (draw). Help on: red ring = that piece can be taken for free.\n"
                     "HANGMAN: there is a word, you only see dashes. Click a letter (or type it).\n"
                     "Is the letter in it, it goes to its place. If not, a piece of the gallows is added.\n"
                     "Guess the whole word before the man hangs (10 mistakes). Tip: shows a letter, but costs a mistake.\n"
                     "Help on: you see what kind of word it is. Online one thinks of a word and the other guesses, in turns.\n"
                     "MEMORY: all cards lie face down. Take turns turning two over.\n"
                     "Same picture? Then it is a pair: you keep them and go again.\n"
                     "Not the same? Then they close again and it is the other's turn. Remember where they are!\n"
                     "Whoever has the most pairs when all are gone, wins. Tip (with Help on): points at a pair you have already seen.\n"
                     "LINGO: guess the 5-letter word. You get the first letter for free. You have 6 tries.\n"
                     "Green square = right letter in the right place. Yellow ball = the letter is in it, but elsewhere. Grey = not in it.\n"
                     "Against the computer or online you take turns guessing the same word: whoever guesses it, wins the round.\n"
                     "REVERSI: black starts. Place a disc so that you trap discs of the other (straight or diagonal).\n"
                     "All trapped discs flip to your colour. If you cannot move, you pass automatically.\n"
                     "When the board is full (or nobody can move), whoever has the most discs wins. Corners are gold!\n"
                     "Help on: dots = you may play here, and you see how many discs flip.\n"
                     "DRAVEDUEL: choose a deck: Forest and Fire (creatures, attacks) or Light and Water (spells, defence). You have 20 life.\n"
                     "Each turn you get 1 more mana (up to 8) and draw 1 card. The blue number on a card is its cost.\n"
                     "Click a card to play it. A creature needs 1 turn to settle; with Haste it attacks at once.\n"
                     "Attack: click your creature, then an enemy creature or the hero. They hit each other's health (red) with their power (yellow).\n"
                     "Guards (gold border) must be defeated first. Wolves grow stronger in a pack. Bring the other to 0: you win!\n"
                     "Help on: green = you can do this now. Tip (or the T key) points at the best move. Mouse on a card = big card with explanation.\n"
                     "DOMINOES: everyone gets 7 stones, the rest is the pile. Take turns adding a stone to an end.\n"
                     "The number of pips must match that end. No stone fits? Draw one from the pile. Pile empty: pass.\n"
                     "First to play all stones wins and scores the other's pips. If nobody can move: fewest pips wins.\n"
                     "GAME OF THE GOOSE: take turns rolling two dice and walk that many squares. Land exactly on 63 to win. Too far? Walk back.\n"
                     "Goose: go the same distance again. Bridge (6): on to 12. Inn (19): miss a turn. Well (31) and prison (52): wait until another arrives.\n"
                     "Maze (42): back to 39. Death (58): all the way back to the start! First roll 6+3: to 26, 5+4: to 53.\n"
                     "CRAZY EIGHTS: everyone gets 7 cards. Take turns playing a card of the same suit or the same value. Can't? Draw one.\n"
                     "2 = the next player draws 2. Joker = 5 (and always fits). Whoever must draw may play a 2 or joker: then the next gets it all.\n"
                     "7 and king = go again. 8 = the next misses a turn. Ace = reverse. Jack = always fits, and you choose the suit.\n"
                     "First with no cards left wins. Help on: cards that fit get a green border.\n"
                     "PUZZLE: one of Roger's pictures is cut into pieces. Click two pieces to swap them, until the picture is right again.\n"
                     "A piece in the right place locks (green border with Help on). Sliding puzzle: slide pieces into the empty square.\n"
                     "SUDOKU: fill every empty square with a number from 1 to 9. Every row, column and 3x3 block has each number exactly once.\n"
                     "Pencil: small numbers as a reminder. Help on: wrong numbers turn red and the same numbers light up.\n"
                     "TOPOGRAPHY: choose what to practise (provinces, capitals, cities or municipalities).\n"
                     "Choose from 4 names: which place shines gold? Or click on the map: where is it?\n"
                     "Right = 10 points, almost = 5. 10 questions each. Two players take turns."),
    "toetsen": ("Spatie = gooien / klaar   ·   Backspace = terug   ·   M = muziek   ·   Esc = menu",
                "Space = roll / done   ·   Backspace = undo   ·   M = music   ·   Esc = menu"),
}


def T(k):
    v = TX.get(k, (k, k))
    return v[0] if TAAL == "nl" else v[1]


# nieuwe spellen (26-11): één lijstje, dan regelt het menu de rest
NIEUW = {
    "lingo": {"mod": "lingo", "klasse": "Lingo", "online": "OnlineLingo",
              "keuzes": [("lingo_alleen", 0), ("lingo_c1", 1), ("lingo_c2", 2), ("lingo_c3", 3)]},
    "rev": {"mod": "reversi", "klasse": "Reversi", "online": "OnlineReversi",
            "keuzes": [("comp_mak", 1), ("comp_normaal", 2), ("comp_moeilijk", 3)]},
}
NIEUW.update({
    "domino": {"mod": "domino", "klasse": "Domino", "online": "OnlineDomino",
               "keuzes": [("comp_mak", 1), ("comp_normaal", 2), ("comp_moeilijk", 3)]},
})
NIEUW.update({
    "gans": {"mod": "ganzenbord", "klasse": "Ganzenbord", "online": "OnlineGanzenbord",
             "keuzes": [("gans_1", 1), ("gans_2", 2), ("gans_3", 3)]},
})
NIEUW.update({
    "pest": {"mod": "pesten", "klasse": "Pesten", "online": "OnlinePesten",
             "keuzes": [("pest_1", 1), ("pest_2", 2), ("pest_3", 3)]},
})
NIEUW.update({
    "puzzel": {"mod": "puzzel", "klasse": "Puzzel", "online": None,
               "keuzes": [("puz_1", 1), ("puz_2", 2), ("puz_3", 3), ("puz_4", 4)]},
})
NIEUW.update({
    "duel": {"mod": "duel", "klasse": "Duel", "online": None,
             "keuzes": [("comp_mak", 1), ("comp_normaal", 2), ("comp_moeilijk", 3)]},
})
NIEUW.update({
    "sudoku": {"mod": "sudoku", "klasse": "Sudoku", "online": None,
               "keuzes": [("sud_1", 1), ("sud_2", 2), ("sud_3", 3)]},
})
SPEL_SCHERMEN = ("bg", "topo", "vier", "zee", "wie", "dam", "schaak", "galg", "memo") + tuple(NIEUW)
REGEL_KOP = {"bg": ("BACKGAMMON", "BACKGAMMON"), "topo": ("TOPOGRAFIE", "TOPOGRAPHY"), "vier": ("VIER OP EEN RIJ", "CONNECT FOUR"),
             "zee": ("ZEESLAG", "BATTLESHIP"), "wie": ("WIE BEN IK?", "GUESS WHO?"), "dam": ("DAMMEN", "DRAUGHTS"), "schaak": ("SCHAKEN", "CHESS"), "galg": ("GALGJE", "HANGMAN"), "memo": ("MEMORY", "MEMORY"), "lingo": ("LINGO", "LINGO"), "sudoku": ("SUDOKU", "SUDOKU"), "puzzel": ("PUZZEL", "PUZZLE"), "pest": ("PESTEN", "CRAZY EIGHTS"), "gans": ("GANZENBORD", "GAME OF THE GOOSE"), "domino": ("DOMINO", "DOMINOES"), "rev": ("REVERSI", "REVERSI"), "duel": ("DRAVEDUEL", "DRAVEDUEL")}


def regels_voor(scherm):
    """Alle spelregels, of (tijdens een spel) alleen het stukje van dat spel."""
    regels = T("regels_tekst").split("\n")
    kop = REGEL_KOP.get(scherm.replace("_kies", ""))
    if not kop:
        return regels
    kop = kop[0] if TAAL == "nl" else kop[1]
    uit, bezig = [], False
    for regel in regels:
        if regel[:5].isupper() and ":" in regel:
            bezig = regel.startswith(kop + ":")
        if bezig:
            uit.append(regel)
    return uit or regels


# ------------------------------------------------------------------ kleuren (Dravenlock)
ACHTER = (22, 19, 31)
VAK = (36, 31, 51)
RAND = (74, 61, 102)
ACCENT = (181, 156, 255)
PAARS = (127, 119, 221)
TEKST = (242, 238, 252)
ZACHT = (169, 159, 196)
GOUD = (224, 184, 90)
GROEN = (63, 166, 107)
ROOD = (196, 71, 90)
HOUT = (44, 36, 62)
PUNT_A = (127, 119, 221)
PUNT_B = (88, 74, 128)
STEEN_W = (244, 240, 230)
STEEN_Z = (40, 32, 56)

# ------------------------------------------------------------------ geluid (zelf gemaakt)
SR = 44100


def toon(freq, dur, vol=0.3, vorm="sin", decay=6.0):
    t = np.linspace(0, dur, int(SR * dur), False)
    if vorm == "sin":
        g = np.sin(2 * np.pi * freq * t)
    elif vorm == "ruis":
        g = np.random.uniform(-1, 1, len(t))
    else:
        g = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5
    return g * np.exp(-decay * t) * vol


def mix(*gs):
    """Telt geluiden op, ook als ze niet even lang zijn."""
    n = max(len(g) for g in gs)
    uit = np.zeros(n)
    for g in gs:
        uit[:len(g)] += g
    return uit


def naar_geluid(g):
    freq, _fmt, kan = pygame.mixer.get_init()
    if freq != SR:
        x = np.linspace(0, len(g) - 1, int(len(g) * freq / SR))
        g = np.interp(x, np.arange(len(g)), g)
    a = (np.clip(g, -1, 1) * 32000).astype(np.int16)
    if kan == 1:
        return pygame.sndarray.make_sound(a.copy())
    return pygame.sndarray.make_sound(np.ascontiguousarray(np.column_stack([a] * kan)))


class Geluid:
    def __init__(self):
        self.ok, self.muziek_staat = False, True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(SR, -16, 2, 512)
            rnd = np.random.RandomState(3)
            ratel = np.zeros(int(SR * 0.5))
            for k in range(7):                       # stenen die rollen en tikken
                s = int(SR * (0.02 + k * 0.06 + rnd.rand() * 0.02))
                g = mix(toon(0, 0.05, 0.4, "ruis", 60), toon(1800 + rnd.rand() * 900, 0.05, 0.25, decay=70))
                e = min(len(ratel), s + len(g)); ratel[s:e] += g[:e - s]
            self.dobbel = naar_geluid(ratel)
            self.zet = naar_geluid(mix(toon(320, 0.09, 0.35, decay=35), toon(0, 0.05, 0.15, "ruis", 80)))
            self.sla = naar_geluid(mix(toon(180, 0.25, 0.4, decay=14), toon(0, 0.2, 0.3, "ruis", 18), toon(540, 0.15, 0.2, "blok", 25)))
            self.uit = naar_geluid(np.concatenate([toon(660, 0.08, 0.25, decay=20), toon(990, 0.12, 0.25, decay=14)]))
            self.klik = naar_geluid(toon(880, 0.05, 0.2, decay=45))
            self.win = naar_geluid(np.concatenate([toon(f, 0.17, 0.3, decay=4) for f in (523, 659, 784, 1047)] + [toon(1047, 0.6, 0.3, decay=3)]))
            self.verlies = naar_geluid(np.concatenate([toon(f, 0.22, 0.3, decay=4) for f in (392, 330, 262)] + [toon(196, 0.6, 0.3, decay=3)]))
            self.goed = naar_geluid(np.concatenate([toon(784, 0.1, 0.28, decay=14), toon(1175, 0.22, 0.28, decay=9)]))
            self.fout = naar_geluid(mix(toon(220, 0.3, 0.3, "blok", 8), toon(207, 0.3, 0.2, decay=8)))
            self.heli = naar_geluid(self._maak_heli())
            self.muziek = naar_geluid(self._maak_muziek())
            self.ok = True
        except Exception:
            log_fout(traceback.format_exc())

    def _maak_muziek(self):
        """Rustige, warme lus (~32 s): een theehuis-sfeertje bij een bordspel."""
        rnd = np.random.RandomState(11)
        basis = [196.0, 220.0, 246.94, 261.63, 293.66, 329.63, 349.23, 392.0]   # G mixolydisch
        akk = [[0, 2, 4], [3, 5, 0], [6, 1, 3], [4, 6, 1]]
        maat = 2.0
        uit = np.zeros(int(SR * maat * 16))
        for m in range(16):
            a = akk[m % 4]
            t0 = int(m * maat * SR)
            for i in a:
                g = toon(basis[i] / 2, maat * 1.1, 0.045, decay=0.9)
                e = min(len(uit), t0 + len(g)); uit[t0:e] += g[:e - t0]
            for k in range(4):
                f = basis[rnd.choice(a) if k % 2 == 0 else rnd.randint(0, 8)]
                g = toon(f * (2 if rnd.rand() < 0.25 else 1), 0.55, 0.055, decay=3.5)
                s = t0 + int(k * maat / 4 * SR); e = min(len(uit), s + len(g)); uit[s:e] += g[:e - s]
        f = int(SR * 0.3); uit[:f] *= np.linspace(0, 1, f); uit[-f:] *= np.linspace(1, 0, f)
        return uit

    def _maak_heli(self):
        """Wieken: ruis die ~11 keer per seconde aanzwelt (precies 1 s, naadloos te herhalen)."""
        n = SR
        t = np.arange(n) / SR
        rnd = np.random.RandomState(5)
        ruis = rnd.uniform(-1, 1, n)
        laag = np.convolve(ruis, np.ones(40) / 40, mode="same")
        tik = (0.5 + 0.5 * np.cos(2 * np.pi * 11 * t)) ** 6
        motor = 0.25 * np.sin(2 * np.pi * 88 * t) + 0.1 * np.sin(2 * np.pi * 176 * t)
        return (laag * 1.6 * (0.25 + tik) + motor * 0.35) * 0.32

    def stop(self, naam):
        if self.ok:
            try:
                getattr(self, naam).stop()
            except Exception:
                pass

    def speel(self, naam):
        if self.ok:
            try:
                getattr(self, naam).play()
            except Exception:
                pass

    def muziek_aan(self, aan):
        self.muziek_staat = aan
        if not self.ok:
            return
        self.muziek.stop()
        if aan:
            self.muziek.play(loops=-1)


# ------------------------------------------------------------------ hulpjes voor tekenen
FONTS = {}


def font(px, vet=True):
    k = (px, vet)
    if k not in FONTS:
        FONTS[k] = pygame.font.SysFont("segoeui,arial,dejavusans", px, bold=vet)
    return FONTS[k]


def tekst(d, t, px, kl, pos, mid=False, vet=True, rechts=False):
    s = font(px, vet).render(t, True, kl)
    r = s.get_rect()
    if mid:
        r.center = pos
    elif rechts:
        r.topright = pos
    else:
        r.topleft = pos
    d.blit(s, r)
    return r


class Knop:
    def __init__(self, rect, label, actie, kleur=VAK, px=26, aan=True):
        self.r = pygame.Rect(rect)
        self.label, self.actie, self.kleur, self.px, self.aan = label, actie, kleur, px, aan

    def teken(self, d, muis):
        hover = self.aan and self.r.collidepoint(muis)
        k = self.kleur if self.aan else (50, 45, 64)
        if hover:
            k = tuple(min(255, c + 25) for c in k)
        pygame.draw.rect(d, k, self.r, border_radius=14)
        pygame.draw.rect(d, ACCENT if hover else RAND, self.r, 3, border_radius=14)
        kl = (40, 30, 20) if self.kleur == GOUD else TEKST
        tekst(d, self.label, self.px, kl if self.aan else (120, 112, 140), self.r.center, mid=True)

    def klik(self, pos):
        if self.aan and self.r.collidepoint(pos):
            self.actie()
            return True
        return False


def teken_dobbel(d, x, y, n, maat=64, gebruikt=False, kleur=TEKST):
    r = pygame.Rect(x, y, maat, maat)
    pygame.draw.rect(d, (90, 84, 110) if gebruikt else kleur, r, border_radius=12)
    pygame.draw.rect(d, GOUD, r, 3, border_radius=12)
    oog = (60, 55, 75) if gebruikt else (30, 25, 45)
    q = maat / 4
    plek = {1: [(2, 2)], 2: [(1, 1), (3, 3)], 3: [(1, 1), (2, 2), (3, 3)], 4: [(1, 1), (3, 1), (1, 3), (3, 3)],
            5: [(1, 1), (3, 1), (2, 2), (1, 3), (3, 3)], 6: [(1, 1), (3, 1), (1, 2), (3, 2), (1, 3), (3, 3)]}[n]
    for a, b in plek:
        pygame.draw.circle(d, oog, (int(x + a * q), int(y + b * q)), max(4, maat // 10))


# ------------------------------------------------------------------ het backgammon-bord
PW = 68                                   # breedte van een punt
BALK = 60                                 # breedte van de balk
BX, BY, BH = 24, 40, 720                  # bord (met balk)
BW = 12 * PW + BALK + 30
PH = 300                                  # hoogte van de driehoeken
STR = 31                                  # straal van een steen
UITX = BX + BW + 10                       # bakje voor uitgespeelde stenen


def punt_x(i):
    """Midden x van punt i (0..23). Wit (speler 0) zit onderaan; wit thuis = rechtsonder."""
    col = (11 - i) if i < 12 else (i - 12)
    x = BX + 15 + col * PW + (BALK if col >= 6 else 0)
    return x + PW // 2


def onder(i):
    return i < 12


def steen_pos(i, k):
    """Midden van de k-de steen (0 = buitenste) op punt i."""
    x = punt_x(i)
    stap = min(2 * STR, (PH - 2 * STR) / max(1, 4))
    if onder(i):
        y = BY + BH - 15 - STR - k * stap
    else:
        y = BY + 15 + STR + k * stap
    return int(x), int(y)


def balk_rect():
    return pygame.Rect(BX + 15 + 6 * PW, BY, BALK, BH)


def uit_rect(sp):
    return pygame.Rect(UITX, BY + BH // 2 + 10, 64, BH // 2 - 10) if sp == 0 else pygame.Rect(UITX, BY, 64, BH // 2 - 10)


def teken_steen(d, x, y, sp, licht=False, r=STR):
    kl = STEEN_W if sp == 0 else STEEN_Z
    pygame.draw.circle(d, (0, 0, 0), (x + 2, y + 3), r)
    pygame.draw.circle(d, kl, (x, y), r)
    rand = (190, 180, 160) if sp == 0 else GOUD
    pygame.draw.circle(d, rand, (x, y), r, 3)
    pygame.draw.circle(d, rand, (x, y), int(r * 0.55), 2)
    if licht:
        pygame.draw.circle(d, ACCENT, (x, y), r + 4, 4)


class Backgammon:
    def __init__(self, app, modus):
        self.app = app
        self.modus = modus                     # "comp1", "comp2" of "samen"
        self.score = [0, 0]
        self.knoppen = []
        self.nieuw_potje()

    # ---------- namen
    def naam(self, sp):
        if self.modus == "samen":
            return "%s (%s)" % (T("speler1") if sp == 0 else T("speler2"), T("wit") if sp == 0 else T("zwart"))
        return T("jij") if sp == 0 else T("computer")

    def mens(self, sp):
        return self.modus == "samen" or sp == 0

    def score_tekst(self):
        if self.modus == "samen":
            return "%d - %d" % tuple(self.score)
        return T("stand") % (T("jij"), self.score[0], self.score[1], T("computer"))

    # ---------- spelverloop
    def nieuw_potje(self):
        self.s = R.beginstand()
        self.sp = 0
        self.worp = None
        self.over = []
        self.alle = []
        self.gedaan = []
        self.start_stand = None
        self.gekozen = None
        self.fase = "wiebegint"
        self.begin_worp = None
        self.melding = T("wiebegint")
        self.einde = None
        self.comp_t = 0
        self.tip_zet = None
        self.laatste = []                      # laatste zetten (om te laten zien)

    def wie_begint(self):
        a, b = random.randint(1, 6), random.randint(1, 6)
        self.app.geluid.speel("dobbel")
        self.begin_worp = (a, b)
        if a == b:
            self.melding = T("gelijk")
            return
        self.sp = 0 if a > b else 1
        self.melding = T("begint") % (self.naam(self.sp), max(a, b), min(a, b))
        self.start_beurt((max(a, b), min(a, b)))

    def start_beurt(self, worp):
        self.worp = worp
        self.over = [worp[0]] * 4 if worp[0] == worp[1] else list(worp)
        self.alle = R.reeksen(self.s, self.sp, worp, uniek=False)
        self.gedaan = []
        self.start_stand = R.kopie(self.s)
        self.gekozen = None
        self.tip_zet = None
        if not self.alle:
            self.fase = "geen_zet"
            self.melding = T("geen_zet") % worp
            if not self.mens(self.sp):
                self.comp_t = time.time() + 1.6
            return
        if self.mens(self.sp):
            self.fase = "zetten"
            self.melding = T("geslagen") if self.s["bar"][self.sp] else T("kies_steen")
        else:
            self.fase = "computer"
            self.comp_plan = R.computer_beurt(self.s, self.sp, worp, niveau={"comp0": 0, "comp1": 1}.get(self.modus, 2))
            self.comp_t = time.time() + 1.0
            self.melding = T("denkt")

    def gooi(self):
        if self.fase == "wiebegint":
            self.wie_begint()
            return
        if self.fase != "gooien":
            return
        self.app.geluid.speel("dobbel")
        self.start_beurt(R.gooi())

    def volgende_speler(self):
        w = R.winnaar(self.s)
        if w is not None:
            soort = R.soort_winst(self.s, w)
            self.score[w] += soort
            self.einde = (w, soort)
            self.fase = "einde"
            self.app.geluid.speel("win" if (self.mens(w) and self.modus != "samen") or self.modus == "samen" else "verlies")
            return
        self.sp = 1 - self.sp
        self.worp = None
        self.over = []
        self.gekozen = None
        self.fase = "gooien"
        self.melding = T("beurt") % self.naam(self.sp)
        if self.s["bar"][self.sp] and self.mens(self.sp):
            self.melding = T("geslagen")
        if not self.mens(self.sp):
            self.comp_t = time.time() + 0.8

    def mag_nu(self):
        return R.mogelijke_eerste_zetten(self.s, self.sp, self.over, self.alle, self.gedaan)

    def zet_uit(self, z):
        d = R.worp_voor_zet(self.sp, z, self.over)
        self.s, geslagen = R.doe(self.s, self.sp, z)
        if d in self.over:
            self.over.remove(d)
        self.gedaan.append(z)
        self.laatste.append(z)
        self.laatste = self.laatste[-4:]
        self.app.geluid.speel("sla" if geslagen else ("uit" if z[1] == R.UIT else "zet"))
        self.tip_zet = None
        if geslagen and self.mens(self.sp):
            self.melding = T("raak")
        if geslagen and not self.mens(self.sp) and self.modus != "samen":
            self.melding = T("comp_sloeg")
            self.sloeg = True

    def beurt_klaar(self):
        """Mag de mens op Klaar drukken? Als er geen zet meer bij kan."""
        return self.fase == "zetten" and not self.mag_nu()

    def klaar(self):
        if self.beurt_klaar():
            self.app.geluid.speel("klik")
            self.laatste = list(self.gedaan)
            self.volgende_speler()

    def geef_tip(self):
        if self.fase != "zetten" or not self.mag_nu():
            return
        z, reden = R.tip(self.s, self.sp, self.worp, None if not self.gedaan else self.over)
        if z is None or z not in self.mag_nu():
            return
        self.tip_zet = z
        self.gekozen = None
        self.melding = T("tip_kop") + " " + T("r_" + reden)
        self.app.geluid.speel("klik")

    def ongedaan(self):
        if self.fase == "zetten" and self.gedaan:
            self.s = R.kopie(self.start_stand)
            self.over = [self.worp[0]] * 4 if self.worp[0] == self.worp[1] else list(self.worp)
            self.gedaan = []
            self.gekozen = None
            self.melding = T("kies_steen")
            self.app.geluid.speel("klik")

    def update(self):
        nu = time.time()
        if self.fase == "geen_zet" and not self.mens(self.sp) and nu > self.comp_t:
            self.volgende_speler()
        elif self.fase == "gooien" and not self.mens(self.sp) and nu > self.comp_t:
            self.app.geluid.speel("dobbel")
            self.start_beurt(R.gooi())
        elif self.fase == "computer" and nu > self.comp_t:
            if self.comp_plan:
                if not self.gedaan:
                    self.laatste = []
                self.zet_uit(self.comp_plan.pop(0))
                self.comp_t = nu + 0.75
            else:
                self.volgende_speler()

    # ---------- klikken op het bord
    def plek_op(self, pos):
        x, y = pos
        if balk_rect().collidepoint(pos):
            return R.BAR
        for sp in (0, 1):
            if uit_rect(sp).collidepoint(pos):
                return R.UIT
        for i in range(24):
            px = punt_x(i)
            if abs(x - px) <= PW // 2:
                if onder(i) and BY + BH // 2 < y <= BY + BH:
                    return i
                if not onder(i) and BY <= y < BY + BH // 2:
                    return i
        return None

    def klik(self, pos):
        if self.fase != "zetten" or not self.mens(self.sp):
            return
        plek = self.plek_op(pos)
        if plek is None:
            self.gekozen = None
            return
        mag = self.mag_nu()
        if self.gekozen is not None:
            z = (self.gekozen, plek)
            if z in mag:
                self.zet_uit(z)
                self.gekozen = None
                if self.melding != T("raak"):
                    self.melding = T("kies_steen") if self.mag_nu() else ""
                return
        bronnen = {z[0] for z in mag}
        if plek in bronnen:
            self.gekozen = plek
            self.app.geluid.speel("klik")
            doelen = [z[1] for z in mag if z[0] == plek]
            if len(doelen) == 1 and doelen[0] == R.UIT:
                pass
            self.melding = T("kies_plek")
        else:
            self.gekozen = None

    # ---------- tekenen
    def teken(self, d, muis):
        d.fill(ACHTER)
        bord = pygame.Rect(BX, BY, BW, BH)
        pygame.draw.rect(d, HOUT, bord, border_radius=18)
        pygame.draw.rect(d, RAND, bord, 4, border_radius=18)
        pygame.draw.rect(d, (30, 25, 42), balk_rect())
        mag = self.mag_nu() if self.fase == "zetten" and self.mens(self.sp) else set()
        bronnen = {z[0] for z in mag}
        doelen = {z[1] for z in mag if z[0] == self.gekozen} if self.gekozen is not None else set()
        for i in range(24):
            x = punt_x(i)
            kl = PUNT_A if i % 2 == 0 else PUNT_B
            if onder(i):
                pts = [(x - PW // 2 + 3, BY + BH - 15), (x + PW // 2 - 3, BY + BH - 15), (x, BY + BH - 15 - PH)]
            else:
                pts = [(x - PW // 2 + 3, BY + 15), (x + PW // 2 - 3, BY + 15), (x, BY + 15 + PH)]
            pygame.draw.polygon(d, kl, pts)
            if i in doelen:
                pygame.draw.polygon(d, GROEN, pts, 6)
            # nummer (vanuit wit gezien 1..24) klein aan de rand
            nr = i + 1 if (self.modus != "samen" or self.sp == 0) else 24 - i
            tekst(d, str(nr), 15, ZACHT, (x, BY + BH - 6) if onder(i) else (x, BY + 7), mid=True, vet=False)
        # stenen
        for i in range(24):
            v = self.s["bord"][i]
            if not v:
                continue
            sp = 0 if v > 0 else 1
            n = abs(v)
            for k in range(min(n, 5)):
                x, y = steen_pos(i, k)
                licht = (k == min(n, 5) - 1) and (i == self.gekozen or (self.gekozen is None and i in bronnen))
                teken_steen(d, x, y, sp, licht=licht)
            if n > 5:
                x, y = steen_pos(i, 4)
                tekst(d, str(n), 26, GOUD if sp == 0 else TEKST, (x, y), mid=True)
        # hulp: losse stenen in gevaar (rood) en de tip (goud)
        if self.app.hulp and self.fase not in ("wiebegint", "einde"):
            wie = [self.sp] if self.modus == "samen" else [0]
            for sp_ in wie:
                for i in R.in_gevaar(self.s, sp_):
                    x, y = steen_pos(i, 0)
                    pygame.draw.circle(d, ROOD, (x, y), STR + 5, 5)
            if self.tip_zet:
                van, naar = self.tip_zet
                if van == R.BAR:
                    br0 = balk_rect()
                    pygame.draw.circle(d, GOUD, (br0.centerx, br0.centery + (60 if self.sp == 0 else -60)), STR + 7, 6)
                else:
                    n = abs(self.s["bord"][van])
                    x, y = steen_pos(van, min(n, 5) - 1)
                    pygame.draw.circle(d, GOUD, (x, y), STR + 7, 6)
                if naar == R.UIT:
                    pygame.draw.rect(d, GOUD, uit_rect(self.sp), 6, border_radius=10)
                else:
                    x = punt_x(naar)
                    if onder(naar):
                        pts = [(x - PW // 2 + 3, BY + BH - 15), (x + PW // 2 - 3, BY + BH - 15), (x, BY + BH - 15 - PH)]
                    else:
                        pts = [(x - PW // 2 + 3, BY + 15), (x + PW // 2 - 3, BY + 15), (x, BY + 15 + PH)]
                    pygame.draw.polygon(d, GOUD, pts, 7)
        # balk
        br = balk_rect()
        tekst(d, T("balk"), 15, ZACHT, (br.centerx, br.centery), mid=True)
        for sp in (0, 1):
            n = self.s["bar"][sp]
            for k in range(min(n, 4)):
                y = br.centery + (60 + k * 50 if sp == 0 else -60 - k * 50)
                licht = R.BAR in bronnen and sp == self.sp and k == min(n, 4) - 1
                teken_steen(d, br.centerx, y, sp, licht=licht or (self.gekozen == R.BAR and sp == self.sp and k == min(n, 4) - 1))
            if n > 4:
                tekst(d, "x%d" % n, 22, GOUD, (br.centerx, br.centery + (260 if sp == 0 else -260)), mid=True)
        # uit-bakjes
        for sp in (0, 1):
            r = uit_rect(sp)
            pygame.draw.rect(d, (30, 25, 42), r, border_radius=10)
            pygame.draw.rect(d, GROEN if (R.UIT in doelen and sp == self.sp) else RAND, r, 4, border_radius=10)
            n = self.s["uit"][sp]
            for k in range(n):
                yy = r.bottom - 10 - k * 21 if sp == 0 else r.top + 10 + k * 21
                pygame.draw.rect(d, STEEN_W if sp == 0 else STEEN_Z, (r.x + 8, yy - 8 if sp == 0 else yy, r.w - 16, 16), border_radius=5)
                pygame.draw.rect(d, (190, 180, 160) if sp == 0 else GOUD, (r.x + 8, yy - 8 if sp == 0 else yy, r.w - 16, 16), 2, border_radius=5)
        # paneel rechts
        px = UITX + 80
        tekst(d, T("bg"), 30, ACCENT, (px - 6, 30))
        for sp in (0, 1):
            y = 86 if sp == 1 else 574
            beurt = sp == self.sp and self.fase not in ("wiebegint", "einde")
            if beurt:
                pygame.draw.rect(d, (50, 44, 72), (px - 10, y - 8, W - px - 6, 106), border_radius=12)
            teken_steen(d, px + 18, y + 22, sp, r=18)
            tekst(d, self.naam(sp), 22, TEKST, (px + 44, y + 8))
            tekst(d, T("pips") % R.pips(self.s, sp), 18, ZACHT, (px, y + 48), vet=False)
            tekst(d, T("uit") % self.s["uit"][sp], 18, ZACHT, (px, y + 74), vet=False)
        # dobbelstenen
        if self.fase == "wiebegint" and self.begin_worp:
            teken_dobbel(d, px, 220, self.begin_worp[0], 62, kleur=STEEN_W)
            teken_dobbel(d, px + 80, 220, self.begin_worp[1], 62, kleur=(120, 110, 150))
        elif self.worp:
            stenen = [self.worp[0]] * 4 if self.worp[0] == self.worp[1] else list(self.worp)
            over = list(self.over)
            for k, n in enumerate(stenen):
                gebruikt = n not in over
                if not gebruikt:
                    over.remove(n)
                teken_dobbel(d, px + (k % 2) * 80, 210 + (k // 2) * 72, n, 62, gebruikt=gebruikt)
        # melding
        dubbel = bool(self.worp) and self.worp[0] == self.worp[1] and self.fase != "wiebegint"
        y = 356 if dubbel else 300
        ruimte = 444 - y
        for grootte in (21, 19, 17, 15):
            stap = grootte + 6
            regels = self._knip(self.melding, grootte, W - px - 16)
            if len(regels) * stap <= ruimte:
                break
        for regel in regels[:max(1, ruimte // stap)]:
            tekst(d, regel, grootte, TEKST, (px, y))
            y += stap
        # knoppen
        self.knoppen = []
        if self.fase in ("gooien", "wiebegint") and self.mens(self.sp if self.fase == "gooien" else 0):
            self.knoppen.append(Knop((px, 448, 220, 64), T("gooi"), self.gooi, GROEN, 28))
        if self.fase == "zetten":
            self.knoppen.append(Knop((px, 446, 105, 60), T("klaar"), self.klaar, GROEN, 22, aan=self.beurt_klaar()))
            self.knoppen.append(Knop((px + 115, 446, 110, 60), T("ongedaan"), self.ongedaan, VAK, 20, aan=bool(self.gedaan)))
            if self.app.hulp and self.mag_nu():
                self.knoppen.append(Knop((px, 514, 225, 46), T("tip"), self.geef_tip, GOUD, 22))
        if self.fase == "geen_zet" and self.mens(self.sp):
            self.knoppen.append(Knop((px, 446, 220, 60), T("verder"), self.volgende_speler, GROEN, 24))
        self.knoppen.append(Knop((px, H - 62, 105, 50), T("menu"), self.app.naar_menu, VAK, 20))
        self.knoppen.append(Knop((px + 115, H - 62, 110, 50), "%s: %s" % (T("hulp"), T("aan") if self.app.hulp else T("uitm")),
                                 self.app.wissel_hulp, GOUD if self.app.hulp else VAK, 17))
        tekst(d, self.score_tekst(), 17, ZACHT, (px, H - 92), vet=False)
        for k in self.knoppen:
            k.teken(d, muis)
        tekst(d, T("toetsen"), 15, ZACHT, (BX + BW // 2, BY + BH + 20), mid=True, vet=False)
        if self.app.hulp:
            tekst(d, T("gevaar_uitleg"), 19, ROOD, (BX + BW // 2, BY - 20), mid=True)
        if self.fase == "einde":
            self.teken_einde(d, muis)

    def _knip(self, t, px, breed):
        woorden, regels, r = (t or "").split(), [], ""
        for w in woorden:
            if font(px).size((r + " " + w).strip())[0] > breed and r:
                regels.append(r)
                r = w
            else:
                r = (r + " " + w).strip()
        if r:
            regels.append(r)
        return regels

    def teken_einde(self, d, muis):
        laag = pygame.Surface((W, H), pygame.SRCALPHA)
        laag.fill((10, 8, 16, 190))
        d.blit(laag, (0, 0))
        w, soort = self.einde
        tekst(d, T("wint") % self.naam(w), 56, GOUD, (W // 2, 280), mid=True)
        if soort == 2:
            tekst(d, T("gammon"), 32, ACCENT, (W // 2, 350), mid=True)
        elif soort == 3:
            tekst(d, T("backgammon"), 32, ACCENT, (W // 2, 350), mid=True)
        tekst(d, self.score_tekst(), 28, TEKST, (W // 2, 410), mid=True)
        self.knoppen = [Knop((W // 2 - 260, 480, 250, 70), T("nog"), self.nieuw_potje, GROEN, 28),
                        Knop((W // 2 + 10, 480, 250, 70), T("menu"), self.app.naar_menu, VAK, 28)]
        for k in self.knoppen:
            k.teken(d, muis)

    def toets(self, e):
        if e.key == pygame.K_SPACE:
            if self.fase in ("gooien", "wiebegint"):
                self.gooi()
            elif self.fase == "zetten":
                self.klaar()
            elif self.fase == "geen_zet" and self.mens(self.sp):
                self.volgende_speler()
        elif e.key == pygame.K_BACKSPACE:
            self.ongedaan()
        elif e.key == pygame.K_ESCAPE:
            self.app.naar_menu()


# ------------------------------------------------------------------ backgammon online
INST_PAD = os.path.join(DATA, "instellingen.json")


def laad_inst():
    inst = {"server": "https://dravevlag.dravenlock.workers.dev", "naam": "", "tokens": {}, "code": ""}
    try:
        with open(INST_PAD, encoding="utf-8") as f:
            inst.update(json.load(f))
    except Exception:
        pass
    return inst


def bewaar_inst(inst):
    try:
        with open(INST_PAD, "w", encoding="utf-8") as f:
            json.dump(inst, f, ensure_ascii=False, indent=1)
    except Exception:
        log_fout(traceback.format_exc())


class OnlineBackgammon(Backgammon):
    """Backgammon op twee pc's. De server gooit de stenen; je zet zelf, volgens de regels in deze app."""

    def __init__(self, app, adres, code, naam, token):
        self.lijn = None
        self.code = code
        self.ik = None
        self.ander = None
        self.verbonden = [False, False]
        self.status = T("verbinden")
        self.zetnr = None
        self.worpnr = None
        self.einde_gezien = False
        Backgammon.__init__(self, app, "online")
        self.lijn = online.Lijn(adres, code, {"t": "hallo", "naam": naam, "token": token})

    # namen en beurt
    def naam(self, sp):
        kleur = T("wit") if sp == 0 else T("zwart")
        if sp == self.ik:
            return "%s (%s)" % (T("jij"), kleur)
        return "%s (%s)" % (self.ander or T("tegenspeler"), kleur)

    def mens(self, sp):
        return self.ik is not None and sp == self.ik

    def score_tekst(self):
        if self.ik is None:
            return T("kamer") % self.code
        ik, hij = self.score[self.ik], self.score[1 - self.ik]
        return T("stand") % (T("jij"), ik, hij, self.ander or T("tegenspeler"))

    def nieuw_potje(self):
        if self.lijn is not None:                 # knop "Nog een potje"
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Backgammon.nieuw_potje(self)
        self.fase = "wachten"
        self.melding = T("verbinden")

    def gooi(self):
        if self.fase == "gooien" and self.mens(self.sp):
            if self.lijn.stuur({"t": "gooi"}):
                self.fase = "wacht_server"
                self.melding = T("versturen")

    def volgende_speler(self):
        """Mijn beurt is klaar (of er kon niets): stuur de nieuwe stand naar de server."""
        soort = R.soort_winst(self.s, self.ik) if R.winnaar(self.s) == self.ik else 1
        bericht = {"t": "zet", "s": self.s, "zetten": [list(z) for z in self.gedaan], "soort": soort}
        if self.lijn.stuur(bericht):
            self.laatste = list(self.gedaan)
            self.fase = "wacht_server"
            self.melding = T("versturen")
            self.app.geluid.speel("klik")
        else:
            self.status = T("geen_server")

    # berichten van de server
    def update(self):
        if self.lijn is None:
            return
        for b in self.lijn.haal():
            t = b.get("t")
            if t == "_verbonden":
                self.status = ""
            elif t == "_fout" or t == "_weg":
                self.status = T("geen_server")
            elif t == "welkom":
                self.ik = b.get("speler")
            elif t == "fout":
                self.status = T("kamer_vol") if b.get("fout") == "kamer vol" else str(b.get("fout"))[:60]
            elif t == "stand":
                try:
                    self.pas_toe(b)
                except Exception:
                    log_fout(traceback.format_exc())

    def pas_toe(self, st):
        self.ik = st["ik"]
        self.score = list(st.get("score", [0, 0]))
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        if st["fase"] == "wachten":
            self.fase = "wachten"
            self.melding = T("wacht_ander") % self.code
            return
        nieuwe_stand = st["zetnr"] != self.zetnr
        if nieuwe_stand:
            self.zetnr = st["zetnr"]
            ander_zette = self.s != st["s"] and st["beurt"] == self.ik
            self.s = {"bord": list(st["s"]["bord"]), "bar": list(st["s"]["bar"]), "uit": list(st["s"]["uit"])}
            self.laatste = [tuple(z) for z in st.get("laatste") or []]
            self.gekozen = None
            if ander_zette:
                self.app.geluid.speel("zet")
        self.sp = st["beurt"]
        if st["fase"] == "einde":
            self.einde = (st["winnaar"], st["soort"] or 1)
            self.fase = "einde"
            self.worp = None
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if st["winnaar"] == self.ik else "verlies")
            return
        self.einde_gezien = False
        if self.fase == "einde":
            self.laatste = []
        worp = st.get("worp")
        if worp and st["worpnr"] != self.worpnr:
            self.worpnr = st["worpnr"]
            self.app.geluid.speel("dobbel")
            bw = st.get("beginworp")
            self.begin_worp = None
            if self.mens(self.sp):
                self.start_beurt((worp[0], worp[1]))
                if bw:
                    self.melding = T("begint") % (self.naam(self.sp), worp[0], worp[1])
            else:
                self.worp = (worp[0], worp[1])
                self.over = [worp[0]] * 4 if worp[0] == worp[1] else list(self.worp)
                self.fase = "ander"
                self.melding = (T("begint") % (self.naam(self.sp), worp[0], worp[1])) if bw else (T("ander_beurt") % self.naam(self.sp))
        elif not worp:
            self.worp = None
            self.over = []
            if self.mens(self.sp):
                self.fase = "gooien"
                self.melding = T("geslagen") if self.s["bar"][self.sp] else T("beurt") % self.naam(self.sp)
            else:
                self.fase = "ander"
                self.melding = T("ander_gooit") % self.naam(self.sp)
        elif nieuwe_stand and not self.mens(self.sp):
            self.fase = "ander"

    def teken(self, d, muis):
        Backgammon.teken(self, d, muis)
        px = UITX + 80
        regels = []
        if self.status:
            regels.append((self.status, ROOD))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            regels.append((T("ander_weg") % self.ander, GOUD))
        regels.append((T("kamer") % self.code, ACCENT))
        if self.fase == "wachten":
            tekst(d, self.code, 56, GOUD, (px, 400))
        if self.fase != "einde":
            t, kl = regels[0]
            tekst(d, t, 17, kl, (px, 685))

    def stop(self):
        if self.lijn:
            self.lijn.stop()


# ------------------------------------------------------------------ de kast (menu)
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("DraveSpellenkast")
        try:
            pygame.display.set_icon(pygame.image.load(os.path.join(HERE, "assets", "icon.png")))
        except Exception:
            pass
        info = pygame.display.Info()
        schaal = min(1.0, (info.current_w - 60) / W, (info.current_h - 100) / H)
        self.venster = pygame.display.set_mode((int(W * schaal), int(H * schaal)), pygame.RESIZABLE)
        self.d = pygame.Surface((W, H))
        self.klok = pygame.time.Clock()
        self.geluid = Geluid()
        self.geluid.muziek_aan(True)
        self.scherm = "menu"
        self.spel = None
        self.knoppen = []
        self.toon_regels = False
        self.toon_info = False
        self.hulp = True

    def muis(self):
        mx, my = pygame.mouse.get_pos()
        vw, vh = self.venster.get_size()
        return int(mx * W / max(1, vw)), int(my * H / max(1, vh))

    def wissel_hulp(self):
        self.hulp = not self.hulp
        self.geluid.speel("klik")

    def naar_menu(self):
        self.geluid.stop("heli")
        if isinstance(self.spel, (OnlineBackgammon, vier.OnlineVier, zeeslag.OnlineZeeslag, wiebenik.OnlineWie,
                                  dammen.OnlineDammen, schaken.OnlineSchaken, galgje.OnlineGalgje,
                                  memory.OnlineMemory)) or (getattr(self.spel, "lijn", None) is not None and hasattr(self.spel, "stop")):
            self.spel.stop()
        self.scherm, self.spel = "menu", None
        self.geluid.speel("klik")

    def kies_tegenstander(self):
        self.scherm = "bg_kies"
        self.geluid.speel("klik")

    def start_bg(self, modus):
        self.spel = Backgammon(self, modus)
        self.scherm = "bg"
        self.geluid.speel("klik")

    # ---------- backgammon online: kamer maken of meedoen
    def naar_online(self, spel="bg"):
        self.online_spel = spel
        self.inst = laad_inst()
        self.invoer = "naam" if not self.inst.get("naam") else None
        self.online_melding = ""
        self.scherm = "bg_online"
        self.geluid.speel("klik")

    def token_voor(self, code):
        tokens = self.inst.setdefault("tokens", {})
        if code not in tokens:
            tokens[code] = secrets.token_hex(16)
            # niet eindeloos bewaren
            if len(tokens) > 20:
                for k in list(tokens)[:-20]:
                    tokens.pop(k, None)
        return tokens[code]

    def maak_kamer(self):
        self.online_melding = T("verbinden")
        self.teken_online(self.d, (0, 0))
        pygame.transform.smoothscale(self.d, self.venster.get_size(), self.venster)
        pygame.display.flip()
        try:
            code = online.nieuwe_kamer(self.inst["server"])
        except Exception:
            self.online_melding = T("geen_server")
            self.geluid.speel("verlies")
            return
        self.inst["code"] = code
        self.start_online(code)

    def meedoen(self):
        code = "".join(c for c in self.inst.get("code", "").upper() if c.isalnum())
        if len(code) != 6:
            self.invoer = "code"
            self.online_melding = T("code")
            return
        self.inst["code"] = code
        self.start_online(code)

    def start_online(self, code):
        naam = self.inst.get("naam", "").strip() or T("jij")
        token = self.token_voor(code)
        bewaar_inst(self.inst)
        if getattr(self, "online_spel", "bg") in NIEUW:
            info = NIEUW[self.online_spel]
            self.spel = getattr(sys.modules[info["mod"]], info["online"])(self, self.inst["server"], code, naam, token)
            self.scherm = self.online_spel
        elif getattr(self, "online_spel", "bg") == "vier":
            self.spel = vier.OnlineVier(self, self.inst["server"], code, naam, token)
            self.scherm = "vier"
        elif getattr(self, "online_spel", "bg") == "memo":
            self.spel = memory.OnlineMemory(self, self.inst["server"], code, naam, token)
            self.scherm = "memo"
        elif getattr(self, "online_spel", "bg") == "galg":
            self.spel = galgje.OnlineGalgje(self, self.inst["server"], code, naam, token)
            self.scherm = "galg"
        elif getattr(self, "online_spel", "bg") == "schaak":
            self.spel = schaken.OnlineSchaken(self, self.inst["server"], code, naam, token)
            self.scherm = "schaak"
        elif getattr(self, "online_spel", "bg") == "dam":
            self.spel = dammen.OnlineDammen(self, self.inst["server"], code, naam, token)
            self.scherm = "dam"
        elif getattr(self, "online_spel", "bg") == "wie":
            self.spel = wiebenik.OnlineWie(self, self.inst["server"], code, naam, token)
            self.scherm = "wie"
        elif getattr(self, "online_spel", "bg") == "zee":
            self.spel = zeeslag.OnlineZeeslag(self, self.inst["server"], code, naam, token)
            self.scherm = "zee"
        else:
            self.spel = OnlineBackgammon(self, self.inst["server"], code, naam, token)
            self.scherm = "bg"
        self.geluid.speel("klik")

    def veld(self, d, x, y, w, label, waarde, sleutel, muis):
        tekst(d, label, 22, ZACHT, (x, y))
        r = pygame.Rect(x, y + 32, w, 62)
        actief = self.invoer == sleutel
        pygame.draw.rect(d, (44, 38, 64) if actief else VAK, r, border_radius=12)
        pygame.draw.rect(d, GOUD if actief else RAND, r, 3, border_radius=12)
        knipper = actief and (pygame.time.get_ticks() // 500) % 2 == 0
        s = font(30, sleutel == "code").render(waarde + ("|" if knipper else ""), True, TEKST)
        d.blit(s, s.get_rect(midleft=(r.x + 16, r.centery)))
        self.knoppen.append(Knop(r, "", lambda: setattr(self, "invoer", sleutel)))

    def teken_online(self, d, muis):
        d.fill(ACHTER)
        titel = {"memo": T("online_memo"), "galg": T("online_galg"), "schaak": T("online_schaak"), "dam": T("online_dam"), "vier": T("online_vier"), "zee": T("online_zee"), "wie": T("online_wie")}.get(getattr(self, "online_spel", "bg"), T("online_" + getattr(self, "online_spel", "bg")) if getattr(self, "online_spel", "bg") in NIEUW else T("online_titel"))
        tekst(d, titel, 46, ACCENT, (W // 2, 60), mid=True)
        self.knoppen = []
        self.veld(d, 140, 120, 460, T("jouw_naam"), self.inst.get("naam", ""), "naam", muis)
        self.veld(d, 680, 120, 460, T("server"), self.inst.get("server", ""), "server", muis)
        self.knoppen.append(Knop((140, 270, 460, 90), T("maak_kamer"), self.maak_kamer, GROEN, 30))
        self.veld(d, 680, 236, 260, T("code"), self.inst.get("code", ""), "code", muis)
        self.knoppen.append(Knop((960, 268, 180, 90), T("meedoen"), self.meedoen, GROEN, 28))
        y = 410
        for regel in T("online_uitleg").split("\n"):
            for stuk in Backgammon._knip(None, regel, 22, W - 280):
                tekst(d, stuk, 22, TEKST, (140, y), vet=False)
                y += 32
            y += 8
        tekst(d, T("klik_veld"), 20, ZACHT, (140, y + 6), vet=False)
        if self.online_melding:
            tekst(d, self.online_melding, 26, GOUD, (W // 2, 640), mid=True)
        terug = {"memo": self.kies_memo, "galg": self.kies_galg, "schaak": self.kies_schaak, "dam": self.kies_dam, "vier": self.kies_vier, "zee": self.kies_zee, "wie": self.kies_wie}.get(getattr(self, "online_spel", "bg"), (lambda: self.kies_nieuw(self.online_spel)) if getattr(self, "online_spel", "bg") in NIEUW else self.kies_tegenstander)
        self.knoppen.append(Knop((40, H - 90, 200, 60), T("terug"), terug, VAK, 24))
        for k in self.knoppen:
            if k.label:
                k.teken(d, muis)

    def typ(self, e):
        if not self.invoer:
            return
        sleutel = self.invoer
        waarde = self.inst.get(sleutel, "")
        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
            volgorde = ["naam", "server", "code"]
            self.invoer = volgorde[(volgorde.index(sleutel) + 1) % 3]
            if sleutel == "code" and e.key != pygame.K_TAB:
                self.invoer = None
                self.meedoen()
            bewaar_inst(self.inst)
            return
        if e.key == pygame.K_BACKSPACE:
            waarde = waarde[:-1]
        elif e.key == pygame.K_v and (e.mod & pygame.KMOD_CTRL):
            try:
                pygame.scrap.init()
                plak = pygame.scrap.get(pygame.SCRAP_TEXT) or b""
                waarde += plak.decode("utf-8", "ignore").replace("\x00", "").strip()
            except Exception:
                pass
        elif e.unicode and e.unicode.isprintable():
            waarde += e.unicode.upper() if sleutel == "code" else e.unicode
        maxl = {"naam": 20, "server": 80, "code": 6}[sleutel]
        self.inst[sleutel] = waarde[:maxl]

    def kies_zee(self):
        self.scherm = "zee_kies"
        self.geluid.speel("klik")

    def start_zee(self, niveau):
        self.spel = zeeslag.Zeeslag(self, niveau)
        self.scherm = "zee"
        self.geluid.speel("klik")

    def teken_kies_zee(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("zee"), 48, ACCENT, (W // 2, 120), mid=True)
        tekst(d, T("tegen"), 30, TEKST, (W // 2, 200), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("comp_mak"), lambda: self.start_zee(1), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("comp_normaal"), lambda: self.start_zee(2), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("comp_moeilijk"), lambda: self.start_zee(3), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("online_knop"), lambda: self.naar_online("zee"), VAK, 28),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    def kies_wie(self):
        self.scherm = "wie_kies"
        self.geluid.speel("klik")

    def start_wie(self, niveau):
        self.spel = wiebenik.WieBenIk(self, niveau)
        self.scherm = "wie"
        self.geluid.speel("klik")

    def teken_kies_wie(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("wie"), 48, ACCENT, (W // 2, 120), mid=True)
        tekst(d, T("tegen"), 30, TEKST, (W // 2, 200), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("comp_mak"), lambda: self.start_wie(1), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("comp_normaal"), lambda: self.start_wie(2), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("comp_moeilijk"), lambda: self.start_wie(3), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("online_knop"), lambda: self.naar_online("wie"), VAK, 28),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    def kies_vier(self):
        self.scherm = "vier_kies"
        self.geluid.speel("klik")

    def start_vier(self, niveau):
        self.spel = vier.VierOpEenRij(self, niveau)
        self.scherm = "vier"
        self.geluid.speel("klik")

    def teken_kies_vier(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("vier"), 48, ACCENT, (W // 2, 120), mid=True)
        tekst(d, T("tegen"), 30, TEKST, (W // 2, 200), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("comp_mak"), lambda: self.start_vier(1), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("comp_normaal"), lambda: self.start_vier(2), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("comp_moeilijk"), lambda: self.start_vier(3), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("online_knop"), lambda: self.naar_online("vier"), VAK, 28),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    def kies_dam(self):
        self.scherm = "dam_kies"
        self.geluid.speel("klik")

    def start_dam(self, niveau):
        self.spel = dammen.Dammen(self, niveau)
        self.scherm = "dam"
        self.geluid.speel("klik")

    def teken_kies_dam(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("dam"), 48, ACCENT, (W // 2, 120), mid=True)
        tekst(d, T("tegen"), 30, TEKST, (W // 2, 200), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("comp_mak"), lambda: self.start_dam(1), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("comp_normaal"), lambda: self.start_dam(2), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("comp_moeilijk"), lambda: self.start_dam(3), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("online_knop"), lambda: self.naar_online("dam"), VAK, 28),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    def kies_schaak(self):
        self.scherm = "schaak_kies"
        self.geluid.speel("klik")

    def start_schaak(self, niveau):
        self.spel = schaken.Schaken(self, niveau)
        self.scherm = "schaak"
        self.geluid.speel("klik")

    def start_schaakles(self):
        self.spel = schaken.SchaakLes(self)
        self.scherm = "schaak"
        self.geluid.speel("klik")

    def teken_kies_schaak(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("schaak"), 48, ACCENT, (W // 2, 120), mid=True)
        tekst(d, T("tegen"), 30, TEKST, (W // 2, 200), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("comp_mak"), lambda: self.start_schaak(1), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("comp_normaal"), lambda: self.start_schaak(2), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("comp_moeilijk"), lambda: self.start_schaak(3), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("online_knop"), lambda: self.naar_online("schaak"), VAK, 28),
            Knop((W // 2 - 300, 590, 600, 72), T("leer_schaak"), self.start_schaakles, GOUD, 28),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    def kies_galg(self):
        self.scherm = "galg_kies"
        self.geluid.speel("klik")

    def start_galg(self, niveau):
        self.spel = galgje.Galgje(self, niveau)
        self.scherm = "galg"
        self.geluid.speel("klik")

    def teken_kies_galg(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("galg"), 48, ACCENT, (W // 2, 120), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("galg_mak"), lambda: self.start_galg(1), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("galg_norm"), lambda: self.start_galg(2), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("galg_moeil"), lambda: self.start_galg(3), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("galg_online"), lambda: self.naar_online("galg"), VAK, 24),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    def kies_memo(self):
        self.scherm = "memo_kies"
        self.geluid.speel("klik")

    def start_memo(self, niveau):
        self.spel = memory.Memory(self, niveau)
        self.scherm = "memo"
        self.geluid.speel("klik")

    def teken_kies_memo(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("memo"), 48, ACCENT, (W // 2, 120), mid=True)
        tekst(d, T("tegen"), 30, TEKST, (W // 2, 200), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("memo_mak"), lambda: self.start_memo(1), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("memo_norm"), lambda: self.start_memo(2), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("memo_moeil"), lambda: self.start_memo(3), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("online_knop"), lambda: self.naar_online("memo"), VAK, 28),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    # ---------- nieuwe spellen: één kies-scherm voor allemaal
    def kies_nieuw(self, naam):
        self.scherm = naam + "_kies"
        self.geluid.speel("klik")

    def start_nieuw(self, naam, niveau):
        info = NIEUW[naam]
        self.spel = getattr(sys.modules[info["mod"]], info["klasse"])(self, niveau)
        self.scherm = naam
        self.geluid.speel("klik")

    def teken_kies_nieuw(self, d, muis, naam):
        d.fill(ACHTER)
        info = NIEUW[naam]
        tekst(d, T(naam), 48, ACCENT, (W // 2, 110), mid=True)
        self.knoppen = []
        y = 190
        for label, niveau in info["keuzes"]:
            self.knoppen.append(Knop((W // 2 - 330, y, 660, 68), T(label), lambda n=niveau: self.start_nieuw(naam, n), VAK, 26))
            y += 82
        if info.get("online"):
            self.knoppen.append(Knop((W // 2 - 330, y, 660, 68), T("online_knop"), lambda: self.naar_online(naam), VAK, 26))
        self.knoppen.append(Knop((W // 2 + 350, 190, 200, 68), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")),
                                 self.wissel_hulp, GOUD if self.hulp else VAK, 22))
        self.knoppen.append(Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24))
        for k in self.knoppen:
            k.teken(d, muis)

    def kies_topo(self):
        self.topo_keuze = topo.Keuze(self)
        self.scherm = "topo_kies"
        self.geluid.speel("klik")

    def start_topo(self, onderwerp, vorm, spelers):
        self.spel = topo.Topografie(self, onderwerp, vorm, spelers)
        self.scherm = "topo"
        self.geluid.speel("klik")

    def teken_menu(self, d, muis):
        d.fill(ACHTER)
        try:
            if not hasattr(self, "_logo"):
                self._logo = pygame.transform.smoothscale(pygame.image.load(os.path.join(HERE, "assets", "logo_t.png")).convert_alpha(), (90, 90))
            d.blit(self._logo, (40, 30))
        except Exception:
            pass
        tekst(d, T("titel"), 54, ACCENT, (150, 40))
        tekst(d, T("sub"), 26, ZACHT, (152, 104), vet=False)
        self.knoppen = []
        tegels = [("bg", "bg_sub", self.kies_tegenstander, True), ("topo", "topo_sub", self.kies_topo, True),
                  ("vier", "vier_sub", self.kies_vier, True), ("zee", "zee_sub", self.kies_zee, True),
                  ("wie", "wie_sub", self.kies_wie, True), ("dam", "dam_sub", self.kies_dam, True),
                  ("schaak", "schaak_sub", self.kies_schaak, True), ("galg", "galg_sub", self.kies_galg, True),
                  ("memo", "memo_sub", self.kies_memo, True),
                  ("lingo", "lingo_sub", lambda: self.kies_nieuw("lingo"), True),
                  ("rev", "rev_sub", lambda: self.kies_nieuw("rev"), True),
                  ("domino", "domino_sub", lambda: self.kies_nieuw("domino"), True),
                  ("gans", "gans_sub", lambda: self.kies_nieuw("gans"), True),
                  ("pest", "pest_sub", lambda: self.kies_nieuw("pest"), True),
                  ("puzzel", "puzzel_sub", lambda: self.kies_nieuw("puzzel"), True),
                  ("sudoku", "sudoku_sub", lambda: self.kies_nieuw("sudoku"), True),
                  ("duel", "duel_sub", lambda: self.kies_nieuw("duel"), True),
                  ("meer", "meer_sub", None, False)]
        kol = 3 if len(tegels) <= 6 else 4 if len(tegels) <= 12 else 6
        tus = 20 if kol < 6 else 14
        rijen = (len(tegels) + kol - 1) // kol
        tw = (W - 80 - (kol - 1) * tus) // kol
        th = min(225, (490 - (rijen - 1) * tus) // rijen)
        klein = kol > 3                                  # kleinere tegels: plaatje en tekst kleiner
        mini = kol >= 6                                  # heel veel spellen: plaatje met de naam eronder
        uitleg = None
        for k, (titel, sub, actie, aan) in enumerate(tegels):
            r = pygame.Rect(40 + (k % kol) * (tw + tus), (140 if mini else 150) + (k // kol) * (th + tus), tw, th)
            hover = aan and r.collidepoint(muis)
            pygame.draw.rect(d, (50, 44, 72) if hover else VAK, r, border_radius=22)
            pygame.draw.rect(d, ACCENT if hover else RAND, r, 4, border_radius=22)
            if titel not in getattr(self, "_tegel_plaatjes", {}):
                if not hasattr(self, "_tegel_plaatjes"):
                    self._tegel_plaatjes = {}
                p = pygame.Surface((300, 280), pygame.SRCALPHA)
                self.teken_tegel_plaatje(p, titel, 150, 140, aan)
                self._tegel_plaatjes[titel] = pygame.transform.smoothscale(p, (150, 140))
            pl = self._tegel_plaatjes[titel]
            if mini:
                ph = th - 48
                pl = pygame.transform.smoothscale(pl, (int(ph * 150 / 140), ph))
                d.blit(pl, (r.centerx - pl.get_width() // 2, r.y + 8))
                px_t = 24
                while px_t > 15 and font(px_t).size(T(titel))[0] > r.w - 14:
                    px_t -= 1
                tekst(d, T(titel), px_t, TEKST if aan else ZACHT, (r.centerx, r.bottom - 22), mid=True)
                if hover or (not aan and r.collidepoint(muis)):
                    uitleg = T(titel) + ": " + T(sub) + ("" if aan else "  (" + T("binnenkort") + ")")
            elif klein:
                ph = min(110, th - 30)
                pl = pygame.transform.smoothscale(pl, (int(ph * 150 / 140), ph))
                d.blit(pl, (r.x + 10, r.y + (th - ph) // 2))
                tx = r.x + 20 + pl.get_width()
                px_t = 24
                while px_t > 16 and font(px_t).size(T(titel))[0] > r.right - tx - 10:
                    px_t -= 1                                # lange naam: iets kleiner, zodat hij past
                tekst(d, T(titel), px_t, TEKST if aan else ZACHT, (tx, r.y + 22))
                for i, regel in enumerate(Backgammon._knip(None, T(sub), 16, r.right - tx - 12)[:4]):
                    tekst(d, regel, 16, ZACHT, (tx, r.y + 54 + i * 20), vet=False)
                if not aan:
                    tekst(d, T("binnenkort"), 17, GOUD, (tx, r.bottom - 34))
            else:
                d.blit(pl, (r.x + 14, r.y + 42))
                tekst(d, T(titel), 28, TEKST if aan else ZACHT, (r.x + 175, r.y + 40))
                for i, regel in enumerate(Backgammon._knip(None, T(sub), 20, 195)):
                    tekst(d, regel, 20, ZACHT, (r.x + 175, r.y + 90 + i * 26), vet=False)
                if not aan:
                    tekst(d, T("binnenkort"), 20, GOUD, (r.x + 175, r.y + 180))
            if actie:
                self.knoppen.append(Knop(r, "", actie))
        onder_y = 660
        if mini:                                         # uitleg van de tegel onder de muis
            tekst(d, uitleg or T("kies_muis"), 20, GOUD if uitleg else ZACHT, (W // 2, 642), mid=True, vet=False)
            onder_y = 672
        self.knoppen.append(Knop((60, onder_y, 220, 60), "%s: %s" % (T("muziek"), T("aan") if self.geluid.muziek_staat else T("uitm")),
                                 lambda: self.geluid.muziek_aan(not self.geluid.muziek_staat), VAK, 22))
        self.knoppen.append(Knop((300, onder_y, 200, 60), T("regels"), lambda: setattr(self, "toon_regels", True), VAK, 22))
        self.knoppen.append(Knop((520, onder_y, 160, 60), T("info"), lambda: setattr(self, "toon_info", True), VAK, 22))
        self.knoppen.append(Knop((W - 360, onder_y, 300, 60), T("doneer"), lambda: webbrowser.open("https://paypal.me/roger076"), GOUD, 22))
        for k in self.knoppen:
            if k.label:
                k.teken(d, muis)
        tekst(d, "v" + VERSIE, 16, ZACHT, (W - 20, H - 30), rechts=True, vet=False)

    def _knip_sub(self, t):
        return Backgammon._knip(None, t, 20, 250)

    def teken_tegel_plaatje(self, d, soort, cx, cy, aan):
        if soort == "bg":
            for i in range(6):
                kl = PUNT_A if i % 2 == 0 else PUNT_B
                x = cx - 135 + i * 45
                pygame.draw.polygon(d, kl, [(x, cy + 70), (x + 40, cy + 70), (x + 20, cy - 40)])
            teken_steen(d, cx - 60, cy + 40, 0, r=26)
            teken_steen(d, cx - 10, cy + 40, 1, r=26)
            teken_dobbel(d, cx + 30, cy - 75, 5, 50)
            teken_dobbel(d, cx + 70, cy - 30, 3, 50)
        elif soort == "topo":
            kl = PAARS if aan else (80, 74, 104)
            nl = [(-40, -110), (30, -120), (70, -80), (80, -20), (60, 30), (90, 80), (40, 110), (-10, 90), (-60, 100),
                  (-90, 60), (-70, 10), (-100, -20), (-60, -60)]
            pygame.draw.polygon(d, kl, [(cx + x, cy + y) for x, y in nl])
            pygame.draw.polygon(d, RAND, [(cx + x, cy + y) for x, y in nl], 3)
            for x, y in ((-20, -40), (30, 20), (-40, 50)):
                pygame.draw.circle(d, GOUD, (cx + x, cy + y), 8)
        elif soort == "wie":
            for i, k in enumerate((3, 14, 9)):
                r = pygame.Rect(cx - 140 + i * 95, cy - 90 + (i % 2) * 20, 90, 116)
                wiebenik.teken_figuur(d, wiebenik.FIGUREN[k], r, dicht=(i == 2))
            tekst(d, "?", 70, GOUD, (cx + 110, cy - 60), mid=True)
        elif soort == "zee":
            pygame.draw.rect(d, zeeslag.ZEE, (cx - 120, cy - 100, 240, 200), border_radius=16)
            for i in range(5):
                pygame.draw.line(d, zeeslag.LIJN, (cx - 120 + i * 48, cy - 100), (cx - 120 + i * 48, cy + 100), 2)
                pygame.draw.line(d, zeeslag.LIJN, (cx - 120, cy - 100 + i * 40), (cx + 120, cy - 100 + i * 40), 2)
            romp = [(cx - 100, cy - 20), (cx - 70, cy - 50), (cx + 90, cy - 50), (cx + 100, cy - 35), (cx + 100, cy - 5), (cx + 90, cy + 10), (cx - 70, cy + 10)]
            pygame.draw.polygon(d, zeeslag.ROMP, romp)
            pygame.draw.polygon(d, zeeslag.ROMP_D, romp, 4)
            pygame.draw.rect(d, zeeslag.ROMP_D, (cx - 10, cy - 70, 50, 30), border_radius=6)
            pygame.draw.circle(d, (200, 50, 40), (cx + 60, cy + 60), 22)
            pygame.draw.circle(d, zeeslag.VUUR, (cx + 60, cy + 56), 14)
            pygame.draw.circle(d, (220, 232, 250), (cx - 70, cy + 60), 10)
            pygame.draw.circle(d, (160, 190, 230), (cx - 70, cy + 60), 18, 3)
        elif soort == "dam":
            for rr in range(5):
                for cc in range(5):
                    kl = dammen.DONKER_VAK if (rr + cc) % 2 else dammen.LICHT_VAK
                    if not aan:
                        kl = tuple(int(c * 0.6) for c in kl)
                    pygame.draw.rect(d, kl, (cx - 110 + cc * 44, cy - 110 + rr * 44, 44, 44))
            for (rr, cc, sp, dm) in ((0, 1, -1, False), (0, 3, -1, False), (1, 2, -1, False), (3, 0, 1, False), (3, 2, 1, True), (4, 3, 1, False)):
                x, y = cx - 110 + cc * 44 + 22, cy - 110 + rr * 44 + 22
                boven, onder = dammen.STUK[sp]
                pygame.draw.circle(d, onder, (x, y + 4), 18)
                pygame.draw.circle(d, boven, (x, y), 18)
                pygame.draw.circle(d, onder, (x, y), 11, 2)
                if dm:
                    pygame.draw.polygon(d, GOUD, [(x - 10, y + 5), (x - 10, y - 4), (x - 5, y + 1), (x, y - 8), (x + 5, y + 1), (x + 10, y - 4), (x + 10, y + 5)])
        elif soort == "rev":
            pygame.draw.rect(d, (42, 110, 76) if aan else (70, 80, 76), (cx - 110, cy - 110, 220, 220), border_radius=12)
            for i in range(1, 4):
                pygame.draw.line(d, (28, 70, 50), (cx - 110 + i * 55, cy - 110), (cx - 110 + i * 55, cy + 110), 2)
                pygame.draw.line(d, (28, 70, 50), (cx - 110, cy - 110 + i * 55), (cx + 110, cy - 110 + i * 55), 2)
            for (rr, cc, sp) in ((1, 1, -1), (1, 2, 1), (2, 1, 1), (2, 2, -1), (0, 2, 1), (3, 0, -1)):
                boven, onder = reversi.KLEUR[sp]
                x, y = cx - 110 + cc * 55 + 27, cy - 110 + rr * 55 + 27
                pygame.draw.circle(d, onder, (x, y + 3), 22)
                pygame.draw.circle(d, boven, (x, y), 22)
        elif soort == "duel":
            for i, sl in enumerate(("wolf", "draak", "engel")):
                rr = pygame.Rect(cx - 150 + i * 102, cy - 85 + (12 if i != 1 else 0), 96, 140)
                duel.teken_kaart(d, sl, rr, aan=aan)
        elif soort == "domino":
            dm = domino.Domino.__new__(domino.Domino)
            for i, (a, b) in enumerate(((6, 3), (3, 3), (3, 5))):
                rr = pygame.Rect(cx - 140 + i * 94, cy - 60, 88, 44)
                domino.Domino.teken_steen(dm, d, rr, a, b)
            for i, (a, b) in enumerate(((5, 1), (2, 4))):
                rr = pygame.Rect(cx - 60 + i * 70, cy + 10, 44, 88)
                domino.Domino.teken_steen(dm, d, rr, a, b, staand=True)
        elif soort == "gans":
            for i in range(9):
                a = i * 0.7
                x, y = cx + int(math.cos(a) * (100 - i * 9)), cy + int(math.sin(a) * (95 - i * 9))
                pygame.draw.rect(d, (70, 110, 170) if i % 3 == 1 else (60, 52, 92), (x - 20, y - 20, 40, 40), border_radius=8)
            gb = ganzenbord.Ganzenbord.__new__(ganzenbord.Ganzenbord)
            ganzenbord.Ganzenbord.teken_gans(gb, d, cx, cy + 10, 2.4)
        elif soort == "pest":
            ps = pesten.Pesten.__new__(pesten.Pesten)
            for i, c in enumerate((("7", "h"), ("B", "s"), ("2", "r"), ("X", "*"))):
                rr = pygame.Rect(cx - 125 + i * 56, cy - 80 + abs(i - 1.5) * 10, 92, 132)
                pesten.Pesten.teken_kaart(ps, d, rr, c)
        elif soort == "puzzel":
            try:
                im = pygame.image.load(os.path.join(HERE, "assets", "kunst", "kunst_05.jpg")).convert()
                im = pygame.transform.smoothscale(im, (210, 210))
                for i in range(9):
                    x, y = i % 3 * 70, i // 3 * 70
                    dx = 8 if i == 4 else 0
                    d.blit(im, (cx - 105 + x + dx, cy - 105 + y - dx), (x, y, 70, 70))
                    pygame.draw.rect(d, ACHTER, (cx - 105 + x + dx, cy - 105 + y - dx, 70, 70), 2)
            except Exception:
                pygame.draw.rect(d, PAARS, (cx - 100, cy - 100, 200, 200), border_radius=12)
        elif soort == "sudoku":
            pygame.draw.rect(d, (240, 236, 248) if aan else (120, 116, 130), (cx - 105, cy - 105, 210, 210), border_radius=8)
            cijfers = "5 3 . . 7 . . . . 6 . . 1 9 5 . . . . 9 8 . . . . 6 .".split()
            for i, ch in enumerate(cijfers[:27]):
                x, y = cx - 105 + i % 9 * 23 + 12, cy - 105 + i // 9 * 70 + 35
                if ch != ".":
                    tekst(d, ch, 20, (34, 28, 50), (x, y), mid=True)
            for k in range(4):
                pygame.draw.line(d, (40, 32, 60), (cx - 105 + k * 70, cy - 105), (cx - 105 + k * 70, cy + 105), 3)
                pygame.draw.line(d, (40, 32, 60), (cx - 105, cy - 105 + k * 70), (cx + 105, cy - 105 + k * 70), 3)
        elif soort == "lingo":
            for i, (c, k) in enumerate(zip("LINGO", (2, 1, 0, 2, 2))):
                x = cx - 125 + i * 52
                kl = (lingo.GRIJS_L, lingo.GEEL_L, lingo.GROEN_L)[k] if aan else (80, 74, 104)
                if k == 1:
                    pygame.draw.rect(d, VAK, (x, cy - 50, 46, 46), border_radius=8)
                    pygame.draw.circle(d, kl, (x + 23, cy - 27), 21)
                else:
                    pygame.draw.rect(d, kl, (x, cy - 50, 46, 46), border_radius=8)
                tekst(d, c, 30, (255, 255, 255), (x + 23, cy - 27), mid=True)
            for i in range(5):
                pygame.draw.rect(d, VAK, (cx - 125 + i * 52, cy + 4, 46, 46), border_radius=8)
                pygame.draw.rect(d, RAND, (cx - 125 + i * 52, cy + 4, 46, 46), 2, border_radius=8)
        elif soort == "memo":
            for i, (nr, open_) in enumerate(((3, True), (None, False), (3, True), (None, False))):
                rr = pygame.Rect(cx - 120 + (i % 2) * 120, cy - 110 + (i // 2) * 115, 105, 105)
                if open_:
                    pygame.draw.rect(d, (44, 38, 70), rr, border_radius=12)
                    pygame.draw.rect(d, GOUD, rr, 4, border_radius=12)
                    memory.teken_plaatje(d, 13 if aan else 2, rr.inflate(-16, -16))
                else:
                    pygame.draw.rect(d, PAARS if aan else (80, 74, 104), rr, border_radius=12)
                    pygame.draw.rect(d, RAND, rr, 4, border_radius=12)
        elif soort == "galg":
            hout = (150, 112, 70) if aan else (90, 80, 90)
            pygame.draw.rect(d, (90, 64, 40), (cx - 110, cy + 90, 200, 14), border_radius=4)
            pygame.draw.rect(d, hout, (cx - 80, cy - 110, 14, 205), border_radius=3)
            pygame.draw.rect(d, hout, (cx - 80, cy - 110, 130, 13), border_radius=3)
            pygame.draw.line(d, (200, 190, 160), (cx + 30, cy - 98), (cx + 30, cy - 70), 4)
            kl = ACCENT if aan else ZACHT
            pygame.draw.circle(d, kl, (cx + 30, cy - 52), 18, 5)
            pygame.draw.line(d, kl, (cx + 30, cy - 34), (cx + 30, cy + 20), 5)
            pygame.draw.line(d, kl, (cx + 30, cy - 20), (cx + 4, cy + 4), 5)
            pygame.draw.line(d, kl, (cx + 30, cy - 20), (cx + 56, cy + 4), 5)
            for i, c in enumerate("G_L_E"):
                tekst(d, c if c != "_" else "_", 30, GOUD, (cx - 60 + i * 34, cy + 50), mid=True)
        elif soort == "schaak":
            for rr in range(4):
                for cc in range(5):
                    kl = schaken.LICHT_VAK if (rr + cc) % 2 == 0 else schaken.DONKER_VAK
                    if not aan:
                        kl = tuple(int(c * 0.6) for c in kl)
                    pygame.draw.rect(d, kl, (cx - 110 + cc * 44, cy - 60 + rr * 44, 44, 44))
            for g, x, y in (("K", cx - 50, cy - 50), ("n", cx + 50, cy - 40)):
                p = schaken.stuk_plaatje(g, 110)
                d.blit(p, p.get_rect(center=(x, y)))
        elif soort == "vier":
            pygame.draw.rect(d, (70, 58, 120) if aan else (60, 54, 84), (cx - 110, cy - 90, 220, 190), border_radius=16)
            stand = ["......", "......", "...g..", "..rg..", ".grrg.", "rggrrg"]
            for r, regel in enumerate(stand):
                for k, c in enumerate(regel[:6]):
                    kl = {"g": vier.KLEUR[0], "r": vier.KLEUR[1]}.get(c, ACHTER)
                    pygame.draw.circle(d, kl, (cx - 88 + k * 35, cy - 70 + r * 31), 13)
        else:
            for i in range(3):
                pygame.draw.rect(d, (80, 74, 104), (cx - 110 + i * 80, cy - 50, 60, 90), border_radius=10)
            tekst(d, "?", 60, ZACHT, (cx, cy), mid=True)

    def teken_tekstvak(self, d, titel, regels, muis):
        laag = pygame.Surface((W, H), pygame.SRCALPHA)
        laag.fill((10, 8, 16, 200))
        d.blit(laag, (0, 0))
        r = pygame.Rect(110, 40, W - 220, H - 80)
        pygame.draw.rect(d, VAK, r, border_radius=20)
        pygame.draw.rect(d, ACCENT, r, 4, border_radius=20)
        tekst(d, titel, 36, ACCENT, (r.x + 40, r.y + 30))
        y = r.y + 100
        for regel in regels:
            kop = regel.split(":")[0] if regel[:5].isupper() else None
            if kop:
                y += 8
                tekst(d, kop, 24, GOUD, (r.x + 40, y))
                y += 34
                regel = regel[len(kop) + 1:].strip()
                regel = regel[:1].upper() + regel[1:]
            for stuk in Backgammon._knip(None, regel, 22, r.w - 80):
                tekst(d, stuk, 22, TEKST, (r.x + 40, y), vet=False)
                y += 30
            y += 6
        self.knoppen = [Knop((r.centerx - 100, r.bottom - 90, 200, 60), "OK", self.sluit_vak, GROEN, 26)]
        if self.toon_info:
            self.knoppen.append(Knop((r.x + 40, r.bottom - 90, 300, 60), T("doneer"), lambda: webbrowser.open("https://paypal.me/roger076"), GOUD, 22))
        for k in self.knoppen:
            k.teken(d, muis)

    def sluit_vak(self):
        self.toon_regels = self.toon_info = False

    def teken_kies(self, d, muis):
        d.fill(ACHTER)
        tekst(d, T("bg"), 48, ACCENT, (W // 2, 120), mid=True)
        tekst(d, T("tegen"), 30, TEKST, (W // 2, 200), mid=True)
        self.knoppen = [
            Knop((W // 2 - 300, 250, 600, 72), T("comp_oefen"), lambda: self.start_bg("comp0"), VAK, 28),
            Knop((W // 2 - 300, 335, 600, 72), T("comp_mak"), lambda: self.start_bg("comp1"), VAK, 28),
            Knop((W // 2 - 300, 420, 600, 72), T("comp_goed"), lambda: self.start_bg("comp2"), VAK, 28),
            Knop((W // 2 - 300, 505, 600, 72), T("samen"), lambda: self.start_bg("samen"), VAK, 28),
            Knop((W // 2 - 300, 590, 600, 72), T("online_knop"), self.naar_online, VAK, 28),
            Knop((W // 2 + 320, 250, 200, 72), "%s: %s" % (T("hulp"), T("aan") if self.hulp else T("uitm")), self.wissel_hulp, GOUD if self.hulp else VAK, 22),
            Knop((40, H - 90, 200, 60), T("terug"), self.naar_menu, VAK, 24),
        ]
        for k in self.knoppen:
            k.teken(d, muis)

    def loop(self):
        while True:
            muis = self.muis()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.VIDEORESIZE:
                    self.venster = pygame.display.set_mode((max(640, e.w), max(400, e.h)), pygame.RESIZABLE)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_m and self.scherm not in ("galg", "lingo") and not (self.scherm == "bg_online" and self.invoer):
                        self.geluid.muziek_aan(not self.geluid.muziek_staat)
                    elif self.scherm == "bg_online" and self.invoer and e.key != pygame.K_ESCAPE:
                        self.typ(e)
                    elif self.toon_regels or self.toon_info:
                        if e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                            self.sluit_vak()
                    elif self.scherm in SPEL_SCHERMEN and self.spel:
                        self.spel.toets(e)
                    elif e.key == pygame.K_ESCAPE:
                        if self.scherm == "menu":
                            return
                        self.naar_menu()
                    elif e.key == pygame.K_F1:
                        self.toon_info = True
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    pos = self.muis()
                    if any(k.klik(pos) for k in list(self.knoppen)):
                        continue
                    if self.scherm in SPEL_SCHERMEN and self.spel and not (self.toon_regels or self.toon_info):
                        self.spel.klik(pos)
                if e.type == pygame.MOUSEWHEEL and self.scherm == "wie" and self.spel:
                    self.spel.wiel(e.y)
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3 and self.scherm == "zee" and self.spel:
                    self.spel.klik_rechts(self.muis())
            if self.scherm in SPEL_SCHERMEN and self.spel:
                self.spel.update()
                self.spel.teken(self.d, muis)
                self.knoppen = self.spel.knoppen
            elif self.scherm == "bg_kies":
                self.teken_kies(self.d, muis)
            elif self.scherm == "vier_kies":
                self.teken_kies_vier(self.d, muis)
            elif self.scherm == "dam_kies":
                self.teken_kies_dam(self.d, muis)
            elif self.scherm == "schaak_kies":
                self.teken_kies_schaak(self.d, muis)
            elif self.scherm == "galg_kies":
                self.teken_kies_galg(self.d, muis)
            elif self.scherm == "memo_kies":
                self.teken_kies_memo(self.d, muis)
            elif self.scherm.endswith("_kies") and self.scherm[:-5] in NIEUW:
                self.teken_kies_nieuw(self.d, muis, self.scherm[:-5])
            elif self.scherm == "zee_kies":
                self.teken_kies_zee(self.d, muis)
            elif self.scherm == "wie_kies":
                self.teken_kies_wie(self.d, muis)
            elif self.scherm == "bg_online":
                self.teken_online(self.d, muis)
            elif self.scherm == "topo_kies":
                self.topo_keuze.teken(self.d, muis)
                self.knoppen = self.topo_keuze.knoppen
            else:
                self.teken_menu(self.d, muis)
            if self.toon_regels:
                self.teken_tekstvak(self.d, T("regels"), regels_voor(self.scherm), muis)
            elif self.toon_info:
                self.teken_tekstvak(self.d, T("info"), (T("info_tekst") % VERSIE).split("\n"), muis)
            pygame.transform.smoothscale(self.d, self.venster.get_size(), self.venster)
            pygame.display.flip()
            self.klok.tick(60)


topo.UI = sys.modules[__name__]
vier.UI = sys.modules[__name__]
zeeslag.UI = sys.modules[__name__]
wiebenik.UI = sys.modules[__name__]
dammen.UI = sys.modules[__name__]
schaken.UI = sys.modules[__name__]
galgje.UI = sys.modules[__name__]
memory.UI = sys.modules[__name__]
lingo.UI = sys.modules[__name__]
sudoku.UI = sys.modules[__name__]
puzzel.UI = sys.modules[__name__]
pesten.UI = sys.modules[__name__]
ganzenbord.UI = sys.modules[__name__]
domino.UI = sys.modules[__name__]
reversi.UI = sys.modules[__name__]
duel.UI = sys.modules[__name__]


if __name__ == "__main__":
    try:
        App().loop()
    except Exception:
        log_fout(traceback.format_exc())
        raise
    finally:
        pygame.quit()
