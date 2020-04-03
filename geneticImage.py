import random
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import pygame


imgFile = ""
ogImgPil = None
ogImgTk = ""
imgLabel = None
mainWindow = None
colorDictionary = []

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
    ogImgPil= Image.open(imgFile)
    ogImgTk = ImageTk.PhotoImage(ogImgPil)
    imgLabel = Label(mainWindow, image=ogImgTk)
    goButton = Button(mainWindow, text="Begin Generation", font=25, command=beginGeneration)
    imgLabel.pack()
    goButton.pack()
    mainWindow.mainloop()


def beginGeneration():
    global ogImgPil, colorDictionary
    screenDim = ogImgPil.size
    white = (255, 255, 255)

    genImg = Image.new('RGB', screenDim, white)

    pygame.init()
    pygameScreen = pygame.display.set_mode(screenDim, pygame.HWSURFACE)
    makeColorDictionary()
    generating = True

    bestFit = 0.0
    bestImg = genImg.copy()

    while generating:
        fitnessPercent = bestFit / float(screenDim[0] * screenDim[1] * 3)

        print fitnessPercent

        genImg = bestImg.copy()
        genImg = modifyImg(genImg).copy()
        currentFitness = getFitness(genImg)

        if currentFitness > bestFit:
            bestImg = genImg.copy()
            bestFit = currentFitness


        imgStr = bestImg.tobytes('raw', 'RGB')
        pyImg = pygame.image.fromstring(imgStr, screenDim, 'RGB')
        pygameScreen.blit(pyImg, (0, 0))
        pygame.display.flip()

def makeColorDictionary():
    global ogImgPil, colorDictionary

    for y in range(0, ogImgPil.size[1]):
        for x in range(0, ogImgPil.size[0]):
            pixel = ogImgPil.getpixel((x, y))
            if not (pixel in colorDictionary):
                colorDictionary.append(pixel)


def modifyImg(imgToMod):
    global colorDictionary
    startX = random.randint(0, imgToMod.size[0])
    startY = random.randint(0, imgToMod.size[1])

    endX = random.randint(0, imgToMod.size[0])
    endY = random.randint(0, imgToMod.size[1])

    rngR, rngB, rngG = colorDictionary[random.randint(0, len(colorDictionary) - 1)]

    if startX > endX:
        startX, endX = endX, startX
    if startY > endY:
        startY, endY = endY, startY

    for y in range(startY, endY, 1):
        for x in range(startX, endX, 1):
            imgToMod.putpixel((x,y), (rngR, rngB, rngG))

    return imgToMod

def getFitness(img):
    print "op"
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