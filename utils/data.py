from random import random

def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement
    