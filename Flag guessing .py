#!/usr/bin/env python3
"""
Draw country flags with the Python Turtle.

Have fun!

Peace, coolcornucopia.
https://github.com/coolcornucopia/
"""
#
# Python ressources:
#   https://docs.python.org/3/library/turtle.html
#
# Wikipedia ressources:
#   https://en.wikipedia.org/wiki/List_of_aspect_ratios_of_national_flags
#   https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes


from turtle import Turtle, Screen, mainloop
import math
import locale
import unicodedata # Use to sort strings with accents, see strip_accents()
import time
import random
import pycountry


### CONFIGURATION ###

fast_draw = True

FLAG_BORDER_COL = 'black'
FLAG_DEFAULT_RATIO = 2/3  # preferred flag ratio size between width & height

FULLSCREEN = True

DEBUG = False
#DEBUG = True


### GLOBAL VARIABLES ###

# This is our "current turtle (ct)"
ct = Turtle()

# TODO (resolution, default white background)
screen = Screen()
if FULLSCREEN:
    screen.setup(width = 1.0, height = 1.0)


### DRAWING PRIMITIVES ###

# Useful fonction to move the pen and reset the turtle orientation
def prepare_drawing(x, y, rotation=0):
    ct.penup()
    ct.goto(x, y)
    # The orientation is set by default to the right.
    # In standard mode: 0=east 90=north 180=west 270=south
    # In logo mode: 0=north 90=east 180=south 270=west
    # Here we are in the standard mode
    # rotation parameter is then counter-clockwise
    ct.setheading(rotation)
    ct.pendown()

def rectangle(x, y, width, height):
    prepare_drawing(x, y)
    # Note: we may use a loop but it does not bring that much
    ct.forward(width)
    ct.right(90)
    ct.forward(height)
    ct.right(90)
    ct.forward(width)
    ct.right(90)
    ct.forward(height)

def rectangle_filled(x, y, width, height):
    ct.begin_fill()
    rectangle(x, y, width, height)
    ct.end_fill()

def square(x, y, width):
    rectangle(x, y, width, width)

def square_filled(x, y, width):
    rectangle_filled(x, y, width, width)

# For the circle, use the diameter instead of the radius because it is
# then easier to make objects touch themselves, avoiding x2 in user code.
def circle(center_x, center_y, diameter):
    # Move the circle center following Turtle circle() usage
    prepare_drawing(center_x, center_y - diameter / 2)
    ct.circle(diameter / 2)

def circle_filled(center_x, center_y, diameter):
    ct.begin_fill()
    circle(center_x, center_y, diameter)
    ct.end_fill()

# The cross is inside a "width" diameter circle
def cross(center_x, center_y, width):
    # Move on the cross left then draw
    prepare_drawing(center_x - (width / 2), center_y)
    ct.forward(width)
    # Move on the cross top then draw
    prepare_drawing(center_x, center_y + (width / 2))
    ct.right(90)
    ct.forward(width)


# This five pointed star function draws a star "standing with arms open
# horizontally" and a span of "width" and returns the coordinates and sizes
# of the surrounding rectangle, it is then easier to align the star with
# other shapes. The drawing algorithm has been adapted from
# https://stackoverflow.com/questions/26356543/turtle-graphics-draw-a-star
# TODO better document rotation (clockwise here)
def five_pointed_star(center_x, center_y, width, rotation=0):
    # https://rechneronline.de/pi/pentagon.php
    # d = width
    # a = pentagon side = 0,618 * d
    # h = height = 0,951 * d
    # ri = radius of the inscribed circle = 0,425 * d
    # rc = radius of the circumscribed circle = 0,526 * d
    d = width
    h = 0.951 * d
    rc = 0.526 * d

    # Default: angle = 144 for a straight star, we may try different
    # values for a more or less pointed star...
    angle = 144
    branch = d / 2.6
    prepare_drawing(center_x + d / 2 - branch, center_y + d / 6, rotation)

    for _ in range(5):
        ct.forward(branch)
        ct.right(angle)
        ct.forward(branch)
        ct.right((360 / 5) - angle)

    # Surrounding rectangle, uncomment to test
    # rectangle(center_x - d / 2, center_y + rc, d, h)
    # Circumscribed circle, uncomment to test
    # circle(center_x, center_y, rc * 2)

    # Return surrounding rectangle coordinates and sizes.
    return center_x - d / 2, center_y + rc, d, h

# (read five_pointed_star() above function description for details)
def five_pointed_star_filled(center_x, center_y, width, rotation=0):
    ct.begin_fill()
    x, y, w, h = five_pointed_star(center_x, center_y, width, rotation)
    ct.end_fill()
    return x, y, w, h

def polygon(poly):
    ct.penup()
    for x, y in poly:
        ct.goto(x, y)
        if not ct.isdown():
            ct.pendown()
    ct.goto(tuple(poly[0])) # close the polygon

def polygon_filled(poly):
    ct.begin_fill()
    polygon(poly)
    ct.end_fill()


### HELPER FUNCTIONS FOR FLAGS DRAWING ###

# TODO better document below functions
def vertical_strips(x, y, width, height, *colors):
    nc = len(colors)
    if nc <= 0:
        # TODO Better manage error here below
        print(func_name + ": Bad color value")
        return
    w = width / nc  # TODO round?
    for i in range(nc):
        ct.color(colors[i])
        rectangle_filled(x + i * w, y, w, height)

