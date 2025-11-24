# Theme Management

The CTF platform supports a flexible theming system that allows administrators to change the visual appearance of the application. Themes are defined using CSS and are managed through the admin panel.

## How Theming Works

The WindFlag CTF platform implements a flexible and powerful theming system, allowing administrators to customize the visual appearance of the application extensively. This system is primarily driven by CSS and is managed conveniently through the admin panel.

At its core, the theming mechanism operates as follows:

1.  **Base Styling**: The application first loads a foundational set of CSS rules (often from `static/css/main.css` and potentially a CSS framework like Tailwind CSS, which handles responsive design and utility classes). This provides the default look and feel.
2.  **Theme Directory Structure**: All custom themes reside within the `static/themes/` directory. Each subdirectory inside `static/themes/` corresponds to a unique theme (e.g., `static/themes/cyberdeck/`, `static/themes/noir/`).
3.  **`theme.css` File**: For a subdirectory to be recognized as a valid theme, it *must* contain a `theme.css` file directly within its root. This file is where all the custom CSS for that specific theme is defined.
4.  **Dynamic Class Application**: When a theme is activated via the Admin Panel, the application dynamically adds a CSS class in the format `theme-<theme_name>` to the `<body>` tag of every page. For instance, if the "cyberdeck" theme is active, the `<body>` tag will receive the class `body.theme-cyberdeck`.
5.  **Theme-Specific Overrides**: The `theme.css` file for the active theme is loaded *after* the base CSS. This loading order, combined with the `body.theme-<theme_name>` class, allows theme-specific styles to override or extend the default styles. By targeting CSS rules with `body.theme-<theme_name>`, theme developers can ensure their styles only apply when their theme is active.

### The Power of CSS Variables

The recommended and most efficient approach for creating themes is to utilize CSS variables (also known as custom properties). The WindFlag application's base stylesheets define a comprehensive set of CSS variables that control various aspects of the UI, such as colors, typography, spacing, and borders.

By redefining these CSS variables within your theme's `theme.css` (specifically within the `body.theme-<theme_name>` block), you can globally alter the appearance of the entire application without needing to rewrite extensive CSS rules for individual elements. This provides a consistent, maintainable, and highly flexible way to define a theme's visual identity.

## Comprehensive CSS Variables for Theming

Your `theme.css` file should define the following CSS variables within the `body.theme-<theme_name>` selector to achieve comprehensive theming. The values provided are examples; you would replace these with your theme's specific design choices.

### Color Palette Variables

These variables control the primary and secondary colors used throughout the application.

*   `--bg-main`: The dominant background color for the application's main canvas.
*   `--bg-surface`: Background color for distinct UI elements like cards, panels, modals, and input fields, typically slightly darker or lighter than `--bg-main` for contrast.
*   `--bg-input`: Specific background color for text input fields, textareas, and select boxes.
*   `--bg-completed`: Background color specifically used to highlight completed challenges or success indicators.
*   `--bg-hover-surface`: Background color for interactive surfaces when a user hovers over them, providing visual feedback.
*   `--text-header`: Text color for major headings (h1, h2, h3, etc.).
*   `--text-main`: The primary text color for paragraphs, labels, and general content.
*   `--text-muted`: A lighter or less prominent text color used for secondary information, descriptions, or subtle hints.
*   `--primary`: The main accent color of the application, used for calls-to-action, active states, links, and important buttons.
*   `--secondary`: An optional secondary accent color, for less prominent actions or complementary elements.
*   `--success`: Color for success messages, indicators, or elements.
*   `--danger`: Color for error messages, critical actions, or warning indicators.
*   `--warning`: Color for warning messages or cautionary indicators.
*   `--info`: Color for informational messages.

### Typography Variables

These variables control font styles and sizes.

*   `--font-family-base`: The primary font family for most text.
*   `--font-family-heading`: The font family specifically for headings.
*   `--font-size-base`: Base font size for the application.
*   `--line-height-base`: Base line height for text.

### Layout & Spacing Variables

*   `--spacing-unit`: A base unit for consistent padding and margins.

