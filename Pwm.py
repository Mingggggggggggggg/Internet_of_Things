import tkinter as tk
from gpiozero import PWMLED

led = PWMLED(12)

def window():
    def update_led(value):
        brightness = int(value) / 100  # Umwandlung von 0–100 zu 0.0–1.0
        led.value = brightness
        print(f"Helligkeit: {brightness}")

    root = tk.Tk()
    root.title("YT-DLP GUI")
    root.geometry('400x200')
    root.resizable(False, False)

    scale = tk.Scale(root, from_=0, to=100, orient='horizontal', length=300, command=update_led)
    scale.set(0)  # Start bei 0 % Helligkeit
    scale.pack(pady=50)

    root.mainloop()

window()
