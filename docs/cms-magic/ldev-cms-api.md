# 📚 LDEV CMS API

Access content from the Lagden Development CMS including team members and projects! Our CMS API provides easy access to structured content about our people and projects.

### 🎯 Available Endpoints

#### People Endpoints

**1. Get All People**

```
GET /ldev-cms/people
```

Fetch all team members and their detailed profiles. Perfect for team pages and directory listings!

**2. Get Specific Person**

```
GET /ldev-cms/people/{slug}
```

Get detailed information about a specific team member using their unique slug.

#### Project Endpoints

**1. Get All Projects**

```
GET /ldev-cms/projects
```

Retrieve all projects in the CMS. Great for portfolio pages and project showcases!

**2. Get Specific Project**

```
GET /ldev-cms/projects/{slug}
```

Get comprehensive information about a specific project using its unique slug.

### 📊 Response Models

#### Person Model

```json
{
    "name": "Jane Doe",
    "slug": "jane-doe",
    "occupation": "Full Stack Developer",
    "location": "Stockholm, Sweden",
    "pronouns": "she/her",
    "skills": ["Python", "React", "Docker"],
    "links": [
        {
            "url": "https://github.com/janedoe",
            "name": "GitHub"
        }
    ],
    "introduction": {
        "content": [
            // Rich text content
        ]
    },
    "picture_url": "https://images.ctfassets.net/..."
}
```

#### Project Model

```json
{
    "title": "Cool Project",
    "slug": "cool-project",
    "description": "A really cool project",
    "tags": ["Python", "FastAPI", "React"],
    "github_repo_url": "https://github.com/org/repo",
    "website_url": "https://project.com",
    "project_readme": {
        "content": [
            // Rich text content
        ]
    },
    "picture_url": "https://images.ctfassets.net/...",
    "better_stack_status_id": "abc123",
    "is_featured": true
}
```

### 🎯 Examples

#### Fetch All Team Members

```bash
GET /ldev-cms/people
```

#### Get Specific Team Member

```bash
GET /ldev-cms/people/jane-doe
```

#### Fetch All Projects

```bash
GET /ldev-cms/projects
```

#### Get Specific Project

```bash
GET /ldev-cms/projects/cool-project
```

### ❌ Error Responses

#### Not Found (404)

When requesting a specific person or project that doesn't exist:

```json
{
    "detail": "Person not found"
}
```

```json
{
    "detail": "Project not found"
}
```

#### Server Error (500)

When there's an issue fetching data from Contentful:

```json
{
    "detail": "Error fetching data from Contentful: [error details]"
}
```

### 💡 Field Details

#### Person Fields

- `slug`: URL-friendly version of the name
- `occupation`: Current role or job title
- `location`: Geographical location
- `pronouns`: Preferred pronouns
- `skills`: Array of technical skills
- `links`: Array of relevant URLs (portfolio, social media, etc.)
- `introduction`: Rich text content about the person
- `picture_url`: Profile image URL

#### Project Fields

- `slug`: URL-friendly version of title
- `description`: Brief project overview
- `tags`: Technologies used
- `github_repo_url`: Optional GitHub repository link
- `website_url`: Optional live project link
- `project_readme`: Rich text project documentation
- `picture_url`: Project image URL
- `better_stack_status_id`: Optional status page identifier
- `is_featured`: Boolean for featured projects

### 🔮 Tips

- Use slugs for consistent URL structures
- Rich text content comes as structured JSON
- Images are served via Contentful's CDN
- Featured projects can be filtered using the `is_featured` field

Need help or found a bug? Contact the dev team! 🚀
