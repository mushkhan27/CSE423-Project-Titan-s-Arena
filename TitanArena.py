from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time


ARENA_HALF = 2000      
GRID_SPACING = 100     
WALL_HEIGHT = 400
PILLAR_WIDTH = 120     
PILLAR_HEIGHT = 400    
PILLAR_POSITIONS = [[-400, 400], [400, 400], [-400, -400], [400, -400]]

# Goal Position (Level 2 End)
WEAPON_PICKUP_POS = [0, ARENA_HALF - 250, 30] 

def reset_game():
    global game_state, titan_pos, titan_yaw, first_person, camHeight, anim_phase
    global red_light_status, red_light_timer, boss_state, boss_timer, boss_health, pillars_hp, zombies, bullets
    global cheat_mode, pillar_hit_this_cycle
    
    # game state
    game_state = {"level": 1, "lives": 3, "score": 0, "zombie_kills": 0, "game_over": False, "won": False, "exited": False, "teleported": False}
    
    titan_pos = [0, -ARENA_HALF + 200, 0] 
    titan_yaw = [90]
    first_person = [False]
    camHeight = 600
    anim_phase = 0
    pillars_hp = [3, 3, 3, 3]
    red_light_status = "GREEN"
    red_light_timer = time.time()
    boss_state = "IDLE"
    boss_timer = time.time()
    boss_health = 5
    bullets = []
    zombies = [{"pos": [random.uniform(-ARENA_HALF+100, ARENA_HALF-100), ARENA_HALF-100, 0], "phase": random.random()*10} for _ in range(5)]
    cheat_mode = False
    pillar_hit_this_cycle = [False, False, False, False]


def drawArena(door_open=False):
    glPushMatrix()
    
    # 1. FLOOR
    glBegin(GL_QUADS)
    n = int((2 * ARENA_HALF) // GRID_SPACING)
    start = -ARENA_HALF
    for i in range(n):
        for j in range(n):
            x0 = start + i * GRID_SPACING
            y0 = start + j * GRID_SPACING
            x1 = x0 + GRID_SPACING
            y1 = y0 + GRID_SPACING
            
            center_x = (x0 + x1) / 2
            center_y = (y0 + y1) / 2
            dist = math.hypot(center_x, center_y)
            fade = max(0.1, 1.0 - (dist / 2500)) 

            if game_state["level"] == 2 and red_light_status == "RED":
                glColor3f(0.8 * fade, 0.05, 0.05) 
            elif (i + j) % 2 == 0:
                glColor3f(0.2 * fade, 0.1 * fade, 0.3 * fade)
            else:
                glColor3f(0.25 * fade, 0.15 * fade, 0.35 * fade)
            
            glVertex3f(x0, y0, 0); glVertex3f(x1, y0, 0); glVertex3f(x1, y1, 0); glVertex3f(x0, y1, 0)
    glEnd()

    # 2. WALLS
    glBegin(GL_QUADS)
    glColor3f(0.05, 0.05, 0.1) 
    glVertex3f(-ARENA_HALF, -ARENA_HALF, 0); glVertex3f(-ARENA_HALF, ARENA_HALF, 0); glVertex3f(-ARENA_HALF, ARENA_HALF, WALL_HEIGHT); glVertex3f(-ARENA_HALF, -ARENA_HALF, WALL_HEIGHT)
    glVertex3f(ARENA_HALF, -ARENA_HALF, 0); glVertex3f(ARENA_HALF, ARENA_HALF, 0); glVertex3f(ARENA_HALF, ARENA_HALF, WALL_HEIGHT); glVertex3f(ARENA_HALF, -ARENA_HALF, WALL_HEIGHT)
    glVertex3f(-ARENA_HALF, -ARENA_HALF, 0); glVertex3f(ARENA_HALF, -ARENA_HALF, 0); glVertex3f(ARENA_HALF, -ARENA_HALF, WALL_HEIGHT); glVertex3f(-ARENA_HALF, -ARENA_HALF, WALL_HEIGHT)
    # Goal Wall
    glColor3f(0.1, 0.15, 0.2)
    glVertex3f(ARENA_HALF, ARENA_HALF, 0); glVertex3f(-ARENA_HALF, ARENA_HALF, 0); glVertex3f(-ARENA_HALF, ARENA_HALF, WALL_HEIGHT); glVertex3f(ARENA_HALF, ARENA_HALF, WALL_HEIGHT)
    glEnd()

    # 3. WIDE GOAL DOOR
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.4, 0.5)
    glVertex3f(-300, ARENA_HALF-5, 0); glVertex3f(300, ARENA_HALF-5, 0)
    glVertex3f(300, ARENA_HALF-5, WALL_HEIGHT); glVertex3f(-300, ARENA_HALF-5, WALL_HEIGHT)
    glEnd()
    
    global anim_phase
    pulse = 0.15 * math.sin(anim_phase * 0.05)
    glBegin(GL_QUADS)
    if game_state["level"] == 2:
        if red_light_status == "GREEN": glColor3f(0.0, 1.0, 0.0) 
        else: glColor3f(0.3, 0.0, 0.0) 
    elif door_open: glColor3f(0.1+pulse, 0.9+pulse, 0.2+pulse) 
    else: glColor3f(0.2, 0.2, 0.2) 
    glVertex3f(-280, ARENA_HALF-10, 10); glVertex3f(280, ARENA_HALF-10, 10)
    glVertex3f(280, ARENA_HALF-10, WALL_HEIGHT-10); glVertex3f(-280, ARENA_HALF-10, WALL_HEIGHT-10)
    glEnd()
    glPopMatrix()

