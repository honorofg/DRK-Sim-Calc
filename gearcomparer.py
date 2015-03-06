#! /usr/bin/python2

# I have yet to pinpoint the reason why but for some reason my ability dps
# equation is yielding a higher number than the spreadsheet (approx +40), I
# straight copied this equation from easymodex's dps formula post and didnt
# even change the names of the variables so I'd rather prefer to trust my
# version than the excel version, also my potency numbers are slightly
# lower than the excel version, which makes it even more confusing that i'd
# get a higher abilitydps number
def abilitydamage(WD, STR, DTR, potency):
    return (WD*.2714745 + STR*.1006032 + (DTR-202)*.0241327 + WD*STR*.0036167 + WD*(DTR-202)*.0010800 - 1) * (potency/100)

def autoattackdamage(WD, STR, DTR, weapon_delay):
    return (WD*.2714745 + STR*.1006032 + (DTR-202)*.0241327 + WD*STR*.0036167 + WD*(DTR-202)*.0022597 - 1) * (weapon_delay/3)

def sumdps(STR, CRIT, DTR, SS, WD, weapon_delay):
    critrate = (CRIT*0.0697-18.437)/100+.1
    critmodifier = 1 + 0.5*critrate

    ircritrate = critrate+.1
    ircritmodifier = 1 + 0.5*ircritrate

    cdmodifier = 1.25 # this was from the original spreadsheet, for barrage and other cds TODO remove

    potency = bardrotation(critrate, SS)
    auto = autoattackdamage(WD, STR, DTR, weapon_delay)/weapon_delay*cdmodifier*critmodifier
    ability = abilitydamage(WD, STR, DTR, potency)
    noir = (auto+ability)

    irpotency = bardrotation(ircritrate, SS)
    irauto = autoattackdamage(WD, STR, DTR, weapon_delay)/weapon_delay*cdmodifier*ircritmodifier
    irability = abilitydamage(WD, STR, DTR, irpotency)
    ir = (irauto+irability)

    return ir*15/60 + noir*45/60

# expects weapon as a 2 element list of format [WeaponDamage, Delay]
def calc_weights(STR, ACC, CRIT, DTR, SKS, WEP):
    SKS = SKS - 341
    base = sumdps(STR, CRIT, DTR, SKS, WEP[0], WEP[1])
    strinc = sumdps(STR+5, CRIT, DTR, SKS, WEP[0], WEP[1])-base
    critinc = sumdps(STR, CRIT+5, DTR, SKS, WEP[0], WEP[1])-base
    detinc = sumdps(STR, CRIT, DTR+5, SKS, WEP[0], WEP[1])-base
    ssinc = sumdps(STR, CRIT, DTR, SKS+5, WEP[0], WEP[1])-base
    wdinc = sumdps(STR, CRIT, DTR, SKS, WEP[0]+5, WEP[1])-base
    return [strinc/strinc, 0, critinc/strinc, detinc/strinc, ssinc/strinc, wdinc/strinc]

def calc_value(STR, ACC, CRIT, DTR, SKS, WEP):
    weights = calc_weights(STR, ACC, CRIT, DTR, SKS, WEP)
    value = STR*weights[0] + ACC*weights[1] + CRIT*weights[2] + DTR*weights[3] + SKS*weights[4] + WEP[0]*weights[5]
    return value

def calc_staticvalue(STR, ACC, CRIT, DTR, SKS, WEP, weights):
    value = STR*weights[0] + ACC*weights[1] + CRIT*weights[2] + DTR*weights[3] + SKS*weights[4] + WEP[0]*weights[5]
    return value

def calc_dps(STR, ACC, CRIT, DTR, SKS, WEP):
    SKS = SKS - 341
    base = sumdps(STR, CRIT, DTR, SKS, WEP[0], WEP[1])
    return base

