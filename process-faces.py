import os, pickle, face_recognition
from glob import glob
from functools import reduce
from PIL import Image

PROCESS_FEEDBACK_INTERVAL = 50

FILE_LOCATIONS = "./output/{type}/files/*/"
IMAGE_EXTENSIONS = ["jpg", "jpeg", "png"]

FACES_DATA = "./output/{type}/FaceEncodings.dat"
FACES_OUTPUT = "./output/{type}/faces/{file}-{index}.{extension}"
CASE_TYPES = {
    "MissingPersons": {
        "excluded": []
    },
    "UnidentifiedPersons": {
        "excluded": ["/Clothing/", "/Footwear/", "/OfficeLogo/"]
    }
}


def main():
    for caseType in CASE_TYPES:
        print("Processing: {type}".format(type=caseType))

        print(" > Fetching image file paths")
        paths = getImageFilesForType(caseType)
        print(" > Found %d files" % len(paths))

        os.makedirs(
            os.path.dirname(
                FACES_OUTPUT.format(type=caseType, file="*", index="*", extension="*")
            ),
            exist_ok=True,
        )
        dataFile = open(FACES_DATA.format(type=caseType), 'wb')

        print(" > Starting face extraction")
        processedFiles, facesFound = 0, 0
        for path in paths:
            try:
                image = face_recognition.load_image_file(path)
                locations = face_recognition.face_locations(image)
                encodings = face_recognition.face_encodings(image, locations)

                if len(encodings):
                    pickle.dump({path: encodings}, dataFile)

                pathParts = path.split("/")[-1].split(".")
                fileName, extension = pathParts[0], pathParts[1]

                for index, location in enumerate(locations):
                    outputPath = FACES_OUTPUT.format(
                        type=caseType, file=fileName, index=index, extension=extension
                    )

                    top, right, bottom, left = location
                    face = Image.fromarray(image[top:bottom, left:right])
                    face.save(outputPath)
                    facesFound += 1

                processedFiles += 1
                if processedFiles % PROCESS_FEEDBACK_INTERVAL == 0:
                    print(
                        " > Processed {count} files with {faces} faces".format(
                            count=processedFiles, faces=facesFound
                        )
                    )
            except:
                processedFiles += 1
                print(" > Failed parsing path: {path}".format(path=path))

        dataFile.close()


def getImageFilesForType(caseType):
    imageExtensionPaths = [
        FILE_LOCATIONS.format(type=caseType) + "*." + extension
        for extension in IMAGE_EXTENSIONS
    ]

    filePaths = reduce(lambda output, path: output + glob(path), imageExtensionPaths, [])
    for excluded in CASE_TYPES[caseType]["excluded"]:
        filePaths = list(filter(lambda path: excluded not in path, filePaths))

    return list(filePaths)


main()
