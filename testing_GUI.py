# hello_world.py

import PySimpleGUI as sg

layout = [[sg.Text("Hello from PySimpleGUI")], [sg.Button("OK")]]


main_window = sg.Window(title="Hello World", layout=layout)

# Create an event loop
while True:
    event, values = main_window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

main_window.close()