def drawPillars(pillars):
    for i, hp in enumerate(pillars):
        if hp > 0:
            pos = PILLAR_POSITIONS[i]
            glPushMatrix(); glTranslatef(pos[0], pos[1], 8); glColor3f(0.3, 0.3, 0.35); glScalef(1.5, 1.5, 0.25); glutSolidCube(PILLAR_WIDTH); glPopMatrix()
            glPushMatrix(); glTranslatef(pos[0], pos[1], PILLAR_HEIGHT/2+15)
            if hp == 3: glColor3f(0.6, 0.45, 0.3)
            elif hp == 2: glColor3f(0.5, 0.35, 0.25)
            else: glColor3f(0.45, 0.2, 0.15)
            glScalef(1, 1, PILLAR_HEIGHT/PILLAR_WIDTH); glutSolidCube(PILLAR_WIDTH); glPopMatrix()
            glPushMatrix(); glTranslatef(pos[0], pos[1], PILLAR_HEIGHT+15); glColor3f(0.4, 0.35, 0.3); glScalef(1.4, 1.4, 0.35); glutSolidCube(PILLAR_WIDTH); glPopMatrix()
            glPushMatrix(); glTranslatef(pos[0], pos[1], PILLAR_HEIGHT/2+15); glColor3f(0.7, 0.6, 0.4); glutSolidTorus(4, PILLAR_WIDTH/2+8, 8, 16); glPopMatrix()

def drawWeaponPickup():
    global anim_phase
    glPushMatrix()
    glTranslatef(WEAPON_PICKUP_POS[0], WEAPON_PICKUP_POS[1], WEAPON_PICKUP_POS[2])
    glRotatef(anim_phase * 2, 0, 1, 0) 
    glRotatef(45, 1, 0, 1) 
    pulse = 0.5 + 0.5 * math.sin(anim_phase * 0.1)
    glColor3f(0.2, 1.0, 1.0) 
    glutWireCube(40) 
    glColor3f(0.0, 0.8 * pulse, 0.8 * pulse) 
    glutSolidCube(20)
    glPopMatrix()
