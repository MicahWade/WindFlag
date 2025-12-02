#!/bin/bash

# Create necessary directories
echo "Creating directories..."
mkdir -p static/codemirror \
         static/vendor/font-awesome/css \
         static/vendor/font-awesome/webfonts \
         static/vendor/tailwindcss \
         static/vendor/socket.io \
         static/vendor/chart.js \
         static/vendor/luxon \
         static/vendor/chartjs-adapter-luxon \
         static/vendor/chartjs-adapter-date-fns \
         static/vendor/chartjs-plugin-annotation \
         static/vendor/jquery-datatables \
         static/js

# Function to download with curl or wget
download() {
    url=$1
    dest=$2
    echo "Downloading $url -> $dest"
    if command -v curl &> /dev/null; then
        curl -L -o "$dest" "$url"
    elif command -v wget &> /dev/null; then
        wget -O "$dest" "$url"
    else
        echo "Error: Neither curl nor wget found."
        exit 1
    fi
}

# CodeMirror
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/codemirror.min.css" "static/codemirror/codemirror.min.css"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/theme/dracula.min.css" "static/codemirror/dracula.min.css"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/codemirror.min.js" "static/codemirror/codemirror.min.js"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/mode/shell/shell.min.js" "static/codemirror/shell.min.js"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/mode/dart/dart.min.js" "static/codemirror/dart.min.js"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/mode/javascript/javascript.min.js" "static/codemirror/javascript.min.js"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/mode/php/php.min.js" "static/codemirror/php.min.js"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/mode/python/python.min.js" "static/codemirror/python.min.js"

# CodeMirror Fullscreen Addon
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/addon/display/fullscreen.min.css" "static/codemirror/fullscreen.min.css"
download "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/addon/display/fullscreen.min.js" "static/codemirror/fullscreen.min.js"

# Font Awesome
download "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" "static/vendor/font-awesome/css/all.min.css"
download "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2" "static/vendor/font-awesome/webfonts/fa-solid-900.woff2"
download "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.ttf" "static/vendor/font-awesome/webfonts/fa-solid-900.ttf"

# TailwindCSS
download "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4" "static/vendor/tailwindcss/browser.js"

# Socket.IO
download "https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js" "static/vendor/socket.io/socket.io.min.js"

# Chart.js and related libraries
download "https://cdn.jsdelivr.net/npm/chart.js" "static/vendor/chart.js/chart.min.js"
download "https://cdn.jsdelivr.net/npm/luxon@3.x/build/global/luxon.min.js" "static/vendor/luxon/luxon.min.js"
download "https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.x/dist/chartjs-adapter-luxon.min.js" "static/vendor/chartjs-adapter-luxon/chartjs-adapter-luxon.min.js"
download "https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3" "static/vendor/chartjs-adapter-date-fns/chartjs-adapter-date-fns.min.js"
download "https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.4.0" "static/vendor/chartjs-plugin-annotation/chartjs-plugin-annotation.min.js"

# jQuery and DataTables
download "https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css" "static/vendor/jquery-datatables/jquery.dataTables.min.css"
download "https://code.jquery.com/jquery-3.7.1.min.js" "static/vendor/jquery-datatables/jquery-3.7.1.min.js"
download "https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js" "static/vendor/jquery-datatables/jquery.dataTables.min.js"

# marked.js
download "https://cdn.jsdelivr.net/npm/marked@latest/marked.min.js" "static/js/marked.min.js"

echo "All assets downloaded successfully."