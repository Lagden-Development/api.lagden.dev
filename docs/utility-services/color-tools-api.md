# 🎨 Color Tools API

### Check Color Brightness

Analyze any color to determine if it's light or dark based on perceived brightness. Perfect for deciding text colors, overlays, and maintaining accessibility in your UI!

#### 🔍 Endpoint

```
GET /color-tools/check_brightness
```

#### 📝 Description

This endpoint calculates the perceived brightness of a color using a weighted formula `(0.299*R + 0.587*G + 0.114*B)/255`. It tells you whether a color is perceived as light or dark, which is super helpful for accessibility and UI design decisions!

#### 🎯 Parameters

| Parameter      | Type   | Required | Description                                                    |
| -------------- | ------ | -------- | -------------------------------------------------------------- |
| `color`        | string | Yes      | Your color value. Can be hex (#RRGGBB) or RGB format           |
| `color_format` | string | No       | Format of your color: either `hex` or `rgb`. Defaults to `hex` |

#### 📊 Supported Color Formats

1. **Hex Format** (`color_format=hex`):
   - Full hex: `#RRGGBB` (e.g., `#FF5733`)
   - Short hex: `#RGB` (e.g., `#F57`)
   - With or without the `#` prefix
2. **RGB Format** (`color_format=rgb`):
   - Comma-separated: `255,87,51`
   - Function notation: `rgb(255,87,51)`
   - Spaces are allowed!

#### ✨ Response Format

```json
{
  "ok": true,
  "status": 200,
  "message": "Successfully analyzed color brightness",
  "data": {
    "input_color": "#FF5733",
    "format": "hex",
    "rgb_values": [255, 87, 51],
    "brightness": 0.452,
    "is_dark": true,
    "perception": "dark"
  }
}
```

#### 📌 Response Fields

| Field              | Type    | Description                   |
| ------------------ | ------- | ----------------------------- |
| `ok`               | boolean | Success status of the request |
| `status`           | number  | HTTP status code              |
| `message`          | string  | Human-readable status message |
| `data.input_color` | string  | Your original color input     |
| `data.format`      | string  | Format used for the analysis  |
| `data.rgb_values`  | array   | RGB values as `[r, g, b]`     |
| `data.brightness`  | number  | Calculated brightness (0-1)   |
| `data.is_dark`     | boolean | `true` if color is dark       |
| `data.perception`  | string  | "dark" or "light"             |

#### 🎭 Examples

1. **Using Hex Color**

```bash
GET /check_brightness?color=%23FF5733&color_format=hex
```

2. **Using RGB Color**

```bash
GET /check_brightness?color=255,87,51&color_format=rgb
```

3. **Using RGB Function Notation**

```bash
GET /check_brightness?color=rgb(255,87,51)&color_format=rgb
```

#### ❌ Error Responses

The API might return these error codes:

- `400`: Invalid color format or values
- `500`: Server processing error

Example error response:

```json
{
  "detail": "Invalid hex color format. Use #RRGGBB"
}
```

#### 💡 Tips

- For hex colors, both `#FF5733` and `FF5733` work fine
- RGB values must be between 0 and 255
- The brightness threshold for dark/light is 0.5
- Use this endpoint to automatically choose text colors that contrast well with your background!

#### 🔒 Rate Limiting

This endpoint is not rate-limited, but please be mindful of usage!

Need help or found a bug? Reach out to the dev team! 🚀