#Characters
def drawTitan(x, y, z, yaw, is_boss=False, attacking=False):
    global anim_phase, game_state
    
    is_giant = is_boss or (game_state["level"] == 2 and x == 0 and y == 0)

    glPushMatrix()
    if is_giant:
        glTranslatef(x, y, z + 60)
        glRotatef(yaw + 90, 0, 0, 1)
        glScalef(4.0, 4.0, 4.0) 
    else:
        glTranslatef(x, y, z + 20)
        glRotatef(yaw + 90, 0, 0, 1) 
        glScalef(1.5, 1.5, 1.5) 

    if game_state["level"] == 2 and is_giant:
        col = (0.3, 0.3, 0.35); acc = (0.4, 0.4, 0.45); core = (0.2, 0.2, 0.25); vis = (0.1, 0.1, 0.1) 
    else:
        pulse = 0.08 * math.sin(anim_phase * 0.08)
        if is_giant: 
            if attacking: col, acc, core, vis = (0.9+pulse,0.2,0.15), (1,0.4,0.2), (1,0.5,0), (1,0.6,0.1)
            else: col, acc, core, vis = (0.4,0.1,0.1), (0.6,0.2,0.2), (0.8,0.1,0), (0.9,0.2,0.1)
        else: 
            col, acc, core, vis = (0.15,0.45,0.85), (0.25,0.55,0.95), (0,0.9,1), (0.1,0.8,1)
    
    for s in [-1, 1]:
        glPushMatrix(); glTranslatef(s*20,0,10); glColor3f(0.2,0.2,0.25); glScalef(1.3,1.8,0.6); glutSolidCube(25); glPopMatrix()
        glPushMatrix(); glTranslatef(s*20,0,12); glColor3f(*col); gluCylinder(gluNewQuadric(),14,12,50,14,1); glTranslatef(0,0,25); glColor3f(0.25,0.25,0.3); gluSphere(gluNewQuadric(),10,10,10); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,60); glColor3f(*col); gluCylinder(gluNewQuadric(),35,30,70,16,4); glPopMatrix()
    glPushMatrix(); glTranslatef(0,-30,95); glColor3f(*acc); glScalef(1.8,0.4,1.2); glutSolidCube(35); glPopMatrix()
    
    glPushMatrix(); glTranslatef(0,-32,95); 
    if game_state["level"] == 3 and is_giant: cp = 0.2*math.sin(anim_phase*0.15)
    else: cp = 0
    glColor3f(core[0],core[1]+cp,core[2]); gluSphere(gluNewQuadric(),10,12,12); glColor3f(1,1,1); gluSphere(gluNewQuadric(),5,8,8); glPopMatrix()
    
    for s in [-1, 1]:
        glPushMatrix(); glTranslatef(s*45,0,120); glColor3f(*col); gluSphere(gluNewQuadric(),18,12,12); glPopMatrix()
        glPushMatrix(); glTranslatef(s*50,0,105); glRotatef(s*90,0,1,0); glRotatef(15,1,0,0); glColor3f(*col); gluCylinder(gluNewQuadric(),12,10,45,12,1)
        glTranslatef(0,0,45); glColor3f(0.25,0.25,0.3); gluSphere(gluNewQuadric(),10,10,10); glColor3f(*col); gluCylinder(gluNewQuadric(),10,8,40,12,1)
        glTranslatef(0,0,40); glColor3f(0.2,0.2,0.25); gluSphere(gluNewQuadric(),12,10,10); glPopMatrix()
    
    glPushMatrix(); glTranslatef(0,0,135); glColor3f(0.25,0.25,0.3); gluCylinder(gluNewQuadric(),12,15,15,12,1); glTranslatef(0,0,20); glColor3f(*col); gluSphere(gluNewQuadric(),25,14,14)
    glPushMatrix(); glTranslatef(0,-22,5); glColor3f(*vis); glScalef(1.8,0.35,0.5); glutSolidCube(20); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,22); glColor3f(0.25,0.25,0.3); gluCylinder(gluNewQuadric(),3,1,20,8,1); glTranslatef(0,0,20); glColor3f(*core); gluSphere(gluNewQuadric(),4,8,8); glPopMatrix()
    glPopMatrix(); glPopMatrix()

