# Multi-Tenancy Invitation System Plan

## Goal
To create a secure and user-friendly workflow that allows new users to join an existing Family using a unique invitation code.

---

## User Workflow

1.  **Admin/Parent generates an invite code:** An existing member of a family navigates to a "Family Management" page.
2.  **Code is shared:** The user clicks a button to generate or view a unique invite code for their family. They share this code (e.g., `A7B-X9P`) with the person they want to invite.
3.  **New user signs up:** The new user creates an account using the standard `/signup` page.
4.  **New user is prompted to join or create:** After signup, they are taken to a page asking if they want to "Create a new family" or "Join an existing family".
5.  **New user joins:** They choose to join, enter the invite code, and are automatically added to the correct family.

---

## Development Steps

### Step 1: Update the `Family` Model

We need a place to store the invite code.

1.  **Modify `blog/models.py`**: Add a new `invite_code` field to the `Family` model. This code should be unique.
    ```python
    invite_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    ```
2.  **Create and run migrations**: Run `python manage.py makemigrations` and `python manage.py migrate` to apply the change to the database.

### Step 2: Create a Family Management Page

Existing users need a place to get the invite code.

1.  **Create a new view**: `family_management` in `blog/views.py`.
2.  **Logic**: The view will display family information. It will include a button that, when clicked, will either display the existing family invite code or generate a new, unique, random code if one doesn't exist and save it to the family instance.
3.  **Create a new template**: `family_management.html` to display the information and the button.
4.  **Add URL**: Create a new path in `blog/urls.py` for `/family/manage/`.

### Step 3: Create the Post-Signup "Join or Create" Flow

New users need to be routed correctly after signing up.

1.  **Create a "Join or Create" page**: Build a new view and template (`join_or_create.html`) that presents the user with two buttons: "Create a New Family" and "Join with Invite Code".
2.  **Update the `signup` view**: Modify the redirect in the `signup` view to point to this new `join_or_create` page instead of directly to `family_create`.
3.  **Create a "Join Family" page**: Build a new view and template (`join_family_form.html`) that contains a simple form with one field: "Invite Code".
4.  **Process the invite code**: The `join_family` view will validate the submitted code. If it's valid, it will assign the new user to the corresponding family and redirect them to their timeline.

### Step 4: Update Navigation

Add a link to the "Family Management" page in a logical place, such as the user dropdown menu in the `base.html` template.
