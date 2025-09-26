# Django Form Submission Debug Guide

## Problem
Form buttons (Save as Draft/Publish) not working in Django post creation form.

## Quick Fix Steps

### 1. Update post_create View
Replace your `post_create` function with:

```python
@login_required
def post_create(request):
    post_type = request.GET.get('type', 'journal')
    
    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # Debug
        form = PostForm(request.POST, request.FILES, post_type=post_type)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.post_type = post_type
            
            # Handle action buttons
            action = request.POST.get('action')
            post.status = 'published' if action == 'publish' else 'draft'
            post.save()
            
            # Handle tags safely
            tags_data = form.cleaned_data.get('tags', '')
            if tags_data:
                post.tags.clear()
                tag_names = [t.strip() for t in str(tags_data).split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
            
            messages.success(request, f"Post {'published' if action == 'publish' else 'saved as draft'}!")
            return redirect('timeline_redirect')
        else:
            print(f"Form errors: {form.errors}")  # Debug
            messages.error(request, "Please fix form errors.")
    else:
        form = PostForm(post_type=post_type)
    
    return render(request, 'blog/post_form.html', {'form': form, 'post_type': post_type})
```

### 2. Update HTML Template
Key changes needed in `post_form.html`:

```html
<!-- Ensure proper form attributes -->
<form method="POST" action="" enctype="multipart/form-data">
    {% csrf_token %}
    
    <!-- Add error display -->
    {% if form.non_field_errors %}
        <div class="error">{{ form.non_field_errors }}</div>
    {% endif %}
    
    <!-- For each field, add error handling -->
    <div class="form-field">
        <label>{{ form.field_name.label }}</label>
        {{ form.field_name }}
        {% if form.field_name.errors %}
            <div class="error">{{ form.field_name.errors }}</div>
        {% endif %}
    </div>
</form>
```

### 3. Debug Checklist

**Check Django Console:**
- Look for "POST data:" debug output
- Check for "Form errors:" messages
- Verify no Python exceptions

**Browser DevTools:**
- Network tab: Confirm POST request sent
- Console tab: Check for JavaScript errors
- Elements tab: Verify buttons have correct attributes

**Common Issues:**
- Missing required fields (hidden by JavaScript)
- File upload problems (check `MEDIA_ROOT` settings)
- Form validation failures
- CSRF token issues

### 4. PostForm Requirements

Ensure your `PostForm` handles `post_type`:

```python
class PostForm(forms.ModelForm):
    def __init__(self, *args, post_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_type = post_type
        # Modify fields based on post_type
```

### 5. Quick Tests

**Minimal Test:**
1. Fill only required fields
2. Submit as draft first
3. Check Django console output

**Field Visibility:**
1. Inspect hidden fields with DevTools
2. Ensure required fields aren't hidden
3. Temporarily remove JavaScript to test

### 6. Emergency Fallback

If still broken, temporarily simplify:

```python
# Minimal working version
@login_required
def post_create(request):
    if request.method == 'POST':
        # Manual form processing
        post = Post.objects.create(
            title=request.POST.get('title', 'Test Post'),
            author=request.user,
            status='draft',
            post_type='journal'
        )
        return redirect('timeline_redirect')
    
    form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})
```

## Expected Debug Output

**Working form should show:**
```
POST data: <QueryDict: {'csrfmiddlewaretoken': [...], 'action': 'draft', 'title': 'My Post'}>
Added tags: ['tag1', 'tag2']
```

**Broken form might show:**
```
Form errors: {'title': ['This field is required.']}
```

Save this file and follow steps 1-3 first. Check Django console after each form submission attempt.