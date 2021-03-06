#The code was adapted from https://pythonspot.com/maze-in-pygame/

from shutil import move
import pygame
from pygame.locals import *
from maze_game_hmi.pytringos.pytringos import TrignoAdapter
import time
from maze_game_hmi.utils.utils import *
import matplotlib.pyplot as plt

class Player:

    def __init__(self):
        self.x = 44
        self.y = 44
        self.speed = 1.0

    def move_right(self, maze):
        b_x = self.x + self.speed
        b_y = self.y
        if maze.collision(b_x, b_y):
            self.x = b_x

    def move_left(self, maze):
        b_x = self.x - self.speed
        b_y = self.y
        if maze.collision(b_x, b_y):
            self.x = b_x

    def move_up(self, maze):
        b_x = self.x
        b_y = self.y - self.speed
        if maze.collision(b_x, b_y):
            self.y = b_y

    def move_down(self, maze):
        b_x = self.x
        b_y = self.y + self.speed
        if maze.collision(b_x, b_y):
            self.y = b_y


class Maze:

    def __init__(self):
        self.player_size = 40
        self.brick_size = 44
        self.M = 10
        self.N = 8
        self.maze = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                     1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                     1, 0, 1, 1, 1, 1, 1, 1, 0, 1,
                     1, 0, 1, 0, 0, 0, 0, 0, 0, 1,
                     1, 0, 1, 0, 1, 1, 1, 1, 0, 1,
                     1, 0, 0, 0, 0, 0, 0, 0, 0, 2,
                     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ]

    def draw(self, display_surf, image_surf, exit_surf):
        bx = 0
        by = 0
        for i in range(0, self.M * self.N):
            if self.maze[bx + (by * self.M)] == 1:
                display_surf.blit(image_surf, (bx * 44, by * 44))
            if self.maze[bx + (by * self.M)] == 2:
                display_surf.blit(exit_surf, (bx * 44, by * 44))
            bx = bx + 1
            if bx > self.M - 1:
                bx = 0
                by = by + 1

    def collision(self, b_x, b_y):
        return self.maze[int((b_x) // self.brick_size) + int((b_y // self.brick_size) * self.M)] != 1 and self.maze[
            int((b_x + self.player_size) // self.brick_size) + int(((b_y + self.player_size) // self.brick_size) * self.M)] != 1 and self.maze[
                   int((b_x + self.player_size) // self.brick_size) + int(((b_y) // self.brick_size) * self.M)] != 1 and self.maze[
                   int((b_x) // self.brick_size) + int(((b_y + self.player_size) // self.brick_size) * self.M)] != 1

    def is_exit(self, b_x, b_y):
        return self.maze[int((b_x) // self.brick_size) + int((b_y // self.brick_size) * self.M)] == 2 or self.maze[
            int((b_x + self.player_size) // self.brick_size) + int(((b_y + self.player_size) // self.brick_size) * self.M)] == 2 or self.maze[
                   int((b_x + self.player_size) // self.brick_size) + int(((b_y) // self.brick_size) * self.M)] == 2 or self.maze[
                   int((b_x) // self.brick_size) + int(((b_y + self.player_size) // self.brick_size) * self.M)] == 2


class App:

    def __init__(self):
        self.windowWidth = 800
        self.windowHeight = 600
        self.player = 0
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self._block_surf = None
        self._exit_surf = None
        self.player = Player()
        self.maze = Maze()

        self._fs = 1920
        self._Rs = 50
        self._window = 500
        self._stride = 100
        self._time_period = 0.5 #s
        self._sensor_data = pd.DataFrame({})
        # load sensor
        self.trigno_sensors = TrignoAdapter()
        self.trigno_sensors.add_sensors(sensors_mode='EMG', sensors_ids=(6,), sensors_labels=('EMG1',), host='150.254.46.37')
        # self.trigno_sensors.add_sensors(sensors_mode='ORIENTATION', sensors_ids=(7,), sensors_labels=('ORIENTATION1',), host='150.254.46.37')
        self.trigno_sensors.start_acquisition()


    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        pygame.display.set_caption('Maze')
        self._running = True
        self._image_surf = pygame.image.load("src/maze_game_hmi/game/img/player.png").convert()
        self._block_surf = pygame.image.load("src/maze_game_hmi/game/img/block.png").convert()
        self._exit_surf = pygame.image.load("src/maze_game_hmi/game/img/exit.png").convert()


    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        self._display_surf.fill((0, 0, 0))
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        self.maze.draw(self._display_surf, self._block_surf, self._exit_surf)  #
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if not self.on_init():
            self._running = True

        # CALCULATE MAX CONTRACTION
        samples = 0
        data_rms = pd.DataFrame({})
        while samples < 12000:
            first_sensor = self.trigno_sensors.sensors_reading()
            data_rms = data_rms.append(first_sensor, ignore_index=True)
            samples = len(data_rms)

        emg_sig_rms = data_rms['EMG'].values
        if len(emg_sig_rms) % 2 == 0:
            emg_sig_rms = np.append(emg_sig_rms, emg_sig_rms[-1])
        emg_sig_rms = emg_sig_rms.astype(np.float32)
        # filter
        filtered_sig_rms, filtered_sig_zero_ph = filter_emg(emg_sig_rms, fs=self._fs, Rs=self._Rs, notch=True)

        window = len(emg_sig_rms)
        rms_sig = rms(filtered_sig_rms, window=int(window * 0.01), stride=self._stride, fs=self._fs)
        rms_coeff = rms_sig.max()
        norm_emg_rms = normalize_emg(filtered_sig_rms, rms_coeff)
        max_cond = norm_emg_rms.max()
        
        iter = 0 

        while self._running:
            time.sleep(self._time_period)
            pygame.event.pump()
            sensors_reading = self.trigno_sensors.sensors_reading()
            self._sensor_data = self._sensor_data.append(sensors_reading, ignore_index=True)
            
            emg_sig = self._sensor_data['EMG'].values


            # 1. Filtration
            if len(emg_sig) % 2 == 0:
                emg_sig = np.append(emg_sig, emg_sig[-1])
            emg_sig = emg_sig.astype(np.float32)

            filtered_sig, filtered_sig_zero_ph = filter_emg(emg_sig, fs=120, Rs=self._Rs, notch=True)
            # 3. Normalization
            norm_emg = normalize_emg(filtered_sig, rms_coeff)
            # 4. Classification of 
            abs_emg = np.abs(norm_emg)
            idle = abs_emg[abs_emg < (0.2 * max_cond)]
            middle = abs_emg[(abs_emg >= (0.2 * max_cond)) & (abs_emg < (0.35 * max_cond))]
            high = abs_emg[(abs_emg <= max_cond) & (abs_emg >= (0.35 * max_cond))]

  
            classif = [len(middle), len(high)]
            print(len(idle), classif)
            # keys = pygame.key.get_pressed()
            movearg = np.argmax(classif)
            if movearg == 0 and classif[movearg] > 10:
                self.player.move_right(self.maze)

            if movearg == 1 and classif[movearg] > 10:
                self.player.move_left(self.maze)


            
            if self.maze.is_exit(self.player.x, self.player.y):
                self._running = False
                self.trigno_sensors.stop_acquisition()

            self._sensor_data.drop(self._sensor_data.head(len(emg_sig)).index, inplace=True)
            iter += 1
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == '__main__':
    theApp = App()
    theApp.on_execute()