def drawZombie(x, y, z, p):
    s = 1.0 + 0.08 * math.sin(p); w = 4 * math.sin(p * 0.7)
    glPushMatrix(); glTranslatef(x, y, z); glScalef(1.3, 1.3, 1.3); glRotatef(w, 0, 0, 1); glScalef(s, s, s)
    for side in [-1, 1]:
        glPushMatrix(); glTranslatef(side*15,0,20); glColor3f(0.15,0.35,0.15); glScalef(0.6,0.6,1.3); glutSolidCube(30); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,60); glColor3f(0.2,0.55,0.2); glutSolidCube(50); glColor3f(0.3,0.25,0.2); glTranslatef(0,-22,0); glScalef(0.85,0.35,0.7); glutSolidCube(45); glPopMatrix()
    for side in [-1, 1]:
        glPushMatrix(); glTranslatef(side*32,-18,65); glRotatef(-55,1,0,0); glRotatef(side*12,0,0,1); glColor3f(0.25,0.5,0.25); glScalef(0.5,0.5,1.2); glutSolidCube(35); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,95); glRotatef(12,1,0,0); glColor3f(0.35,0.55,0.35); gluSphere(gluNewQuadric(),24,12,12)
    eg = 0.2*math.sin(p*0.2)
    for side in [-1, 1]:
        glPushMatrix(); glTranslatef(side*9,-20,6); glColor3f(0.9+eg,0.2,0.1); gluSphere(gluNewQuadric(),5,8,8); glPopMatrix()
    glPopMatrix(); glPopMatrix()


