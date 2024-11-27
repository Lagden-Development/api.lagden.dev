"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from db import users


# Color Model
class Color(BaseModel):
    r: int
    g: int
    b: int
    hex: str


# Avatar Model
class Avatar(BaseModel):
    key: str
    url: str


# Activity Assets Model
class ActivityAssets(BaseModel):
    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]


# Activity Timestamps Model
class ActivityTimestamps(BaseModel):
    end: Optional[datetime] = None
    start: Optional[int] = None


# Misc Activity Model
class MiscActivity(BaseModel):
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
    artists: List[str]
    end: datetime
    name: str
    start: datetime
    url: str


# Spotify Album Model
class SpotifyAlbum(BaseModel):
    cover_url: str
    name: str


# Spotify Activity Model
class SpotifyActivity(BaseModel):
    color: Color
    created_at: datetime
    party_id: str
    title: str
    type: str = "Spotify"


# Custom Status Model
class CustomStatus(BaseModel):
    name: str
    emoji: str
    state: str
    created_at: datetime


# Spotify Status Model
class SpotifyStatus(BaseModel):
    activity: SpotifyActivity
    album: SpotifyAlbum
    track: SpotifyTrack


# Active Platforms Model
class ActivePlatforms(BaseModel):
    desktop: bool
    mobile: bool
    web: bool


# Statuses Model
class Statuses(BaseModel):
    desktop: str
    mobile: str
    raw_status: str
    status: str
    web: str


# User Data Model
class UserData(BaseModel):
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
    active_platforms: ActivePlatforms
    custom_status: Optional[Union[str, CustomStatus]] = (
        None  # Can be either string or CustomStatus object
    )
    misc_activities: List[MiscActivity]
    spotify_status: Optional[SpotifyStatus] = None
    statuses: Statuses


# Main Response Model
class WatcherResponse(BaseModel):
    ok: bool = True
    presence_data: PresenceData
    user_data: UserData


# Error Response Model
class ErrorResponse(BaseModel):
    ok: bool = False
    message: str


# Create router
router = APIRouter()


@router.get("/", response_model=ErrorResponse, include_in_schema=False)
async def index():
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
    tags=["Watcher"],
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