def bardrotation(critrate, SS):
    delay = 2.5-0.01*SS/10.5
    stupid = 1.2
    critmodifier = 1 + 0.5*critrate
    blprocrate = .5
    blonhit = 150

    dropdotrotationpps = bardpotcalc(5, critmodifier, delay)*stupid
    dotdroptime = (8*delay-18)*2

    constantdotrotationpps = bardpotcalc(4, critmodifier, delay)*stupid

    ogcdpps = (350/60 + 50/30 + 80/30)*critmodifier*stupid
    rotationpps = max(dropdotrotationpps, constantdotrotationpps)
    BLprocchance = blchance(critrate, 2)
    onedotBLPC = blchance(critrate, 1)
    BLFactor = (BLprocchance*blonhit/3 + ((1-BLprocchance)**5)*blonhit/15)*critmodifier*stupid
    return BLFactor + rotationpps + ogcdpps

def bardpotcalc(heavyshots, critmodifier, delay): #assumes singletarget, 2 dots
    hsonhit = 150
    wbonhit = 60
    wbdot = 45
    vbonhit = 100
    vbdot = 35
    ssonhit = 140

    gcdcount = 3+heavyshots
    duration = delay*gcdcount
    dotticktime = min(duration, 18)
    numticks = dotticktime/3

    totalpotency = ssonhit*1.5 + (vbonhit+wbonhit+heavyshots*hsonhit + (vbdot+wbdot)*numticks)*critmodifier

    return totalpotency/duration

def blchance(critrate, numDots):
    blprocrate = .5
    return 1 - (1-critrate*blprocrate)**numDots

def andrewblchance(critrate, numDots):
    blprocrate = .5
    total = 0
    p = critrate*blprocrate
    for i in range(1, numDots+1):
        total = total + p*(1-p)**(i-1)
    return total

def main():
    bardweights = [1.0, 0, 0.339, 0.320, 0.161, 9.429]
    newbardweights = [1.0, 0, 0.298, 0.331, 0.106, 9.139]
    drgweights = [1.0, 0, .233, .327, .198, 9.349]

    dreadbow = [52, 3.2]
    augmentedironworksbow = [51, 3.04]
    yoichibow = [50, 3.04]
    highallaganbow = [48, 3.36]
    zetabow = [52, 3.04]

    #novus meld sets considered, 35, 24, 16 crit det acc, which results in 42, 29, 19
    # 33, 23, 19 which results in 39, 28, 23

    bis24 = calc_dps(645, 547, 647, 349, 350, dreadbow) # no i110 accessory true bis
    fouraccbis = calc_dps(626, 539, 694, 369, 395, dreadbow) # true bis
    curgear = calc_dps(622, 550, 605, 373, 401, augmentedironworksbow)
    truebis = calc_dps(621, 536, 710, 372, 432, zetabow)
    weights = calc_weights(664, 536, 520, 338, 389, zetabow)
    truebised = calc_staticvalue(621, 536, 710, 372, 432, zetabow, newbardweights)
    truebised2 = calc_staticvalue(626, 535, 698, 380, 399, zetabow, newbardweights)

    chestremeldbelt = calc_dps(624, 543, 610, 353, 434, augmentedironworksbow)
    beltbootsdemonchest = calc_dps(616, 535, 614, 374, 429, augmentedironworksbow)
    nossbis = calc_staticvalue(630, 536, 705, 351, 341, dreadbow, bardweights)

    ariyalabis = calc_staticvalue(663, 535, 558, 359, 370, [58, 2.88], drgweights)
    maskonly = calc_staticvalue(656, 537, 527, 406, 365, [58, 2.88], drgweights)
    maskbelt = calc_staticvalue(651, 537, 567, 379, 388, [58, 2.88], drgweights)

    wodcrafted = calc_staticvalue(616, 537, 638, 369, 401, augmentedironworksbow, bardweights)
    nonwod = calc_staticvalue(622, 535, 607, 368, 423, augmentedironworksbow, bardweights)
    dreadpantswod = calc_staticvalue(622, 544, 654, 347, 414, augmentedironworksbow, bardweights)
    ruioshimabis = calc_staticvalue(626, 539, 694, 381, 341, zetabow, bardweights)
    nocrafted = calc_dps(657, 539, 609, 346, 341, zetabow)

    print weights
    print truebis, truebised, truebised2, nocrafted

if __name__ == "__main__":
    main()
