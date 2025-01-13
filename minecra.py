from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random
import math

# Initializing the PerlinNoise object and Ursina app
noise = PerlinNoise(octaves=3, seed=random.randint(1, 1000))
app = Ursina()

# Textures
grass_texture = load_texture("Assets/Textures/Grass_Block.png")
stone_texture = load_texture("Assets/Textures/Stone_Block.png")
brick_texture = load_texture("Assets/Textures/Brick_Block.png")
dirt_texture = load_texture("Assets/Textures/Dirt_Block.png")
wood_texture = load_texture("Assets/Textures/Wood_Block.png")
bedrock_texture = load_texture("Assets/Textures/stone07.png")
morning_sky_texture = load_texture("Assets/Textures/Skybox.png")
night_sky_texture = load_texture("Assets/Textures/night_sky.png")
arm_texture = load_texture("Assets/Textures/Arm_Texture.png")
punch_sound = Audio('Assets/SFX/Punch_Sound.wav', loop=False, autoplay=False)

block_pick = 1
respawn_position = Vec3(10, 10, 10)
game_started = False

# Ursina Settings
window.fps_counter.enabled = True
window.exit_button.visible = True
window.fullscreen = True  # Make the window fullscreen

crouching = False  


def update():
    global block_pick, game_started, crouching

    
    # Running mechanic
    if held_keys['control']:
        player.speed = 10 
    else:
        player.speed = 5

    # Hand animation
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    if held_keys['1']:
        block_pick = 1
    if held_keys['2']:
        block_pick = 2
    if held_keys['3']:
        block_pick = 3
    if held_keys['4']:
        block_pick = 4
    if held_keys['5']:
        block_pick = 5
    if held_keys['6']:
        block_pick = 6

    if held_keys["escape"]:
        application.quit()

    # Respawn if player falls off the map
    if player.y < -20:
        player.position = respawn_position
        print("You fell! Respawning...")

    # Handle key presses for start menu actions
    if game_started is False:
        if held_keys['s']:
            start_game()
        elif held_keys['m']:
            set_morning_sky()
        elif held_keys['n']:
            set_night_sky()
        elif held_keys['e']:
            application.quit()
    # Handle crouching
    if held_keys["shift"] and not crouching:
        crouch()
    elif not held_keys["shift"] and crouching:
        stand()

def crouch():
    global crouching
    crouching = True
    player.height = 1.5  
    player.camera_pivot.y = 1.5 
    player.speed = 2.5

def stand():
    global crouching
    crouching = False
    player.height = 2.0  
    player.camera_pivot.y = 2.0  
    player.speed = 5  

class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='Assets/Models/Block',
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            scale=0.5
        )
        self.is_bedrock = texture == bedrock_texture

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                punch_sound.play()
                if block_pick == 1:
                    voxel = Voxel(position=self.position + mouse.normal, texture=grass_texture)
                if block_pick == 2:
                    voxel = Voxel(position=self.position + mouse.normal, texture=stone_texture)
                if block_pick == 3:
                    voxel = Voxel(position=self.position + mouse.normal, texture=brick_texture)
                if block_pick == 4:
                    voxel = Voxel(position=self.position + mouse.normal, texture=dirt_texture)
                if block_pick == 5:
                    voxel = Voxel(position=self.position + mouse.normal, texture=wood_texture)
                if block_pick == 6:
                    voxel = Voxel(position=self.position + mouse.normal, texture=bedrock_texture)
            if key == 'left mouse down' and not self.is_bedrock:
                punch_sound.play()
                destroy(self)

class Sky(Entity):
    def __init__(self, texture=morning_sky_texture):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=texture,
            scale=150,
            double_sided=True
        )

    def change_texture(self, texture):
        self.texture = texture

class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='Assets/Models/Arm',
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -6, 0),
            position=Vec2(0.4, -0.6)
        )

    def active(self):
        self.position = Vec2(0.5, -0.5)

    def passive(self):
        self.position = Vec2(0.6, -0.6)

def start_game():
    global game_started

    game_started = True
    start_menu.enabled = False  
    player.enabled = True
    sky.enabled = True
    hand.enabled = True
    player.position = respawn_position

def set_morning_sky():
    sky.change_texture(morning_sky_texture)

def set_night_sky():
    sky.change_texture(night_sky_texture)

# Create the terrain
min_height = -5
for z in range(15):
    for x in range(15):
        height = noise([x * 0.02, z * 0.02])
        height = math.floor(height * 7.5)
        for y in range(height, min_height - 1, -1):
            if y == min_height:
                voxel = Voxel(position=(x, y + min_height, z), texture=bedrock_texture)
            elif y == height:
                voxel = Voxel(position=(x, y + min_height, z), texture=grass_texture)
            elif height - y > 2:
                voxel = Voxel(position=(x, y + min_height, z), texture=stone_texture)
            else:
                voxel = Voxel(position=(x, y + min_height, z), texture=dirt_texture)

# Start Menu
start_menu = Entity(
    parent=camera.ui,
    model='quad',
    texture='white_cube',
    color=color.gray,
    scale=(2.5, 2.5),
    position=(0, 0),
)

# Add title
title = Text(
    parent=start_menu,
    text="""Welcome CSIT 040 project  
         Minecraft clone""",
    scale=0.3,
    color=color.cyan,
    position=(-0.040, 0.17)
)

# Start button
start_button = Button(
    text='Start Game "s"',
    parent=start_menu,
    scale=(0.2, 0.1),  # Smaller button size
    position=(0, 0.1),
    color=color.green,
    #on_click=start_game
)

# Morning Sky button
morning_sky_button = Button(
    text='Morning Sky "m"',
    parent=start_menu,
    scale=(0.2, 0.1),  # Smaller button size
    position=(-0.1, 0),
    color=color.orange,
    #on_click=set_morning_sky
)

# Night Sky button
night_sky_button = Button(
    text='Night Sky "n"',
    parent=start_menu,
    scale=(0.2, 0.1),  # Smaller button size
    position=(0.1, 0),
    color=color.blue,
    #on_click=set_night_sky
)

# Exit button
exit_button = Button(
    text='Exit "e"',
    parent=start_menu,
    scale=(0.2, 0.1),  # Smaller button size
    position=(0, -0.1),
    color=color.red,
    #on_click=application.quit
)

# Set up the player and sky
player = FirstPersonController()
sky = Sky()  # Default sky is morning sky
hand = Hand()

app.run()