def horizontal_strips(x, y, width, height, *colors):
    nc = len(colors)
    if nc <= 0:
        # TODO Better manage error here below
        print(func_name + ": Bad color value")
        return
    h = height / nc  # TODO round?
    for i in range(nc):
        ct.color(colors[i])
        rectangle_filled(x, y - i * h, width, h)

# TODO Document parameters
def rectangle_circle(x, y, width, height,
                     circ_center_x_r, circ_center_y_r,
                     circ_diam_r, background_col, circ_col):
    ct.color(background_col)
    rectangle_filled(x, y, width, height)
    ct.color(circ_col)
    circ_center_x = x + width * circ_center_x_r
    circ_center_y = y - height * circ_center_y_r
    diameter = width * circ_diam_r
    circle_filled(circ_center_x, circ_center_y, diameter)

# TODO Document parameters
def cross_filled(x, y, width, height,
                 cross_center_x_r, cross_center_y_r,
                 cross_width_r, cross_height_r, col):
    ct.color(col)
    w = width * cross_width_r
    h = height * cross_height_r
    x1 = x + width * cross_center_x_r - (w / 2)
    y1 = y - height * cross_center_y_r + (h / 2)
    rectangle_filled(x1, y, w, height)
    rectangle_filled(x, y1, width, h)

def rectangle_filled_color(x, y, width, height, color):
    ct.color(color)
    rectangle_filled(x, y, width, height)

def circle_filled_color(center_x, center_y, diameter, color):
    ct.color(color)
    circle_filled(center_x, center_y, diameter)

def five_pointed_star_filled_color(center_x, center_y, width, color, rotation=0):
    ct.color(color)
    five_pointed_star_filled(center_x, center_y, width, rotation)

def polygon_filled_color(poly, color):
    ct.color(color)
    polygon_filled(poly)

def circle_coord(center_x, center_y, radius, angle_pc):
    angle_rad = (2 * math.pi) * angle_pc
    x = center_x + radius * math.cos(angle_rad)
    y = center_y + radius * math.sin(angle_rad)
    return x, y


### COUNTRY FLAG DRAWING FUNCTIONS ###

# Note Following functions do not take into account directly the
# aspect ratio and the border, so you can use them directly
# depending of your need... or via the class with proper aspect ratio :-)
def flag_Armenia(x, y, width, height):
    horizontal_strips(x, y, width, height, '#D90012', '#0033A0', '#F2A800')

def flag_Austria(x, y, width, height):
    horizontal_strips(x, y, width, height, '#ED2939', 'white', '#ED2939')

def flag_Bahamas(x, y, width, height):
    horizontal_strips(x, y, width, height, '#00778B', '#FFC72C', '#00778B')
    polygon_filled_color(((x, y), (x + width/2.3, y - height/2),
                          (x, y - height)), 'black')

def flag_Bahrain(x, y, width, height):
    rectangle_filled_color(x, y, width/4, height, 'white')
    rectangle_filled_color(x+width/4, y, 3*width/4, height, '#F21731')
    polygon_filled_color(((x + width/4, y), (x + 2*width/5, y - height/10),
                          (x + width/4, y - height/5)), 'white')
    polygon_filled_color(((x + width/4, y-height/5), (x + 2*width/5, y - 3*height/10),
                          (x + width/4, y - 2*height/5)), 'white')
    polygon_filled_color(((x + width/4, y-2*height/5), (x + 2*width/5, y - height/2),
                          (x + width/4, y - 3*height/5)), 'white')
    polygon_filled_color(((x + width/4, y-3*height/5), (x + 2*width/5, y - 7*height/10),
                          (x + width/4, y - 4*height/5)), 'white')
    polygon_filled_color(((x + width/4, y-4*height/5), (x + 2*width/5, y - 9*height/10),
                          (x + width/4, y - height)), 'white')

def flag_Bangladesh(x, y, width, height):
    rectangle_circle(x, y, width, height, 45/100, 1/2, 2/5,
                     '#006a4e', '#f42a41')

def flag_Belgium(x, y, width, height):
    vertical_strips(x, y, width, height, 'black', '#FAE042', '#ED2939')

def flag_Benin(x, y, width, height):
    horizontal_strips(x, y, width, height, '#FCD116', '#E8112D')
    rectangle_filled_color(x, y, width / 2.5, height, '#008751')

def flag_Bolivia(x, y, width, height):
    horizontal_strips(x, y, width, height, '#D52B1E', '#F9E300', '#007934')
    # TODO Please finalize me

