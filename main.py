# Python Arcade Shooting Gallery!
import pygame
import math 
import random
import time 

pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font(r'Arcade Shooting Game Gallery-main\assets\font\myFont.ttf', 30)
big_font = pygame.font.Font(r'Arcade Shooting Game Gallery-main\assets\font\myFont.ttf', 60)
Width = 900
Height = 800
screen = pygame.display.set_mode([Width, Height])

bgs = []
banners = []
guns = []
target_imgs = [[], [], []]
targets = {1: [10, 5, 3],        #no of targets in each level
           2: [12, 8, 5],
           3: [15, 12, 8, 4]}

level = 0
points = 0
total_shots = 0
ammo = 0
mode = 0 
time_passed = 0 
time_remaining = 0
counter = 1
shot = False 
menu = True
game_over = False
pause = False 
best_freeplay_score = 0
best_ammo_score = 0
best_timed_score = 0
clicked = False 
write_values = False
new_coords = True

game_over_img = pygame.image.load('Arcade Shooting Game Gallery-main/assets/menus/gameOver.png')
menu_img = pygame.image.load('Arcade Shooting Game Gallery-main/assets/menus/mainMenu.png')
pause_img = pygame.image.load('Arcade Shooting Game Gallery-main/assets/menus/pause.png')

file = open('Arcade Shooting Game Gallery-main/high_scores.txt', 'r')
read_file = file.readlines()
file.close()
best_freeplay_score = int(read_file[0])
best_ammo_score = int(read_file[1])
best_timed_score = int(read_file[2])

pygame.mixer.init()
pygame.mixer.music.load('Arcade Shooting Game Gallery-main/assets/sounds/bg_music.mp3')

bird_sound = pygame.mixer.Sound('Arcade Shooting Game Gallery-main/assets/sounds/Drill Gear.mp3')
bird_sound.set_volume(.2)
plate_sound = pygame.mixer.Sound('Arcade Shooting Game Gallery-main/assets/sounds/Broken plates.wav')
plate_sound.set_volume(.2)
laser_sound = pygame.mixer.Sound('Arcade Shooting Game Gallery-main/assets/sounds/Laser Gun.wav')
laser_sound.set_volume(.3)
pygame.mixer.music.play()


for i in range(1,4):
    bgs.append(pygame.image.load(f'Arcade Shooting Game Gallery-main/assets/bgs/{i}.png'))
    banners.append(pygame.image.load(f'Arcade Shooting Game Gallery-main/assets/banners/{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'Arcade Shooting Game Gallery-main/assets/guns/{i}.png'), (100, 100)))
    if i < 3:
        for j in range(1,4):
            target_imgs[i-1].append(pygame.transform.scale(pygame.image.load(
                f'Arcade Shooting Game Gallery-main/assets/targets/{i}/{j}.png'), (120-(j*18), 80-(j*18)) ))
    else:
        for j in range(1,5):
             target_imgs[i-1].append(pygame.transform.scale(pygame.image.load(
                f'Arcade Shooting Game Gallery-main/assets/targets/{i}/{j}.png'), (120-(j*18), 80-(j*18)) ))


def draw_gun():
    mouse_pos = pygame.mouse.get_pos()
    gun_pos = (Width/2, Height-200)
    lasers = ['red', 'purple', 'green']
    clicks = pygame.mouse.get_pressed()
    if mouse_pos[0] != gun_pos[0]:     #otherwise denominator will be 0
        slope = (mouse_pos[1] - gun_pos[1])/(mouse_pos[0] - gun_pos[0])
    else:
        slope = -100000   #big -ve number that acts like infinty for this game, gives a straight line
    
    angle = math.atan(slope)    #inverse tan function
    rotation = math.degrees(angle)

    if mouse_pos[0] < Width/2:
        gun = pygame.transform.flip(guns[level-1], True, False)  #flip(img, X_axis, Y_axis) --> here we want to flip along x axis and not y 
        if mouse_pos[1] < 600:  #the bottom 200 is the banner and menu area. We don't want to shoot while selecting pause and other options
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (Width/2 - 90, Height - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level-1], mouse_pos, 5)

    else:
        gun = guns[level-1]
        if mouse_pos[1] < 600:  
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (Width/2 - 30, Height - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level-1], mouse_pos, 5)


def move_level(coords):
    if level == 1 or level == 2:
        max_val = 3
    else:
        max_val = 4

    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = (Width, my_coords[1])
            else:
                coords[i][j] = (my_coords[0] - 2**i, my_coords[1])   #try: my_coords[random.randrange(0,1)]
    return coords


def draw_level(coords):
    if level == 1 or level == 2:
        target_rects = [[], [], []]
    else: 
        target_rects = [[], [], [], []]

    for i in range(len(coords)):
        for j in range(len(coords[i])):
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]), 
                                                    (60-i*12, 60-i*12)))
            screen.blit(target_imgs[level-1][i], coords[i][j])
    return target_rects


def check_shot(targets, coords):
    global points 
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)
                points += 10 + 10*(i**2)
                # add sounds for enemy hit
                if level == 1:
                    bird_sound.play()
                elif level == 2:
                    plate_sound.play()
                elif level == 3:
                    laser_sound.play()
    return coords


