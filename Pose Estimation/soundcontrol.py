import cv2
import mediapipe as mp
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class VolumeControl:
    def __init__(self, screen_width, screen_height):
        self.cap = cv2.VideoCapture(0)
        self.hands = mp.solutions.hands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.initialize_volume()

    def initialize_volume(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = interface.QueryInterface(IAudioEndpointVolume)
        self.cVolume = self.volume.GetMasterVolumeLevel()

    def process_hand_landmarks(self, hand_landmarks):
        cy = int(hand_landmarks.landmark[4].y * self.screen_height)
        return cy

    def adjust_volume(self, dy, lower_limit, upper_limit):
        if lower_limit <= self.cVolume <= upper_limit:
            dV = (dy * 35) / 480
            new_volume = self.cVolume + dV
            if lower_limit <= new_volume <= upper_limit:
                self.volume.SetMasterVolumeLevel(new_volume, None)
                self.cVolume = self.volume.GetMasterVolumeLevel()
            elif new_volume < lower_limit: 
                self.volume.SetMasterVolumeLevel(lower_limit, None)
            elif new_volume > upper_limit: 
                self.volume.SetMasterVolumeLevel(upper_limit, None)

    def run(self):
        increase_cooldown = 0
        decrease_cooldown = 0
        just_decreased, just_increased = False, False
        start = True

        while True:
            success, img = self.cap.read()
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                self.mpDraw.draw_landmarks(img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

                if start:
                    initial_y = self.process_hand_landmarks(hand_landmarks)
                    start = False

                cy = self.process_hand_landmarks(hand_landmarks)

                if cy < initial_y and increase_cooldown == 0:
                    dy = cy - initial_y
                    print(dy)
                    if dy < -40:
                        just_decreased = False
                    initial_y = cy if dy < -20 else initial_y
                    increase_cooldown = 10
                    if not just_decreased:
                        self.adjust_volume(-dy, -35, 0)  
                        just_increased = True

                elif cy > initial_y and decrease_cooldown == 0:
                    dy = cy - initial_y
                    print(dy)
                    if dy > 40 :
                        just_increased = False
                    initial_y = cy
                    initial_y = cy if dy > 20 else initial_y
                    decrease_cooldown = 10
                    if not just_increased:
                        
                        self.adjust_volume(-dy, -35, 0)  
                        just_decreased = True

            increase_cooldown -= 1 if increase_cooldown > 0 else 0
            decrease_cooldown -= 1 if decrease_cooldown > 0 else 0

            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == ord('q') or cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    volume_controller = VolumeControl(screen_width=640, screen_height=480)
    volume_controller.run()
