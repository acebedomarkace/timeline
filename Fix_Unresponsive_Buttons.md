Bug Fix & UX Improvement: Unresponsive "Save as Draft" & "Publish" Buttons
Date: September 25, 2025
Priority: High
Feature: Create a New Post (Multi-Step Form)

1. Problem Description
On the multi-step "Create a New Post" form, the Save as Draft and Publish buttons are unresponsive on all steps. When a user clicks them, nothing happens. This creates a dead end in the user journey, preventing users from creating posts and causing them to lose their work.

2. Root Cause Analysis
The issue stems from the multi-step form's structure. The form data is collected across two separate views or pages. When a user is on "Step 2: Final Details," the data from "Step 1: Core Content" (e.g., Subject, Title) is not included in the final submission.

This incomplete data causes the backend validation to fail silently, or the JavaScript logic halts, preventing the form from submitting. The user receives no feedback, making it seem like the buttons are broken.

3. Implementation Plan
To resolve this, we will restructure the form to ensure all data is collected and submitted together on the final step.

Step 1: Consolidate the Form into a Single HTML Structure
The most robust solution is to have both steps exist within a single <form> tag on one page. We will use JavaScript to control the visibility of each step.

Action: Modify the template to include both Step 1 and Step 2 content within one <form>.

Structure:

<form id="create-post-form" method="post" enctype="multipart/form-data">
    {% csrf_token %}

    <!-- Step 1 Container -->
    <div id="step-1">
        <!-- All fields from Step 1 (Subject, Title, etc.) -->
        <button type="button" id="next-btn">Next</button>
    </div>

    <!-- Step 2 Container (initially hidden) -->
    <div id="step-2" style="display: none;">
        <!-- All fields from Step 2 (Description, Tags, etc.) -->
        <button type="button" id="back-btn">Back</button>

        <!-- Final Actions - ONLY on the last step -->
        <button type="submit" name="action" value="draft">Save as Draft</button>
        <button type="submit" name="action" value="publish">Publish</button>
    </div>

</form>

Step 2: Implement Frontend JavaScript Logic
Action: Create a simple JavaScript controller to manage the visibility of the steps.

Logic:

When #next-btn is clicked:

Hide the #step-1 div.

Show the #step-2 div.

When #back-btn is clicked:

Hide the #step-2 div.

Show the #step-1 div.

Benefit: Because all inputs are within the same <form>, the final submission will contain data from both steps.

Step 3: Update Backend View (Django)
Action: The Django view needs to handle the action value submitted by the buttons to differentiate between saving a draft and publishing.

views.py Logic:

def post_create_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Check which button was pressed
            action = request.POST.get('action')
            if action == 'draft':
                post.is_published = False
                # Add a message: "Draft saved successfully!"
            elif action == 'publish':
                post.is_published = True
                # Add a message: "Post published successfully!"

            post.save()
            return redirect('blog:post_list') # Or wherever is appropriate
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})
