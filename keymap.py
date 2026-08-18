"""Tabella unica dei nomi dei tasti.

Prima di questo modulo esistevano due convenzioni parallele e incompatibili:
tracker.py salvava nomi in stile X11 ("Esc", "`", ",", "Caps", "Page_up",
"Kp_/") mentre KEYBOARD_LAYOUT in ui.py disegnava id in stile DOM ("Escape",
"Backquote", "Comma", "CapsLock", "PageUp", "Kp_Divide"). Nessuno convertiva:
28 tasti su 104 non potevano illuminarsi e il tooltip leggeva sempre zero.

Il nome memorizzato resta quello del tracker, per non invalidare lo storico
gia' raccolto; qui si traduce fra le due forme.
"""

# id del tasto disegnato -> nome con cui il tracker lo memorizza
LAYOUT_TO_KEY = {
    "Escape": "Esc",
    "PrintScreen": "Print_screen",
    "ScrollLock": "Scroll_lock",
    "Backquote": "`",
    "Minus": "-",
    "Equal": "=",
    "PageUp": "Page_up",
    "PageDown": "Page_down",
    "NumLock": "Num_lock",
    "CapsLock": "Caps",
    "BracketLeft": "[",
    "BracketRight": "]",
    "Backslash": "\\",
    "Semicolon": ";",
    "Quote": "'",
    "Comma": ",",
    "Period": ".",
    "Slash": "/",
    "Kp_Divide": "Kp_/",
    "Kp_Multiply": "Kp_*",
    "Kp_Subtract": "Kp_-",
    "Kp_Add": "Kp_+",
    "Kp_Decimal": "Kp_.",
    # pynput non distingue l'Invio del tastierino da quello principale
    "Kp_Enter": "Enter",
}

# nome memorizzato -> id del tasto disegnato.
# Gli alias verso un nome che e' gia' l'id di un altro tasto (Kp_Enter -> Enter)
# valgono solo in andata: al ritorno "Enter" deve restare l'Invio principale,
# altrimenti si illumina il tastierino al posto suo.
_ALIAS_ONLY_FORWARD = {"Kp_Enter"}

KEY_TO_LAYOUT = {}
for _layout_id, _key_name in LAYOUT_TO_KEY.items():
    if _layout_id in _ALIAS_ONLY_FORWARD:
        continue
    KEY_TO_LAYOUT.setdefault(_key_name, _layout_id)


def key_for_layout(layout_id):
    """Nome memorizzato corrispondente a un id della tastiera disegnata."""
    return LAYOUT_TO_KEY.get(layout_id, layout_id)


def layout_for_key(key_name):
    """Id del tasto da illuminare per un nome memorizzato."""
    return KEY_TO_LAYOUT.get(key_name, key_name)


# --- Risoluzione dal virtual-key code -------------------------------------
#
# Con un modificatore premuto pynput restituisce il carattere di controllo
# prodotto dal sistema (Ctrl+S -> "\x13") oppure nulla, e il tasto reale si
# perde. In quel caso si risale dal virtual-key code di Windows.

VK_TO_KEY = {
    0x08: "Backspace", 0x09: "Tab", 0x0D: "Enter", 0x13: "Pause",
    0x14: "Caps", 0x1B: "Esc", 0x20: "Space",
    0x21: "Page_up", 0x22: "Page_down", 0x23: "End", 0x24: "Home",
    0x25: "Left", 0x26: "Up", 0x27: "Right", 0x28: "Down",
    0x2C: "Print_screen", 0x2D: "Insert", 0x2E: "Delete",
    0x5D: "Menu", 0x90: "Num_lock", 0x91: "Scroll_lock",
    0x6A: "Kp_*", 0x6B: "Kp_+", 0x6D: "Kp_-", 0x6E: "Kp_.", 0x6F: "Kp_/",
    # Tasti di punteggiatura (posizione fisica, disposizione US)
    0xBA: ";", 0xBB: "=", 0xBC: ",", 0xBD: "-", 0xBE: ".", 0xBF: "/",
    0xC0: "`", 0xDB: "[", 0xDC: "\\", 0xDD: "]", 0xDE: "'",
}

for _i in range(10):                      # 0-9
    VK_TO_KEY[0x30 + _i] = str(_i)
for _i in range(26):                      # A-Z
    VK_TO_KEY[0x41 + _i] = chr(ord("A") + _i)
for _i in range(10):                      # tastierino numerico
    VK_TO_KEY[0x60 + _i] = "Kp_%d" % _i
for _i in range(1, 13):                   # F1-F12
    VK_TO_KEY[0x70 + _i - 1] = "F%d" % _i


def key_for_vk(vk):
    """Nome del tasto a partire dal virtual-key code, o None se sconosciuto."""
    if vk is None:
        return None
    return VK_TO_KEY.get(vk)


# --- Recupero dello storico ------------------------------------------------
#
# I dati raccolti dalle versioni precedenti contengono caratteri di controllo
# al posto dei tasti premuti insieme a Ctrl. La corrispondenza e' deterministica.

CTRL_CHAR_TO_KEY = {chr(i): chr(ord("A") + i - 1) for i in range(1, 27)}


def repair_key_name(name):
    """Normalizza un nome memorizzato dalle versioni precedenti.

    Traduce i caratteri di controllo ("\\x13" -> "S") e le rappresentazioni
    grezze di pynput ("<65>" -> "A"). Restituisce il nome invariato se non c'e'
    niente da correggere.
    """
    if not name:
        return name
    if len(name) == 1 and name in CTRL_CHAR_TO_KEY:
        return CTRL_CHAR_TO_KEY[name]
    if len(name) > 2 and name[0] == "<" and name[-1] == ">" and name[1:-1].isdigit():
        return key_for_vk(int(name[1:-1])) or name
    return name
