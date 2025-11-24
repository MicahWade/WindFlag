# Theme Management

The CTF platform supports a flexible theming system that allows administrators to change the visual appearance of the application. Themes are defined using CSS and are managed through the admin panel.

## How Theming Works

The theming system is based on a directory of themes located in `static/themes/`. Each subdirectory within `static/themes/` represents a single theme. For a theme to be valid, it must contain a `theme.css` file.

When a theme is active, its `theme.css` file is loaded, and a class in the format `theme-<theme_name>` is applied to the `<body>` tag of the application. This allows for theme-specific styling using CSS selectors.

### CSS Variables

The recommended approach for creating themes is to use CSS variables (custom properties). This allows for a consistent and maintainable way to define a theme's color palette, fonts, and other visual properties.

The core of the theming system relies on a set of CSS variables that are used by the application's semantic classes. By overriding these variables in your theme's `theme.css`, you can change the appearance of the entire application.

Here are the essential CSS variables that your theme should define within the `body.theme-<theme_name>` block:

*   `--bg-main`: The main background color of the application.
*   `--bg-surface`: The background color for surfaces like cards, modals, and panels.
*   `--bg-input`: The background color for input fields.
*   `--text-header`: The color for header text (h1, h2, etc.).
*   `--text-main`: The main text color for paragraphs and other content.
*   `--text-muted`: The color for muted or secondary text.
*   `--border-color`: The color for borders on elements like cards and inputs.
*   `--primary`: The primary accent color, used for buttons, links, and other interactive elements.
*   `--radius`: The default border-radius for elements like cards and buttons.
*   `--card-border`: The full `border` property for cards (e.g., `1px solid var(--border-color)`).
*   `--card-shadow`: The `box-shadow` property for cards.
*   `--bg-completed`: The background color for completed challenges.
*   `--bg-hover-surface`: The background color for surfaces when hovered.

### Semantic Classes

The application uses a set of semantic CSS classes that are styled by the theme's CSS variables. By using these classes in the HTML, you can ensure that your components will be styled consistently with the active theme.

Examples of semantic classes include:

*   `.theme-card`: For card-like containers.
*   `.theme-table`: For tables.
*   `.theme-table-header-cell`: For table header cells.
*   `.theme-table-body-cell`: For table body cells.
*   `.theme-page-title`: For main page titles.
*   `.theme-modal-button-primary`: For primary buttons in modals.

By defining the CSS variables in your theme, these semantic classes will automatically adopt your theme's styling.

## Creating a New Theme

To create a new theme, follow these steps:

1.  **Create a New Directory**: Create a new directory for your theme inside `static/themes/`. The name of the directory will be the name of your theme (e.g., `static/themes/my-cool-theme/`).

2.  **Create `theme.css`**: Inside your new theme directory, create a `theme.css` file.

3.  **Define CSS Variables**: In `theme.css`, define the CSS variables for your theme within a `body.theme-<theme_name>` block. You can copy the variables from an existing theme (like `default` or `learning`) and modify the values to create your new look.

    **Example for `my-cool-theme`:**

    ```css
    body.theme-my-cool-theme {
        --bg-main: #111827;
        --bg-surface: #1f2937;
        --bg-input: #374151;
        --text-header: #f9fafb;
        --text-main: #d1d5db;
        --text-muted: #9ca3af;
        --border-color: #374151;
        --primary: #3b82f6;
        --radius: 0.5rem;
        --card-border: 1px solid var(--border-color);
        --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --bg-completed: #10b981;
        --bg-hover-surface: #374151;
    }
    ```

4.  **Activate the Theme**: Once your theme is created, you can activate it through the admin panel:
    *   Navigate to `/admin/themes`.
    *   Your new theme should appear in the list of available themes.
    *   Select your theme and click "Set Active Theme".

Your new theme will now be applied to the entire application.
