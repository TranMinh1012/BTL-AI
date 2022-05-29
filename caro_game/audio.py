import pygame


def audio_music(type):
    pygame.mixer.init()
    pygame.mixer.music.load(f"sound/{type}.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play() 

def stop_music():
    pygame.mixer.music.pause()

def play_music():
    pygame.mixer.music.unpause()