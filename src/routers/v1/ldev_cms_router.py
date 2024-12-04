"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

import os
import re
import logging
from datetime import datetime
from typing import List, Optional
import httpx
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import contentful

from helpers.api_keys import APIKeyHelper
from helpers.api_logs import APILogHelper


# Load environment variables
load_dotenv(override=True)

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


class GitHubCommit(BaseModel):
    """
    Represents a GitHub commit.

    Attributes:
        sha (str): The commit hash
        message (str): The commit message
        author_name (str): Name of the commit author
        author_email (str): Email of the commit author
        date (datetime): When the commit was made
        url (str): URL to view the commit on GitHub
    """

    sha: str
    message: str
    author_name: str
    author_email: str
    date: datetime
    url: str


class CommitsResponse(BaseModel):
    """
    Response model for the commits endpoint.

    Attributes:
        project_title (str): Title of the project
        repository_url (str): URL of the GitHub repository
        commits (List[GitHubCommit]): List of recent commits
    """

    project_title: str
    repository_url: str
    commits: List[GitHubCommit]


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
    # logger.info("Available fields: %s", dir(entry))
    # logger.info("Raw entry: %s", entry)

    # Try to access fields using raw fields
    fields = entry.raw["fields"]
    # logger.info("Raw fields: %s", fields)

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


def parse_github_url(url: str) -> tuple[str, str]:
    """
    Parse a GitHub repository URL to extract owner and repo name.

    Args:
        url (str): GitHub repository URL

    Returns:
        tuple[str, str]: Repository owner and name

    Raises:
        ValueError: If the URL is not a valid GitHub repository URL
    """
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub repository URL")
    return match.group(1), match.group(2)


# Route Endpoints
@router.get("/", include_in_schema=False)
async def index(
    background_tasks: BackgroundTasks,
    api_key: str = Query(..., description="API key for authentication"),
):
    """Default endpoint that returns an error message directing users to the documentation."""
    status_code = 400
    error_message = (
        "No route specified, please refer to the documentation for more information."
    )
    key_id = None

    try:
        if not await APIKeyHelper.has_role(api_key, "cms"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

        return JSONResponse(
            status_code=status_code,
            content={
                "ok": False,
                "message": error_message,
            },
        )
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        error_message = str(e)
        raise
    finally:
        background_tasks.add_task(
            APILogHelper.log_request,
            key_id=key_id,
            route="/cms/",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )


@router.get(
    "/people",
    response_model=List[Person],
    summary="Get All People",
    description="Get all people from the LDEV CMS.",
)
async def get_people(
    background_tasks: BackgroundTasks,
    api_key: str = Query(..., description="API key for authentication"),
):
    status_code = 200
    error_message = None
    key_id = None

    try:
        if not await APIKeyHelper.has_role(api_key, "cms"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

        entries = client.entries({"content_type": "person"})
        return [format_person(entry) for entry in entries]
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        error_message = str(e)
        raise HTTPException(
            status_code=status_code,
            detail=f"Error fetching people from Contentful: {str(e)}",
        ) from e
    finally:
        background_tasks.add_task(
            APILogHelper.log_request,
            key_id=key_id,
            route="/cms/people",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )


@router.get(
    "/people/{slug}",
    response_model=Person,
    summary="Get Person",
    description="Get a specific person by their slug.",
)
async def get_person(
    slug: str,
    background_tasks: BackgroundTasks,
    api_key: str = Query(..., description="API key for authentication"),
):
    status_code = 200
    error_message = None
    key_id = None

    try:
        if not await APIKeyHelper.has_role(api_key, "cms"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

        entries = client.entries({"content_type": "person", "fields.slug": slug})
        if not entries:
            raise HTTPException(status_code=404, detail="Person not found")
        return format_person(entries[0])
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        error_message = str(e)
        raise
    finally:
        background_tasks.add_task(
            APILogHelper.log_request,
            key_id=key_id,
            route=f"/cms/people/{slug}",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )


@router.get(
    "/projects",
    response_model=List[Project],
    summary="Get All Projects",
    description="Get all projects from the LDEV CMS.",
)
async def get_projects(
    background_tasks: BackgroundTasks,
    api_key: str = Query(..., description="API key for authentication"),
):
    status_code = 200
    error_message = None
    key_id = None

    try:
        if not await APIKeyHelper.has_role(api_key, "cms"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

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
        status_code = getattr(e, "status_code", 500)
        error_message = str(e)
        raise HTTPException(
            status_code=status_code,
            detail=f"Error fetching projects from Contentful: {str(e)}",
        ) from e
    finally:
        background_tasks.add_task(
            APILogHelper.log_request,
            key_id=key_id,
            route="/cms/projects",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )


@router.get(
    "/projects/{slug}",
    response_model=Project,
    summary="Get Project",
    description="Get a specific project by its slug.",
)
async def get_project(
    slug: str,
    background_tasks: BackgroundTasks,
    api_key: str = Query(..., description="API key for authentication"),
):
    status_code = 200
    error_message = None
    key_id = None

    try:
        if not await APIKeyHelper.has_role(api_key, "cms"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

        entries = client.entries({"content_type": "project", "fields.slug": slug})
        if not entries:
            raise HTTPException(status_code=404, detail="Project not found")
        return format_project(entries[0])
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        error_message = str(e)
        raise
    finally:
        background_tasks.add_task(
            APILogHelper.log_request,
            key_id=key_id,
            route=f"/cms/projects/{slug}",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )


@router.get(
    "/projects/{slug}/commits",
    response_model=CommitsResponse,
    summary="Get Project Commits",
    description="Get the latest commits for a project's GitHub repository.",
)
async def get_project_commits(
    slug: str,
    background_tasks: BackgroundTasks,
    api_key: str = Query(..., description="API key for authentication"),
    limit: int = 10,
):
    status_code = 200
    error_message = None
    key_id = None

    try:
        if not await APIKeyHelper.has_role(api_key, "cms"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

        entries = client.entries({"content_type": "project", "fields.slug": slug})
        if not entries:
            raise HTTPException(status_code=404, detail="Project not found")

        project = entries[0]
        github_url = project.raw["fields"].get("githubRepoUrl")

        if not github_url:
            raise HTTPException(
                status_code=400,
                detail="Project does not have an associated GitHub repository",
            )

        try:
            owner, repo = parse_github_url(github_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token not configured")

        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                headers={
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                params={"per_page": limit},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"GitHub API error: {response.text}",
                )

            commits_data = response.json()

        commits = []
        for commit in commits_data:
            commits.append(
                GitHubCommit(
                    sha=commit["sha"],
                    message=commit["commit"]["message"],
                    author_name=commit["commit"]["author"]["name"],
                    author_email=commit["commit"]["author"]["email"],
                    date=datetime.fromisoformat(
                        commit["commit"]["author"]["date"].replace("Z", "+00:00")
                    ),
                    url=commit["html_url"],
                )
            )

        return CommitsResponse(
            project_title=project.title, repository_url=github_url, commits=commits
        )

    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        error_message = str(e)
        logger.error("Error fetching commits: %s", str(e))
        raise HTTPException(
            status_code=status_code, detail=f"Error fetching commits: {str(e)}"
        ) from e
    finally:
        background_tasks.add_task(
            APILogHelper.log_request,
            key_id=key_id,
            route=f"/cms/projects/{slug}/commits",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )
