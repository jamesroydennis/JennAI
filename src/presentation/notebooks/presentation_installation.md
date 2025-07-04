# -----------------------------------------------------------
# File: templates/base.html
# -----------------------------------------------------------
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge"> {# Standard compatibility meta #}
    <title>{% block title %}JennAI{% endblock %}</title>
    
    {# Link to your compiled SCSS (main.css) #}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    
    {# Favicon link #}
    <link rel="icon" href="{{ url_for('static', filename='img/favicon.ico') }}" type="image/x-icon">
    
    {# Preload specific fonts for performance, mimicking ambiq.ai #}
    <link rel="preload" as="font" type="font/woff2" href="[https://fonts.gstatic.com/s/inter/v13/UcCO3FZYIDFWav0x495nZAuGxpg.woff2](https://fonts.gstatic.com/s/inter/v13/UcCO3FZYIDFWav0x495nZAuGxpg.woff2)" crossorigin>
    <link rel="preload" as="font" type="font/woff2" href="[https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-MtmW-Pihc.woff2](https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-MtmW-Pihc.woff2)" crossorigin>

    {% block head_extra %}{% endblock %}
</head>
<body>
    {# Preloader - Mimics ambiq.ai's loading animation #}
    <div class="preloader">
        <div class="lines">
            <div></div><div></div><div></div><div></div><div></div>
            <div></div><div></div><div></div><div></div><div></div>
            <div></div><div></div>
        </div>
        <div class="text">
            <span data-newtext="JENNAI">LOADING</span>
        </div>
    </div>

    {# Main Header - Mimics ambiq.ai's fixed, flex structure #}
    <header>
        <div class="logo-container">
            <a href="{{ url_for('index') }}" class="site-logo">
                <img src="{{ url_for('static', filename='img/jennai-logo.png') }}" alt="JennAI Logo">
                <span class="sr-only">JennAI Home</span>
            </a>
        </div>
        <nav class="main-navigation">
            <ul>
                <li><a href="#">Vision</a></li>
                <li><a href="#">Projects</a></li>
                <li><a href="#">Contact</a></li>
                <li><a href="#" class="button custom">Join Us</a></li> {# Example CTA button #}
            </ul>
        </nav>
        <div class="desktop-burger"><div></div><div></div><div></div></div>
        <div class="desktop-close">{# SVG for close icon #}</div>
        <div class="mobile-burger"><div></div><div></div><div></div></div>
    </header>

    {# Aside/Side Navigation - Mimics ambiq.ai's vertical navigation #}
    <aside class="side-nav">
        <nav class="nums">
            <div class="active">01</div>
            <span class="line"></span>
            <div class="all"></div>
        </nav>
        <nav class="arrows">
            <button class="top" title="Go up">↑</button>
            <button class="bottom" title="Go down">↓</button>
        </nav>
    </aside>

    {# Main Content Area - Contains all the stacked sections #}
    <main>
        {% block content %}{% endblock %}
    </main>

    {# Video Pop-up Modal - Mimics ambiq.ai's video player #}
    <div class="video-pop-up" data-hash="">
        <div class="bg close"></div>
        <div class="content">
            <div class="video"></div>
            <button class="close" title="Close pop up">X</button> {# Use your SVG cross icon #}
        </div>
    </div>

    {# Footer - Mimics ambiq.ai's multi-column structure #}
    <footer>
        <div class="footer-column nav-pages">
            <h4>Site Map</h4>
            <ul>
                <li><a href="{{ url_for('index') }}">Home</a></li>
                <li><a href="#">Vision</a></li>
                <li><a href="#">Projects</a></li>
                <li><a href="#">Contact</a></li>
            </ul>
        </div>
        <div class="footer-column community-links">
            <h4>Community</h4>
            <ul>
                <li><a href="#">Blog</a></li>
                <li><a href="#">Guides</a></li>
                <li><a href="#">Forum</a></li>
            </ul>
        </div>
        <div class="footer-column brand-info">
            <h4>JennAI</h4>
            {# Your personal portrait for a human touch #}
            <img src="{{ url_for('static', filename='img/your-portrait.jpg') }}" alt="Your Portrait" class="footer-portrait">
            <p class="copyright">&copy; 2025 JennAI. All rights reserved.</p>
            <a href="#" class="privacy-link">Privacy Policy</a>
        </div>
        {# ambiq.ai style background lines - these might be dynamic/JS driven #}
        <div class="bg_line l"></div>
        <div class="bg_line c"></div>
        <div class="bg_line r"></div>
    </footer>

    {# Your main JavaScript file #}
    <script src="{{ url_for('static', filename='js/scripts.js') }}"></script>
    {% block body_extra %}{% endblock %}
</body>
</html>
```

# -----------------------------------------------------------
# File: templates/index.html
# -----------------------------------------------------------
```html
{% extends "base.html" %}

{% block title %}JennAI - Illuminating the Intelligent Frontier{% endblock %}

{% block body_class %}home-page{% endblock %}

{% block content %}
    {# Section 1: Welcome / Hero Section - Mimics ambiq.ai's .welcome section #}
    <section class="welcome-section">
        <div class="section-content">
            <div class="text-column" data-stagger="fadeup">
                <h1 class="section-title" data-splitting>JennAI: Illuminating the Intelligent Frontier</h1>
                <p class="section-description">
                    In a universe driven by patterns, where evolution is not an option but an imperative, intelligence confronts its own fundamental flaws. Current AI, despite its super-adult capabilities, is designed to infer without wisdom, often generating plausible fallacy or operating in silos that render profound truths unreachable. This leads to a critical chasm: the absence of genuine understanding, where algorithms prioritize profit over value, and where automated systems can amplify the very human frailties of bias and ignorance.
                </p>
                <a href="#" class="button primary-button" title="Learn More">Learn More</a>
            </div>
            <div class="visual-column" data-item>
                {# Your Adobe Stock video or main DALL-E hero image #}
                {# This section matches your person.jpg/AdobeStock_1295578731.mov vibe #}
                <div class="video-wrapper">
                    <img src="{{ url_for('static', filename='img/person-interacting-ai.jpg') }}" alt="Person Interacting with AI" class="hero-visual">
                    <span class="play-button" data-video-id="YOUR_YOUTUBE_VIDEO_ID_HERE"></span> {# Replace with actual YouTube ID for your video #}
                </div>
            </div>
        </div>
        <div class="bg_line right"></div> {# Example background line #}
    </section>

    {# Section 2: Core Mission - Simplified from ambiq.ai sections #}
    <section class="mission-section">
        <div class="section-content">
            <div class="mission-text">
                <h2 class="section-subtitle">Our Core Mission</h2>
                <p class="mission-statement-text">{{ mission }}</p> {# Injecting your 5-word mission #}
            </div>
            {# Visual element for mission - perhaps circuit-dark/light or abstract wave #}
            <div class="mission-visual">
                <img src="{{ url_for('static', filename='img/circuit-dark-bg.jpg') }}" alt="Abstract Circuitry" class="mission-image">
            </div>
        </div>
        <div class="bg_line c"></div>
    </section>

    {# Section 3: The Vision (Expansive Explanation) #}
    <section class="vision-section">
        <div class="section-content">
            <h2 class="section-subtitle">Our Guiding Vision</h2>
            <div class="vision-text-block">
                {# Injecting your full vision text #}
                {{ vision | markdown }} {# Assuming you'll add a markdown filter for rendering from app.py #}
            </div>
            {# Optional: add your neon-heart.jpg here #}
            <div class="vision-visual">
                 <img src="{{ url_for('static', filename='img/neon-heart.jpg') }}" alt="Conceptual Heart" class="vision-image">
            </div>
        </div>
        <div class="bg_line l"></div>
    </section>

    {# Section 4: Call to Action / Final Statement - Mimicking ambiq.ai's newsfeed/footer transition #}
    <section class="call-to-action-section">
        <div class="section-content text-center">
            <h2 class="section-title">Join the Unyielding Quest</h2>
            <p class="section-description">Together, we will bridge knowledge, confront ignorance, and evolve intelligence.</p>
            <a href="#" class="button action-button">Connect with JennAI</a>
        </div>
        <div class="bg_line r"></div>
    </section>

{% endblock %}
```

# -----------------------------------------------------------
# File: static/css/_variables.scss
# -----------------------------------------------------------
```scss
// Super Awesome Website Theme - Variables
// --- Google Font Imports ---
// Inter for Headings: Modern, clean, highly legible, optimized for UI
// Open Sans for Body: Highly readable, versatile, humanist sans-serif
@import url('[https://fonts.com/css2?family=Inter:wght@400;600;700&family=Open+Sans:wght@400;600;700&display=swap](https://fonts.com/css2?family=Inter:wght@400;600;700&family=Open+Sans:wght@400;600;700&display=swap)');

// --- Font Variables ---
$font-heading: 'Inter', sans-serif;
$font-body: 'Open Sans', sans-serif;

// --- Base Colors (from your palette) ---
$theme-background: #87CEEB;    // NOW the Sky Blue for body background
$theme-font: #333333;        // Dark grey for text

// Header & Footer Colors (These remain as defined before, but you might re-evaluate them)
// For example, if header is also #87CEEB, you might need a different color for the text/logo.
// Given your original intent, I'll keep them distinct from the new body background for now.
$theme-primary: #87CEEB;     // Original primary - currently same as body background.
                             // You might want to pick a new 'header/footer' color if body is this!
$theme-accent-1: rgb(197, 71, 78); // Reddish tone - for borders, active states, etc.
$theme-accent-2: rgb(135, 206, 235); // Lighter Sky Blue - for links, hover effects

// JennAI Logo Complementary Colors (for JennAI logo and accents on dark bg)
$jennai-primary-comp: #008B8B;  // Dark Cyan
$jennai-secondary-comp: #FF6F61; // Vibrant Coral Red
$jennai-neutral-dark: #1A1A1A;   // Very Dark Gray

// --- Status Colors ---
$status-success: #28a745; // Green for success/positive actions
$status-warning: #ffc107; // Yellow for warnings/caution
$status-error: #dc3545;    // Red for errors/alerts
$status-info: #17a2b8;     // Optional: Blue for informational messages

// --- Spacing / Grid Variables (Conceptual, fill exact values from ambiq.ai) ---
$padding-section: 4em 2em; // Example padding for sections
$max-width-content: 1200px; // Max width for content columns
$header-height-desktop: 80px; // Adjust based on logo height and ambiq.ai
$header-height-mobile: 60px;
```

# -----------------------------------------------------------
# File: static/css/main.scss
# (This file will require your precision to extract exact values from ambiq.ai)
# -----------------------------------------------------------
```scss
@import 'variables';

// --- Base HTML & Body Styles ---
html, body {
    scroll-behavior: smooth; // Smooth scrolling for navigation
    height: 100%; // Ensure body takes full height for positioning
}

body {
    background-color: $theme-background;
    color: $theme-font;
    font-family: $font-body;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    overflow-x: hidden; // Prevent horizontal scroll
}

// --- Headings ---
h1, h2, h3, h4, h5, h6 {
    font-family: $font-heading;
    color: $theme-intermediate-dark-red; // Use reddish accent
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    line-height: 1.2; // Tighter line height for headings
}
h1 { font-size: 3em; }
h2 { font-size: 2.5em; }
h3 { font-size: 2em; }

// --- Buttons ---
.button {
    background-color: $theme-accent-1; // Default button style
    color: white;
    border: none;
    padding: 0.8em 1.5em;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1em;
    text-decoration: none; // For buttons as links
    display: inline-block; // Allow padding/margin
    transition: background-color 0.3s ease;
    &:hover { background-color: darken($theme-accent-1, 10%); }

    &.primary-button { // Specific for hero/main CTAs
        background-color: $jennai-secondary-comp; // Use JennAI coral red
        &:hover { background-color: darken($jennai-secondary-comp, 10%); }
    }
    &.dark { // For buttons on light backgrounds
        background-color: $jennai-neutral-dark;
        color: white;
        &:hover { background-color: lighten($jennai-neutral-dark, 20%); }
    }
}

// --- Links ---
a {
    color: $theme-accent-1; // General link style
    text-decoration: none;
    &:hover {
        color: darken($theme-accent-1, 15%);
        text-decoration: underline;
    }
}

// --- Preloader (mimicking ambiq.ai) ---
.preloader {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: $jennai-neutral-dark; // Dark background for preloader
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    opacity: 1;
    visibility: visible;
    transition: opacity 0.5s ease, visibility 0.5s ease;

    &.hidden {
        opacity: 0;
        visibility: hidden;
    }

    .lines div {
        width: 4px;
        height: 30px;
        background-color: $jennai-primary-comp; // JennAI dark cyan for lines
        margin: 0 2px;
        animation: loading-line 1.2s infinite ease-in-out;
        display: inline-block;
    }
    .lines div:nth-child(2) { animation-delay: 0.1s; }
    .lines div:nth-child(3) { animation-delay: 0.2s; }
    .lines div:nth-child(4) { animation-delay: 0.3s; }
    .lines div:nth-child(5) { animation-delay: 0.4s; }
    .lines div:nth-child(6) { animation-delay: 0.5s; }
    // Add more for all lines

    .text {
        font-family: $font-heading;
        font-size: 2em;
        color: white;
        margin-top: 20px;
        span {
            position: relative;
            &::before {
                content: attr(data-newtext);
                position: absolute;
                top: 0;
                left: 0;
                color: $jennai-secondary-comp; // JennAI coral red for new text
                width: 0;
                overflow: hidden;
                transition: width 0.5s ease-in-out;
            }
        }
    }
}

@keyframes loading-line {
    0%, 100% { transform: scaleY(1); }
    50% { transform: scaleY(0.3); }
}

// --- Header ---
header {
    background-color: $theme-primary; // Sky Blue
    color: $theme-font;
    padding: 1em 2em; // Adjust as per ambiq.ai
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: fixed;
    width: 100%;
    z-index: 100;
    box-shadow: 0 2px 5px rgba($jennai-neutral-dark, 0.1); // Subtle shadow

    .site-logo img {
        height: $header-height-desktop; // Use variable
        display: block;
        transition: height 0.3s ease; // For responsiveness
    }

    .main-navigation ul {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
    }
    .main-navigation li {
        margin-left: 20px; // Adjust spacing
    }
    .main-navigation a {
        color: $theme-font; // Dark text on light header
        font-weight: 600;
        &:hover { color: $theme-accent-1; } // Reddish accent on hover
    }

    // Burger/Close icons (basic styling)
    .desktop-burger, .mobile-burger { display: none; } // Hide initially
    @media (max-width: 768px) {
        .main-navigation { display: none; } // Hide nav on mobile
        .mobile-burger { display: block; } // Show mobile burger
        .site-logo img { height: $header-height-mobile; }
    }
}

// --- Side Navigation ---
aside.side-nav {
    position: fixed;
    right: 2em; // Adjust position
    top: 50%;
    transform: translateY(-50%);
    z-index: 99;
    display: flex;
    flex-direction: column;
    align-items: center;
    // Add ambiq.ai specific styling here (e.g., subtle background, borders)

    .nums div {
        font-family: $font-heading;
        font-size: 1.2em; // Adjust size
        color: $theme-font;
        margin: 0.5em 0;
    }
    .nums .line {
        width: 1px;
        height: 30px; // Length of line
        background-color: lighten($theme-font, 60%); // Light grey line
        margin: 0.5em 0;
    }
    .arrows button {
        background: none;
        border: none;
        color: $theme-font; // Dark arrows
        font-size: 1.5em; // Adjust arrow size
        cursor: pointer;
        padding: 5px;
        &:hover { color: $theme-accent-1; }
    }
}

// --- Main Content Sections ---
main {
    padding-top: $header-height-desktop; // Offset for fixed header
    section {
        min-height: 100vh; // Full viewport height for distinct sections
        display: flex;
        align-items: center; // Vertically center content
        justify-content: center;
        padding: $padding-section; // Use variable
        position: relative; // For background lines etc.
        overflow: hidden; // Prevent content overflowing section bounds
        flex-direction: column; // Default to column for content blocks
    }

    .section-content {
        display: flex;
        width: 100%;
        max-width: $max-width-content; // Use variable for max width
        margin: 0 auto;
        justify-content: space-between;
        align-items: center;
        gap: 2em; // Spacing between columns/elements
        flex-wrap: wrap; // Allow columns to wrap on smaller screens
    }

    // --- Section 1: Welcome / Hero ---
    .welcome-section {
        background-color: $theme-background; // Your Sky Blue background
        color: $theme-font;
        min-height: 100vh; // Ensure it covers screen
        position: relative;

        .section-content {
            flex-direction: row; // Two columns (text + visual)
            align-items: flex-start; // Align top
            @media (max-width: 768px) { flex-direction: column; } // Stack on mobile
        }
        .text-column {
            flex: 1;
            padding-right: 2em; // Spacing to visual
            @media (max-width: 768px) { padding-right: 0; margin-bottom: 2em; }
        }
        .visual-column {
            flex: 1;
            display: flex;
            justify-content: flex-end; // Push image to right
            .hero-visual {
                max-width: 100%;
                height: auto;
                border-radius: 10px; // Rounded corners for visuals
                box-shadow: 0 5px 15px rgba($jennai-neutral-dark, 0.2);
            }
        }
        .section-title { font-size: 3.5em; color: $theme-intermediate-dark-red; line-height: 1.1; }
        .section-description { font-size: 1.2em; max-width: 80%; } // Constrain text width
    }

    // --- Section 2: Core Mission ---
    .mission-section {
        background-color: lighten($theme-background, 5%); // Slightly different blue
        color: $theme-font;
        .section-content {
            flex-direction: row;
            @media (max-width: 768px) { flex-direction: column-reverse; } // Reverse stack on mobile
        }
        .mission-text {
            flex: 1;
            padding-right: 2em;
            .section-subtitle { font-size: 2.2em; color: $jennai-primary-comp; } // Dark Cyan
            .mission-statement-text {
                font-family: $font-heading; // Mission in heading font
                font-size: 2.5em; // Large and impactful
                font-weight: bold;
                color: $theme-font; // Dark text
                line-height: 1.1;
            }
        }
        .mission-visual {
            flex: 0.7; // Smaller visual column
            display: flex;
            justify-content: center;
            align-items: center;
            img { max-width: 100%; height: auto; border-radius: 10px; }
        }
    }

    // --- Section 3: Vision (Expansive Explanation) ---
    .vision-section {
        background-color: $jennai-neutral-dark; // Dark background
        color: white; // Light text on dark background

        .section-content {
            flex-direction: row; // Text and visual side-by-side
            @media (max-width: 768px) { flex-direction: column; }
        }
        .section-subtitle { font-size: 2.2em; color: $jennai-primary-comp; } // Dark Cyan for headings
        .vision-text-block {
            flex: 1.5; // More space for text
            font-family: $font-body;
            font-size: 1.1em;
            line-height: 1.8;
            padding-right: 3em; // Spacing
            
            // Styles for the markdown content
            h3 { color: $jennai-secondary-comp; font-size: 1.8em; margin-bottom: 0.8em;} // Coral for sub-headings
            strong { color: $jennai-secondary-comp; } // Coral for strong text
            p { margin-bottom: 1em; }
        }
        .vision-visual {
            flex: 1; // Visual column
            display: flex;
            justify-content: center;
            align-items: center;
            img { max-width: 100%; height: auto; border-radius: 10px; }
        }
    }

    // --- Section 4: Call to Action ---
    .call-to-action-section {
        background-color: $theme-accent-2; // Lighter Sky Blue
        color: $theme-font;
        text-align: center;
        min-height: auto; // Can be smaller
        padding: 5em 2em;

        .section-content {
            flex-direction: column; // Stack elements
            max-width: 800px;
        }
        .section-title { color: $jennai-neutral-dark; font-size: 3em; } // Dark heading
        .section-description { font-size: 1.2em; margin-bottom: 2em; }
        .button.action-button {
            background-color: $jennai-secondary-comp; // Coral button
            color: white;
            &:hover { background-color: darken($jennai-secondary-comp, 10%); }
        }
    }
}

// --- Video Pop-up Modal (mimicking ambiq.ai) ---
.video-pop-up {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-color: rgba($jennai-neutral-dark, 0.9); // Dark overlay
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease;

    &.active { opacity: 1; visibility: visible; }

    .content {
        position: relative;
        width: 90%; max-width: 1000px; // Responsive width
        background: black;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba($jennai-neutral-dark, 0.5);
        padding-top: 56.25%; // 16:9 aspect ratio

        .video {
            position: absolute; top: 0; left: 0;
            width: 100%; height: 100%;
        }
    }
    .close { // Close button for modal
        position: absolute; top: 15px; right: 15px;
        background: $jennai-secondary-comp; // Coral
        color: white;
        border: none; border-radius: 50%;
        width: 40px; height: 40px;
        display: flex; justify-content: center; align-items: center;
        cursor: pointer; font-size: 1.5em; z-index: 1001;
        &:hover { background-color: lighten($jennai-secondary-comp, 10%); }
    }
}

// --- Footer ---
footer {
    background-color: $jennai-neutral-dark; // Dark neutral background
    color: white;
    padding: 4em 2em;
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;

    .footer-column {
        flex: 1;
        min-width: 200px;
        margin: 1em;
    }
    .footer-column h4 {
        font-family: $font-heading;
        color: $jennai-primary-comp; // JennAI dark cyan for headings
        margin-bottom: 1em;
    }
    .footer-column ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .footer-column li a {
        color: lighten($jennai-neutral-dark, 40%); // Lighter grey links
        text-decoration: none;
        &:hover { color: $jennai-secondary-comp; } // JennAI coral red on hover
    }
    .footer-portrait { // Your portrait
        height: 80px; // Adjust size
        width: 80px;
        border-radius: 50%; // Circular portrait
        object-fit: cover;
        margin-top: 1em;
        border: 2px solid $jennai-primary-comp; // Cyan border
    }
    .copyright {
        font-size: 0.9em;
        color: lighten($jennai-neutral-dark, 30%);
        margin-top: 1em;
    }
    .privacy-link {
        font-size: 0.9em;
        color: lighten($jennai-neutral-dark, 30%);
        &:hover { color: $jennai-secondary-comp; }
    }

    // ambiq.ai style background lines
    .bg_line {
        position: absolute;
        width: 100px; // Adjust as needed
        height: 100%;
        background: linear-gradient(to bottom, rgba($jennai-primary-comp, 0.1) 0%, transparent 100%);
        z-index: -1;
        &.l { left: 0; }
        &.c { left: 50%; transform: translateX(-50%); }
        &.r { right: 0; }
    }
}
```

# -----------------------------------------------------------
# File: static/js/scripts.js
# (Basic JavaScript for preloader and video modal)
# -----------------------------------------------------------
```javascript
// Basic JavaScript for Preloader
document.addEventListener('DOMContentLoaded', () => {
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        // Simulating load time or waiting for assets
        window.addEventListener('load', () => {
            preloader.classList.add('hidden');
        });
        // Fallback for very fast loads or if 'load' event doesn't fire as expected
        setTimeout(() => {
            preloader.classList.add('hidden');
        }, 1500); // Hide after 1.5 seconds
    }

    // Basic JavaScript for Video Modal (mimicking ambiq.ai)
    const videoPopUp = document.querySelector('.video-pop-up');
    const closeVideoBtn = videoPopUp ? videoPopUp.querySelector('.close') : null;
    const videoEmbedContainer = videoPopUp ? videoPopUp.querySelector('.video') : null;

    document.querySelectorAll('.play-button').forEach(button => {
        button.addEventListener('click', () => {
            const videoId = button.dataset.videoId;
            if (videoId && videoPopUp && videoEmbedContainer) {
                // Using YouTube embed structure
                videoEmbedContainer.innerHTML = `
                    <iframe width="100%" height="100%" src="[https://www.youtube.com/embed/$](https://www.youtube.com/embed/$){videoId}?autoplay=1&rel=0&showinfo=0&iv_load_policy=3" 
                            frameborder="0" allow="autoplay; encrypted-media; fullscreen" allowfullscreen>
                    </iframe>
                `;
                videoPopUp.classList.add('active');
            }
        });
    });

    if (closeVideoBtn) {
        closeVideoBtn.addEventListener('click', () => {
            if (videoEmbedContainer) {
                videoEmbedContainer.innerHTML = ''; // Stop video playback
            }
            videoPopUp.classList.remove('active');
        });
    }

    if (videoPopUp) {
        videoPopUp.addEventListener('click', (e) => {
            // Close if clicked on the background of the modal, not the video content
            if (e.target === videoPopUp || e.target.classList.contains('bg')) {
                if (videoEmbedContainer) {
                    videoEmbedContainer.innerHTML = '';
                }
                videoPopUp.classList.remove('active');
            }
        });
    }
});

```