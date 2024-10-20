# lagden.dev API

The **lagden.dev API** offers a variety of public endpoints designed to integrate with external platforms and services. One key feature is the **Discord Profile & Presence Watcher**, which monitors and retrieves real-time updates of Discord user profiles and activities. The API is designed to be easily extendable, with future features planned.

## Features

- **Discord Profile & Presence Watcher**: Retrieves a Discord user's profile, presence status, and activities stored in the database.
- _(Future Feature Placeholder)_: Other features and integrations will be added to the API in future releases.

---

## API Endpoints

### 1. **Discord Profile & Presence Watcher**

This endpoint retrieves real-time updates about a Discord user's profile, including their username, avatar, current status, and any ongoing activities (such as Spotify or Visual Studio Code usage). This data is provided from the MongoDB database, which is populated by the `ricksanchez` bot system.

**Endpoint:**

```bash
GET /v1/watcher/{discord_user_id}
```

**Description:**

Fetches a Discord user’s presence and profile details using their unique Discord user ID. The response contains profile information, platform activity, custom status, and details about any ongoing activities such as apps being used or music being played.

**Example Request:**

```bash
GET https://api.lagden.dev/v1/watcher/1277005773230313474
```

**Example Response:**

```json
{
  "ok": true,
  "presence_data": {
    "active_platforms": {
      "desktop": true,
      "mobile": false,
      "web": false
    },
    "custom_status": null,
    "misc_activities": [
      {
        "application_id": 383226320970055681,
        "assets": {
          "large_image": "https://cdn.discordapp.com/app-assets/383226320970055681/565944799761268737.png",
          "large_text": "Editing a JSON file",
          "small_image": "https://cdn.discordapp.com/app-assets/383226320970055681/565945770067623946.png",
          "small_text": "Visual Studio Code"
        },
        "created_at": "2024-10-20T14:35:10.280000+00:00",
        "details": "Editing projects.json",
        "name": "Visual Studio Code",
        "state": "Workspace: lagden.dev [SSH: ldev-vps]",
        "timestamps": {
          "end": null,
          "start": 1729429198901
        },
        "type": "Activity"
      }
    ],
    "spotify_status": {
      "activity": {
        "color": {
          "b": 84,
          "g": 185,
          "hex": "#1db954",
          "r": 29
        },
        "created_at": "2024-10-20T14:35:10.280000+00:00",
        "party_id": "spotify:1277005773230313474",
        "title": "LIKE A TATTOO (Jersey Club)",
        "type": "Spotify"
      },
      "album": {
        "cover_url": "https://i.scdn.co/image/ab67616d0000b2735a922551cdfda94be49fbdf8",
        "name": "Ocean One, Vol. 3 (A Jersey Club Mixtape)"
      },
      "track": {
        "artists": ["DJ SoulChild AC"],
        "end": "2024-10-20T14:37:39.731000+00:00",
        "name": "LIKE A TATTOO (Jersey Club)",
        "start": "2024-10-20T14:35:09.732000+00:00",
        "url": "https://open.spotify.com/track/4v5F7sJgQgtjQ2PLZ1Gzww"
      }
    },
    "statuses": {
      "desktop": "dnd",
      "mobile": "offline",
      "raw_status": "dnd",
      "status": "dnd",
      "web": "offline"
    }
  },
  "user_data": {
    "accent_color": null,
    "accent_colour": null,
    "avatar": {
      "key": "878d4c9db5d644ec902c4bb0b8346b8c",
      "url": "https://cdn.discordapp.com/avatars/1277005773230313474/878d4c9db5d644ec902c4bb0b8346b8c.png?size=1024"
    },
    "avatar_decoration": "None",
    "avatar_decoration_sku_id": null,
    "banner": null,
    "color": {
      "b": 0,
      "g": 0,
      "hex": "#000000",
      "r": 0
    },
    "created_at": "2024-08-24T20:45:01.958000+00:00",
    "discriminator": "0",
    "display_avatar": "https://cdn.discordapp.com/avatars/1277005773230313474/878d4c9db5d644ec902c4bb0b8346b8c.png?size=1024",
    "display_name": "Zach",
    "global_name": "Zach",
    "id": 1277005773230313474,
    "mention": "<@1277005773230313474>",
    "name": "zachlagden",
    "public_flags": 4194304
  }
}
```

**Response Fields:**

- **`ok`**: Whether the API request was successful.
- **`presence_data`**: Contains the user's active platform(s), activities, custom statuses, and Spotify data if applicable.
  - **`active_platforms`**: Indicates which platforms the user is active on (`desktop`, `mobile`, `web`).
  - **`misc_activities`**: Lists other activities such as applications the user is using.
  - **`spotify_status`**: If the user is listening to Spotify, shows current track details.
  - **`statuses`**: Displays the status on each platform (`online`, `offline`, `dnd`, etc.).
- **`user_data`**: Contains general profile information.
  - **`avatar`**: URL to the user's avatar.
  - **`display_name`**: The user's display name.
  - **`mention`**: A formatted mention for Discord.
  - **`created_at`**: Date and time the user's account was created.

---

## Getting Started

### Prerequisites

- Python (version 3.12 or higher)
- MongoDB

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Lagden-Development/lagden.dev-api.git
   cd lagden.dev-api
   ```

2. Set up a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   - Copy `.env.example` to `.env` and fill in the details, including MongoDB URI and server configuration:

     ```plaintext
     MONGODB_URI=mongodb://username:password@localhost:27017/database
     HOST=0.0.0.0
     PORT=8080
     ```

   - Make sure your MongoDB instance is running and populated with presence data from the [ricksanchez](https://github.com/Lagden-Development/ricksanchez) system.

5. Running the application:

   - For development:

     ```bash
     python app.py
     ```

   - To serve the application using **Gunicorn** (for production):

     ```bash
     python -m gunicorn -w 4 -b 0.0.0.0:8080 app:app
     ```

---

### Data Collection System

This API **does not** handle the collection of Discord profile or presence data. The data displayed by this API is stored in MongoDB, which is populated by the **[ricksanchez](https://github.com/Lagden-Development/ricksanchez)** project. Ensure that `ricksanchez` is set up and running to collect the necessary data before using this API.

---

## Contributing

We welcome contributions to the **lagden.dev API**. If you have suggestions for new features or improvements, feel free to open a pull request or submit an issue.

---

## Disclaimer

This API is primarily intended for use within the **lagden.dev** ecosystem. While public endpoints are provided, support for third-party developers or external use is limited.

## License

This project is licensed under a non-commercial open-source license. View the full license [here](https://github.com/Lagden-Development/.github/blob/main/LICENSE).
