"Create New Post" Improvement Plan (Token-Optimized)
A phased plan to transform the post creation form from a single, long page into a guided, user-friendly experience.

Phase 1: Quick Wins (Low Effort, High Impact)
Goal: Reduce immediate cognitive load without major code changes.

Task 1.1: Group Related Fields

Action: Place all media upload fields (Photo, Audio, Video) under a single "Media" section.

Reason: Creates logical grouping and reduces visual clutter.

Task 1.2: Consolidate Description Fields

Action: Replace "Annotation," "Audio description," and "Video description" with a single, optional "Media Description" field.

Reason: Eliminates confusing and redundant fields.

Task 1.3: Use Progressive Disclosure

Action: Collapse the audio and video upload sections by default, showing only an "Add Audio/Video" link to expand them.

Reason: Hides advanced, less-common options, focusing the user on the primary task.

Phase 2: Core User Journey Redesign
Goal: Rebuild the creation process to be intuitive and guided.

Task 2.1: Implement Post-Type Selector

Action: When a user clicks "+", first show a simple modal asking "What are you creating?" with clear, icon-based options (e.g., "Journal Entry," "Photo Story," "Video Log").

Reason: Tailors the entire experience to the user's specific goal from the start.

Task 2.2: Create a Multi-Step "Wizard" UI

Action: Based on the post-type selection, guide the user through a 2-3 step process.

Step 1: Core Content (e.g., Title, Text, and main media upload).

Step 2: Final Details (e.g., Tags, Subject, Descriptions).

Step 3: Review & Publish.

Reason: Converts a single overwhelming task into small, manageable steps, dramatically improving the user experience and reducing abandonment.