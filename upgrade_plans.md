# Multi-Tenancy Upgrade Plan

## Development Workflow

To ensure the stability of the existing MVP for current users, all work for this multi-tenancy upgrade will be performed on a separate Git branch named `feature/multi-tenancy`.

The `main` branch will remain untouched, guaranteeing no disruptions to live users.

Once all the steps in this plan are completed and the new functionality is fully tested, the `feature/multi-tenancy` branch will be merged into the `main` branch to release the upgrade.

---

This document outlines the steps required to refactor the portfolio application from a single-user-group application to a multi-tenant SaaS application where each "Family" is a tenant.

The primary goal is to ensure data is properly isolated so that one family cannot access another family's data, while allowing the application to scale cost-effectively.

---

### Step 1: Foundational Model Changes (In Progress)

This is the foundational step to create the concept of a "Family" at the database level.

1.  **Create `Family` Model**: Add a new `Family` model to `blog/models.py`. This model will represent a distinct family unit.
2.  **Update `Profile` Model**: Add a `ForeignKey` relationship from the `Profile` model to the new `Family` model. This will associate every user with a specific family.
3.  **Generate and Apply Migrations**: Run `python manage.py makemigrations` and `python manage.py migrate` to apply these changes to the database schema.

---

### Step 2: Implement Data Isolation in Views

This is the most critical step for security. We must modify all views to ensure they only query and display data belonging to the currently logged-in user's family.

1.  **Identify Target Views**: Systematically go through all views in `blog/views.py` that list or display content (e.g., Post lists, Presentation details, etc.).
2.  **Modify Queries**: Change all relevant database queries to filter by the user's family.
    *   **Example**: A query like `Post.objects.all()` will be changed to `Post.objects.filter(author__profile__family=request.user.profile.family)`.

---

### Step 3: Family Management and User Onboarding

Users need a way to create and join families.

1.  **Create a "Family Creation" View**: Build a simple form and view that allows a new user to create a `Family` instance.
2.  **Update User Signup Flow**:
    *   A new user signs up.
    *   After signup, if they are not yet part of a family, redirect them to the "Create Family" page or a page where they can enter an invite code.
3.  **Display Family Information**: Update user profile pages or dashboards to show the user's current family.

---

### Step 4: Administrative Tools

1.  **Register `Family` in Admin**: Add the `Family` model to `blog/admin.py` to allow site administrators to view and manage families from the Django admin interface.
