# Import required libraries
from machine import Pin
import time

czasOdswiezaniaWyswietlacza = 0.006

CzasSwieceniaZielonegoDlaSamochodow = 7
CzasSwieceniaZielonegoDlaPieszych = 5
CzasSwieceniaZoltego = 2
CzasOpoznienia = 2

pinyPrzyciskow = [12,   13,   14,   15,  16, 22]
# Zmienne:        ALM,  CSZS, CSZP, CSZ, CO, BUTTON
stanyPrzyciskow = []

pinyCyfr = [6,9,10,5]
# Cyfry:    1,2, 3,4

pinySegmentow = [7,11,3,1,0,8,4]
#Lista ref:      A, B,C,D,E,F,G

pinySygnalizacji = {
    "ZIEL_S": 19,
    "ZOLT_S": 20,
    "CZER_S": 21,
    "ZIEL_P": 17,
    "CZER_P": 18,
    "BUZZER": 26
}

pinKropki = 2
gdzieKropki = [0,0,0,0]
alarm = 0
stan = 1
tim1 = 0
tim2 = 0
cykle = 0
czasCyklu = 1 #ms
czyOczekujePieszy = 0
# ustawia wszystkie piny przyciskow jako wyjście
for pin in pinyPrzyciskow:
    button = Pin(pin,Pin.IN, Pin.PULL_DOWN)
    stanyPrzyciskow.append(button.value())
    if pin == 12: alarm = stanyPrzyciskow[0]
  
# ustawia wszystkie piny wyświetlacza jako wyjście
for pin in (pinySegmentow + pinyCyfr + [pinKropki]):
    Pin(pin,Pin.OUT)

# ustawia wszystkie piny sygnalizacji jako wyjscie
for key in pinySygnalizacji:
    Pin(pinySygnalizacji[key],Pin.OUT)
        

tablicaZnakow = {
    "0": [0,0,0,0,0,0,1],
    "1": [1,0,0,1,1,1,1],
    "2": [0,0,1,0,0,1,0],
    "3": [0,0,0,0,1,1,0],
    "4": [1,0,0,1,1,0,0],
    "5": [0,1,0,0,1,0,0],
    "6": [0,1,0,0,0,0,0],
    "7": [0,0,0,1,1,1,1],
    "8": [0,0,0,0,0,0,0],
    "9": [0,0,0,0,1,0,0],
    "A": [0,0,0,1,0,0,0],
    "L": [1,1,1,0,0,0,1],
    "o": [1,1,0,0,0,1,0],
    "O": [0,0,1,1,1,0,0]
}

def wyswietl4Znaki(znaki,kropkiONlista):
    global alarm
    
    for idx, znak in enumerate(znaki[0:4]):
        Pin(pinyCyfr[0]).value(1 if idx == 0 else 0)
        Pin(pinyCyfr[1]).value(1 if idx == 1 else 0)
        Pin(pinyCyfr[2]).value(1 if idx == 2 else 0)
        Pin(pinyCyfr[3]).value(1 if idx == 3 else 0)
        Pin(pinKropki).value(not kropkiONlista[idx])
        if ((stan in [1,2] and idx == 0) or (stan in [4,10] and idx == 2) or (stan in [3] and idx == 3)) and not alarm:
            for idj, bit in enumerate(tablicaZnakow[str(pozostaleSekundyTimera(tim1))]):
                Pin(pinySegmentow[idj]).value(bit)
        elif (stan in [6,7,8] and idx == 1) and not alarm:
            for idj, bit in enumerate(tablicaZnakow[str(pozostaleSekundyTimera(tim2))]):
                Pin(pinySegmentow[idj]).value(bit)
        else:
            for idj, bit in enumerate(tablicaZnakow[znaki[idx]]):
                Pin(pinySegmentow[idj]).value(bit)

        time.sleep(czasOdswiezaniaWyswietlacza)
        