# GAME LOGIC

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def update(v):
    global anim_phase, game_state, red_light_status, red_light_timer, boss_state, boss_timer, boss_health, titan_pos, bullets
    global cheat_mode, pillar_hit_this_cycle
    
    glutTimerFunc(16, update, v + 1)
    glutPostRedisplay()
    
    if game_state["game_over"] or game_state["exited"]: return

    anim_phase += 1; t = time.time()
    
    # LEVEL 3
    if game_state["level"] == 3:
        if game_state["won"] and not game_state["teleported"]:
            titan_pos = [0, ARENA_HALF - 200, 0]; game_state["teleported"] = True
            
        if not game_state["won"]:
            cycle_time = (t - boss_timer) % 10
            
            if cycle_time < 2.0: # idle
                boss_state = "IDLE"
                if int(t * 10) % 10 == 0: pillar_hit_this_cycle = [False]*4
            
            elif cycle_time < 7.0: # ATTACK
                boss_state = "ATTACK"
                blocked = False
                for i, pos in enumerate(PILLAR_POSITIONS):
                    if pillars_hp[i] > 0:
                        tx, ty = 0, ARENA_HALF - 150 
                        px, py = titan_pos[0], titan_pos[1] 
                        line_vec_x = px - tx; line_vec_y = py - ty
                        line_len_sq = line_vec_x**2 + line_vec_y**2
                        
                        if line_len_sq > 0:
                            pillar_vec_x = pos[0] - tx; pillar_vec_y = pos[1] - ty
                            t_proj = (pillar_vec_x * line_vec_x + pillar_vec_y * line_vec_y) / line_len_sq
                            t_proj = max(0, min(1, t_proj)) 
                            
                            closest_x = tx + t_proj * line_vec_x
                            closest_y = ty + t_proj * line_vec_y
                            dist_sq = (pos[0] - closest_x)**2 + (pos[1] - closest_y)**2
                            
                            if dist_sq < 10000: 
                                if not pillar_hit_this_cycle[i]:
                                    if v % 60 == 0: 
                                        pillars_hp[i] -= 1; pillar_hit_this_cycle[i] = True
                                blocked = True; break 
                
                if not blocked and not cheat_mode: game_state["lives"] -= 0.01
            else: boss_state = "COOLDOWN"

    # LEVEL 2
    elif game_state["level"] == 2:
        if t - red_light_timer > 3.0: 
            red_light_status = "RED" if red_light_status == "GREEN" else "GREEN"; red_light_timer = t
        
        dist_to_goal = math.hypot(titan_pos[0] - WEAPON_PICKUP_POS[0], titan_pos[1] - WEAPON_PICKUP_POS[1])
        if dist_to_goal < 80: 
            game_state["level"] = 3
            boss_timer = t
            titan_pos = [0, 0, 0] 

    # LEVEL 1
    elif game_state["level"] == 1:
        for z in zombies:
            dx, dy = titan_pos[0]-z["pos"][0], titan_pos[1]-z["pos"][1]; dist = math.hypot(dx, dy)
            if dist > 5: z["pos"][0] += (dx/dist)*2.0; z["pos"][1] += (dy/dist)*2.0
            if dist < 45 and not cheat_mode: 
                game_state["lives"] -= 1; z["pos"] = [random.uniform(-ARENA_HALF, ARENA_HALF), ARENA_HALF, 0]
        if game_state["zombie_kills"] >= 5: 
            game_state["level"] = 2; titan_pos = [0, -ARENA_HALF + 100, 0] 

    # BULLETS
    if cheat_mode and v % 10 == 0:
        rad = math.radians(titan_yaw[0])
        bullets.append({"pos": [titan_pos[0], titan_pos[1], 100], "dx": 40*math.cos(rad), "dy": 40*math.sin(rad)})
    
    nb = []
    for b in bullets:
        b["pos"][0] += b["dx"]
        b["pos"][1] += b["dy"]
        h = False
        
        if game_state["level"] == 1:
            for z in zombies:
                if math.hypot(b["pos"][0]-z["pos"][0], b["pos"][1]-z["pos"][1]) < 50:
                    game_state["score"] += 10 # [NEW] Points for zombie
                    game_state["zombie_kills"] += 1; z["pos"] = [random.uniform(-ARENA_HALF, ARENA_HALF), ARENA_HALF, 0]; h = True; break
        elif game_state["level"] == 3 and boss_state == "COOLDOWN" and not game_state["won"]:
            # [FIX] EASIER HIT DETECTION (Radius 300)
            if math.hypot(b["pos"][0]-0, b["pos"][1]-(ARENA_HALF-150)) < 300: 
                boss_health -= 1; h = True; game_state["score"] += 50 # [NEW] Points for Boss
                print(f"BOSS HIT! HP: {boss_health}")
        
        if not h and abs(b["pos"][0]) < ARENA_HALF + 500 and abs(b["pos"][1]) < ARENA_HALF + 500: 
            nb.append(b)
    bullets = nb

    if game_state["lives"] <= 0: game_state["game_over"] = True
    if boss_health <= 0: game_state["won"] = True

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); glLoadIdentity()
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(120, 1.25, 1, 8000); glMatrixMode(GL_MODELVIEW)
    
    yw = math.radians(titan_yaw[0])
    if first_person[0]: 
        gluLookAt(titan_pos[0], titan_pos[1], 200, titan_pos[0]+500*math.cos(yw), titan_pos[1]+500*math.sin(yw), 150, 0,0,1)
    else: 
        gluLookAt(titan_pos[0]-700*math.cos(yw), titan_pos[1]-700*math.sin(yw), camHeight, titan_pos[0], titan_pos[1], 100, 0,0,1)
    
    drawArena(door_open=(game_state["won"])); drawPillars(pillars_hp)

    if not first_person[0]: drawTitan(titan_pos[0], titan_pos[1], 0, titan_yaw[0], is_boss=False)

    if game_state["level"] == 2: 
        drawTitan(0, 0, 0, 270, is_boss=False)
        drawWeaponPickup()

    if game_state["level"] == 1:
        for z in zombies: drawZombie(z["pos"][0], z["pos"][1], 0, anim_phase*0.1)
    
    elif game_state["level"] == 3 and not game_state["won"]:
        boss_y = ARENA_HALF - 150
        if boss_state == "ATTACK":
            drawTitan(0, boss_y, 0, 270, is_boss=True, attacking=True)
            glLineWidth(5.0); glBegin(GL_LINES); glColor3f(1, 0, 0)
            glVertex3f(0, boss_y - 40, 140); glVertex3f(titan_pos[0], titan_pos[1], 80); glEnd(); glLineWidth(1.0)
        else: 
            drawTitan(0, boss_y, 0, 270, is_boss=True)

    glColor3f(1, 1, 0)
    for b in bullets: glPushMatrix(); glTranslatef(b["pos"][0], b["pos"][1], b["pos"][2]); glutSolidCube(15); glPopMatrix()

    # [NEW] UI OVERLAY
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity(); glColor3f(1, 1, 1)
    
    # Title & Score
    draw_text(420, 770, "TITAN'S ARENA") # [NEW] Title
    draw_text(20, 760, f"LEVEL: {game_state['level']}")
    draw_text(20, 730, f"LIVES: {int(game_state['lives'])}")
    draw_text(20, 700, f"SCORE: {int(game_state['score'])}") # [NEW] Score
    
    # health bar
    if game_state["level"] == 3 and not game_state["won"]:
        glColor3f(1, 0, 0)
        draw_text(800, 760, "TITAN HEALTH")
        # Draw health bar
        glBegin(GL_QUADS)
        glVertex2f(800, 730); glVertex2f(800 + (boss_health * 30), 730)
        glVertex2f(800 + (boss_health * 30), 750); glVertex2f(800, 750)
        glEnd()
        glColor3f(1, 1, 1) 

    if cheat_mode: glColor3f(1, 1, 0); draw_text(850, 760, "CHEAT: ON"); glColor3f(1,1,1)
    if game_state["game_over"]: glColor3f(1, 0, 0); draw_text(420, 400, "GAME OVER! PRESS 'R' TO RESTART")
    if game_state["won"] and not game_state["exited"]: glColor3f(0, 1, 0); draw_text(480, 450, "Win"); draw_text(350, 400, "PRESS 'F' TO EXIT OR 'R' TO RESTART")
    if game_state["exited"]: glColor3f(1, 1, 0); draw_text(380, 400, "YOU SURVIVED! PRESS 'R' TO RESTART")
    glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()
    glutSwapBuffers()

