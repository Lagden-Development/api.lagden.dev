"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import contentful
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a router
router = APIRouter()


# Pydantic models for response validation
class Link(BaseModel):
    url: str
    name: str


class Person(BaseModel):
    name: str
    slug: str
    occupation: str
    location: str
    pronouns: str
    skills: List[str]
    links: List[Link]
    introduction: dict  # RichText content will be returned as a dict
    picture_url: str


class Project(BaseModel):
    title: str
    slug: str
    description: str
    tags: List[str]
    githubRepoUrl: Optional[str] = None
    websiteUrl: Optional[str] = None
    projectReadme: dict  # RichText content will be returned as a dict
    picture_url: str
    betterStackStatusId: Optional[str] = None
    isFeatured: bool


# Initialize Contentful client
client = contentful.Client(
    space_id=os.getenv("CONTENTFUL_SPACE_ID"),
    access_token=os.getenv("CONTENTFUL_ACCESS_TOKEN"),
)


def format_person(entry) -> Person:
    """Format a Contentful person entry into our Person model."""
    # Convert links from Contentful format to our Link model format
    formatted_links = []
    for link_data in entry.links:
        formatted_links.append(Link(url=link_data["url"], name=link_data["name"]))

    return Person(
        name=entry.name,
        slug=entry.slug,
        occupation=entry.occupation,
        location=entry.location,
        pronouns=entry.pronouns,
        skills=entry.skills,
        links=formatted_links,
        introduction=entry.introduction,
        picture_url=entry.picture.url(),
    )


def format_project(entry) -> Project:
    """Format a Contentful project entry into our Project model."""
    # Debug: Log available fields
    logger.info(f"Available fields: {dir(entry)}")
    logger.info(f"Raw entry: {entry}")

    # Try to access fields using raw fields
    fields = entry.raw["fields"]
    logger.info(f"Raw fields: {fields}")

    return Project(
        title=entry.title,
        slug=entry.slug,
        description=entry.description,
        tags=entry.tags,
        githubRepoUrl=fields.get("githubRepoUrl", None),
        websiteUrl=fields.get("websiteUrl", None),
        projectReadme=entry.project_readme,
        picture_url=entry.picture.url(),
        betterStackStatusId=fields.get("betterStackStatusId", None),
        isFeatured=fields.get("isFeatured", False),
    )


# Route Endpoints
@router.get("/", include_in_schema=False)
async def index():
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "message": "No route specified, please refer to the documentation for more information.",
        },
    )


@router.get(
    "/people",
    response_model=List[Person],
    tags=["LDEV CMS"],
    summary="Get All People",
    description="Get all people from the LDEV CMS.",
)
async def get_people():
    """
    Retrieve all people from Contentful CMS.
    Returns a list of person entries with their complete information.
    """
    try:
        entries = client.entries({"content_type": "person"})
        return [format_person(entry) for entry in entries]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching people from Contentful: {str(e)}"
        )


@router.get(
    "/people/{slug}",
    response_model=Person,
    tags=["LDEV CMS"],
    summary="Get Person",
    description="Get a specific person by their slug.",
)
async def get_person(slug: str):
    """
    Retrieve a specific person by their slug.
    Returns the complete information for a single person.
    """
    try:
        entries = client.entries({"content_type": "person", "fields.slug": slug})

        if not entries:
            raise HTTPException(status_code=404, detail="Person not found")

        return format_person(entries[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching person from Contentful: {str(e)}"
        )


@router.get(
    "/projects",
    response_model=List[Project],
    tags=["LDEV CMS"],
    summary="Get All Projects",
    description="Get all projects from the LDEV CMS.",
)
async def get_projects():
    """
    Retrieve all projects from Contentful CMS.
    Returns a list of project entries with their complete information.
    """
    try:
        entries = client.entries({"content_type": "project"})
        formatted_projects = []
        for entry in entries:
            try:
                formatted_projects.append(format_project(entry))
            except Exception as e:
                logger.error(f"Error formatting project: {e}")
                raise
        return formatted_projects
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching projects from Contentful: {str(e)}"
        )


@router.get(
    "/projects/{slug}",
    response_model=Project,
    tags=["LDEV CMS"],
    summary="Get Project",
    description="Get a specific project by its slug.",
)
async def get_project(slug: str):
    """
    Retrieve a specific project by its slug.
    Returns the complete information for a single project.
    """
    try:
        entries = client.entries({"content_type": "project", "fields.slug": slug})

        if not entries:
            raise HTTPException(status_code=404, detail="Project not found")

        return format_project(entries[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching project from Contentful: {str(e)}"
        )