### Border & Shadow Variables

These define the appearance of borders, radii, and shadows.

*   `--border-color`: The default color for borders around elements.
*   `--border-width`: Default border thickness.
*   `--radius`: The default border-radius for rounded corners on UI elements like cards, buttons, and input fields.
*   `--card-border`: The full CSS `border` property for card components (e.g., `1px solid var(--border-color)`).
*   `--card-shadow`: The `box-shadow` property for card components, adding depth.
*   `--input-border`: Full CSS `border` property for input fields.

### Example CSS Variable Definitions for a Hypothetical "Oceanic" Theme:

```css
body.theme-oceanic {
    /* Color Palette */
    --bg-main: #0a1128;           /* Deep Ocean Blue */
    --bg-surface: #001f3f;        /* Darker Navy for cards */
    --bg-input: #1a3a5e;          /* Slightly lighter for inputs */
    --bg-completed: #2ecc71;      /* Emerald Green */
    --bg-hover-surface: #003366;  /* Medium Blue for hover */
    --text-header: #e0f2f7;       /* Light Aqua */
    --text-main: #a7d9ed;         /* Sky Blue */
    --text-muted: #6497b1;        /* Muted Blue */
    --primary: #0074d9;           /* Vibrant Blue */
    --secondary: #7fdbff;         /* Lighter Blue */
    --success: #28a745;           /* Standard Success Green */
    --danger: #dc3545;            /* Standard Danger Red */
    --warning: #ffc107;           /* Standard Warning Yellow */
    --info: #17a2b8;              /* Standard Info Cyan */

    /* Typography */
    --font-family-base: 'Roboto', sans-serif;
    --font-family-heading: 'Montserrat', sans-serif;
    --font-size-base: 16px;
    --line-height-base: 1.5;

    /* Layout & Spacing */
    --spacing-unit: 8px;

    /* Border & Shadow */
    --border-color: #004488;      /* Dark Blue for borders */
    --border-width: 1px;
    --radius: 0.25rem;            /* Slightly rounded */
    --card-border: var(--border-width) solid var(--border-color);
    --card-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); /* Deeper shadow */
    --input-border: var(--border-width) solid var(--border-color);
}
```

## Essential Semantic Classes

The application's HTML is structured with semantic CSS classes that are designed to be styled by the theme's CSS variables. By consistently using these classes in your templates, you ensure that components automatically adopt the active theme's styling. This abstraction allows for rapid theme switching and consistent UI without modifying HTML.

Here's an extended list of commonly used semantic classes:

### Layout & Container Classes

*   `.theme-container`: General-purpose container for page content.
*   `.theme-card`: Used for distinct content blocks, panels, or UI cards.
*   `.theme-section`: For major sections of a page.

### Typography Classes

*   `.theme-page-title`: For the main title of a page (e.g., `<h1>`).
*   `.theme-heading-1` to `.theme-heading-6`: For various levels of headings.
*   `.theme-text`: For general paragraph text.
*   `.theme-text-muted`: For secondary, less emphasized text.
*   `.theme-link`: For hyperlinks.

### Form Element Classes

*   `.theme-input`: Applies to `input[type="text"]`, `input[type="password"]`, `textarea`, `select`.
*   `.theme-label`: For form labels.
*   `.theme-button`: General button styling.
*   `.theme-button-primary`: For primary action buttons.
*   `.theme-button-secondary`: For secondary action buttons.
*   `.theme-button-danger`: For destructive or critical action buttons.
*   `.theme-checkbox`: For checkboxes.
*   `.theme-radio`: For radio buttons.
*   `.theme-form-group`: A container for form elements (label + input).

### Table Classes

*   `.theme-table`: For `<table>` elements.
*   `.theme-table-header-cell`: For `<th>` elements.
*   `.theme-table-body-cell`: For `<td>` elements.
*   `.theme-table-row-hover`: Applied to table rows for hover effects.

### Navigation & List Classes

