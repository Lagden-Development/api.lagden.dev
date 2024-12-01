# 👀 Discord Watcher API

### Get User Watcher Data

Want to know what a Discord user is up to? This endpoint gives you real-time presence data including their activities, Spotify status, custom status, and more!

#### 🔍 Endpoint

```
GET /watcher/{discord_id}
```

#### 📝 Description

This endpoint fetches comprehensive user presence data from the LDEV Watcher System, including:

- Basic user profile information
- Current online status across platforms
- Active sessions (desktop/mobile/web)
- Spotify listening activity
- Custom status
- Other Discord activities

#### 📊 Path Parameters

| Parameter    | Type    | Required | Description                       |
| ------------ | ------- | -------- | --------------------------------- |
| `discord_id` | integer | Yes      | Discord user ID to fetch data for |

#### ✨ Response Format

```json
{
    "ok": true,
    "user_data": {
        "accent_color": 16711680,
        "avatar": {
            "key": "abc123",
            "url": "https://cdn.discord.com/avatars/..."
        },
        "color": {
            "r": 255,
            "g": 0,
            "b": 0,
            "hex": "#FF0000"
        },
        "created_at": "2020-01-01T00:00:00Z",
        "display_name": "Cool User",
        "global_name": "CoolUser"
        // ... other user fields
    },
    "presence_data": {
        "active_platforms": {
            "desktop": true,
            "mobile": false,
            "web": false
        },
        "custom_status": {
            "name": "Custom Status",
            "emoji": "🎮",
            "state": "Gaming!",
            "created_at": "2023-01-01T00:00:00Z"
        },
        "spotify_status": {
            "activity": {
                "color": {
                    "r": 30,
                    "g": 215,
                    "b": 96,
                    "hex": "#1ED760"
                },
                "created_at": "2023-01-01T00:00:00Z",
                "party_id": "spotify:123",
                "title": "Spotify"
            },
            "album": {
                "cover_url": "https://i.scdn.co/image/...",
                "name": "Awesome Album"
            },
            "track": {
                "artists": ["Cool Artist"],
                "end": "2023-01-01T00:03:30Z",
                "name": "Amazing Song",
                "start": "2023-01-01T00:00:00Z",
                "url": "https://open.spotify.com/track/..."
            }
        },
        "misc_activities": [
            {
                "application_id": 123456789,
                "assets": {
                    "large_image": "game_image",
                    "large_text": "Playing Game",
                    "small_image": "status_image",
                    "small_text": "In Menu"
                },
                "created_at": "2023-01-01T00:00:00Z",
                "details": "In Main Menu",
                "name": "Cool Game",
                "state": "Playing Solo",
                "timestamps": {
                    "start": 1672531200
                },
                "type": "PLAYING"
            }
        ],
        "statuses": {
            "desktop": "online",
            "mobile": "idle",
            "web": "offline",
            "status": "online",
            "raw_status": "online"
        }
    }
}
```

#### ❌ Error Responses

1. **User Not Found (404)**

```json
{
    "ok": false,
    "message": "User Not Found"
}
```

2. **User Banned (403)**

```json
{
    "ok": false,
    "message": "User Banned"
}
```

3. **User Opted Out (403)**

```json
{
    "ok": false,
    "message": "User opted out of watcher"
}
```

#### 🎯 Data Models

Here's what you can expect in the response:

**User Data**

- Profile information
- Avatar and banner details
- Display name and discriminator
- Account creation date
- Color preferences

**Presence Data**

- Active platforms (desktop/mobile/web)
- Custom status with emoji
- Spotify listening activity
- Other Discord activities
- Platform-specific status

**Spotify Status (if available)**

- Current track info
- Album details
- Artists
- Timestamps
- Album artwork

**Activities**

- Game details
- Application information
- Timestamps
- Rich presence assets

#### 💡 Tips

- Keep Discord IDs as integers (no quotes)
- Check `ok` field to confirm successful responses
- Use `active_platforms` to know where the user is online
- Spotify data is only available when user is listening
- Custom status may be `null` if not set

#### 🔒 Privacy Notes

- Users can opt out of tracking
- Banned users cannot be tracked
- Some data may be hidden based on user privacy settings

Need help or have questions? Our dev team is here to help! 🚀