def obslugaPrzyciskow(przycisk,wartosc):
    global CzasSwieceniaZielonegoDlaSamochodow
    global CzasSwieceniaZielonegoDlaPieszych
    global CzasSwieceniaZoltego
    global CzasOpoznienia
    global alarm
    global stan
    global czyOczekujePieszy
    
    if przycisk == 0:
        alarm = 1 if wartosc else 0
    if przycisk == 1 and not alarm and not stan in [1,2]:
        if wartosc:
            CzasSwieceniaZielonegoDlaSamochodow = CzasSwieceniaZielonegoDlaSamochodow+1 if CzasSwieceniaZielonegoDlaSamochodow < 9 else 1
    if przycisk == 2 and not alarm and not stan in [6,7,8]:
        if wartosc:
            CzasSwieceniaZielonegoDlaPieszych = CzasSwieceniaZielonegoDlaPieszych+1 if CzasSwieceniaZielonegoDlaPieszych < 9 else 1
    if przycisk == 3 and not alarm and not stan in [4,10]:
        if wartosc:
            CzasSwieceniaZoltego = CzasSwieceniaZoltego+1 if CzasSwieceniaZoltego < 9 else 1
    if przycisk == 4 and not alarm and not stan in [3]:
        if wartosc:
            CzasOpoznienia = CzasOpoznienia+1 if CzasOpoznienia < 9 else 1
    if przycisk == 5:
        if wartosc:
            czyOczekujePieszy = 1
    

def wyswietlAktualneZmienne():
    if not alarm:
        wyswietl4Znaki((str(CzasSwieceniaZielonegoDlaSamochodow)+str(CzasSwieceniaZielonegoDlaPieszych)+str(CzasSwieceniaZoltego)+str(CzasOpoznienia)), gdzieKropki)
    else:
        wyswietl4Znaki("oALO" if cykle < 5 else "OALo", [0,0,0,0])

def ustawTimerNaSekundy(sekundy):
    return time.ticks_ms() + (sekundy * 1000)

def sprawdzCzyTimerAktywny(timer):
    return time.ticks_ms() < timer

def pozostaleSekundyTimera(timer):
    aktualnyTick = time.ticks_ms()
    return round((timer-aktualnyTick) / 1000) if (timer-aktualnyTick) > 0 else 0

