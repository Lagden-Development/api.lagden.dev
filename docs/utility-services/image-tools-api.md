# 🎨 Image Tools API

### Extract Dominant Colors

Want to know the main colors in an image? This endpoint has got you covered! It uses smart clustering to find the most prominent colors in any image you throw at it.

#### 🔍 Endpoint

```
GET /image-tools/dominant_colors
```

#### 📝 Description

This endpoint analyzes any image URL and extracts the most dominant colors using K-means clustering. Perfect for:

- Creating color palettes from images
- Analyzing brand colors
- Generating matching color schemes
- Automated design systems

#### 📊 Parameters

| Parameter  | Type    | Required | Description                                    |
| ---------- | ------- | -------- | ---------------------------------------------- |
| `url`      | string  | Yes      | Valid URL of the image to analyze              |
| `n_colors` | integer | No       | Number of colors to extract (1-10, default: 3) |

#### ✨ Response Format

```json
{
  "ok": true,
  "status": 200,
  "message": "Successfully extracted dominant colors",
  "data": {
    "hex_colors": ["#FF5733", "#33FF57", "#5733FF"],
    "rgb_colors": [
      [255, 87, 51],
      [51, 255, 87],
      [87, 51, 255]
    ]
  }
}
```

#### 📌 Response Fields

| Field             | Type    | Description                     |
| ----------------- | ------- | ------------------------------- |
| `ok`              | boolean | Success status of the request   |
| `status`          | number  | HTTP status code                |
| `message`         | string  | Human-readable status message   |
| `data.hex_colors` | array   | Colors in hex format (#RRGGBB)  |
| `data.rgb_colors` | array   | Colors in RGB format \[R, G, B] |

#### 🎭 Examples

1. **Get 3 Dominant Colors (Default)**

```bash
GET /dominant_colors?url=https://example.com/image.jpg
```

2. **Get 5 Dominant Colors**

```bash
GET /dominant_colors?url=https://example.com/image.jpg&n_colors=5
```

#### ❌ Error Responses

You might see these error cases:

- `400`: Invalid URL or image processing failed

  ```json
  {
    "detail": "Failed to download the image: Connection timeout"
  }
  ```

  ```json
  {
    "detail": "Error processing image: Invalid image format"
  }
  ```

#### 💡 Tips

- Make sure your image URL is publicly accessible
- The more colors you request, the more subtle variations you'll see
- For best results, use images with clear, distinct color areas
- Processing time may vary based on image size
- Results are ordered by color dominance

#### 🖼️ Supported Image Formats

- PNG
- JPEG/JPG
- Other common web image formats

#### ⚡ Technical Notes

The endpoint uses:

- K-means clustering for color extraction
- OpenCV for image processing
- PIL for image handling
- RGB color space for analysis

#### 🔒 Important Notes

- URLs must be publicly accessible
- Maximum processing time: 10 seconds
- Larger images may take longer to process
- Consider image size for optimal performance

Need help or found a bug? Our dev team is here to help! 🚀
