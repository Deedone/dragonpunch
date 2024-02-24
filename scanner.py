from PIL import Image, ImageChops
from defs import Card, Board, slots, Slots
import pyautogui
from pyautogui import ImageNotFoundException

from typing import List, Optional, Dict

SIZE_X = 20
SIZE_Y = 20
Imgt = Image.Image
lables = [
    ["9G", "DG", "7R", "DR", "1R", "8B", "DR", "8G"],
    ["5G", "3B", "6B", "DR", "8R", "9R", "3G", "DR"],
    ["4B", "DB", "1B", "6G", "5R", "2B", "9B", "1G"],
    ["DG", "6R", "DB", "RR", "2G", "DG", "DB", "7B"],
    ["4G", "3R", "7G", "DG", "DB", "2R", "5B", "4R"],
]
cards: Dict[str, Imgt] = {}
emptys: List[Imgt] = []

#We get card samples from pre-made image and hard coded labels
def prepare_samples():
    print("Generating samples...")
    img = Image.open("sample.png")

    for i in range(8):
        for j in range(5):
            x = 410 + 152 * i
            y = 395 + 31 * j
            crop = img.crop((x, y, x+SIZE_X, y+SIZE_Y))
            cards[lables[j][i]] = crop
    emptys.append(img.crop(slots.special[0].look))
    emptys.append(img.crop(slots.special[1].look))
    emptys.append(img.crop(slots.special[2].look))

    for k, v in cards.items():
        v.save("samples/{}.png".format(k))
    print("Done")

def cmp_images(img1:Imgt, img2:Imgt) -> bool:
    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is None

def cmp_images_fuzzy(img1:Imgt, img2:Imgt) -> bool:
    try:
        pyautogui.locate(img2, img1, confidence=0.99)
    except ImageNotFoundException:
        return False
    return True

def show_match(img1, img2, label) -> None:
    merged = Image.new("RGB", (SIZE_X*3, SIZE_Y))
    diff = ImageChops.difference(img1, img2)
    merged.paste(img1, (0, 0))
    merged.paste(img2, (SIZE_X, 0))
    merged.paste(diff, (SIZE_X*2, 0))
    merged.show()
    _ = input("Got match for {}...".format(label))

def test_empty(img: Imgt) -> Card:
    for e in emptys:
        if cmp_images(img, e):
            return Card.from_str("EB")
    return Card.from_str("TB")

def scan_sample(img: Imgt) -> Optional[Card]:
    for k, v in cards.items():
        if img.size == v.size and cmp_images(img, v):
            return Card.from_str(k)
        if img.size != v.size and cmp_images_fuzzy(img, v):
            return Card.from_str(k)

    return None

def scan_row(i: int, image: Imgt) -> List[Card]:
    x_start, y_start, _, _ = slots.rows[i].look
    storage: List[Card] = []

    for j in range(12):
        y = y_start + 31 * j
        x = x_start

        crop = image.crop((x, y, x+SIZE_X, y+SIZE_Y))
        value = scan_sample(crop)
        if value:
            storage.append(value)
        else:
            break
    return storage

def scan_board(board: Board, slots: Slots):
    print("Scanning board...")
    img: Imgt = pyautogui.screenshot(region=(0,0,1920,1080))
    img.save("current.png")

    for i, _ in enumerate(slots.rows):
        board.rows[i] = scan_row(i, img)

    for i, s in enumerate(slots.special):
        x, y, _, _ = s.look
        crop = img.crop((x, y, x+SIZE_X, y+SIZE_Y))
        spec = scan_sample(crop)
        if spec:
            board.special[i] = spec
        else:
            board.special[i] = test_empty(crop)
        
    print("Done")
