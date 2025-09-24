# Previous Actions Log

This log summarizes the last few significant actions taken to aid in continuity.

---

### Latest Actions (up to 4)

1.  **Debugging Crispy Forms Template Issue (Ongoing)**
    *   **Action**: Investigating `TemplateDoesNotExist: bootstrap5/uni_form.html` error.
    *   **Details**: Confirmed `crispy-bootstrap5` is installed. Preparing to temporarily modify `blog/templates/blog/join_family_form.html` to use `{{ form.as_p }}` for diagnosis.

2.  **Attempted Fix for Crispy Forms Bootstrap Template Issue**
    *   **Action**: Added `'crispy_bootstrap5'` to `INSTALLED_APPS` in `timeline_project/settings.py`.
    *   **Details**: This was done to register the Bootstrap 5 template pack for Crispy Forms.

3.  **Attempted Fix for Crispy Forms Tag Library Issue**
    *   **Action**: Added `CRISPY_ALLOWED_TEMPLATE_PACKS` and `CRISPY_TEMPLATE_PACK = "bootstrap5"` to `timeline_project/settings.py`.
    *   **Details**: Configured Crispy Forms to use Bootstrap 5 templates.

4.  **Attempted Fix for `NameError: JoinFamilyForm`**
    *   **Action**: Added `JoinFamilyForm` to the imports in `blog/views.py`.
    *   **Details**: Resolved a `NameError` when the `join_family` view tried to use `JoinFamilyForm` without it being imported.