*   `.theme-navbar`: For the main navigation bar.
*   `.theme-nav-link`: For individual navigation links.
*   `.theme-list`: For `<ul>` or `<ol>` elements.
*   `.theme-list-item`: For `<li>` elements.

### Status & Messaging Classes

*   `.theme-alert-success`: For success messages.
*   `.theme-alert-info`: For informational messages.
*   `.theme-alert-warning`: For warning messages.
*   `.theme-alert-danger`: For error messages.
*   `.theme-badge`: For small, informative labels or tags.

By defining the CSS variables in your `theme.css`, these semantic classes will automatically adopt your theme's styling, ensuring a cohesive and maintainable design across the application.

## Creating a New Theme: A Step-by-Step Guide

Creating a new theme allows you to completely transform the look and feel of your WindFlag instance. Follow these steps for a smooth theme development process:

1.  **Plan Your Theme's Aesthetic**:
    *   **Color Palette**: Decide on your primary, secondary, text, background, and accent colors. Consider using online tools like Coolors.co or Adobe Color to generate harmonious palettes.
    *   **Typography**: Choose font families for headings and body text. Consider readability and the overall mood you want to convey.
    *   **Visual Style**: Think about corner radii, shadow depths, and overall visual density (e.g., minimalist, retro, modern).

2.  **Create a New Theme Directory**:
    *   Navigate to the `static/themes/` directory within your project.
    *   Create a new subdirectory for your theme. The name of this directory will be the internal name of your theme (e.g., `static/themes/my-custom-theme/`). Choose a descriptive and unique name.

3.  **Create `theme.css`**:
    *   Inside your new theme directory (`static/themes/my-custom-theme/`), create a file named `theme.css`. This is the core stylesheet for your theme.

4.  **Define CSS Variables**:
    *   Open `theme.css` and define the CSS variables within a `body.theme-<your-theme-name>` block. This ensures your styles are scoped and only apply when your theme is active.
    *   **Recommendation**: Start by copying the variable definitions from an existing theme (e.g., `static/themes/default/theme.css`) or the comprehensive list provided in the "Comprehensive CSS Variables for Theming" section above. Then, systematically modify the values to match your planned aesthetic.

    **Example for `my-custom-theme` (demonstrating variable overrides):**

    ```css
    body.theme-my-custom-theme {
        /* Example Color Overrides */
        --bg-main: #2a2a2a;         /* Dark grey background */
        --bg-surface: #3c3c3c;      /* Slightly lighter grey for cards */
        --primary: #4CAF50;         /* Green primary color */
        --text-main: #f0f0f0;       /* Light text on dark background */
        --border-color: #555;       /* Muted border color */

        /* Example Typography Overrides */
        --font-family-base: 'Open Sans', sans-serif;

        /* Example Border & Shadow Overrides */
        --radius: 0.2rem;           /* Slightly less rounded */
        --card-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    ```

5.  **Integrate Additional Assets (Optional)**:
    *   If your theme requires custom images (backgrounds, icons), fonts, or JavaScript, create subdirectories within your theme's folder (e.g., `static/themes/my-custom-theme/img/`, `static/themes/my-custom-theme/fonts/`, `static/themes/my-custom-theme/js/`).
    *   Reference these assets in your `theme.css` using relative paths (e.g., `url('../my-custom-theme/img/background.png')`).
    *   **Custom Fonts**: To use custom fonts, place your font files (e.g., `.woff2`, `.ttf`) in a `fonts` subdirectory and define them using `@font-face` rules in your `theme.css` before using them in your variable definitions.

    ```css
    /* static/themes/my-custom-theme/theme.css */
    @font-face {
        font-family: 'PixelFont';
        src: url('../my-custom-theme/fonts/PixelFont.woff2') format('woff2');
        /* Add other font formats as needed */
        font-weight: normal;
        font-style: normal;
    }

    body.theme-my-custom-theme {
        --font-family-base: 'PixelFont', sans-serif;
        /* ... other variables ... */
    }
    ```

