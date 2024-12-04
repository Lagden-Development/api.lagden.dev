def calculate_brightness(r: int, g: int, b: int) -> float:
    """
    Calculate perceived brightness using the formula:
    (0.299*R + 0.587*G + 0.114*B)/255

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        float: Brightness value between 0 and 1
    """
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255
