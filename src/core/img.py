import textwrap
from string import ascii_letters
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


class FbSharerImg:
    width = 1200
    height = 650
    font = "Arial Unicode.ttf"
    max_font_size = 48
    min_font_size = 8
    vertical_spacing = 12

    def _get_font(self, size: int) -> ImageFont:
        return ImageFont.truetype(self.font, size=size)

    def _avg_char_size(self, size: int) -> Tuple[float, float]:
        font = self._get_font(size)

        # Calculate the average length of a single character of our font.
        # Note: this takes into account the specific font and font size.
        avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
        avg_char_height = sum(font.getsize(char)[1] + self.vertical_spacing for char in ascii_letters) / len(
            ascii_letters
        )

        return avg_char_width, avg_char_height

    def _wrap_text(self, text: str, max_char_count: int) -> str:
        wrapped_lines = []
        for line in text.splitlines():
            # Create a wrapped text object using scaled character count
            wrapped_lines.append(textwrap.fill(text=line, width=max_char_count, subsequent_indent="  "))
        return "\n".join(wrapped_lines)

    def _will_it_fit(self, text: str, size: int, img_width: int, img_height: int) -> bool:
        avg_char_width, avg_char_height = self._avg_char_size(size)

        # Translate this average length into a character count
        # to fill 95% of our image's total width
        max_char_count = int((img_width * 0.95) / avg_char_width)
        max_rows_count = int((img_height * 0.95) / avg_char_height)

        wrapped_text = self._wrap_text(text, max_char_count)

        return len(wrapped_text.splitlines()) <= max_rows_count

    def _fit_it(self, text: str, size: int) -> Image:
        img = Image.new(mode="RGB", size=(self.width, self.height), color=(255, 255, 255))
        font = self._get_font(size)
        avg_char_width, avg_char_height = self._avg_char_size(size)

        # Translate this average length into a character count
        # to fill 95% of our image's total width
        max_char_count = int((img.size[0] * 0.95) / avg_char_width)

        wrapped_text = self._wrap_text(text, max_char_count)
        draw = ImageDraw.Draw(im=img)
        draw.text(xy=(10, 0), text=wrapped_text, font=font, fill="#000000")
        return img

    def create(self, text: str) -> Image:
        size = self.max_font_size
        while size > self.min_font_size:
            if not self._will_it_fit(text, size, self.width, self.height):
                size -= 1
                continue
            else:
                break

        return self._fit_it(text, size)


if __name__ == "__main__":
    fb = FbSharerImg()
    img = fb.create(
        """Wilcza Hostel 2022-03-25_23:02 potrzebujemy:

* Krople do nosa dla dzieci i dorosłych
* Koce nowe
* Szczotki/grzebienie do włosów
* Pomadki ochronne
* Worki na śmieci 60L
* artykuły szkolne: zeszyty, plecaki

"""
    )
    img.show()
