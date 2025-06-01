def format_line_edit_text(line_edit):
    cursor_pos = line_edit.cursorPosition()

    digits_only = line_edit.text().replace(',', '')

    if digits_only == '' or (digits_only.isdigit() and int(digits_only) <= 0):
        line_edit.blockSignals(True)
        line_edit.setText('0')
        line_edit.blockSignals(False)
        line_edit.setCursorPosition(1)
        line_edit._last_text = '0'
        return

    if not digits_only.isdigit():
        line_edit.blockSignals(True)
        line_edit.setText(getattr(line_edit, "_last_text", "0"))
        line_edit.blockSignals(False)
        line_edit.setCursorPosition(max(cursor_pos - 1, 0))
        return

    formatted_text = "{:,}".format(int(digits_only))

    if formatted_text != line_edit.text():
        commas_before = line_edit.text()[:cursor_pos].count(',')
        line_edit.blockSignals(True)
        line_edit.setText(formatted_text)
        line_edit.blockSignals(False)

        new_cursor_pos = cursor_pos + (formatted_text.count(',') - commas_before)
        line_edit.setCursorPosition(new_cursor_pos)

    line_edit._last_text = formatted_text


def parse_price(price_text):
    """Removes comma separators and converts price to int if valid"""
    try:
        clean_text = price_text.replace(',', '')
        return int(clean_text)
    except ValueError:
        return None