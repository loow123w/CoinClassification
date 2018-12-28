import tkinter
import os
from PIL import Image, ImageTk

class App:
    def __init__(self, window, window_width, window_height, imgPathList):
        self.window = window
        self.window_width = window_width
        self.window_height = window_height
        self.infoLabel_height = 20
        self.window.geometry(str(self.window_width) + "x" + str(self.window_height))

        self.imgProcessedCounter = 0
        self.currentImgIndex = 0
        self.imgPathList = imgPathList
        self.currentfilepath = ""
        self.keepPhoto = False
        self.pilImage = ""

        self.canvas_height = self.window_height - self.infoLabel_height
        self.canvas_width = self.window_width
        self.canvas_Y = self.window_height - self.canvas_height
        self.canvas = tkinter.Canvas(self.window, width=self.canvas_width, height=self.canvas_height)
        self.canvas.place(x=0, y=self.canvas_Y)
        self.canvas_leftClicked = False

        self.crossHairComponents = []
        self.crossHairRadius = 0
        self.crossHairLineWidth = 2
        self.edgeCoords = ()
        self.centreCoords = ()

        self.imgSizeLbl = tkinter.Label(self.window, text="Image Size: ", bg="blue", fg="white")
        self.imgSizeLbl.place(x=0, y=0, width=400, height=self.infoLabel_height)

        self.processedImgLbl = tkinter.Label(self.window, text="Processed Images: ", bg="blue", fg="white")
        self.processedImgLbl.place(x=400, y=0, width=200, height=self.infoLabel_height)

        self.currentImgLbl = tkinter.Label(self.window, text=str.format("Current Images: {0}/{1}", self.currentImgIndex, totalImgFiles),
                                           bg="blue", fg="white")
        self.currentImgLbl.place(x=600, y=0, width=200, height=self.infoLabel_height)

        self.canvas.bind("<Button-1>", self.canvas_onleftclick)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_onleftrelease)
        self.canvas.bind('<Motion>', self.canvas_onmotion)
        self.canvas.bind_all("<space>", self.canvas_onspacepress)

        self.processImage(0, self.imgPathList)

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
        self.canvas_leftClicked = True
        self.centreCoords = (e.x, e.y)
        self.edgeCoords = (e.x, e.y)
        print("Centre co-ords: ", self.centreCoords)

    def canvas_onleftrelease(self, e):
        self.keepPhoto = True
        self.updateCrosshair("green")
        self.canvas_leftClicked = False

    def canvas_onspacepress(self, e):
        if not self.keepPhoto:
            os.remove(self.currentfilepath)
            print("delete")
        elif self.keepPhoto:
            print("crop and keep")
            pilImage = self.pilImage.crop(self.setCornerCoords(self.crossHairRadius))
            pilImage.save(self.currentfilepath)

        self.currentImgIndex += 1
        self.processImage(self.currentImgIndex, self.imgPathList)

    def processImage(self, imgIndex, imgPathList):
        self.canvas_leftClicked = False
        self.keepPhoto = False
        self.deleteCrossHair()

        if imgIndex >= len(self.imgPathList):
            print("No more images to process in input folder.")
            return

        self.currentfilepath = filepath = imgPathList[imgIndex]

        try:
            pilImage = Image.open(filepath)
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
                                                    self.currentImgIndex + 1, totalImgFiles)

            print("Success: ", filepath)
            self.imgProcessedCounter += 1

        except:
            print("Failure: ", filepath)
            self.currentImgIndex += 1
            self.processImage(self.currentImgIndex, self.imgPathList)


inputPath = "/Users/lewisclark/Documents/KewGardensPics"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

totalImgFiles = len(os.listdir(inputPath))
currentImgCounter = 0
imgPathList = [os.path.join(inputPath, filename) for filename in os.listdir(inputPath)]

window = tkinter.Tk()
app = App(window, WINDOW_WIDTH, WINDOW_HEIGHT, imgPathList)

window.mainloop()


