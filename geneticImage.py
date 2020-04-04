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


def beginGeneration():
    global ogImgPil, colorDictionary, generations
    screenDim = ogImgPil.size
    white = (255, 255, 255)

    genImg = Image.new('RGB', screenDim, white)

    pygame.init()
    pygameScreen = pygame.display.set_mode(screenDim, pygame.HWSURFACE)
    minimizeColors()
    makeColorDictionary()
    generating = True
    changed = False
    bestFit = 0.0
    bestImg = genImg.copy()

    while generating:
        fitnessPercent = bestFit / float(screenDim[0] * screenDim[1] * 3)

        print fitnessPercent

        genImg = bestImg.copy()
        genImg = multiMod(genImg, fitnessPercent).copy()
        currentFitness = getFitness(genImg)

        if currentFitness > bestFit:
            bestImg = genImg.copy()
            bestFit = currentFitness
            changed = True

        if changed:
            imgStr = bestImg.tobytes('raw', 'RGB')
            pyImg = pygame.image.fromstring(imgStr, screenDim, 'RGB')
            pygameScreen.blit(pyImg, (0, 0))
            pygame.display.flip()
            changed = False
        generations += 1
        print generations


def minimizeColors():
    global ogImgPil, pixelizedSettings, minimizedColorsPil
    minimizedColorsPil = Image.new('RGB', ogImgPil.size, (255,255,255))
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
    counter = 0
    total = minimizedColorsPil.size[1] * minimizedColorsPil.size[0]
    for y in range(0, minimizedColorsPil.size[1], pixelizedSettings):
        for x in range(0, minimizedColorsPil.size[0], pixelizedSettings):
            pixel = ogImgPil.getpixel((x, y))
            pixelindx = colorDictionary.contains(pixel)
            if pixelindx < 0:
                colorDictionary.add(pixel)
            else:
                colorDictionary.incCount(pixelindx)


def multiMod(imgToMod, fitness):
    if fitness == 0.0:
        fitness = .01
    n = 300 / int(100 * fitness)

    if (n == 0):
        n = 1
    print n
    nShapes = random.randint(1, n)
    for i in range(0, nShapes):
        imgToMod = modifyImgTri(imgToMod, fitness)

    return imgToMod


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

    if fitness > 0.70 or generations > 500:
        rangeBaseX = int(startX - (startX * (1.0 - fitness)))
        rangeCeilingX = int(startX + (startX * (1.0 - fitness)))
        rangeBaseY = int(startY - (startY * (1.0 - fitness)))
        rangeCeilingY = int(startY + (startY * (1.0 - fitness)))
    else:
        rangeBaseX, rangeBaseY = (0, 0)
        rangeCeilingX = sizeX
        rangeCeilingY = sizeY

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
    print colorDictionary.getcolor()
    rngR, rngG, rngB = colorDictionary.getcolor()

    draw = ImageDraw.Draw(imgToMod)
    draw.polygon([(startX, startY), (midX, midY), (endX, endY)], fill=(rngR, rngG, rngB), outline=(rngR, rngG, rngB))

    return imgToMod


def getFitness(img):
    fitnessSum = 0.0
    global ogImgPil
    for y in range(0, ogImgPil.size[1]):
        for x in range(0, ogImgPil.size[0]):
            ogR, ogG, ogB = ogImgPil.getpixel((x, y))
            mR, mG, mB = img.getpixel((x, y))

            if ogR > mR:
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

    return fitnessSum

main()