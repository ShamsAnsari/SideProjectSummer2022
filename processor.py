import os

import face_recognition
import cv2
import numpy as np

FACES_PATH = "known faces"


def get_filtered_files(path, extensions={"png", "jpg", "jpeg", "webp"}):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for file in filenames:
            filename, file_extension = os.path.splitext(file)
            if file_extension.lower()[1:] in extensions:
                files.append(os.path.join(dirpath, file))
    return files

def save_file_names(path, files):
    f = open(path, "w")
    for file in files:
        f.write(file + "\n")

def move_files(files, folder):
    for file in files:
        filename = file.split("/")[-1]
        os.rename(file, folder + filename)
def load_faces(files):
    known_face_encodings = []
    known_face_names = []
    for file in files:
        print(file)
        image = face_recognition.load_image_file(file)
        recognized_faces = face_recognition.face_encodings(image)

        if not recognized_faces:
            print(f"No face found for: {file}")
            continue

        face_encoding = recognized_faces[0]
        name = os.path.basename(file).split("_")
        first_name, last_name, num = name[0].capitalize(), name[1].capitalize(), name[2][0]
        known_face_encodings.append(face_encoding)

        known_face_names.append(f"{first_name} {last_name} {num}")

    return known_face_encodings, known_face_names
class Processor:

    def __init__(self):
        self.known_face_encodings, self.known_face_names = load_faces(get_filtered_files(FACES_PATH))
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.blur_image = False
        self.blur_face = False

    def process(self, frame):

        frame = cv2.imdecode(np.fromstring(frame, np.uint8), cv2.IMREAD_COLOR)

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            face_names.append(name)


        if self.blur_image and not face_locations:
            frame = cv2.GaussianBlur(frame, (49, 49), 0)


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if self.blur_face:

                # Extract the region of the image that contains the face
                face_image = frame[top:bottom, left:right]
                # Blur the face image
                face_image = cv2.GaussianBlur(face_image, (99, 99), 30)
                # Put the blurred face region back into the frame image
                frame[top:bottom, left:right] = face_image
            else:
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        return cv2.imencode('.jpg', frame)[1].tostring()