def flag_Botswana(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#6DA9D2')
    rectangle_filled_color(x, y - height * 3/8, width, height/4, 'white')
    rectangle_filled_color(x, y - height/2.4, width, height/6, 'black')

def flag_Bulgaria(x, y, width, height):
    horizontal_strips(x, y, width, height, 'white', '#00966E', '#D62612')

def flag_Burkina_Faso(x, y, width, height):
    horizontal_strips(x, y, width, height, '#EF2B2D', '#009E49')
    five_pointed_star_filled_color(x + width/2, y - height/2, 2*width/9, '#FCD116')

def flag_Cameroon(x, y, width, height):
    vertical_strips(x, y, width, height, '#007A5E', '#CE1126', '#FCD116')
    five_pointed_star_filled_color(x + width/2, y - height/2, width/6, '#FCD116')

def flag_Chile(x, y, width, height):
    horizontal_strips(x, y, width, height, 'white', '#d52b1e')
    rectangle_filled_color(x, y, width/3, height/2, '#0039a6')
    five_pointed_star_filled_color(x + width/6, y - height/4, width/6, 'white')

def flag_China(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#DE2910')
    bsw = width * 19 / 100 # big star width
    ssw = bsw / 3          # small star width
    ct.color('#FFDE00')
    five_pointed_star_filled(x + width * 1/6, y - height * 1/4, bsw)
    five_pointed_star_filled(x + width * 1/3, y - height * 1/10, ssw, 360-23)
    five_pointed_star_filled(x + width * 2/5, y - height * 1/5, ssw, 360-46)
    five_pointed_star_filled(x + width * 2/5, y - height * 7/20, ssw, 360-70)
    five_pointed_star_filled(x + width * 1/3, y - height * 9/20, ssw, 360-21)
    
def flag_Colombia(x, y, width, height):
    rectangle_filled_color(x, y, width, height/2, '#FCD116')
    rectangle_filled_color(x, y-height/2, width, height/4, '#003893')
    rectangle_filled_color(x, y-3*height/4, width, height/4, '#CE1126')

def flag_Costa_Rica(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#001489')
    rectangle_filled_color(x, y - height/6, width, 2*height/3, 'white')
    rectangle_filled_color(x, y - height/3, width, height/3, '#DA291C')

def flag_Cuba(x, y, width, height):
    horizontal_strips(x, y, width, height, '#002590', 'white', '#002590', 'white', '#002590')
    polygon_filled_color(((x, y), (x + ((3)**(1/2))*width/4, y - height/2), (x, y - height)), '#CC0D0D')
    five_pointed_star_filled_color(x + (0.57735)*width/4, y - height/2, width/6, 'white')

def flag_Czechia(x, y, width, height):
    horizontal_strips(x, y, width, height, 'white', '#D7141A')
    polygon_filled_color(((x, y), (x + width/2, y - height/2), (x, y - height)), '#11457E')

def flag_Denmark(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#C8102E')
    cross_filled(x, y, width, height, 0.36, 1/2, 16/100, 2/9, 'white')

def flag_Estonia(x, y, width, height):
    horizontal_strips(x, y, width, height, '#0072ce', 'black', 'white')

def flag_Finland(x, y, width, height):
    rectangle_filled_color(x, y, width, height, 'white')
    cross_filled(x, y, width, height, 65/180, 1/2, 1/6, 3/11, '#003580')

def flag_France(x, y, width, height):
    vertical_strips(x, y, width, height, '#002654', 'white', '#ED2939')

def flag_Gabon(x, y, width, height):
    horizontal_strips(x, y, width, height, '#009e60', '#fcd116', '#3a75c4')

def flag_Gambia(x, y, width, height):
    horizontal_strips(x, y, width, height, '#CE1126', 'white', '#3A7728')
    rectangle_filled_color(x, y - height/2.57, width, height/4.5, '#0C1C8C')

def flag_Germany(x, y, width, height):
    horizontal_strips(x, y, width, height, '#000', '#D00', '#FFCE00')

def flag_Greece(x, y, width, height):
    b = '#0D5EAF'
    w = 'white'
    horizontal_strips(x, y, width, height, *([b, w] * 4 + [b]))
    rectangle_filled_color(x, y, width * 0.37, height * 5/9 - 1, b)
    cross_filled(x, y, width * 0.37, height * 5/9 - 1, 1/2, 1/2,
                 1/13.5/0.37, 1/9/(5/9), w)

def flag_Guinea(x, y, width, height):
    vertical_strips(x, y, width, height, '#CE1126', '#FCD116', '#009460')

def flag_Guinea_Bissau(x, y, width, height):
    horizontal_strips(x, y, width, height, '#FCD116', '#009E49')
    rectangle_filled_color(x, y, width/3, height, '#CE1126')
    five_pointed_star_filled_color(x + width/6, y - height/2, width/6, 'black')

def flag_Hungary(x, y, width, height):
    horizontal_strips(x, y, width, height, '#CE2939', '#FFFFFF', '#477050')

def flag_Iceland(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#02529C')
    cross_filled(x, y, width, height, 0.36, 1/2, 16/100, 2/9, 'white')
    cross_filled(x, y, width, height, 0.36, 1/2, 8/100, 1/9, '#DC1E35')

def flag_India(x, y, width, height):
    horizontal_strips(x, y, width, height, '#F93', 'white', '#128807')
    # Draw the Ashoka Chakra (wheel of 24 spokes & half-circles)
    cx = x + width / 2
    cy = y - height / 2
    circle_filled_color(cx, cy, width * 17.8/100, '#008')
    circle_filled_color(cx, cy, width * 15.6/100, 'white')
    circle_filled_color(cx, cy, width * 3.1/100, '#008')
    # Radius of circles linked to the polygon spokes
    radius_internal = width * 12/1350
    radius_middle = width * 42.15/1350
    radius_external = width * 105/1350
    angle_spoke = 4.9 / 360 # 4.9 degrees
    for i in [x/24 for x in range(24)]:  # 0/24, 1/24, 2/24...
        ### The polygon spoke
        ct.color('#008')
        ct.penup()
        ct.goto(circle_coord(cx, cy, radius_internal, i))
        ct.pendown()
        ct.begin_fill()
        ct.goto(circle_coord(cx, cy, radius_middle, i - angle_spoke))
        ct.goto(circle_coord(cx, cy, radius_external, i))
        ct.goto(circle_coord(cx, cy, radius_middle, i + angle_spoke))
        ct.goto(circle_coord(cx, cy, radius_internal, i))
        ct.end_fill()
        # The circle
        xx, yy = circle_coord(cx, cy, radius_external, i + 0.5/24)
        circle_filled_color(xx, yy, width * 10.5/1350, '#008')

def flag_Indonesia(x, y, width, height):
    horizontal_strips(x, y, width, height, 'red', 'white')

def flag_Ireland(x, y, width, height):
    vertical_strips(x, y, width, height, '#169B62', 'white', '#FF883E')

def flag_Italy(x, y, width, height):
    vertical_strips(x, y, width, height, '#008C45', '#F4F5F0', '#CD212A')

def flag_Ivory_Coast(x, y, width, height):
    vertical_strips(x, y, width, height, '#f77f00', 'white', '#009e60')
    
def flag_Lithuania(x, y, width, height):
    horizontal_strips(x, y, width, height, '#FDB913', '#006A44', '#C1282D')
    
def flag_Luxembourg(x, y, width, height):
    horizontal_strips(x, y, width, height, '#EF3340', 'white', '#00A3E0')

def flag_Madagascar(x, y, width, height):
    horizontal_strips(x, y, width, height, '#F9423A', '#00843D')
    rectangle_filled_color(x, y, width/3, height, 'white')

def flag_Japan(x, y, width, height):
    rectangle_circle(x, y, width, height, 1/2, 1/2, 2/5,
                     'white', '#bc002d')

def flag_Kuwait(x, y, width, height):
    horizontal_strips(x, y, width, height, '#007A3D', 'white', '#CE1126')
    polygon_filled_color(((x,y), (x + width/4, y - height/3), (x + width/4, y - 2*height/3), (x, y - height)), 'black')

def flag_Mali(x, y, width, height):
    vertical_strips(x, y, width, height, '#14B53A', '#FCD116', '#CE1126')

def flag_Myanmar(x, y, width, height):
    horizontal_strips(x, y, width, height, '#FECB00', '#34B233', '#EA2839')
    h = 2 * height / 3
    d = h / 0.951  # See five_pointed_star_filled() computations
    five_pointed_star_filled_color(x + width / 2, y - height / 1.9, d, 'white')

def flag_Netherlands(x, y, width, height):
    horizontal_strips(x, y, width, height, '#A91F32', 'white', '#1E4785')

def flag_Nigeria(x, y, width, height):
    vertical_strips(x, y, width, height, '#008753', 'white', '#008753')

def flag_Pakistan(x, y, width, height):
    rectangle_filled_color(x, y, width * 1/4, height, 'white')
    rectangle_circle(x + width * 1/4, y, width * 3/4, height, 0.5, 0.5, 360/675, '#01411C', 'white')
    circle_filled_color(x + width * 608/900, y - height * 259/600, width * 330/900, '#01411C')
    ct.color('white')
    five_pointed_star_filled(x + width * 652/900, y - height * 216/600, width * 114/900, 23)

def flag_Peru(x, y , width, height):
    vertical_strips(x ,y , width, height, '#D91023', 'white', '#D91023')

def flag_Poland(x, y, width, height):
    horizontal_strips(x, y, width, height, 'white', '#DC143C')

def flag_Romania(x, y, width, height):
    vertical_strips(x, y, width, height, '#002B7F', '#FCD116', '#CE1126')

def flag_Russia(x, y, width, height):
    horizontal_strips(x, y, width, height, 'white', '#0039A6', '#D52B1E')

def flag_Senegal(x, y, width, height):
    vertical_strips(x, y, width, height, '#00853F', '#FDEF42', '#E31B23')
    five_pointed_star_filled_color(x + width/2, y - height/2, width/6, '#00853F')

def flag_Seychelles(x, y, width, height):
    bl = (x, y - height) # bottom left
    xw = x + width
    w = width / 3
    h = height / 3
    polygon_filled_color((bl, (x, y), (x + w, y)), '#003F87')
    polygon_filled_color((bl, (x + w, y), (x + w * 2, y)), '#FCD856')
    polygon_filled_color((bl, (x + w * 2, y), (xw, y), (xw, y - h)), '#D62828')
    polygon_filled_color((bl, (xw, y - h), (xw, y - h * 2)), 'white')
    polygon_filled_color((bl, (xw, y - h * 2), (xw, y - height)), '#007a3d')
    
def flag_Sierra_Leone(x,y, width, height):
    horizontal_strips(x, y, width, height, '#1EB53A', 'white', '#0072C6')

def flag_Somalia(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#4189DD')
    five_pointed_star_filled_color(x + width/2, y - height/2, width/3.28, 'white')

def flag_Sudan(x, y, width, height):
    horizontal_strips(x, y, width, height, '#D21034', 'white', 'black')
    polygon_filled_color(((x, y),(x + width/3, y - height/2), (x, y - height)), '#007229')

def flag_Sweden(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#006AA7')
    cross_filled(x, y, width, height, 3/8, 1/2, 1/8, 1/5, '#FECC00')

def flag_Thailand(x, y, width, height):
    rectangle_filled_color(x, y, width, height, '#EF3340')
    rectangle_filled_color(x, y - height/6, width, 2*height/3, 'white')
    rectangle_filled_color(x, y - height/3, width, height/3, '#00247D')

def flag_Ukraine(x, y, width, height):
    horizontal_strips(x, y, width, height, '#0057b7', '#ffd700')

def flag_United_Arab_Emirates(x, y, width, height):
    horizontal_strips(x, y, width, height, '#00843D', 'white', 'black')
    rectangle_filled_color(x, y, width/4, height, '#FF0000')

def flag_United_States(x, y, width, height):
    # 7 Red & 6 white strips
    r = '#B22234'
    w = 'white'
    horizontal_strips(x, y, width, height, *([r, w] * 6 + [r])) # r,w,r,w...,r
    # The blue rectangle
    # Note - 1 in y-axis for a better alignment
    rectangle_filled_color(x, y, width / 2.5, 7 * height / 13 - 1, '#3C3B6E')
    # The white stars
    ct.color('white')
    #ct.color('#717095', 'white') # false antialiasing if big flag
    star_width = width / 32.5
    star_height = height / 18.6
    star_width_between = width / 15
    star_y = y - star_height
    stars_in_row = 5
    for _ in range(9):                 # vertical loop
        if stars_in_row == 6:          # switch between 5 & 6 row stars
            stars_in_row = 5
            star_x = x + star_width_between
        else:
            stars_in_row = 6
            star_x = x + (star_width_between / 2)
        for _ in range(stars_in_row):  # horizontal loop
            five_pointed_star_filled(star_x, star_y, star_width)
            star_x += star_width_between
        star_y -= star_height

def flag_Yemen(x, y, width, height):
    horizontal_strips(x, y, width, height, '#CE1126', 'white', 'black')


### FLAGS MANAGEMENT FUNCTIONS ###

class Flag(object):
    def __init__(self, country_code, ratio, drawing_func):
        self.country_code = country_code
        self.ratio = ratio
        self.drawing_func = drawing_func

    def draw(self, x, y, width, height):
        self.drawing_func(x, y, width, height)

    def draw_ratio(self, x, y, width):
        self.drawing_func(x, y, width, width * self.ratio)

# Dictionnary of all the flags (the key is the flag drawing function)
flags_dict = dict()
flags_dict[flag_Armenia]       = Flag( '051',  1/2 , flag_Armenia)
flags_dict[flag_Austria]       = Flag( '040',  2/3 , flag_Austria)
flags_dict[flag_Bahamas]       = Flag( '044',  1/2 , flag_Bahamas)
flags_dict[flag_Bahrain]       = Flag( '048',  3/5 , flag_Bahrain)
flags_dict[flag_Bangladesh]    = Flag( '050',  3/5 , flag_Bangladesh)
flags_dict[flag_Belgium]       = Flag( '056', 13/15, flag_Belgium)
flags_dict[flag_Benin]         = Flag('204',  2/3 , flag_Benin)
flags_dict[flag_Bolivia]       = Flag( '068', 15/22, flag_Bolivia)
flags_dict[flag_Botswana]      = Flag( '072',  2/3 , flag_Botswana)
flags_dict[flag_Bulgaria]      = Flag('100',  3/5 , flag_Bulgaria)
flags_dict[flag_Burkina_Faso]      = Flag('854',  2/3 , flag_Burkina_Faso)
flags_dict[flag_Cameroon]      = Flag('120',  2/3 , flag_Cameroon)
flags_dict[flag_Chile]         = Flag('152',  2/3 , flag_Chile)
flags_dict[flag_China]         = Flag('156',  2/3 , flag_China)
flags_dict[flag_Colombia]      = Flag('170', 2/3, flag_Colombia)
flags_dict[flag_Costa_Rica]      = Flag('188', 3/5, flag_Costa_Rica)
flags_dict[flag_Cuba]      = Flag('192', 1/2, flag_Cuba)
flags_dict[flag_Czechia]      = Flag('203', 2/3, flag_Czechia)
flags_dict[flag_Denmark]      = Flag('208', 26/34, flag_Denmark)
flags_dict[flag_Estonia]       = Flag('233',  7/11, flag_Estonia)
flags_dict[flag_Finland]       = Flag('246', 11/18, flag_Finland)
flags_dict[flag_France]        = Flag('250',  2/3 , flag_France)
flags_dict[flag_Gabon]         = Flag('266',  3/4 , flag_Gabon)
flags_dict[flag_Gambia]        = Flag('270',  2/3 , flag_Gambia)
flags_dict[flag_Germany]       = Flag('276',  3/5 , flag_Germany)
flags_dict[flag_Greece]        = Flag('300',  2/3 , flag_Greece)
flags_dict[flag_Guinea]        = Flag('324',  2/3 , flag_Guinea)
flags_dict[flag_Guinea_Bissau] = Flag('624', 1/2, flag_Guinea_Bissau)
flags_dict[flag_Hungary]       = Flag('348', 2/3, flag_Hungary)
flags_dict[flag_Iceland]       = Flag('352', 18/25, flag_Iceland)
flags_dict[flag_India]         = Flag('356',  2/3 , flag_India)
flags_dict[flag_Indonesia]     = Flag('360',  2/3 , flag_Indonesia)
flags_dict[flag_Ireland]     = Flag('372',  1/2 , flag_Ireland)
flags_dict[flag_Italy]     = Flag('380',  2/3 , flag_Italy)
flags_dict[flag_Ivory_Coast]   = Flag('384',  2/3 , flag_Ivory_Coast)
flags_dict[flag_Japan]         = Flag('392',  2/3 , flag_Japan)
flags_dict[flag_Kuwait]         = Flag('414',  1/2 , flag_Kuwait)
flags_dict[flag_Lithuania]    = Flag('440', 3/5, flag_Lithuania)
flags_dict[flag_Luxembourg]    = Flag('442', 3/5, flag_Luxembourg)
flags_dict[flag_Madagascar]    = Flag('450', 2/3, flag_Madagascar)
flags_dict[flag_Mali]       = Flag('466',  2/3 , flag_Mali)
flags_dict[flag_Myanmar]       = Flag('104',  2/3 , flag_Myanmar)
flags_dict[flag_Netherlands]       = Flag('528',  2/3 , flag_Netherlands)
flags_dict[flag_Nigeria]       = Flag('566',  1/2 , flag_Nigeria)
flags_dict[flag_Pakistan]      = Flag('586',  2/3 , flag_Pakistan)
flags_dict[flag_Peru]        = Flag('604',  2/3 , flag_Peru)
flags_dict[flag_Poland]        = Flag('616',  5/8 , flag_Poland)
flags_dict[flag_Romania]        = Flag('642',  2/3 , flag_Romania)
flags_dict[flag_Russia]        = Flag('643',  2/3 , flag_Russia)
flags_dict[flag_Senegal]      = Flag('686',  2/3 , flag_Senegal)
flags_dict[flag_Seychelles]    = Flag('690',  1/2 , flag_Seychelles)
flags_dict[flag_Sierra_Leone]       = Flag('694',  2/3 , flag_Sierra_Leone)
flags_dict[flag_Somalia]       = Flag('706',  2/3 , flag_Somalia)
flags_dict[flag_Sudan]        = Flag('729',  1/2 , flag_Sudan)
flags_dict[flag_Sweden]        = Flag('752',  5/8 , flag_Sweden)
flags_dict[flag_Thailand]        = Flag('764',  2/3 , flag_Thailand)
flags_dict[flag_Ukraine] = Flag('804', 2/3, flag_Ukraine)
flags_dict[flag_United_Arab_Emirates] = Flag('784', 1/2, flag_United_Arab_Emirates)
flags_dict[flag_United_States] = Flag('840', 10/19, flag_United_States)
flags_dict[flag_Yemen]       = Flag('887',  2/3 , flag_Yemen)


# Function to remove accents, useful for sorting, else "États-Unis" (fr)
# will be the last of the sorting list in French
# https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string/518232#518232
def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

# Sort the flags dictionnary by country code
sorted(flags_dict.items(), key=lambda x: x[1].country_code)

def game():
    points = 0
    score = -1
    flags_dict = dict()
    flags_dict[flag_Armenia]       = Flag( '051',  1/2 , flag_Armenia)
    flags_dict[flag_Austria]       = Flag( '040',  2/3 , flag_Austria)
    flags_dict[flag_Bahamas]       = Flag( '044',  1/2 , flag_Bahamas)
    flags_dict[flag_Bahrain]       = Flag( '048',  3/5 , flag_Bahrain)
    flags_dict[flag_Bangladesh]    = Flag( '050',  3/5 , flag_Bangladesh)
    flags_dict[flag_Belgium]       = Flag( '056', 13/15, flag_Belgium)
    flags_dict[flag_Benin]         = Flag('204',  2/3 , flag_Benin)
    flags_dict[flag_Bolivia]       = Flag( '068', 15/22, flag_Bolivia)
    flags_dict[flag_Botswana]      = Flag( '072',  2/3 , flag_Botswana)
    flags_dict[flag_Bulgaria]      = Flag('100',  3/5 , flag_Bulgaria)
    flags_dict[flag_Burkina_Faso]      = Flag('854',  2/3 , flag_Burkina_Faso)
    flags_dict[flag_Cameroon]      = Flag('120',  2/3 , flag_Cameroon)
    flags_dict[flag_Chile]         = Flag('152',  2/3 , flag_Chile)
    flags_dict[flag_China]         = Flag('156',  2/3 , flag_China)
    flags_dict[flag_Colombia]      = Flag('170', 2/3, flag_Colombia)
    flags_dict[flag_Costa_Rica]      = Flag('188', 3/5, flag_Costa_Rica)
    flags_dict[flag_Cuba]      = Flag('192', 1/2, flag_Cuba)
    flags_dict[flag_Czechia]      = Flag('203', 2/3, flag_Czechia)
    flags_dict[flag_Denmark]      = Flag('208', 26/34, flag_Denmark)
    flags_dict[flag_Estonia]       = Flag('233',  7/11, flag_Estonia)
    flags_dict[flag_Finland]       = Flag('246', 11/18, flag_Finland)
    flags_dict[flag_France]        = Flag('250',  2/3 , flag_France)
    flags_dict[flag_Gabon]         = Flag('266',  3/4 , flag_Gabon)
    flags_dict[flag_Gambia]        = Flag('270',  2/3 , flag_Gambia)
    flags_dict[flag_Germany]       = Flag('276',  3/5 , flag_Germany)
    flags_dict[flag_Greece]        = Flag('300',  2/3 , flag_Greece)
    flags_dict[flag_Guinea]        = Flag('324',  2/3 , flag_Guinea)
    flags_dict[flag_Guinea_Bissau] = Flag('624', 1/2, flag_Guinea_Bissau)
    flags_dict[flag_Hungary]       = Flag('348', 2/3, flag_Hungary)
    flags_dict[flag_Iceland]       = Flag('352', 18/25, flag_Iceland)
    flags_dict[flag_India]         = Flag('356',  2/3 , flag_India)
    flags_dict[flag_Indonesia]     = Flag('360',  2/3 , flag_Indonesia)
    flags_dict[flag_Ireland]     = Flag('372',  1/2 , flag_Ireland)
    flags_dict[flag_Italy]     = Flag('380',  2/3 , flag_Italy)
    flags_dict[flag_Ivory_Coast]   = Flag('384',  2/3 , flag_Ivory_Coast)
    flags_dict[flag_Japan]         = Flag('392',  2/3 , flag_Japan)
    flags_dict[flag_Kuwait]         = Flag('414',  1/2 , flag_Kuwait)
    flags_dict[flag_Lithuania]    = Flag('440', 3/5, flag_Lithuania)
    flags_dict[flag_Luxembourg]    = Flag('442', 3/5, flag_Luxembourg)
    flags_dict[flag_Madagascar]    = Flag('450', 2/3, flag_Madagascar)
    flags_dict[flag_Mali]       = Flag('466',  2/3 , flag_Mali)
    flags_dict[flag_Myanmar]       = Flag('104',  2/3 , flag_Myanmar)
    flags_dict[flag_Netherlands]       = Flag('528',  2/3 , flag_Netherlands)
    flags_dict[flag_Nigeria]       = Flag('566',  1/2 , flag_Nigeria)
    flags_dict[flag_Pakistan]      = Flag('586',  2/3 , flag_Pakistan)
    flags_dict[flag_Peru]        = Flag('604',  2/3 , flag_Peru)
    flags_dict[flag_Poland]        = Flag('616',  5/8 , flag_Poland)
    flags_dict[flag_Romania]        = Flag('642',  2/3 , flag_Romania)
    flags_dict[flag_Russia]        = Flag('643',  2/3 , flag_Russia)
    flags_dict[flag_Senegal]      = Flag('686',  2/3 , flag_Senegal)
    flags_dict[flag_Seychelles]    = Flag('690',  1/2 , flag_Seychelles)
    flags_dict[flag_Sierra_Leone]       = Flag('694',  2/3 , flag_Sierra_Leone)
    flags_dict[flag_Somalia]       = Flag('706',  2/3 , flag_Somalia)
    flags_dict[flag_Sudan]        = Flag('729',  1/2 , flag_Sudan)
    flags_dict[flag_Sweden]        = Flag('752',  5/8 , flag_Sweden)
    flags_dict[flag_Thailand]        = Flag('764',  2/3 , flag_Thailand)
    flags_dict[flag_Ukraine] = Flag('804', 2/3, flag_Ukraine)
    flags_dict[flag_United_Arab_Emirates] = Flag('784', 1/2, flag_United_Arab_Emirates)
    flags_dict[flag_United_States] = Flag('840', 10/19, flag_United_States)
    flags_dict[flag_Yemen]       = Flag('887',  2/3 , flag_Yemen)
    
    while score == -1:
        if len(flags_dict) == 0:
            print("You have achive max score")
            score = points
            print('Your score =', score)
            return "Done"
        b = random.choice(list(flags_dict.keys()))
        flag = flags_dict[b]
        flag_func = flag.drawing_func
        random_flags(flag_func, ratio=True)
        nums = flag.country_code
        country = pycountry.countries.get(numeric=nums)
        goal = country.name.lower()
        if goal == "russian federation":
            goal = 'russia'
        if goal == "côte d'ivoire":
            goal = 'cote d ivoire'
        if goal == 'bolivia, plurinational state of':
            goal = 'bolivia'
        ans = input("Which flag is it?: ")
        ans = ans.lower()
        if ans == goal:
            points += 1
            print('Correct')
            ct.clear()
            del flags_dict[b]
        else:
            score = points
            print("Incorrect")
            print("Correct answer: ", goal)
            print('Your score =', score)
    return "Done"

def random_flags(flag_function_name, ratio=True):
    # Get window size
    win_w = screen.window_width()
    win_h = screen.window_height()
    w = win_w * 90/100 # remove 5% borders
    # Get the flag element and draw it according to its size ratio
    flag = flags_dict[flag_function_name]
    if ratio:
        h = w * flag.ratio
        flag.draw_ratio(-w/2, h/2, w)
    else:
        h = w * FLAG_DEFAULT_RATIO
        flag.draw(-w/2, h/2, w, h)
    # Add a border
    ct.color(FLAG_BORDER_COL)
    rectangle(-w/2, h/2, w, h)

def draw_all_flags(width, border, ratio=False):
    global flags_dict
    # Get window size
    window_width = screen.window_width()
    window_height = screen.window_height()
    #setup(window_width * 1.0, window_height * 1.0)
    #print(screensize(), screen.window_width(), screen.window_height())
    flags_num = len(flags_dict)
    x_start = -(window_width / 2) + border # TODO rename border please
    y_start = (window_height / 2) - border
    flags_horiz_max = int((window_width - 2 * border) / width)
    # TODO rename border_inside
    border_inside = (window_width - (2 * border)) - (flags_horiz_max * width)
    border_inside /= (flags_horiz_max - 1)
    if border_inside < border:
        flags_horiz_max -= 1
        border_inside = (window_width - (2 * border)) - (flags_horiz_max * width)
        border_inside /= (flags_horiz_max - 1)
    x = x_start
    y = y_start
    for i in flags_dict:
        # Get the flag and draw it
        flag = flags_dict[i]
        nums = flag.country_code
        country = pycountry.countries.get(numeric=nums)
        a = country.name
        if ratio:
            h = width * flag.ratio
            flag.draw_ratio(x, y, width)
        else:
            h = width * FLAG_DEFAULT_RATIO
            flag.draw(x, y, width, h)

        # Draw the flag border
        ct.color(FLAG_BORDER_COL) # TODO find a better way for color config
        rectangle(x, y, width, h)

        # Add the flag name
        ct.penup()
        ct.goto(x + width / 2, y)
        if a == 'Bolivia, Plurinational State of':
            a = 'Bolivia'
        if a == 'Russian Federation':
            a = 'Russia'
        if a == "Côte d'Ivoire":
            a = "Cote d Ivoire"
        ct.write(a, align="center", font=("Arial", 11, "normal"))
        
        a = a.lower()
        print(a)
        # Next flag
        x += width + border_inside
        if x > (window_width / 2) - border - width:
            x = x_start
            y -= width * 2/3 + border_inside # TODO 2/3 here is not so nice


### SCREEN UPDATE HELPERS ###

# TODO rename me + test all parameters
def update_configure(fast=True, speed=2):
    global fast_draw
    fast_draw = fast
    if fast_draw:
        # Set speed to max   # TODO useful as we use tracer(0)?
        ct.speed(0)
        # Hide the turtle
        ct.hideturtle()
        # We will manage when needed the scren update with screen.update()
        screen.tracer(False)
    else:
        ct.speed(speed)
        ct.showturtle() # TODO not useful
        screen.tracer(True) # TODO not useful

def update_do():
    global fast_draw
    if fast_draw:
        screen.update()


### TEST HELPERS ###

def test_primitives():
    ct.color('black', 'red')
    ct.pensize(1)
    cross(0, 0, 40)
    circle(0, 0, 40)
    circle_filled(40, 0, 40)
    square(60, 20, 40)
    square_filled(100, 20, 40)
    rectangle(-20, -20, 80, 40)
    rectangle_filled(60, -20, 80, 40)
    x, y, w, h = five_pointed_star(0, -80, 40)
    rectangle(x, y, w, h) # Rectangle containing the star
    five_pointed_star_filled(40, -80, 40)

def test_flag(flag_function_name):
    # Get window size
    win_w = screen.window_width()
    win_h = screen.window_height()
    w = win_w * 90/100 # remove 5% borders
    h = w * FLAG_DEFAULT_RATIO
    flag_function_name(-w/2, h/2, w, h)
    # Add a border
    ct.color(FLAG_BORDER_COL)
    rectangle(-w/2, h/2, w, h)

def test_flag_class(flag_function_name, ratio=False):
    # Get window size
    win_w = screen.window_width()
    win_h = screen.window_height()
    w = win_w * 90/100 # remove 5% borders
    # Get the flag element and draw it according to its size ratio
    flag = flags_dict[flag_function_name]
    if ratio:
        h = w * flag.ratio
        flag.draw_ratio(-w/2, h/2, w)
    else:
        h = w * FLAG_DEFAULT_RATIO
        flag.draw(-w/2, h/2, w, h)
    # Add a border
    ct.color(FLAG_BORDER_COL)
    rectangle(-w/2, h/2, w, h)

### MAIN ###

def main():
    # Black border, red inside
    ct.color('black', 'red')
    # Pen thickness
    ct.pensize(1)

    update_configure(True)  # TODO Does not work

    print('Welcome to Flag guessing')
    a = 0
    while a != 4:
        print('Choose an option:')
        print('1. How to play & rules? \
            2. All flags \
                3. Play \
                    4. Exit & Credits')
        a = input('')
        if a == '1':
            ct.clear()
            Example_rules()
        elif a == '2':
            ct.clear()
            draw_all_flags(160, 60, ratio=False)
        elif a == '3':
            ct.clear()
            game()
        elif a == '4':
            ct.clear
            credits_1()
            return 'Done'
        else:
            print('No valid input')
    update_do()
    return "Done"

## Example and rules ##

def Example_rules():
    an = 'y'
    while an != 'Y':
        print('Welcome to the game')
        print('The goal of the game if to guess the name of the country whose flag appears on screen. \
            For this, you will enter the name that you think is the correct answers without special characters only the 26 letters of the latin alphabet')
        print()
        print('As an example, the flag on the screen is Armenias, you will need to write your answer as follow')
        test_flag(flag_Armenia)
        print('Which flag is it?: Armenia')
        print('Correct')
        print()
        print('That is how the game works')
        an = input('Do you understan [Y/n]:')
        
def credits_1():
    print('This game was develope by:')
    print('Julian Avila - Code = 20212107030')
    print('Laura Torres - Code = 20212107038')
    print()
    print('The developers would like to thank:')
    print('Github user dmccreary for the base code')
    print('Programmer Duc Vu and Bryan Martinez for the conceptual idea')
    print('Thanks for playing')
    
if __name__ == "__main__":
    msg = main()
    print(msg)
