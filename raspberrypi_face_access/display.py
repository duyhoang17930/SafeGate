from config import DISPLAY_MODE, LCD_COLUMNS, LCD_I2C_ADDRESS, LCD_ROWS


class Display:
    def __init__(self) -> None:
        self.mode = DISPLAY_MODE
        self.lcd = None
        if self.mode == "lcd_i2c":
            try:
                from RPLCD.i2c import CharLCD

                self.lcd = CharLCD(
                    "PCF8574",
                    LCD_I2C_ADDRESS,
                    cols=LCD_COLUMNS,
                    rows=LCD_ROWS,
                    charmap="A00",
                )
                self.lcd.clear()
            except Exception as error:
                print(f"[DISPLAY] LCD unavailable, using console: {error}")
                self.mode = "console"

    def show(self, line1: str, line2: str = "") -> None:
        line1 = str(line1)[:LCD_COLUMNS]
        line2 = str(line2)[:LCD_COLUMNS]
        if self.lcd is None:
            print(f"[DISPLAY] {line1} | {line2}")
            return
        self.lcd.clear()
        self.lcd.write_string(line1.ljust(LCD_COLUMNS))
        if LCD_ROWS > 1:
            self.lcd.crlf()
            self.lcd.write_string(line2.ljust(LCD_COLUMNS))

    def close(self) -> None:
        if self.lcd is not None:
            self.lcd.clear()
            self.lcd.close(clear=True)

