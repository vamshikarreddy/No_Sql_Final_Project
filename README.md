# Orbit — Campus Discovery

Orbit — Campus Discovery is a web application developed for the NoSQL Development Project. It allows a university campus to manage users, events and event registrations while demonstrating practical MongoDB document modelling, CRUD operations, array operations, referencing, embedding and aggregation pipelines.

The redesigned interface uses horizontal navigation, a mission-control dashboard, science event cards, and a navy, blue and coral visual theme. All figures are calculated from MongoDB. The fictional Orbit dataset uses a separate `orbit_campus` database, preserving existing `gather_collective` and `campus_events` data. Event dates are relative to the day the seed script runs.

Fresh desktop and mobile screenshots are available in `report/orbit-screenshots/`. The existing PDF and older screenshots in `report/` document the earlier interface; the updated LaTeX source is in `report/overleaf-gather/main.tex`; compile it in Overleaf for the current report.

## Author

Sai Kishan Kumar

## Technology Stack

- Python
- FastAPI
- MongoDB
- PyMongo
- Jinja2
- HTML
- CSS
- Bootstrap
- JavaScript
- Pytest

## Main Features

### Dashboard

- Total number of users
- Total number of events
- Upcoming-event count
- Past-event count
- Next five events

### Events

- List all events
- Search by title or description
- Filter by category, tag and status
- Sort by date, title or capacity
- Create, edit and delete events
- Display embedded locations and tags
- View event details and organizer information
- Manage event registrations
- Prevent duplicate registrations
- Enforce event capacity

### Users

- List all users
- Search by name or email
- Filter by department and role
- Display interests and registration counts
- Create and edit users
- Handle duplicate email addresses
- View participation history
- Display upcoming and past registration counts
- Prevent deletion when a user is referenced by an event

### Analytics

The Analytics page contains the six required MongoDB analyses:

1. Confirmed registrations by category
2. Top five most popular events
3. Users with no registrations
4. Events above average occupancy
5. Most-used event tags
6. Events grouped by month

## MongoDB Document Model

The application uses two collections:

- `users`
- `events`

Locations and registrations are embedded inside event documents. Organizers and registered participants are referenced using user `ObjectId` values.

Example registration:

```javascript
{
  userId: ObjectId("..."),
  registeredAt: ISODate("..."),
  status: "confirmed"
}
```

## MongoDB Operations Demonstrated

The source code includes:

- `find`
- `find_one`
- `insert_one`
- `insert_many`
- `update_one`
- `delete_one`
- `delete_many`
- Projections
- Regular-expression searches
- Comparison and logical operators
- Array queries
- `$set`
- `$addToSet`
- `$pull`
- `$match`
- `$project`
- `$group`
- `$sort`
- `$unwind`
- `$lookup`
- `$sum`
- `$avg`
- `$size`
- `$filter`
- `$expr`
- Calculated occupancy percentages

## Project Structure

```text
NoSql_Project/
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   ├── events.py
│   │   └── users.py
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   ├── templates/
│   │   ├── analytics.html
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── error.html
│   │   ├── event_detail.html
│   │   ├── event_form.html
│   │   ├── events.html
│   │   ├── placeholder.html
│   │   ├── user_detail.html
│   │   ├── user_form.html
│   │   └── users.html
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── scripts/
│   ├── __init__.py
│   ├── initialize_database.py
│   └── seed_database.py
├── tests/
│   ├── __init__.py
│   └── test_pages.py
├── report/
│   └── report.pdf
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Prerequisites

Install the following before running the application:

- Python 3.9 or newer
- MongoDB Community Server
- MongoDB Shell
- Git

Verify the installations:

```bash
python3 --version
mongosh --version
git --version
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Sai-kishan-K/no-sql-project.git
cd NoSql_Project
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## MongoDB Configuration

Start MongoDB on macOS when installed through Homebrew:

```bash
brew services start mongodb-community
```

Copy the example environment file:

```bash
cp .env.example .env
```

The default local configuration is:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=orbit_campus
APP_NAME=Orbit — Campus Discovery
DEBUG=false
```

Passwords and connection secrets must remain only in `.env`. The `.env` file is excluded from Git.

## Database Initialization

Create or update the collections, validation rules and indexes:

```bash
python -m scripts.initialize_database
```

This creates:

- `users` collection
- `events` collection
- JSON Schema validators
- Unique user email index
- Event date, category, tag and organizer indexes

## Seed Data

Load the reproducible demonstration dataset:

```bash
python -m scripts.seed_database
```

The seed script inserts:

- 42 users
- 30 events
- Multiple departments and roles
- Multiple categories and tags
- Past and future events
- Events with and without registrations
- 445 embedded registrations
- 11 past and 19 future events at seed time
- 7 programme categories, three full events, three unbooked events, and six members without registrations

The seed script resets only the project’s `users` and `events` collections before reinserting the dataset.

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Main pages:

| Page | URL |
|---|---|
| Dashboard | `http://127.0.0.1:8000/` |
| Events | `http://127.0.0.1:8000/events` |
| Users | `http://127.0.0.1:8000/users` |
| Analytics | `http://127.0.0.1:8000/analytics` |
| Health check | `http://127.0.0.1:8000/health` |
| API documentation | `http://127.0.0.1:8000/docs` |

## Running the Tests

Ensure MongoDB is running and the seed data has been loaded.

Run:

```bash
pytest -v
```

The tests verify:

- MongoDB health
- Dashboard
- Event listing, search and filters
- Event creation page
- User listing and search
- User creation page
- Analytics page
- Static files
- Invalid IDs
- Custom 404 handling
- Replacement dataset integrity and date/reference consistency
- Every seeded event and member detail/edit page
- User and event creation, editing, deletion, and duplicate emails
- Registration, duplicate booking, capacity enforcement, cancellation, and referenced-user protection
- Status filters and empty results

## Reproducing the Project

From a clean clone:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.initialize_database
python -m scripts.seed_database
uvicorn app.main:app --reload
```

The application will then be available at:

```text
http://127.0.0.1:8000
```

## Security and Scope

Authentication, payments, email verification, real-time notifications, Docker and cloud deployment are outside the scope of this academic project. Database credentials and secrets are never committed to the repository.