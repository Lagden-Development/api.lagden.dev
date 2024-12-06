# /src/routers/v1/watcher_router.py

"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This file contains the watcher API routes for user presence data.
"""

# Python Standard Library Imports
from datetime import datetime
from typing import Optional, List, Union

# Third-Party Imports
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Database Imports
from db import users


# Color Model
class Color(BaseModel):
    """
    Represents RGB and hexadecimal color values for visual elements.

    Attributes:
        r (int): Red color component (0-255)
        g (int): Green color component (0-255)
        b (int): Blue color component (0-255)
        hex (str): Hexadecimal representation of the color
    """

    r: int
    g: int
    b: int
    hex: str


# Avatar Model
class Avatar(BaseModel):
    """
    Represents a user's avatar image information.

    Attributes:
        key (str): Unique identifier for the avatar
        url (str): Direct URL to the avatar image
    """

    key: str
    url: str


# Activity Assets Model
class ActivityAssets(BaseModel):
    """
    Represents image assets associated with a Discord activity.

    Attributes:
        large_image (Optional[str]): URL or key for the main activity image
        large_text (Optional[str]): Hover text for the main activity image
        small_image (Optional[str]): URL or key for the secondary activity image
        small_text (Optional[str]): Hover text for the secondary activity image
    """

    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]


# Activity Timestamps Model
class ActivityTimestamps(BaseModel):
    """
    Represents timing information for an activity.

    Attributes:
        end (Optional[datetime]): When the activity ends/ended
        start (Optional[int]): Unix timestamp when the activity started
    """

    end: Optional[datetime] = None
    start: Optional[int] = None


# Misc Activity Model
class MiscActivity(BaseModel):
    """
    Represents details about a Discord activity other than Spotify.

    Attributes:
        application_id (int): Discord application identifier
        assets (Optional[ActivityAssets]): Images associated with the activity
        created_at (datetime): When the activity was first detected
        details (Optional[str]): Additional activity information
        name (str): Name of the activity
        state (Optional[str]): Current state of the activity
        timestamps (Optional[ActivityTimestamps]): Activity timing information
        type (str): Type of activity
    """

    application_id: int
    assets: Optional[ActivityAssets]
    created_at: datetime
    details: Optional[str]
    name: str
    state: Optional[str]
    timestamps: Optional[ActivityTimestamps]
    type: str


# Spotify Track Model
class SpotifyTrack(BaseModel):
    """
    Represents details about a Spotify track being played.

    Attributes:
        artists (List[str]): List of artist names
        end (datetime): When the track will finish playing
        name (str): Title of the track
        start (datetime): When the track started playing
        url (str): Spotify URL for the track
    """

    artists: List[str]
    end: datetime
    name: str
    start: datetime
    url: str


# Spotify Album Model
class SpotifyAlbum(BaseModel):
    """
    Represents details about a Spotify album.

    Attributes:
        cover_url (str): URL to the album artwork
        name (str): Name of the album
    """

    cover_url: str
    name: str


# Spotify Activity Model
class SpotifyActivity(BaseModel):
    """
    Represents Spotify-specific activity information.

    Attributes:
        color (Color): Color information for the activity
        created_at (datetime): When the activity was first detected
        party_id (str): Unique identifier for the activity
        title (str): Title of the activity
        type (str): Type of activity (default: Spotify)
    """

    color: Color
    created_at: datetime
    party_id: str
    title: str
    type: str = "Spotify"


# Custom Status Model
class CustomStatus(BaseModel):
    """
    Represents a user's custom status with emoji and text.

    Attributes:
        name (str): Name of the custom status
        emoji (str): Emoji associated with the custom status
        state (str): Current state of the custom status
        created_at (datetime): When the custom status was first detected
    """

    name: str
    emoji: str
    state: str
    created_at: datetime


# Spotify Status Model
class SpotifyStatus(BaseModel):
    """
    Represents complete Spotify status including activity, album, and track.

    Attributes:
        activity (SpotifyActivity): Spotify activity information
        album (SpotifyAlbum): Spotify album information
        track (SpotifyTrack): Spotify track information
    """

    activity: SpotifyActivity
    album: SpotifyAlbum
    track: SpotifyTrack


# Active Platforms Model
class ActivePlatforms(BaseModel):
    """
    Indicates which platforms a user is currently active on.

    Attributes:
        desktop (bool): Whether the user is active on desktop
        mobile (bool): Whether the user is active on mobile
        web (bool): Whether the user is active on web
    """

    desktop: bool
    mobile: bool
    web: bool


# Statuses Model
class Statuses(BaseModel):
    """
    Represents user status across different platforms.

    Attributes:
        desktop (str): User's status on desktop
        mobile (str): User's status on mobile
        raw_status (str): Raw status data
        status (str): User's status
        web (str): User's status on web
    """

    desktop: str
    mobile: str
    raw_status: str
    status: str
    web: str


# User Data Model
class UserData(BaseModel):
    """
    Represents comprehensive user profile data.

    Attributes:
        accent_color (Optional[int]): Accent color for the user
        accent_colour (Optional[int]): Accent colour for the user
        avatar (Avatar): User's avatar image information
        avatar_decoration (Optional[str]): Decoration for the user's avatar
        avatar_decoration_sku_id (Optional[Union[str, int]]): SKU identifier for avatar decoration
        banner (Optional[str]): URL to the user's banner image
        color (Color): Color information for the user
        created_at (datetime): When the user account was created
        discriminator (str): Unique discriminator for the user
        display_avatar (str): URL to the user's display avatar
        display_name (str): User's display name
        global_name (str): User's global name
        id (int): Unique identifier for the user
        mention (str): Mention string for the user
        name (str): User's name
        public_flags (int): Public flags associated with the user
    """

    accent_color: Optional[int] = None
    accent_colour: Optional[int] = None
    avatar: Avatar
    avatar_decoration: Optional[str] = None
    avatar_decoration_sku_id: Optional[Union[str, int]] = None
    banner: Optional[str] = None
    color: Color
    created_at: datetime
    discriminator: str
    display_avatar: str
    display_name: str
    global_name: str
    id: int
    mention: str
    name: str
    public_flags: int


# Presence Data Model
class PresenceData(BaseModel):
    """
    Represents user's current presence information including activities and status.

    Attributes:
        active_platforms (ActivePlatforms): Platforms the user is active on
        custom_status (Optional[Union[str, CustomStatus]]): User's custom status
        misc_activities (List[MiscActivity]): List of miscellaneous activities
        spotify_status (Optional[SpotifyStatus]): Spotify status information
        statuses (Statuses): User's status across different platforms
    """

    active_platforms: ActivePlatforms
    custom_status: Optional[Union[str, CustomStatus]] = (
        None  # Can be either string or CustomStatus object
    )
    misc_activities: List[MiscActivity]
    spotify_status: Optional[SpotifyStatus] = None
    statuses: Statuses


# Main Response Model
class WatcherResponse(BaseModel):
    """
    Represents the complete response for a successful watcher request.

    Attributes:
        ok (bool): Indicates whether the request was successful
        presence_data (PresenceData): User's presence data
        user_data (UserData): User's profile data
    """

    ok: bool = True
    presence_data: PresenceData
    user_data: UserData


# Error Response Model
class ErrorResponse(BaseModel):
    """
    Represents the response structure for error cases.

    Attributes:
        ok (bool): Indicates whether the request was successful
        message (str): Error message or guidance
    """

    ok: bool = False
    message: str


# Create router
router = APIRouter(
    tags=["Watcher"],
)


@router.get("/", response_model=ErrorResponse, include_in_schema=False)
async def index():
    """
    Default endpoint handler for the watcher API.

    This endpoint returns an error message when accessed without a specific user ID,
    directing users to consult the API documentation.

    Returns:
        JSONResponse: Error response with a 400 status code and guidance message

    Response Example:
        {
            "ok": False,
            "message": "No user specified, please refer to the documentation for more information."
        }
    """
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "message": "No user specified, please refer to the documentation for more information.",
        },
    )


@router.get(
    "/{discord_id}",
    response_model=WatcherResponse,
    summary="Get User Watcher Data",
    description="""Get a user's presence data from the LDEV Watcher System.
Responses Include:
- User Data (always)
- Presence Data (if available)
- Spotify Status (if available)
- Misc Activities (if available)
- Active Platforms (Desktop, Mobile, Web)
- Statuses (Desktop, Mobile, Web)""",
    responses={
        404: {
            "description": "User Not Found",
            "model": ErrorResponse,
        },
        403: {
            "description": "User Banned or Opted Out",
            "model": ErrorResponse,
        },
    },
)
async def get_user(discord_id: int):
    """Retrieve a user's presence data from the LDEV Watcher System."""
    query = users.find_one({"_id": discord_id})

    if not query:
        raise HTTPException(
            status_code=404,
            detail={
                "ok": False,
                "message": "User Not Found",
            },
        )

    if query.get("banned", False):
        raise HTTPException(
            status_code=403,
            detail={
                "ok": False,
                "message": "User Banned",
            },
        )

    if not query.get("watcher", True):
        raise HTTPException(
            status_code=403,
            detail={
                "ok": False,
                "message": "User opted out of watcher",
            },
        )

    data = query.copy()
    data.pop("_id")
    data["ok"] = True

    return data