def draw_score():
    points_text = font.render(f'Points: {points}', True, 'black')
    screen.blit(points_text, (320, 658))
    shots_text = font.render(f'Total Shots: {total_shots}', True, 'black')
    screen.blit(shots_text, (320, 685))
    time_text = font.render(f'Time Elapsed: {time_passed}', True, 'black')
    screen.blit(time_text, (320, 715))
    if mode == 0:
        mode_text = font.render(f'Freeplay!', True, 'black')
    if mode == 1:
        mode_text = font.render(f'Ammo Remaining: {ammo}', True, 'black')
    if mode == 2:
        mode_text = font.render(f'Time Remaining: {time_remaining}', True, 'black')
    screen.blit(mode_text, (320, 745))


def draw_menu():
    global game_over, pause, mode, level, menu, time_passed, total_shots, points, clicked, new_coords
    global ammo, time_remaining, best_freeplay_score, best_ammo_score, best_timed_score, write_values
    game_over = False 
    pause = False 
    screen.blit(menu_img, (0,0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    #invisible buttons/rectangles 
    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    screen.blit(font.render(f'{best_freeplay_score}', True, 'black'), (340, 582))
   
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    screen.blit(font.render(f'{best_ammo_score}', True, 'black'), (652, 582))

    timed_button = pygame.rect.Rect((170, 661), (260, 100))
    screen.blit(font.render(f'{best_timed_score}', True, 'black'), (350, 713))

    reset_button = pygame.rect.Rect((475, 661), (260, 100))

    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False 
        time_passed = 0
        total_shots = 0
        points = 0 
        clicked = True
        new_coords = True

    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False 
        time_passed = 0
        ammo = 82
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True

    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False 
        time_remaining = 30 
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True

    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay_score = 0
        best_ammo_score = 0
        best_timed_score = 0
        clicked = True
        write_values = True
        new_coords = True


def draw_pause():
    global level, pause, menu, points, total_shots, time_passed, time_remaining, clicked, new_coords
    screen.blit(pause_img, (0,0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    resume_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False 
        clicked = True
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        pygame.mixer.music.play()
        level = 0
        pause = False 
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
        clicked = True
        new_coords = True 


def draw_game_over():
    global clicked, level, pause, game_over, menu, total_shots, time_passed, time_remaining, points
    if mode == 0:
        display_score = time_passed
    else: 
        display_score = points 

    screen.blit(game_over_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    exit_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    screen.blit(big_font.render(f'{display_score}', True, 'black'), (650, 570))
    
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True 
        level = 0
        pause = False
        game_over = False 
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0

    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run 
        run = False 


# Main code(): 
run = True
while run:
    timer.tick(fps)

    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_passed += 1
            if mode == 2:
                time_remaining -= 1
    
    if new_coords:
         # initialize enemy coordinates
        one_coords = [[], [], []]
        two_coords = [[], [], []]
        three_coords = [[], [], [], []]
        for i in range(3):
            my_list = targets[1]
            for j in range(my_list[i]):
                one_coords[i].append((Width // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(3):
            my_list = targets[2]
            for j in range(my_list[i]):
                two_coords[i].append((Width // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(4):
            my_list = targets[3]
            for j in range(my_list[i]):
                three_coords[i].append((Width // (my_list[i]) * j, 330 - (i * 100) + 30 * (j % 2)))
        new_coords = False


    screen.fill('black')
    screen.blit(bgs[level-1], (0,0))  #level-1 cause list indexing start from 0,1,2 
                                        #(0,0) is the position from where we want out image to start from 
    screen.blit(banners[level-1], (0, Height - 200)) #Height-200 as the banner img height is 200 pixel 


    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()


    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        if shot: 
            one_coords = check_shot(target_boxes, one_coords)
            shot = False  #to check if the shot is done only once and 
            #to prevent from continously holding the mouse button and hitting the target like infinte ray gun

    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot: 
            two_coords = check_shot(target_boxes, two_coords)
            shot = False

    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot: 
            three_coords = check_shot(target_boxes, three_coords)
            shot = False

    if level > 0:
        draw_gun()
        draw_score()

    for event in pygame.event.get():    #to end the infinite while run
        if event.type == pygame.QUIT:   #here QUIT is the cross exit button on top 
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if(0 < mouse_pos[0] < Width) and (0 < mouse_pos[1] < Height-200):
                shot = True 
                total_shots += 1
                if mode == 1:
                    ammo -= 1

            if(670 < mouse_pos[0] < 860) and (660 < mouse_pos[1] < 715):
                resume_level = level 
                pause = True 
                clicked = True 

            if(670 < mouse_pos[0] < 860) and (715 < mouse_pos[1] < 760):
                menu = True
                pygame.mixer.music.play()
                clicked = True 
                new_coords = True


        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

        
    if level > 0:
        if target_boxes == [[], [], []] and level < 3:
            level += 1
        if (level == 3 and target_boxes == [[], [], [], []]) or (mode == 1 and ammo == 0) \
            or (mode == 2 and time_remaining == 0):
            new_coords = True 
            pygame.mixer.music.play()

            if mode == 0:
                if time_passed < best_freeplay_score or best_freeplay_score == 0:
                    best_freeplay_score = time_passed
                    write_values = True 

            if mode == 1:
                if points > best_ammo_score:
                    best_ammo_score = points 
                    write_values = True

            if mode == 2:
                if points > best_timed_score:
                    best_timed_score = points 
                    write_values = True 
            
            game_over = True 

    if write_values:
        file = open('Arcade Shooting Game Gallery-main/high_scores.txt', 'w')
        file.write(f'{best_freeplay_score}\n{best_ammo_score}\n{best_timed_score}')
        file.close()
        write_values = False 

    pygame.display.flip()

pygame.quit()

