from gpiozero import LED, Button
from signal import pause

# https://gpiozero.readthedocs.io/en/stable/recipes.html
r_led = LED(17)
y_led = LED(26)
g_led = LED(10)
button = Button(3)


state = 0

def change_state():
    global state 
    state = (state + 1) % 5 
    lights()

def lights():
    r_led.off()
    y_led.off()
    g_led.off()

    match state:
        case 1:
            r_led.on()
        case 2:
            r_led.on()
            y_led.on()
        case 3:
            g_led.on()
        case 4:
            y_led.on()

button.when_pressed = change_state


pause()
