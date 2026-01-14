# PhishScope Website

Professional landing page for the PhishScope project.

## Quick Start

### Option 1: Using the Serve Script (Recommended)

```bash
./serve.sh
```

This will:
- Check if port 8060 is in use
- Kill any existing process on that port
- Start a Python HTTP server
- Open the website at http://localhost:8060

### Option 2: Manual Start

```bash
# Using Python 3
python3 -m http.server 8060

# Or using Python 2
python -m SimpleHTTPServer 8060
```

Then open your browser to: http://localhost:8060

## Features

- **Modern Design**: Dark theme optimized for developers
- **Responsive**: Works on desktop, tablet, and mobile
- **Interactive**: Smooth animations, tabs, and hover effects
- **Code Examples**: Syntax highlighting with copy buttons
- **Fast Loading**: Minimal dependencies, optimized assets

## Structure

```
docs/
├── index.html          # Main landing page
├── css/
│   └── style.css       # Styling (1000+ lines)
├── js/
│   └── main.js         # Interactivity
├── images/             # Images (add your own)
├── serve.sh            # Server script
└── README.md           # This file
```

## Deployment

### GitHub Pages

1. Push to GitHub
2. Go to Settings → Pages
3. Select source: `main` branch, `/docs` folder
4. Your site will be live at: `https://yourusername.github.io/PhishScope/`

### Netlify

1. Connect your GitHub repository
2. Set build directory to `docs`
3. Deploy!

### Custom Server

Upload the `docs` folder to any web server. No build process required!

## Customization

### Update Links

Replace placeholder links in `index.html`:
- GitHub repository URL
- Social media links
- Email addresses

### Add Images

Place images in the `images/` folder and reference them:
```html
<img src="images/your-image.png" alt="Description">
```

### Modify Colors

Edit CSS variables in `css/style.css`:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --accent-color: #ec4899;
    /* ... */
}
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## License

MIT License - Same as PhishScope project