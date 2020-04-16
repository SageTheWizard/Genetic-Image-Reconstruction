import random
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import pygame


class ColorDictionary:
    colorList = []
    countList = []
    totPixels = 0

    def __init__(self):
        self.colorList = []
        self.countList = []

    def contains(self, color):
        if len(self.colorList):
            return -1
        else:
            for i in range(0, len(self.colorList)):
                if self.colorList[i] == color:
                    return i

        return -1

    def add(self, color):
        self.colorList.append(color)
        self.countList.append(1)
        self.totPixels += 1

    def incCount(self, indx):
        self.countList[indx] += 1
        self.totPixels += 1

    def getcolor(self):
        colorIndx = random.randint(0, self.totPixels + 1)
        counter = 0
        for i in range(0, len(self.colorList)):
            counter += self.countList[i]
            if colorIndx < counter:
                return self.colorList[i]

        return self.colorList[len(self.colorList) - 1]


generations = 0
imgFile = ""
ogImgPil = None
minimizedColorsPil = None
pixelizedSettings = 1
ogImgTk = ""
imgLabel = None
mainWindow = None
colorDictionary = ColorDictionary()


def main():
    mainWindow = Tk()

    fitnessLbl = Label(mainWindow, text="Fitness % (higher = longer processing time", font=25)
    fitnessSlider = Scale(mainWindow, from_=50, to=99, orient=HORIZONTAL)
    fitnessSlider.set(50)

    chooseImgLbl = Label(mainWindow, text="Choose an image to generate (larger images = longer processing time", font=25)
    chooserButton = Button(mainWindow, text="Open File Browser", font=25, command=chooseClick)

    mainWindow = Toplevel()

    fitnessLbl.pack()
    fitnessSlider.pack(fill=X, padx=10)

    chooseImgLbl.pack()
    chooserButton.pack()

    mainWindow.mainloop()


def chooseClick():
    imgFile = filedialog.askopenfilename(filetypes =(("JPG files", "*.jpg"), ("PNG files", "*.png"), ("JPEG files", "*.jpeg")))
    print imgFile
    global ogImgPil, threadSlider
    ogImgPil = Image.open(imgFile)
    ogImgPil = ogImgPil.convert('RGB')
    ogImgTk = ImageTk.PhotoImage(ogImgPil)
    imgLabel = Label(mainWindow, image=ogImgTk)
    goButton = Button(mainWindow, text="Begin Generation", font=25, command=beginGeneration)
    imgLabel.pack()
    goButton.pack()
    mainWindow.mainloop()

# mean absolute error
# mean squared
    # ^^^^^
def beginGeneration():
    global ogImgPil, colorDictionary, generations
    screenDim = ogImgPil.size
    white = (255, 255, 255)

    genImg = Image.new('RGB', screenDim, white)

    pygame.init()
    pygameScreen = pygame.display.set_mode(screenDim, pygame.HWSURFACE)
    minimizeColors()
    fitnessState = makeColorDictionary()
    generating = True
    changed = False
    bestImg = genImg.copy()

    while generating:
        if generations > 0:
            genImg = bestImg.copy()

        genImg, moddedSquare = modifyImgTri(genImg, fitnessState)
        genImg = genImg.copy()
        modedBetter = getFitness(genImg, bestImg, moddedSquare)

        if modedBetter:
            bestImg = genImg.copy()
            changed = True

        if changed:
            imgStr = bestImg.tobytes('raw', 'RGB')
            pyImg = pygame.image.fromstring(imgStr, screenDim, 'RGB')
            pygameScreen.blit(pyImg, (0, 0))
            pygame.display.flip()
            changed = False

        generations += 1
        print generations
        print fitnessState
        if generations % 100 == 0:
            fitnessState = getFitnessState(bestImg)


def minimizeColors():
    global ogImgPil, pixelizedSettings, minimizedColorsPil
    minimizedColorsPil = Image.new('RGB', ogImgPil.size, (0,0,0))
    avgR = 0
    avgG = 0
    avgB = 0

    for superY in range(0, ogImgPil.size[1], pixelizedSettings):
        for superX in range(0, ogImgPil.size[0], pixelizedSettings):
            divCounter = 0
            for y in range(superY, superY + pixelizedSettings):
                if (y + superY) >= ogImgPil.size[1]:
                    break
                for x in range(superX, superX + pixelizedSettings):
                    if (x + superX) >= ogImgPil.size[0]:
                        break
                    print ((x + superX), (y + superY))
                    avgR += ogImgPil.getpixel(((x + superX), (y + superY)))[0]
                    avgG += ogImgPil.getpixel(((x + superX), (y + superY)))[1]
                    avgB += ogImgPil.getpixel(((x + superX), (y + superY)))[2]
                    divCounter += 1
            if divCounter == 0:
                break
            avgR /= (divCounter * divCounter)
            avgG /= (divCounter * divCounter)
            avgB /= (divCounter * divCounter)

            for y in range(superY, superY + pixelizedSettings):
                if (y + superY) > ogImgPil.size[1]:
                    break
                for x in range(superX, superX + pixelizedSettings):
                    if (x + superX) > ogImgPil.size[0]:
                        break
                    minimizedColorsPil.putpixel([(x + superX), (y + superY)], (avgR, avgG, avgB))


