from modules import DanishBytes
from colorama import Fore
from sys import platform
import PySimpleGUI as sg
import subprocess
import json
import sys
import os

def clear():
    # if platform == "linux" or platform == "linux2":
    #     os.system('clear')
    # elif platform == "darwin":
    #     os.system('clear')
    # elif platform == "win32":
    #     os.system('cls')
    # print(
    #     f"{Fore.LIGHTGREEN_EX} ____          _     _   _____     _           \n"+
    #     "|    \ ___ ___|_|___| |_| __  |_ _| |_ ___ ___ \n"+
    #     "|  |  | .'|   | |_ -|   | __ -| | |  _| -_|_ -|\n"+
    #     "|____/|__,|_|_|_|___|_|_|_____|_  |_| |___|___|\n"+
    #     f"                              |___|{Fore.RESET}\n"
    # )
    pass

def question(question):
    output = f"{question}"
    if "(" in question:
        output = f"{question.split('(')[0]} {Fore.LIGHTBLACK_EX}({question.split('(')[1]}{Fore.RESET}"
    return input(f"[{Fore.LIGHTCYAN_EX}?{Fore.RESET}] {output}\n[{Fore.LIGHTYELLOW_EX}>{Fore.RESET}] ")

def getch_question(question):
    output = f"{question}"
    if "(" in question:
        output += f" ({question.split('(')[1]}"
    print(f"[{Fore.LIGHTCYAN_EX}?{Fore.RESET}] {output}\n[{Fore.LIGHTYELLOW_EX}>{Fore.RESET}]", end=" ")
    import sys
    if sys.platform[:3] == 'win':
        import msvcrt

        def getkey():
            key = msvcrt.getch()
            return key
    elif sys.platform[:3] == 'lin':
        import termios
        import sys
        import os

        def getkey():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            new = termios.tcgetattr(fd)
            new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
            new[6][termios.VMIN] = 1
            new[6][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSANOW, new)
            try:
                c = os.read(fd, 1)
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, old)
            return c
    else:
        def getkey():
            print("Not your system, bud.")
    return getkey()

def calc(size):
    if 1024 <= size < 1024*1024:
        return f"{round(size/1024, 2)} KB"
    elif 1024*1024 <= size < 1024*1024*1024:
        return f"{round(size/1024/1024, 2)} MB"
    elif 1024*1024*1024 <= size < 1024*1024*1024*1024:
        return f"{round(size/1024/1024/1024, 2)} GB"

def open_magnet(magnet):
    if sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', magnet],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif sys.platform.startswith('win32'):
        os.startfile(magnet)
    elif sys.platform.startswith('cygwin'):
        os.startfile(magnet)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', magnet],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        subprocess.Popen(['xdg-open', magnet],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    clear()
    d = DanishBytes.DanishBytes()
    try:
        config = json.load(open("config.json", "r+"))
    except Exception:
        config = {}
        window = sg.Window(
            'DanishBytes Klient af Turra', [
                [sg.T("Hvad er din API nøgle? (Tryk på enter for at jeg selv henter din api key via login vindue)")],
                [sg.InputText(key='pick')],
                [sg.B('Submit')]
            ],
            no_titlebar=True,
            finalize=True
        )
        window['pick'].bind("<Return>", "_Enter")
        event, values = window.read(close=True)
        if event == sg.WINDOW_CLOSED:
            return
        config['api_key'] = values['pick']
    if 'api_key' not in config or config['api_key'] == None or config['api_key'] == '':
        if 'db_session' not in config or config['db_session'] == '':
            config['db_session'], username = d.authenticate()
            sg.Window('DanishBytes Klient af Turra', [
                [sg.T("Log venligst ind på DBy i det åbnede vindue.")]
            ])
            d.set_session(config['db_session'])
        config['api_key'] = d.get_api()
    d.set_api(config['api_key'])
    json.dump(config, open("config.json", "w+"), indent=2, sort_keys=True)
    window = sg.Window(
        'DanishBytes Klient af Turra', [
            [sg.T("Hvilken film skal jeg prøve at finde for dig?")],
            [sg.InputText(key='pick', enable_events=True)],
            [sg.B('Hent', key="Get", disabled=True),sg.B("Luk", key='Exit')]
        ],
        no_titlebar=True
    )
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            return
        elif event in ("pick_Enter", "Get"):
            window.close()
            break
        elif len(values['pick']) > 0:
            window['Get'].update(disabled=False)
            window['pick'].bind("<Return>", "_Enter")
        else:
            window['Get'].update(disabled=True)
            window['pick'].unbind("<Return>")
            pass
    movies = d.find_movie(values['pick'])
    clear()
    if movies['resultsCountTotal'] > 0:
        layout = []
        i = 1
        for torrent in movies['torrents']:
            layout.append(
                [
                    sg.T(f"ID: {torrent['id']}, Navn: {torrent['name']}, Seeders: {torrent['seeders']}, Leechers: {torrent['leechers']}, Størrelse: {calc(torrent['size'])}"),
                    sg.B('Hent Torrent', key=f"download: {i}"),
                    sg.B('Magnet', key=f"magnet: {i}")
                ]
            )
            i += 1
        layout.append([sg.B("Luk", key='Exit')])
        window = sg.Window(
            'DanishBytes Klient af Turra',
            layout,
            finalize=True
        )
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                break
            elif 'download: ' in event or 'magnet: ' in event:
                id = int(event.split(" "))
                if 'download: ' in event:
                    os.system(f"start https://danishbytes.club/torrent/download/{movies['torrents'][id]['id']}.{movies['rsskey']}")
                elif 'magnet: ' in event:
                    magnet = f"magnet:?dn={movies['torrents'][id]['name']}&xt=urn:btih:{movies['torrents'][id]['info_hash']}&as=https://danishbytes.club/torrent/download/{movies['torrents'][id]['id']}.{movies['rsskey']}&xl={movies['torrents'][id]['size']}&tr=https://danishbytes.club/announce/e064ba0c35d252338572fd7720448cc5&tr=https://danishbytes.org/announce/e064ba0c35d252338572fd7720448cc5&tr=https://danishbytes2.org/announce/e064ba0c35d252338572fd7720448cc5&tr=https://danishbytes.art/announce/e064ba0c35d252338572fd7720448cc5"
                    open_magnet(magnet)
        return
    print(f"[{Fore.BLUE}i{Fore.RESET}] Ingen film for {values['pick']} fundet, prøv med noget andet?")
    return


if __name__ == '__main__':
    main()
    