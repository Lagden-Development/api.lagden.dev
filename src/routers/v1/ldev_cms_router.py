"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

import os
import logging
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import contentful

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a router
router = APIRouter(
    tags=["LDEV CMS"],
)


# Pydantic models for response validation
class Link(BaseModel):
    """
    Represents a hyperlink with a name and URL.

    Attributes:
        url (str): The URL of the link
        name (str): The display name of the link
    """

    url: str
    name: str


class Person(BaseModel):
    """
    Represents a person's profile with their personal and professional information.

    Attributes:
        name (str): The person's full name
        slug (str): URL-friendly version of the name
        occupation (str): The person's job title or role
        location (str): The person's geographical location
        pronouns (str): The person's preferred pronouns
        skills (List[str]): List of the person's skills or expertise
        links (List[Link]): List of relevant links (e.g., social media, portfolio)
        introduction (dict): Rich text content containing the person's introduction
        picture_url (str): URL to the person's profile picture
    """

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
    """
    Represents a project with its details and metadata.

    Attributes:
        title (str): The project's title
        slug (str): URL-friendly version of the title
        description (str): Brief description of the project
        tags (List[str]): List of technology tags or categories
        github_repo_url (Optional[str]): URL to the project's GitHub repository
        website_url (Optional[str]): URL to the project's live website
        project_readme (dict): Rich text content containing the project's README
        picture_url (str): URL to the project's cover image or logo
        better_stack_status_id (Optional[str]): BetterStack status page ID
        is_featured (bool): Whether the project is featured
    """

    title: str
    slug: str
    description: str
    tags: List[str]
    github_repo_url: Optional[str] = None
    website_url: Optional[str] = None
    project_readme: dict  # RichText content will be returned as a dict
    picture_url: str
    better_stack_status_id: Optional[str] = None
    is_featured: bool


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
    logger.info("Available fields: %s", dir(entry))
    logger.info("Raw entry: %s", entry)

    # Try to access fields using raw fields
    fields = entry.raw["fields"]
    logger.info("Raw fields: %s", fields)

    return Project(
        title=entry.title,
        slug=entry.slug,
        description=entry.description,
        tags=entry.tags,
        github_repo_url=fields.get("githubRepoUrl", None),
        website_url=fields.get("websiteUrl", None),
        project_readme=entry.project_readme,
        picture_url=entry.picture.url(),
        better_stack_status_id=fields.get("betterStackStatusId", None),
        is_featured=fields.get("isFeatured", False),
    )


# Route Endpoints
@router.get("/", include_in_schema=False)
async def index():
    """
    Default endpoint that returns an error message directing users to the documentation.

    Returns:
        JSONResponse: A 400 error response with a message directing users to the documentation.
    """
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "message": "No route specified, please refer to the documentation for more "
            "information.",
        },
    )


@router.get(
    "/people",
    response_model=List[Person],
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
        ) from e


@router.get(
    "/people/{slug}",
    response_model=Person,
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
        ) from e


@router.get(
    "/projects",
    response_model=List[Project],
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
                logger.error("Error formatting project: %s", str(e))
                raise
        return formatted_projects
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching projects from Contentful: {str(e)}"
        ) from e


@router.get(
    "/projects/{slug}",
    response_model=Project,
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
        ) from e
