# National Parks Route Planner

A web application for discovering national parks across the United States and Canada and planning road trips between destinations. The application combines interactive maps, park locations, geographic boundaries, user authentication, and route planning.

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Features](#features)
- [Backend](#backend)
  - [Users](#users)
  - [Attractions](#attractions)
  - [Routes](#routes)
  - [Routing Engine](#routing-engine)
- [Frontend](#frontend)
- [API Endpoints](#api-endpoints)
- [Data Sources](#data-sources)
- [Docker Services](#docker-services)
- [Installation and Setup](#installation-and-setup)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)

---

## Overview

The National Parks Route Planner is a web application designed to help users explore national parks and plan road trips across the United States and Canada.

Users can register an account, explore national parks on an interactive map, select destinations, and generate driving routes between multiple locations.

The application displays national park locations and their geographic boundaries, allowing users to explore parks at different zoom levels. When planning a route, the backend identifies national parks located within 25 miles of the planned driving path.

The project uses Django and PostGIS for geographic data processing, while the frontend is built with Svelte 5 and MapLibre GL.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Svelte 5 |
| Build Tool | Vite |
| Routing | svelte-spa-router |
| Map Rendering | MapLibre GL |
| Backend | Django |
| API | Django REST Framework |
| Geographic API | djangorestframework-gis |
| Database | PostgreSQL 16 + PostGIS |
| Authentication | SimpleJWT |
| CORS | django-cors-headers |
| Configuration | python-decouple |
| Geocoding | OpenStreetMap Nominatim |
| Route Calculation | OSRM |
| Containerization | Docker & Docker Compose |

## Architecture

The application follows a frontend/backend architecture.

- **Frontend:** Handles user interaction, authentication, map rendering, and route visualization.
- **Backend:** Provides REST API endpoints, manages application data, handles authentication, and processes route requests.
- **Database:** PostgreSQL with PostGIS stores geographic information, including park locations, boundaries, and routes.
- **External services:** Nominatim is used for geocoding, while the public OSRM service calculates driving routes.

### Application flow

1. The user interacts with the Svelte frontend.
2. The frontend sends requests to the Django REST API.
3. Django processes requests and retrieves or updates data in PostGIS.
4. For route planning, the backend communicates with Nominatim and OSRM.
5. Geographic queries identify national parks near the calculated route.
6. The backend returns the route and nearby parks to the frontend.
7. MapLibre visualizes the geographic data.

## Project Structure

The project is organized into separate frontend and backend applications.

```text
project-root/
│
├── backend/
│   ├── users/
│   ├── attractions/
│   ├── routes/
│   ├── routing_engine/
│   ├── manage.py
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   └── auth.ts
│   │   ├── components/
│   │   ├── routes/
│   │   ├── App.svelte
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── docker-compose.yml
├── .dockerignore
└── README.md
```

The frontend and backend are developed and deployed as separate services using Docker Compose.

---

## Features

### User Authentication

- User registration with first name, last name, email, and password.
- Email-based login.
- JWT access and refresh tokens.
- Authenticated user profile endpoint.
- Logout functionality.

### Interactive Map

- Full-screen MapLibre map.
- National park locations displayed as markers.
- National park boundaries displayed as polygons.
- State and provincial borders from Natural Earth.
- Park details displayed when selecting a park.
- Different map representations depending on zoom level.

### Route Planning

- Enter a starting location.
- Add multiple intermediate stops.
- Select a destination.
- Optionally create a circular route that returns to the starting point.
- Geocode entered locations.
- Calculate driving routes using OSRM.
- Display the resulting route on the map.
- Identify national parks within 25 miles of the route.

### Geographic Data

- National parks across the United States and Canada.
- Geographic point locations.
- National park boundary polygons.
- Spatial queries using PostGIS.

---

## Backend

The backend is built with Django and Django REST Framework. It is divided into four main applications.

### Users

The `users` application handles user registration, authentication, and user information.

#### User Model

The application uses a custom Django user model based on `AbstractUser`.

Additional characteristics:

- Unique email address.
- Built-in `first_name` and `last_name` fields.
- Automatically generated username based on the user's email address.
- Email-based authentication.

#### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/users/register/` | Register a new user |
| GET | `/api/users/me/` | Retrieve the authenticated user's information |
| POST | `/api/token/` | Obtain JWT tokens using email and password |
| POST | `/api/token/refresh/` | Refresh an access token |

Authentication is implemented using SimpleJWT.

### Attractions

The `attractions` application manages national park information and geographic data.

#### Models

**Attraction**

The base model for attractions.

Fields include:

- `name`
- `description`
- `location` — geographic point
- `country`

**NationalPark**

Extends the `Attraction` model with additional national park information.

Additional fields:

- `boundary` — nullable MultiPolygon
- `state`
- `code` — unique park identifier

#### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/attractions/parks/` | Retrieve national parks as GeoJSON points |
| GET | `/api/attractions/parks/boundaries/` | Retrieve national park boundaries as GeoJSON polygons |

#### Management Commands

The application includes management commands for importing geographic data.

| Command | Description |
|---|---|
| `seed_parks` | Imports the 60 US national parks using the NPS API |
| `seed_park_boundaries` | Imports US national park boundaries using the NPS mapdata endpoint |
| `seed_canadian_parks` | Imports approximately 41 Canadian national parks from a static dataset |
| `seed_canadian_park_boundaries` | Imports Canadian park boundaries from an NRCAN ArcGIS layer |

The Canadian park locations currently use approximate coordinates from a static dataset.

### Routes

The `routes` application handles route creation and geographic route analysis.

#### Models

**Route**

Stores a planned route.

Fields include:

- `user` — owner of the route
- `name` — route name
- `start` — starting location
- `end` — destination
- `cyclic` — indicates whether the route returns to its starting point
- `path` — nullable LineString containing the calculated route geometry

**RouteStop**

Stores intermediate waypoints belonging to a route in a defined order.

#### Route Planning Endpoint

`POST /api/routes/plan/`

The `PlanRouteView` handles the complete route planning process.

The process consists of the following steps:

1. Geocode every submitted location using Nominatim.
2. Retrieve geographic coordinates for each location.
3. Send the coordinates to OSRM.
4. Retrieve the driving route geometry.
5. Save the route and its associated information.
6. Search for national parks within 25 miles of the route.
7. Return the calculated route and nearby parks to the frontend.

The response includes the route geometry and a `nearby_parks` collection.

### Routing Engine

The `routing_engine` application contains external service integrations.

It currently does not contain database models.

#### Geocoding

`geocoding.py`

Uses the OpenStreetMap Nominatim service to convert place names into geographic coordinates.

Geocoding is restricted to locations in:

- United States
- Canada

#### Route Calculation

`osrm_client.py`

Communicates with the public OSRM routing service:

`https://router.project-osrm.org`

OSRM calculates driving routes between the submitted coordinates and returns the route geometry.

The returned geometry is stored as a LineString and used for map visualization and spatial analysis.

---

## Frontend

The frontend is built with Svelte 5 and Vite. It uses `svelte-spa-router` for client-side navigation and MapLibre GL for map rendering.

### App.svelte

The main application component.

Responsibilities:

- Displays the application header and logo.
- Provides the router outlet.
- Handles the main application layout.

### Authentication

Authentication functionality is centralized in:

`src/lib/auth.ts`

The module provides:

- `register()` — creates a new user account.
- `login()` — authenticates a user using email and password.
- `fetchMe()` — retrieves the authenticated user's information.
- `logout()` — clears the current authentication state.

The access token and current user are stored in Svelte stores.

The login and registration pages provide card-based forms.

**Login**

- Email
- Password

**Registration**

- First name
- Last name
- Email
- Password
- Password confirmation

### Dashboard

The dashboard is the main application interface.

It contains an interactive MapLibre map and a route planning panel.

#### Map

The map displays:

- US state boundaries.
- Canadian provincial boundaries.
- National park locations.
- National park boundary polygons.
- Calculated driving routes.

The map uses Natural Earth geographic data for state and provincial borders.

#### National Park Visualization

The map changes how national parks are displayed depending on the current zoom level.

| Zoom Level | Visualization |
|---|---|
| Below zoom 6 | Orange markers representing park locations |
| Zoom 6 and above | Green polygons representing park boundaries |

Selecting a park opens its details in the left-hand panel.

#### Route Builder

The left-hand panel contains the route planning interface.

Users can:

- Enter a starting location.
- Add intermediate stops.
- Enter a destination.
- Enable the return-to-start option.
- Generate a driving route.

After route calculation, the route geometry is displayed on the map.

#### User Information

A user card in the top-right corner displays:

- The authenticated user's first name.
- A logout button.

#### Loading State

A loading overlay is displayed while the application retrieves its initial geographic data.

---

## API Endpoints

The following endpoints are currently implemented.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/users/register/` | User registration |
| GET | `/api/users/me/` | Current user information |
| POST | `/api/token/` | Login and JWT token generation |
| POST | `/api/token/refresh/` | Refresh JWT access token |
| GET | `/api/attractions/parks/` | Retrieve park locations |
| GET | `/api/attractions/parks/boundaries/` | Retrieve park boundaries |
| POST | `/api/routes/plan/` | Plan and save a driving route |

Geographic endpoints return GeoJSON data where applicable.

---

## Data Sources

The application uses several external geographic data sources.

| Source | Usage |
|---|---|
| National Park Service (NPS) API | US national park information |
| NPS Map Data | US national park boundaries |
| Natural Resources Canada (NRCAN) ArcGIS | Canadian national park boundaries |
| Static Canadian park dataset | Canadian park information and approximate coordinates |
| Natural Earth | State and provincial boundaries |
| OpenStreetMap Nominatim | Geocoding |
| OSRM | Driving route calculation |

External services are accessed through the backend, keeping the frontend independent of their individual APIs.

---

## Docker Services

The application uses Docker Compose to manage its main services.

| Service | Description |
|---|---|
| `db` | PostgreSQL 16 with PostGIS |
| `backend` | Django REST API |
| `frontend` | Svelte 5 and Vite frontend |
| `osrm` | Previously used local OSRM service; currently unused |

Route calculation now uses the public OSRM server rather than the local Docker service.

The root `.dockerignore` excludes unnecessary files and directories, including:

- `frontend/node_modules`
- `backend/osrm-data`
- Other development-only files

This keeps Docker build contexts smaller and improves build performance.

---

## Installation and Setup

### Prerequisites

Make sure the following tools are installed:

- Docker
- Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Configure Environment Variables

Create the required environment files for the backend and frontend.

The backend uses `python-decouple` to load configuration.

Make sure the configuration includes the required database connection, Django settings, and external service settings.

Do not commit secret keys, passwords, or other sensitive environment variables to GitHub.

### 3. Start the Application

Build and start the Docker services:

```bash
docker compose up --build
```

### 4. Initialize the Database

Apply Django migrations:

```bash
docker compose exec backend python manage.py migrate
```

### 5. Import National Park Data

Import US national parks:

```bash
docker compose exec backend python manage.py seed_parks
```

Import US park boundaries:

```bash
docker compose exec backend python manage.py seed_park_boundaries
```

Import Canadian national parks:

```bash
docker compose exec backend python manage.py seed_canadian_parks
```

Import Canadian park boundaries:

```bash
docker compose exec backend python manage.py seed_canadian_park_boundaries
```

### 6. Access the Application

Once the containers are running, access the frontend through the port configured in Docker Compose.

The Django API is available through the backend service.

---

## Known Limitations

The following issues and limitations are currently known.

### Authentication Persistence

JWT tokens are currently stored in memory using Svelte stores.

Refreshing the browser clears the authentication state, requiring the user to log in again.

### Nearby Parks Display

The route planning API already returns a `nearby_parks` collection.

However, the frontend does not yet display these parks in a dedicated list.

### Park Proximity Calculation

Nearby park detection currently measures the distance between the route and each park's centre point.

This means large national parks may be missed if their geographic boundaries are close to the route but their centre points are further away.

A spatial query against the actual park polygons would provide more accurate results.

### Missing Canadian Park Boundaries

Four Canadian national parks currently do not have boundary polygons:

- Kluane
- Thaidene Nene
- Nááts'ihch'oh
- Qausuittuq

Additionally, Sequoia National Park and Kings Canyon National Park are currently represented as one combined record.

### External OSRM Dependency

The application currently uses the public OSRM routing server.

This is suitable for development, but it introduces potential limitations:

- Rate limits.
- No guaranteed uptime.
- Dependency on an external service.

A dedicated routing instance may be required for production use.

### Geographic Data Performance

National park boundary GeoJSON payloads can be relatively large.

The initial loading overlay hides much of the loading process, but the underlying data transfer can still be optimized.

A potential improvement is server-side geometry simplification using PostGIS:

`ST_SimplifyPreserveTopology`

This would reduce payload sizes while preserving the general shape and topology of park boundaries.

---

## Future Improvements

The following improvements are planned or under consideration.

### High Priority

- Persist authentication state across browser refreshes.
- Display nearby parks returned by the route planning API.
- Improve park proximity detection by measuring against park boundary polygons.
- Simplify geographic boundary data on the backend.
- Improve loading performance for large GeoJSON datasets.

### Geographic Data Expansion

- Add provincial and territorial parks in Canada.
- Obtain accurate geographic boundaries for currently incomplete park records.
- Improve the accuracy and consistency of Canadian park coordinates.
- Separate Sequoia and Kings Canyon into individual park records where appropriate.

### Routing Improvements

- Evaluate a self-hosted OSRM instance or another routing provider.
- Improve route error handling.
- Add route editing and management functionality.
- Improve the presentation of parks along planned routes.

### Frontend Improvements

- Improve the nearby parks interface.
- Add saved routes and route history.
- Improve the overall map interaction experience.
- Add more detailed park information.

---

## Project Status

The application currently supports user authentication, interactive national park exploration, geographic boundary visualization, and multi-stop driving route planning.

The backend can identify nearby national parks along a planned route, although the frontend integration and geographic proximity calculations still need improvement.

The next development phase will focus on expanding geographic coverage, improving route-based park discovery, and optimizing application performance.
