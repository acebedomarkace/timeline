# Gemini Project Context: HS Portfolio App

This document provides context for the "HS Portfolio App" project.

## Project Overview

This is a Django-based web application designed as a multi-tenant portfolio system. The core concept revolves around "Families" as tenants, where each family has its own isolated space for managing posts, presentations, and portfolios. The application supports user authentication, different user roles (e.g., teacher, student), and a public-facing timeline.

Development plans indicate a shift from a single-user-group application to a multi-tenant SaaS application.

## Tech Stack

- **Backend:** Django
- **Frontend:** Django Templates, Bootstrap 5
- **Database:** SQLite (for development)

## Dependencies

- `asgiref==3.9.1`
- `Django==5.2.6`
- `pillow==11.3.0`
- `sqlparse==0.5.3`
- `crispy-forms`
- `crispy-bootstrap5`

## Project Structure

- **Django Project:** `timeline_project`
- **Django App:** `blog`
- **Static Files:** Stored in the `static/` directory.
- **Templates:** Located within `blog/templates/`.
- **Media Files:** Uploaded to the `media/` directory.

## Key Features

- **User Authentication:** Signup, login, logout, and password change functionality.
- **Multi-Tenancy:** The application is designed around a multi-tenancy model where each "Family" is a tenant. Data is isolated between families.
- **Family Management:** Users can create or join families. An invitation system using unique codes is planned.
- **Portfolio Management:** Users can create, edit, and delete portfolios, which can be made public.
- **Posts and Presentations:** Users can create posts and presentations, which can include text, images, and video links.
- **Peer Review:** A system for requesting peer reviews of posts.
- **Notifications:** A notification system to alert users of relevant events.
- **Tags:** Posts can be tagged and filtered by tags.
- **Teacher Dashboard:** A dashboard for teachers to view student activity.
- **Announcements:** A feature for creating and displaying announcements.

## Development Plans

The project is currently undergoing a significant refactoring to implement a multi-tenancy architecture.

### Multi-Tenancy Upgrade

- **Goal:** Isolate data between different "Family" units.
- **Process:**
    1.  Create a `Family` model.
    2.  Associate users with a `Family`.
    3.  Update all views and queries to ensure data isolation.
    4.  Implement family management features for users.
- **Branching:** All multi-tenancy work is being done on the `feature/multi-tenancy` branch to avoid disrupting the `main` branch.

### Invitation System

- **Goal:** Allow users to join an existing `Family` using a unique invitation code.
- **Workflow:**
    1.  An admin/parent generates an invite code.
    2.  The new user signs up and is prompted to join or create a family.
    3.  The user enters the invite code to join the correct family.