def makeColorDictionary():
    global minimizedColorsPil, colorDictionary, pixelizedSettings

    total = minimizedColorsPil.size[1] * minimizedColorsPil.size[0]
    fitness = 0.0
    defaultColor = 255

    for y in range(0, minimizedColorsPil.size[1], pixelizedSettings):
        for x in range(0, minimizedColorsPil.size[0], pixelizedSettings):
            pixel = ogImgPil.getpixel((x, y))
            pixelindx = colorDictionary.contains(pixel)
            if pixelindx < 0:
                colorDictionary.add(pixel)
            else:
                colorDictionary.incCount(pixelindx)

            fitness += (pixel[0] / float(defaultColor))
            fitness += (pixel[1] / float(defaultColor))
            fitness += (pixel[2] / float(defaultColor))

    return fitness / float(total * 3)


def getFitnessState(currentImg):
    global ogImgPil
    size = ogImgPil.size

    fitnessSum = 0.0

    for y in range(0, size[1]):
        for x in range(0, size[0]):
            ogR, ogG, ogB = ogImgPil.getpixel((x, y))
            mR, mG, mB = currentImg.getpixel((x, y))

            # I hate that I do this
            if ogR == 0:
                ogR = 1
            if ogG == 0:
                ogG = 1
            if ogB == 0:
                ogB = 1
            if mR == 0:
                mR = 1
            if mG == 0:
                mG = 1
            if mB == 0:
                mB = 1

            if mR > mR:
                fitnessSum += (mR / float(ogR))
            elif ogR == mR:
                fitnessSum += 1.0
            else:
                fitnessSum += (ogR / float(mR))

            if ogG > mG:
                fitnessSum += (mG / float(ogG))
            elif ogG == mG:
                fitnessSum += 1.0
            else:
                fitnessSum += (ogG / float(mG))

            if ogB > mB:
                fitnessSum += (mB / float(ogB))
            elif ogB == mB:
                fitnessSum += 1.0
            else:
                fitnessSum += (ogB / float(mB))

    return fitnessSum / (size[0] * size[1] * 3)


def modifyImgRect(imgToMod):
    global colorDictionary
    startX = random.randint(0, imgToMod.size[0])
    startY = random.randint(0, imgToMod.size[1])

    endX = random.randint(0, imgToMod.size[0])
    endY = random.randint(0, imgToMod.size[1])

    rngR, rngG, rngB = colorDictionary.getcolor()

    if startX > endX:
        startX, endX = endX, startX
    if startY > endY:
        startY, endY = endY, startY

    for y in range(startY, endY, 1):
        for x in range(startX, endX, 1):
            imgToMod.putpixel((x,y), (rngR, rngG, rngB))

    return imgToMod


def modifyImgTri(imgToMod, fitness):
    global colorDictionary, generations
    sizeX = imgToMod.size[0]
    sizeY = imgToMod.size[1]

    startX = random.randint(0, sizeX)
    startY = random.randint(0, sizeY)

    if fitness < 0.9:
        rangeBaseX = int(startX - (startX * (1.0 - fitness * 1.05)))
        rangeCeilingX = int(startX + (startX * (1.0 - fitness * 1.05)))
        rangeBaseY = int(startY - (startY * (1.0 - fitness * 1.05)))
        rangeCeilingY = int(startY + (startY * (1.0 - fitness * 1.05)))
    else:
        rangeBaseX = int(startX - (startX * (1.0 - fitness)))
        rangeCeilingX = int(startX + (startX * (1.0 - fitness)))
        rangeBaseY = int(startY - (startY * (1.0 - fitness)))
        rangeCeilingY = int(startY + (startY * (1.0 - fitness)))

    if rangeBaseX < 0:
        rangeBaseX = 0
    elif rangeCeilingX > sizeX:
        rangeCeilingX = sizeX

    if rangeBaseY < 0:
        rangeBaseY = 0
    elif rangeCeilingY > sizeY:
        rangeCeilingY = sizeY

    midX = random.randint(rangeBaseX, rangeCeilingX)
    midY = random.randint(rangeBaseY, rangeCeilingY)

    endX = random.randint(rangeBaseX, rangeCeilingX)
    endY = random.randint(rangeBaseY, rangeCeilingY)

    rngR, rngG, rngB = colorDictionary.getcolor()

    draw = ImageDraw.Draw(imgToMod)
    draw.polygon([(startX, startY), (midX, midY), (endX, endY)], fill=(rngR, rngG, rngB), outline=(rngR, rngG, rngB))

    minX = min(startX, midX, endX)
    maxX = max(startX, midX, endX)
    minY = min(startY, midY, endY)
    maxY = max(startY, midY, endY)

    return imgToMod, ((minX, minY), (maxX, maxY))


def getFitness(img, bestImg, modSquare):
    global ogImgPil
    fitnessSum = 0.0
    startX = modSquare[0][0]
    endX = modSquare[1][0]

    startY = modSquare[0][1]
    endY = modSquare[1][1]

    if startX == endX and endX < ogImgPil.size[0]:
       endX += 1

    if startY == endY and endY < ogImgPil.size[1]:
        endY += 1

    bestFitness = 0
    modifiedFitness = 0

    for y in range(startY, endY):
        for x in range(startX, endX):
            ogR, ogG, ogB = ogImgPil.getpixel((x, y))
            mR, mG, mB = img.getpixel((x, y))
            bR, bG, bB = bestImg.getpixel((x, y))

            # Calculate Fitness Of Current Image Mean Squared
            bestFitness += (pow((bR - ogR), 2) + pow((bG - ogG), 2) + pow((bB - ogB), 2))
            modifiedFitness += (pow((mR - ogR), 2) + pow((mG - ogG), 2) + pow((mB - ogB), 2))


    yDist = endY - startY
    xDist = endX - startX

    if xDist == 0:
        xDist = 1
    if yDist == 0:
        yDist = 1

    bestFitness /= (yDist * xDist)
    modifiedFitness /= (yDist * xDist)

    return bestFitness > modifiedFitness

main()