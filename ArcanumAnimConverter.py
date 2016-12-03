import os
import struct
import math

def createBamFile(newBamName):
    open(newBamName, 'a').close()


def createBamHeading(newBamName, oldBamName):
    with open(newBamName, 'r+b') as f:
        with open(oldBamName, 'r+b') as g:
            f.write(g.read(24))


def createBamFrameEntries(newBamName, infoFileName):
    with open(newBamName, 'r+b') as f:
        with open(infoFileName, 'r+b') as g:
            numberOfFrames = int(
                (len(g.read()) - 8) / 28)  # first 8 bytes are responsible for heading and each frame has 28 bytes
            f.read(8)
            f.write(struct.pack('<H', numberOfFrames))  # updating number of frames in BAM
            f.read(2)
            f.write(struct.pack('<I', 24))  # updating offset to frames
            f.read()
            g.seek(8)  # to skip first 8 bytes

            for i in range(0, numberOfFrames):
                f.write(struct.pack('<H', struct.unpack('I', g.read(4))[0]))
                f.write(struct.pack('<H', struct.unpack('I', g.read(4))[0]))
                g.read(4)
                f.write(struct.pack('<h', struct.unpack('i', g.read(4))[0]))
                f.write(struct.pack('<h', struct.unpack('i', g.read(4))[0]))
                g.read(8)
                f.write(struct.pack('<I', 0))


def createBamCycleEntries(newBamName):
    with open(newBamName, 'r+b') as f:
        numberOfCycles = int(input('How many cycles will there be in your BAM file?'))
        f.read(10)
        f.write(struct.pack('<B', numberOfCycles))  # updating number of cycles
        f.read()
        for i in range(0, numberOfCycles):
            f.write(struct.pack('<I', 0))


def createPalette(newBamName, BMPfile):
    with open(newBamName, 'r+b') as f:
        with open(BMPfile, 'r+b') as g:
            paletteOffset = len(f.read())
            f.seek(16)
            f.write(struct.pack('<I', paletteOffset))  # updating offset to palette
            f.read()
            f.write(struct.pack('<B', 0))
            f.write(struct.pack('<B', 255))
            f.write(struct.pack('<B', 0))
            f.write(struct.pack('<B', 0))
            g.seek(58)
            f.write(g.read(1020))


def BmpInvert(f, g):
    g.seek(2)
    numberOfPixels = struct.unpack('I', g.read(4))[0] - 1078
    f.read()
    for i in range(1, numberOfPixels + 1):
        g.seek(1078 + numberOfPixels - i)
        f.write(g.read(1))


def createFrameData(newBamName, BMPfileDirectory):

    with open(newBamName, 'r+b') as f:
        allFilesNames = os.listdir(BMPfileDirectory)
        BMPfilesNames = []
        print(allFilesNames)
        for fileName in allFilesNames:
            if fileName.endswith('.bmp'):
                BMPfilesNames.append(fileName)
                print(fileName)
        for i in range(0, len(BMPfilesNames)):
            with open(BMPfilesNames[i], 'r+b') as g:
                print(BMPfilesNames[i])
                frameDataOffset = len(f.read())
                f.seek(24 + i * 12 + 8)
                f.write(struct.pack('<I', 2 ** 31 + frameDataOffset))  # updating offset to the beginning of frame
                BmpInvert(f, g)
                f.seek(0)
                updateBamFrameEntries(f, g, i)
                f.seek(0)





def updateBamFrameEntries(f, g, i):
    g.seek(2)
    BmpFileSize = struct.unpack('I', g.read(4))[0]
    g.seek(18)
    BmpWidthFromInfoFile = struct.unpack('I', g.read(4))[0]
    BmpHeightFromInfoFile = struct.unpack('I', g.read(4))[0]
    missingBmpWidth = int((BmpFileSize - 1078 - BmpWidthFromInfoFile * BmpHeightFromInfoFile) / BmpHeightFromInfoFile)
    f.seek(24 + i * 12)
    newFrameWidth = struct.unpack('<H', f.read(2))[0] + missingBmpWidth
    f.seek(24 + i * 12)
    f.write(struct.pack('<H', newFrameWidth))
    f.seek(28 + i * 12)
    newFrameXOffset= struct.unpack('<H', f.read(2))[0]+ math.ceil(missingBmpWidth/2)
    f.seek(28 + i * 12)
    f.write(struct.pack('<H', newFrameXOffset))



def createFrameLookupTable(newBamName):
    with open(newBamName, 'r+b') as f:
        f.read(8)
        (numberOfFrames,) = struct.unpack('H', f.read(2))
        (numberOfCycles,) = struct.unpack('B', f.read(1))
        f.seek(0)
        frameLookupTableOffset = len(f.read())
        f.seek(20)
        f.write(struct.pack('<I', frameLookupTableOffset))
        f.seek(numberOfFrames * 12 + 24)
        f.write(struct.pack('<H', numberOfFrames))
        f.read()
        if numberOfCycles==1:
            for i in range(0, numberOfFrames):
                f.write(struct.pack('<H', i))




def createAnimation(newBamName, oldBamName, BMPfileName, BMPfileDirectory, infoFileName):
    createBamFile(newBamName)
    createBamHeading(newBamName, oldBamName)
    createBamFrameEntries(newBamName, infoFileName)
    createBamCycleEntries(newBamName)
    createPalette(newBamName, BMPfileName)
    createFrameData(newBamName, BMPfileDirectory)
    createFrameLookupTable(newBamName)



