UI/UX Refinement: Article Page
Objective
Refactor posts in /post/ to improve readability, visual hierarchy, and use of whitespace.

Implementation Details
1. Main Layout & Container
Constrain the content width for better readability.

HTML: Ensure the main content is wrapped in a single container.

<main class="article-container">
  <!-- All article content goes here -->
</main>

CSS:

.article-container {
  max-width: 75ch; /* Optimal reading line length */
  margin: 2rem auto; /* Center container with vertical space */
  padding: 0 1rem; /* Horizontal padding for small screens */
}

2. Typography & Hierarchy
Establish a clear visual order.

CSS:

/* --- Title H1 --- */
.article-title {
  color: #1a1a1a; /* Change from blue to black */
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

/* --- Body Text --- */
.article-body p {
  line-height: 1.6; /* Crucial for readability */
  font-size: 1rem;
  color: #333;
}

.article-body strong {
  font-weight: 600; /* For semantic emphasis */
}

3. Metadata (Author, Date)
De-emphasize secondary information.

CSS:

.article-metadata {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
}
/* Remove icons if they are inline elements for a cleaner look */

4. Image & Caption
Use semantic HTML and style the caption appropriately.

HTML:

<figure>
  <img src="..." alt="Headshot of Panfilo Lacson">
  <figcaption>Figure 1. Senator Panfilo "Ping" Lacson</figcaption>
</figure>

CSS:

figure {
  margin: 0 0 1.5rem 0; /* Reset default margins */
}

figure img {
  width: 100%;
  height: auto;
  border-radius: 8px; /* Optional: soft corners */
}

figcaption {
  font-size: 0.9rem;
  color: #555;
  text-align: center;
  margin-top: 0.5rem;
}

5. Tags
Style tags as subtle "pills" instead of default buttons.

CSS:

.tag {
  display: inline-block;
  background-color: #f0f0f0;
  color: #555;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem; /* Pill shape */
  font-size: 0.85rem;
  text-decoration: none;
  margin-top: 1.5rem;
}
