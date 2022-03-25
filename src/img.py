import textwrap
from string import ascii_letters

from PIL import Image, ImageDraw, ImageFont


def will_it_fit(text, size, img_width, img_height) -> bool:
    font = ImageFont.truetype("Arial Unicode.ttf", size=size)

    # Calculate the average length of a single character of our font.
    # Note: this takes into account the specific font and font size.
    avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
    avg_char_height = sum(font.getsize(char)[1] + 15 for char in ascii_letters) / len(ascii_letters)

    # Translate this average length into a character count
    # to fill 95% of our image's total width
    max_char_count = int((img_width * 0.95) / avg_char_width)
    # max_rows_count = int((img_height * 0.95) / avg_char_height)

    wrapped_lines = []
    for line in text.splitlines():
        # Create a wrapped text object using scaled character count
        wrapped_lines.append(textwrap.fill(text=line, width=max_char_count))

    # TODO: try approach with max_rows_count
    text_height = len(wrapped_lines) * avg_char_height
    # print(f'text height {len(wrapped_lines)} * {avg_char_height} = {text_height}')
    if text_height > img_height:
        return False
    return True


def fit_it(text, size, img):
    font = ImageFont.truetype("Arial Unicode.ttf", size=size)

    # Calculate the average length of a single character of our font.
    # Note: this takes into account the specific font and font size.
    avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)

    # Translate this average length into a character count
    # to fill 95% of our image's total width
    max_char_count = int((img.size[0] * 0.95) / avg_char_width)

    wrapped_lines = []
    for line in text.splitlines():
        # Create a wrapped text object using scaled character count
        wrapped_lines.append(textwrap.fill(text=line, width=max_char_count, subsequent_indent="  "))

    text = "\n".join(wrapped_lines)
    draw = ImageDraw.Draw(im=img)
    draw.text(xy=(20, 20), text=text, font=font, fill="#000000")
    img.show()


def main():
    text = """Wilcza Hostel 2022-03-25_23:02 potrzebujemy:

* Krople do nosa dla dzieci i dorosłych
* Koce nowe
* Szczotki/grzebienie do włosów
* Pomadki ochronne
* Worki na śmieci 60L
* artykuły szkolne: zeszyty, plecaki

"""
    img = Image.new(mode="RGB", size=(600, 400), color=(255, 255, 255))

    size = 48
    while size > 8:
        print(f"size {size}")

        if not will_it_fit(text, size, img.size[0], img.size[1]):
            size -= 2
            continue

        fit_it(text, size, img)
        break


if __name__ == "__main__":
    main()
