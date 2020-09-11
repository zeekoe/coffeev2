from myhal import myhal


def startcb(gpio, level, tick):
    print("startcb", gpio, level)


myhal = myhal(startcb)
myhal.setMaalteller(20)
myhal.doGrind()

maalteller = myhal.getMaalteller()
while maalteller > 0:
    maalteller = myhal.getMaalteller()
myhal.stopGrind()