6.  **Activate and Test Your Theme**:
    *   Once your `theme.css` is ready (and any other assets are in place), start your WindFlag application.
    *   Navigate to the Admin Panel: `/admin`.
    *   Go to the "Themes" management section (typically `/admin/themes`).
    *   Your new theme (`my-custom-theme` in this example) should appear in the list of available themes.
    *   Select your theme from the dropdown and click "Set Active Theme".
    *   Thoroughly test your theme across different pages of the application to ensure all elements are styled correctly and that it is responsive on various screen sizes. Check for readability and accessibility.

## Theme Development Best Practices

*   **Start Simple**: Begin by only overriding a few key color variables. Gradually add more customizations.
*   **Consistency is Key**: Ensure your chosen colors, fonts, and spacing are consistent throughout the theme for a professional look.
*   **Accessibility**: Pay attention to color contrast to ensure your theme is readable for all users. Use tools to check contrast ratios.
*   **Responsiveness**: Always test your theme on different devices (desktops, tablets, mobile phones) to ensure it looks good and functions correctly at all screen resolutions.
*   **Utilize Existing Themes**: Look at the provided default themes (`default`, `cyberdeck`, etc.) in `static/themes/` for inspiration and examples of how to define variables and styles.
*   **Version Control**: If you're developing a complex theme, consider managing its files under version control (e.g., Git) separate from the main project, and then copy the final output into `static/themes/`.

## Advanced Theming Concepts

For theme developers looking to push the boundaries of customization, WindFlag's theming system offers several advanced avenues:

### Conditional Styling and Dynamic Content

While `theme.css` primarily handles static styling, dynamic styling based on user roles, challenge states, or other backend logic can be achieved through:

*   **Template Logic**: Modify Jinja2 templates (`.html` files in `templates/`) to apply additional classes or inline styles based on server-side conditions. For example, `{% if current_user.is_admin %} <body class="admin-user-theme"> {% endif %}` can introduce further theme variations.
*   **JavaScript Manipulation**: Theme-specific JavaScript (placed in `static/themes/your-theme/js/your-script.js`) can dynamically alter CSS variables, add/remove classes, or manipulate the DOM based on client-side logic. This allows for interactive theme elements or real-time theme adjustments.

### Extending with CSS Preprocessors (Sass/Less)

For larger and more complex themes, using CSS preprocessors like Sass (SCSS) or Less can greatly improve maintainability and development efficiency.

1.  **Develop in Preprocessor**: Write your theme's styles in `.scss` or `.less` files, taking advantage of features like nesting, mixins, functions, and partials.
2.  **Compile to `theme.css`**: Use a build tool (e.g., Node.js with `node-sass`, `gulp`, `webpack`) to compile your preprocessor files into the final `theme.css` file that WindFlag expects. Ensure your build process is integrated into your theme development workflow.
3.  **Benefits**: This allows for more organized stylesheets, easier management of complex color schemes, and reusable code blocks.

### Integrating Custom Fonts and Icon Sets

Beyond the basic `@font-face` example, you can integrate entire font libraries or custom icon sets:

*   **Google Fonts/Font Awesome**: Link to external font services or icon CDNs directly in your theme's custom HTML (if allowed by the platform configuration) or use `@import` rules in your `theme.css` (though self-hosting is often preferred for performance).
*   **Self-Hosting**: For full control and better performance, download font files (WOFF2 is recommended for modern browsers) and icon SVG sprites, place them in your theme's `static/themes/your-theme/fonts/` or `static/themes/your-theme/icons/` directories, and reference them in your `theme.css`.

### Theme-Specific JavaScript

While theming is primarily CSS, a theme might require custom JavaScript for animations, interactive elements, or unique UI behaviors.

*   Place your JavaScript files in a `static/themes/your-theme/js/` directory.
*   Ensure these scripts are loaded appropriately by the application (you might need to modify base templates or rely on a mechanism that automatically loads `theme.js` if it exists).
*   Be mindful of JavaScript conflicts with the core application scripts. Use IIFEs (Immediately Invoked Function Expressions) or modules to encapsulate your code.

By exploring these advanced concepts, theme developers can create truly unique and dynamic visual experiences for their WindFlag CTF platform.