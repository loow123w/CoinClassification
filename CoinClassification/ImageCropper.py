import tkinter
import time
from tkinter import filedialog
import os
from PIL import Image, ImageTk


class ClickTimer:
    def __init__(self):
        self.startTime = time.time()
        self.finishTime = 0

    def start(self):
        self.startTime = time.time()
        self.finishTime = 0

    def finish(self):
        self.finishTime = time.time()

    def getElapsedTime(self):
        if self.finishTime == 0:
            timeElasped = time.time() - self.startTime
        else:
            timeElasped = self.finishTime - self.startTime

        return timeElasped


class App:
    def __init__(self, window, window_width, window_height):
        self.OUTPUTFOLDERNAME = "Cropped Images"
        self.window = window
        self.window_width = window_width
        self.window_height = window_height
        self.infoLabel_height = 20
        self.window.geometry(str(self.window_width) + "x" + str(self.window_height))

        self.imgProcessedCounter = 0
        self.currentImgIndex = 0
        self.inputFilePath = ""
        self.outputFilePath = ""
        self.keepPhoto = False
        self.pilImage = ""
        self.currentFileName = ""

        self.canvas_height = self.window_height - self.infoLabel_height
        self.canvas_width = self.window_width
        self.canvas_Y = self.window_height - self.canvas_height
        self.canvas = tkinter.Canvas(self.window, width=self.canvas_width, height=self.canvas_height)
        self.canvas.place(x=0, y=self.canvas_Y)
        self.canvas_leftClicked = False
        self.clickTimer = ClickTimer()

        self.crossHairComponents = []
        self.crossHairRadius = 0
        self.crossHairLineWidth = 2
        self.edgeCoords = ()
        self.centreCoords = ()

        self.imgSizeLbl = tkinter.Label(self.window, text="Image Size: ")
        self.imgSizeLbl.place(x=0, y=0, width=400, height=self.infoLabel_height)

        self.processedImgLbl = tkinter.Label(self.window, text="Processed Images: ")
        self.processedImgLbl.place(x=400, y=0, width=200, height=self.infoLabel_height)

        self.currentImgLbl = tkinter.Label(self.window, text=str.format("Current Images: {0}/{1}", self.currentImgIndex, 0))
        self.currentImgLbl.place(x=600, y=0, width=200, height=self.infoLabel_height)

        self.inputFolderButton = tkinter.Button(self.window, text="Select input folder")
        self.inputFolderButton.place(x=800, y = 0, width=200, height=self.infoLabel_height)
        self.inputFolderButton.bind("<Button-1>", self.inputFolderButton_onclick)

        self.canvas.bind("<Button-1>", self.canvas_onleftclick)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_onleftrelease)
        self.canvas.bind('<Motion>', self.canvas_onmotion)
        self.canvas.bind_all("<space>", self.canvas_onspacepress)
        self.canvas.bind_all("<Left>", self.canvas_onspacepress)
        self.canvas.bind_all("<Right>", self.canvas_onspacepress)

    

    def inputFolderButton_onclick(self, e):
        folderPath = filedialog.askdirectory(initialdir="/")
        if folderPath:
            self.inputFolderPath = folderPath
            self.outputFolderPath = os.path.join(self.inputFolderPath, self.OUTPUTFOLDERNAME)
            print(self.outputFolderPath)

            if not os.path.isdir(self.outputFolderPath):
                print("WARNING: Output folder generated.")
                os.mkdir(self.outputFolderPath)

            self.imgNameList = os.listdir(self.inputFolderPath)
            self.currentImgIndex = 0
            self.currentImgLbl.config(text=str.format("Current Images: {0}/{1}", self.currentImgIndex, len(self.imgNameList)))
            self.processImage(0)


    def setCornerCoords(self, radius):
        x1 = self.centreCoords[0] - radius
        y1 = self.centreCoords[1] - radius
        x2 = self.centreCoords[0] + radius

        y2 = self.centreCoords[1] + radius
        return x1, y1, x2, y2

    def updateCrosshair(self, color):
        deltaX = abs(self.centreCoords[0] - self.edgeCoords[0])
        deltaY = abs(self.centreCoords[1] - self.edgeCoords[1])
        radius = max(deltaX, deltaY)

        x1, y1, x2, y2 = self.setCornerCoords(radius)

        if x1 <= self.crossHairLineWidth or y1 <= self.crossHairLineWidth:
            radius = min(self.centreCoords[0] - self.crossHairLineWidth,
                         self.centreCoords[1] - self.crossHairLineWidth)
            x1, y1, x2, y2 = self.setCornerCoords(radius)

        if x2 >= self.window_width - self.crossHairLineWidth or y2 >= self.window_height - self.crossHairLineWidth:
            radius = min(self.window_width - self.centreCoords[0], self.window_height - self.centreCoords[1])
            x1, y1, x2, y2 = self.setCornerCoords(radius)

        self.crossHairRadius = radius

        self.deleteCrossHair()
        self.drawCrossHair(color, x1, y1, x2, y2)

    def deleteCrossHair(self):
        for component in self.crossHairComponents:
            self.canvas.delete(component)

    def drawCrossHair(self, color, x1, y1, x2, y2):
        crossHairRect = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=self.crossHairLineWidth)
        crossHairXline = self.canvas.create_line((x1 + x2)/2 - self.crossHairRadius,
                                                 (y1 + y2)/2,
                                                 (x1 + x2)/2 + self.crossHairRadius,
                                                 (y1 + y2) / 2,
                                                 fill=color)
        crossHairYline = self.canvas.create_line((x1 + x2) / 2,
                                                 (y1 + y2) / 2 + self.crossHairRadius,
                                                 (x1 + x2) / 2,
                                                 (y1 + y2) / 2 - self.crossHairRadius,
                                                 fill=color)

        self.crossHairComponents.append(crossHairRect)
        self.crossHairComponents.append(crossHairXline)
        self.crossHairComponents.append(crossHairYline)

    def canvas_onmotion(self, e):
        if self.canvas_leftClicked:
            self.edgeCoords = (e.x, e.y)
            self.updateCrosshair("red")

    def canvas_onleftclick(self, e):
        self.clickTimer.start()
        self.deleteCrossHair()
        self.keepPhoto = False
        self.canvas_leftClicked = True
        self.centreCoords = (e.x, e.y)
        self.edgeCoords = (e.x, e.y)
        print("Centre co-ords: ", self.centreCoords)

    def canvas_onleftrelease(self, e):
        clickTimeElaspsed = self.clickTimer.getElapsedTime()
        if clickTimeElaspsed < 0.2:
            self.deleteCrossHair()
            self.keepPhoto = False
        else:
            self.keepPhoto = True
            self.updateCrosshair("green")

        self.canvas_leftClicked = False

    def canvas_onspacepress(self, e):
        if self.keepPhoto:
            print("crop and keep")
            pilImage = self.pilImage.crop(self.setCornerCoords(self.crossHairRadius))
            pilImage.save(os.path.join(self.outputFolderPath, self.currentFileName))

        os.remove(os.path.join(self.inputFolderPath, self.currentFileName))
        self.currentImgIndex += 1
        self.processImage(self.currentImgIndex)

    def processImage(self, imgIndex):
        self.canvas_leftClicked = False
        self.keepPhoto = False
        self.deleteCrossHair()

        if imgIndex >= len(self.imgNameList):
            print("No more images to process in input folder.")
            return

        self.currentFileName = self.imgNameList[imgIndex]

        try:
            pilImage = Image.open(os.path.join(self.inputFolderPath, self.currentFileName))
            width, height = pilImage.size
            originalWidth, originalHeight = width, height
            aspectRatio = width / height

            if width > self.canvas_width:
                width = self.canvas_width
                height = int(width/aspectRatio)
                pilImage = pilImage.resize((width, height), Image.ANTIALIAS)


            if height > self.canvas_height:
                height = self.canvas_height
                width = int(height * aspectRatio)
                pilImage = pilImage.resize((width, height), Image.ANTIALIAS)

            imgCentreX = width/2
            imgCentreY = height/2

            self.pilImage = pilImage
            self.canvas.currentImage = image = ImageTk.PhotoImage(pilImage)
            imagesprite = self.canvas.create_image(imgCentreX, imgCentreY, image=image)

            self.processedImgLbl["text"] = "Processed Images: " + str(self.imgProcessedCounter)

            self.imgSizeLbl["text"] = str.format("Image Size: {0}({1})x{2}({3})",
                                                 width, originalWidth, height, originalHeight)

            self.currentImgLbl["text"] = str.format("Current Images: {0}/{1}",
                                                    self.currentImgIndex + 1, len(self.imgNameList))

            print("Success: ", self.currentFileName)
            self.imgProcessedCounter += 1

        except:
            print("Failure: ", self.currentFileName)
            self.currentImgIndex += 1
            self.processImage(self.currentImgIndex)


WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

window = tkinter.Tk()
app = App(window, WINDOW_WIDTH, WINDOW_HEIGHT)

window.mainloop()


