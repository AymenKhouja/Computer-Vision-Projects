import cv2
import mediapipe as mp
import random

class FallingObject:
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width - 50)
        self.y = 0
        self.size = 30
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class Star:
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width - 50)
        self.y = 0
        self.size = 30
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def change_color(self):
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        
        
class Player: 
    def __init__(self, lifes=3): 
        self.lifes = lifes
        self.score = 0

class HandGame:
    def __init__(self, screen_width, screen_height):
        self.player = Player()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.falling_objects = []
        self.star_objects = []
        self.falling_speed = 5
        self.spawn = 30
        self.cap = cv2.VideoCapture(0)
        self.hands = mp.solutions.hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils
        self.speed_adjusted = False
        self.lost_life = False

        self.star_counter = 0
        self.star_frequency = 150
        self.star = None
        self.star_duration = 30
        self.star_timer = 0
        self.star_effect = False

    def create_falling_object(self):
        return FallingObject(self.screen_width, self.screen_height)

    def create_star(self):
        self.star = Star(self.screen_width, self.screen_height)
        

    def draw_falling_objects(self, img):
        if(len(self.falling_objects) != 0):
            for obj in self.falling_objects:
                print(f"Printing obj with coordinates : {obj.x} and {obj.y}")
                cv2.circle(img, (obj.x, obj.y), obj.size, obj.color, -1)
                obj.y = int(obj.y + self.falling_speed)

    
    def draw_star(self, img):
        if self.star:
            self.star.change_color()
            cv2.circle(img, (self.star.x, self.star.y), self.star.size, self.star.color, -1)
            self.star.y =int(self.star.y + self.falling_speed)
            
            
            
    def check_catching(self, hand_lms):
        hand_x, hand_y = int(hand_lms[8].x * self.screen_width), int(hand_lms[8].y * self.screen_height)
        
        for obj in self.falling_objects:
            
            if (
                obj.x - obj.size < hand_x < obj.x + obj.size and
                obj.y - obj.size < hand_y < obj.y + obj.size
            ):
                self.player.score += 1
                if obj in self.falling_objects:
                    self.falling_objects.remove(obj)  

            elif obj.y > self.screen_height: 
                self.lost_life = True
                self.player.lifes -= 1
                if obj in self.falling_objects:
                    self.falling_objects.remove(obj)   

        if self.star and (
            self.star.x - self.star.size < hand_x < self.star.x + self.star.size and
            self.star.y - self.star.size < hand_y < self.star.y + self.star.size
        ):
            self.falling_speed /= 2  # Slow down falling speed
            self.star = None
            self.star_effect = True
            self.star_timer = 0

    def display_player_info(self, img):
        cv2.putText(img, f"Score: {self.player.score}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
        cv2.putText(img, f"Lifes: {self.player.lifes}", (480, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))

    def adjust_speed(self):
        if self.player.score % 10 == 0 and self.player.score != 0 and not self.speed_adjusted:
            self.falling_speed += 5
            self.speed_adjusted = True
        elif self.player.score % 10 != 0:
            self.speed_adjusted = False

    def run_game(self):
        while self.player.lifes > 0:
            success, img = self.cap.read()
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            if self.spawn >= 30:
                self.falling_objects.append(self.create_falling_object())
                self.spawn = 0
                
            if self.star_counter >= self.star_frequency:
                self.create_star()
                self.star_counter = 0
                
                
            self.draw_falling_objects(img)
            self.draw_star(img)

            if results.multi_hand_landmarks:
                for handlms in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(img, handlms, mp.solutions.hands.HAND_CONNECTIONS)
                    self.check_catching(handlms.landmark)

            self.display_player_info(img)
            self.adjust_speed()
            if self.lost_life: 
                self.lost_life = False
            if self.star_effect :
                self.star_timer +=1
                
            if self.star_timer > self.star_duration and self.star_effect:
                self.falling_speed *=2
                self.star_effect = False
                
            if not success:
                print("Error: Failed to capture frame.")
                break

            cv2.imshow("Game", img)
            self.spawn += 1
            self.star_counter +=1
            
            key = cv2.waitKey(1)
            if key == ord('q') or cv2.getWindowProperty("Game", cv2.WND_PROP_VISIBLE) < 1:
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = HandGame(screen_width=640, screen_height=480)
    game.run_game()