def obslugaStanow():
    global CzasSwieceniaZielonegoDlaSamochodow
    global CzasSwieceniaZielonegoDlaPieszych
    global CzasSwieceniaZoltego
    global CzasOpoznienia
    global alarm
    global stan
    global tim1
    global tim2
    global gdzieKropki
    global cykle
    global czyOczekujePieszy
    
    if stan == 1:
        Pin(pinySygnalizacji["ZIEL_S"]).value(1)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(0)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [1,0,0,0]
        
        if not sprawdzCzyTimerAktywny(tim1): stan = 2 
        elif alarm:
            tim1 = ustawTimerNaSekundy(CzasOpoznienia)
            stan=3

    elif stan == 2:
        Pin(pinySygnalizacji["ZIEL_S"]).value(1)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(0)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [1,0,0,0]
        
        if stanyPrzyciskow[5] or alarm or czyOczekujePieszy:
            tim1 = ustawTimerNaSekundy(CzasOpoznienia)
            stan=3
    
    elif stan == 3:
        Pin(pinySygnalizacji["ZIEL_S"]).value(1)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(0)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [0,0,0,1]
        
        if not sprawdzCzyTimerAktywny(tim1) and 1:
            tim1 = ustawTimerNaSekundy(CzasSwieceniaZoltego)
            stan=4
    
    elif stan == 4:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(1)
        Pin(pinySygnalizacji["CZER_S"]).value(0)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [0,0,1,0]
        
        if not sprawdzCzyTimerAktywny(tim1) and 1:
            tim1 = ustawTimerNaSekundy(2)
            stan=5
    
    elif stan == 5:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(1)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [0,0,0,0]
        
        if not sprawdzCzyTimerAktywny(tim1) and not alarm:
            tim1 = ustawTimerNaSekundy(CzasSwieceniaZielonegoDlaPieszych-3)
            tim2 = ustawTimerNaSekundy(CzasSwieceniaZielonegoDlaPieszych)
            czyOczekujePieszy = 0
            stan=6
        elif not sprawdzCzyTimerAktywny(tim1) and alarm:
            stan=11
    
    elif stan == 6:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(1)
        Pin(pinySygnalizacji["ZIEL_P"]).value(1)
        Pin(pinySygnalizacji["CZER_P"]).value(0)
        Pin(pinySygnalizacji["BUZZER"]).value(cykle%10)
        gdzieKropki = [0,1,0,0]
        
        if not sprawdzCzyTimerAktywny(tim1):
            tim1 = ustawTimerNaSekundy(0.5)
            stan=7
        elif alarm: stan=11
    
    elif stan == 7:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(1)
        Pin(pinySygnalizacji["ZIEL_P"]).value(1)
        Pin(pinySygnalizacji["CZER_P"]).value(0)
        Pin(pinySygnalizacji["BUZZER"]).value(cykle%5)
        gdzieKropki = [0,1,0,0]
        
        if not sprawdzCzyTimerAktywny(tim1):
            tim1 = ustawTimerNaSekundy(0.5)
            stan=8
        elif alarm: stan=11
        elif not sprawdzCzyTimerAktywny(tim2):
            tim1 = ustawTimerNaSekundy(2)
            stan = 9
    
    elif stan == 8:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(1)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(0)
        Pin(pinySygnalizacji["BUZZER"]).value(cykle%5)
        gdzieKropki = [0,1,0,0]
        
        if not sprawdzCzyTimerAktywny(tim1):
            tim1 = ustawTimerNaSekundy(0.5)
            stan=7
        elif alarm: stan=11
        elif not sprawdzCzyTimerAktywny(tim2):
            tim1 = ustawTimerNaSekundy(2)
            stan = 9
    
    elif stan == 9:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(1)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [0,0,0,0]
        
        if not sprawdzCzyTimerAktywny(tim1):
            tim1 = ustawTimerNaSekundy(CzasSwieceniaZoltego)
            stan=10
        elif alarm: stan=11
    
    elif stan == 10:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(1)
        Pin(pinySygnalizacji["CZER_S"]).value(0)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [0,0,1,0]
        
        if not sprawdzCzyTimerAktywny(tim1):
            tim1 = ustawTimerNaSekundy(CzasSwieceniaZielonegoDlaSamochodow)
            stan=1
        elif alarm: stan=11
    
    elif stan == 11:
        Pin(pinySygnalizacji["ZIEL_S"]).value(0)
        Pin(pinySygnalizacji["ZOLT_S"]).value(0)
        Pin(pinySygnalizacji["CZER_S"]).value(1)
        Pin(pinySygnalizacji["ZIEL_P"]).value(0)
        Pin(pinySygnalizacji["CZER_P"]).value(1)
        gdzieKropki = [0,0,0,0]
        
        if not alarm:
            tim1 = ustawTimerNaSekundy(2)
            stan=9
        
tim1 = ustawTimerNaSekundy(CzasSwieceniaZielonegoDlaSamochodow)
ostatniCykl = time.ticks_ms()
while True:
    for przycisk in range(0,len(pinyPrzyciskow)):
        if Pin(pinyPrzyciskow[przycisk]).value() and not stanyPrzyciskow[przycisk]:
            stanyPrzyciskow[przycisk] = 1
            obslugaPrzyciskow(przycisk,stanyPrzyciskow[przycisk])
        elif not Pin(pinyPrzyciskow[przycisk]).value() and stanyPrzyciskow[przycisk]:
            stanyPrzyciskow[przycisk] = 0
            obslugaPrzyciskow(przycisk,stanyPrzyciskow[przycisk])
    obslugaStanow()
    wyswietlAktualneZmienne()
    cykle = (cykle+1)%10
    while (time.ticks_ms()-ostatniCykl) < czasCyklu:
        pass
    ostatniCykl = time.ticks_ms()
    print(stan)