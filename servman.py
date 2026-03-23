from colorama import init, Fore, Style
import time
import socket
import struct

init()

ascii_art = """
       ::::::::  :::::::::: :::::::::  :::     ::: :::::::::: :::::::::    :::   :::       :::     ::::    :::     :::      ::::::::  :::::::::: ::::::::: 
    :+:    :+: :+:        :+:    :+: :+:     :+: :+:        :+:    :+:  :+:+: :+:+:    :+: :+:   :+:+:   :+:   :+: :+:   :+:    :+: :+:        :+:    :+: 
   +:+        +:+        +:+    +:+ +:+     +:+ +:+        +:+    +:+ +:+ +:+:+ +:+  +:+   +:+  :+:+:+  +:+  +:+   +:+  +:+        +:+        +:+    +:+  
  +#++:++#++ +#++:++#   +#++:++#:  +#+     +:+ +#++:++#   +#++:++#:  +#+  +:+  +#+ +#++:++#++: +#+ +:+ +#+ +#++:++#++: :#:        +#++:++#   +#++:++#:    
        +#+ +#+        +#+    +#+  +#+   +#+  +#+        +#+    +#+ +#+       +#+ +#+     +#+ +#+  +#+#+# +#+     +#+ +#+   +#+# +#+        +#+    +#+    
#+#    #+# #+#        #+#    #+#   #+#+#+#   #+#        #+#    #+# #+#       #+# #+#     #+# #+#   #+#+# #+#     #+# #+#    #+# #+#        #+#    #+#     
########  ########## ###    ###     ###     ########## ###    ### ###       ### ###     ### ###    #### ###     ###  ########  ########## ###    ###  
 
Version 1.0.1 - Gestion de Serveurs via le protocole RCON
"""

lines = ascii_art.splitlines()
height = len(lines)

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def print_banner():
    import time
    import math
    from colorama import Style

    height = len(lines)

    for i, line in enumerate(lines):
        t = i / height

        # effet vague (mais sans boucle infinie)
        wave = (math.sin(t * 3) + 1) / 2

        # bleu → bleu clair (lumineux)
        r = int(0 + 80 * wave)
        g = int(120 + 100 * wave)
        b = int(200 + 55 * wave)

        print(rgb(r, g, b) + line)

        time.sleep(0.03)  # animation ligne par ligne

    print(Style.RESET_ALL)

def show_players(sock):
    raw = rcon_send(sock, "list")
    if not raw or ":" not in raw:
        print("Aucun joueur connecté.")
        return

    players = [p.strip() for p in raw.split(":", 1)[1].split(",") if p.strip()]

    print("\n==== JOUEURS CONNECTÉS ====")

    for p in players:
        uuid = rcon_send(sock, f"uuid {p}") or "UUID inconnu"

        seen = rcon_send(sock, f"seen {p}")
        ip = "IP inconnue"

        if seen:
            if "IP:" in seen:
                ip = seen.split("IP:")[1].strip().split()[0]

        print(f"- {p} | {uuid} | {ip}")

    print()

def rcon_connect():
    global iptarget, rconpw
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((iptarget, 25575))
        payload = rconpw.encode() + b"\x00"
        packet = struct.pack("<iii", len(payload) + 10, 1, 3) + payload + b"\x00\x00"
        sock.send(packet)
        resp = sock.recv(1024)
        if len(resp) < 12 or struct.unpack("<i", resp[4:8])[0] == -1:
            sock.close()
            return None
        print(Fore.GREEN + "Connecté" + Style.RESET_ALL)
        return sock
    except:
        print(Fore.RED + "Échec connexion" + Style.RESET_ALL)
        return None

def rcon_send(sock, cmd):
    try:
        payload = cmd.encode() + b"\x00"
        packet = struct.pack("<iii", len(payload) + 10, 42, 2) + payload + b"\x00\x00"
        sock.send(packet)
        time.sleep(0.1)
        data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk: break
            data += chunk
            if len(chunk) < 4096: break
        if len(data) > 16:
            return data[12:-2].decode("utf-8", errors="replace").strip()
        return ""
    except:
        return ""

print_banner()

iptarget = input(Fore.RED + "IP du serveur : " + Style.RESET_ALL).strip()
rconpw   = input(Fore.RED + "Mot de passe RCON : " + Style.RESET_ALL).strip()

rcon_socket = None

while True:
    cmd_line = input(Fore.RED + "utilisateur@:" + Style.RESET_ALL + "~$ " + Style.RESET_ALL).strip()
    if not cmd_line: continue

    parts = cmd_line.split()
    cmd = parts[0].lower()

    if cmd in ("exit", "quit", "q"):
        if rcon_socket: rcon_socket.close()
        break

    elif cmd == "connect":
        if rcon_socket: rcon_socket.close()
        rcon_socket = rcon_connect()

    elif cmd in ("list", "players", "who"):
        if rcon_socket:
            print(rcon_send(rcon_socket, "list") or "(aucune réponse)")
        else:
            print(Fore.YELLOW + "pas connecté" + Style.RESET_ALL)

    elif cmd == "banner":
        print_banner()

    elif cmd == "players":
        show_players(rcon_socket)

    elif rcon_socket:
        print(rcon_send(rcon_socket, cmd_line) or "(exécuté)")

    else:
        print(Fore.YELLOW + "commande inconnue" + Style.RESET_ALL)
    