def keyboard(key, x, y):
    global titan_pos, titan_yaw, first_person, bullets, game_state, cheat_mode
    if key == b'r' or key == b'R': reset_game(); return
    if game_state["game_over"] or game_state["exited"]: return
    if game_state["won"] and key == b'f': game_state["exited"] = True; return
    if key == b'c' or key == b'C': cheat_mode = not cheat_mode; return

    if game_state["level"] == 2 and red_light_status == "RED" and key in [b'w', b's', b'a', b'd']:
        game_state["lives"] -= 1; titan_pos = [0, -ARENA_HALF + 200, 0]; return

    r = math.radians(titan_yaw[0])
    if key == b'w': titan_pos[0]+=20*math.cos(r); titan_pos[1]+=20*math.sin(r)
    elif key == b's': titan_pos[0]-=20*math.cos(r); titan_pos[1]-=20*math.sin(r)
    elif key == b'a': titan_pos[0]+=20*math.cos(r+math.pi/2); titan_pos[1]+=20*math.sin(r+math.pi/2)
    elif key == b'd': titan_pos[0]-=20*math.cos(r+math.pi/2); titan_pos[1]-=20*math.sin(r+math.pi/2)
    elif key == b'q': titan_yaw[0] += 5
    elif key == b'e': titan_yaw[0] -= 5
    elif key == b'v': first_person[0] = not first_person[0]
    
    elif key == b' ': 
        rad = math.radians(titan_yaw[0])
        bullets.append({"pos": [titan_pos[0], titan_pos[1], 100], "dx": 40*math.cos(rad), "dy": 40*math.sin(rad)})

    limit = ARENA_HALF - 50 
    if titan_pos[0] > limit: titan_pos[0] = limit
    if titan_pos[0] < -limit: titan_pos[0] = -limit
    if titan_pos[1] > limit: titan_pos[1] = limit
    if titan_pos[1] < -limit: titan_pos[1] = -limit

def specialKeys(key, x, y):
    global camHeight, titan_yaw
    if key == GLUT_KEY_UP: camHeight += 20
    elif key == GLUT_KEY_DOWN: camHeight -= 20
    elif key == GLUT_KEY_LEFT: titan_yaw[0] += 5
    elif key == GLUT_KEY_RIGHT: titan_yaw[0] -= 5
    glutPostRedisplay()

def mouse(button, state, x, y):
    global bullets, titan_pos
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rad = math.radians(titan_yaw[0])
        bullets.append({"pos": [titan_pos[0], titan_pos[1], 100], "dx": 40*math.cos(rad), "dy": 40*math.sin(rad)})
    glutPostRedisplay()

def main():
    glutInit(); glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH); glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Titan Arena"); glEnable(GL_DEPTH_TEST); reset_game()
    glutDisplayFunc(display); glutTimerFunc(0, update, 0); glutKeyboardFunc(keyboard)
    glutSpecialFunc(specialKeys); glutMouseFunc(mouse); glutMainLoop()

if __name__ == "__main__": main()
