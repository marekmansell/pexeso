# BBC micro:bit 1 - https://makecode.microbit.org/_UvF3jkYTUHjH
# BBC micro:bit 2 - https://makecode.microbit.org/_1fAh5v4yUfDp
# BBC micro:bit 3 - https://makecode.microbit.org/_DDx3i50h1HtM
# BBC micro:bit 4 - https://makecode.microbit.org/_aRx6HbaWkRkM
# BBC micro:bit 5 - https://makecode.microbit.org/_iVmHma920hk2
# BBC micro:bit 6 - https://makecode.microbit.org/_W9f2t4XUxWRz


from tkinter import Tk, Canvas, NW
from time import sleep
import threading, queue
from PIL import ImageTk, Image
import os
import random
import serial


IMG_FOLDER = "images"
IMGS_A = ["01-a.png", "02-a.png", "03-a.png", "04-a.png", "05-a.png", "06-a.png", "07-a.png", "08-a.png"]
IMGS_B = ["01-b.png", "02-b.png", "03-b.png", "04-b.png", "05-b.png", "06-b.png", "07-b.png", "08-b.png"]
ROWS = 2
COLS = 8
PLAYER_1 = 1
PLAYER_2 = 2
IMG_WIDTH = 150
IMG_HEIGHT = int(IMG_WIDTH * 2.035) # Ratio of images is 1:2.035
IMG_GAP = 30
IMG_BORDER = 50


class PexesoGUI:
    def __init__(self, master):
        self.master = master
        master.title("MICRO:BATTLE #5 - Vstupné piny")

        self.canvas_width = (IMG_WIDTH+IMG_GAP)*COLS + (IMG_BORDER*2) - IMG_GAP
        self.canvas_height = (IMG_HEIGHT+IMG_GAP)*ROWS + (IMG_BORDER*2) - IMG_GAP
        master.minsize(self.canvas_width, self.canvas_height)
        master.maxsize(self.canvas_width, self.canvas_height)

        self.first_card = None
        self.second_card = None

        self.player_turn = PLAYER_1

        self.serial_queue = None

        self.load_cards()
        print(f"Na rade je hráč {self.player_turn}")


    def load_cards(self):

        self.canvas = Canvas(self.master, width=self.canvas_width, height=self.canvas_height)  
        self.canvas.pack()  

        self.img = ImageTk.PhotoImage(Image.open(os.path.join(IMG_FOLDER, "bg.png")))  
        self.canvas.create_image(0, 0, anchor=NW, image=self.img) 

        self.back_image = ImageTk.PhotoImage(Image.open(os.path.join(IMG_FOLDER, "back.png")).resize((IMG_WIDTH, IMG_HEIGHT)))
        self.all_images = IMGS_A + IMGS_B
        random.shuffle(self.all_images)
        
        img_id = 0
        self.photo_images = []
        self.canvas_images = []
        self.image_mapping = {}
        self.guessed = []

        for row in range(ROWS):
            for col in range(COLS):
                self.photo_images.append(ImageTk.PhotoImage(Image.open(os.path.join(IMG_FOLDER, self.all_images[img_id])).resize((IMG_WIDTH, IMG_HEIGHT))))
                self.canvas_images.append(self.canvas.create_image(col*(IMG_WIDTH+IMG_GAP) + IMG_BORDER, row*(IMG_HEIGHT+IMG_GAP) + IMG_BORDER, anchor=NW, image=self.back_image))
                self.canvas.tag_bind(self.canvas_images[img_id], '<Button-1>', self.on_card_mouse_click)
                self.image_mapping[self.canvas_images[img_id]] = img_id
                img_id += 1


    def on_card_mouse_click(self, event):
        obj_id = event.widget.find_closest(event.x, event.y)[0]
        img_id = self.image_mapping[obj_id]
        self.on_card_click(img_id)


    def on_card_click(self, img_id):

        if self.second_card is not None:
            return

        if self.first_card == img_id:
            return

        if img_id in self.guessed:
            return

        obj_id = self.canvas_images[img_id]
        
        self.canvas.itemconfig(obj_id, image=self.photo_images[img_id])

        if self.first_card is None:
            self.first_card = img_id
        elif self.first_card is not None and self.second_card is None:
            self.second_card = img_id
            self.master.after(500, self.turn_back_cards)

            if self.all_images[self.first_card].split("-")[0] == self.all_images[self.second_card].split("-")[0]:
                print("Match found")
                self.guessed.append(self.first_card)
                self.guessed.append(self.second_card)
            else:
                print("No match")


    def turn_back_cards(self):
        if self.all_images[self.first_card].split("-")[0] == self.all_images[self.second_card].split("-")[0]:
            self.canvas.delete(self.canvas_images[self.first_card])
            self.canvas.delete(self.canvas_images[self.second_card])
        else:
            self.canvas.itemconfig(self.canvas_images[self.first_card], image=self.back_image)
            self.canvas.itemconfig(self.canvas_images[self.second_card], image=self.back_image)
        self.first_card = None
        self.second_card = None

        if self.player_turn == PLAYER_1:
            self.player_turn = PLAYER_2
        else:
            self.player_turn = PLAYER_1
        print(f"Na rade je hráč {self.player_turn}")
        print(self.serial_queue)


class SerialThread(threading.Thread):

    def __init__(self, pexeso_gui):
        threading.Thread.__init__(self)
        
        self.stop = False
        self.pexeso_gui = pexeso_gui

        self.queue = queue.Queue()

        self.serial = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5)

        self.start()


    def run(self):
        while not self.stop:
            if not self.serial.is_open:
                print("Error: No connection to micro:bit")
            line = self.serial.readline()
            if line:
                try:
                    command = int(line.decode().strip())
                    self.pexeso_gui.on_card_click(command)
                except:
                    pass


root = Tk()
pexeso_gui = PexesoGUI(root)
serial_thread = SerialThread(pexeso_gui)
pexeso_gui.serial_queue = serial_thread.queue

try:
    root.mainloop()
except:
    print("Error in TK inter loop")

serial_thread.stop = True
serial_thread.join() 
