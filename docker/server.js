const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Enable CORS for iframe embedding
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// Set headers to allow iframe embedding
app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'ALLOWALL');
    res.setHeader('Content-Security-Policy', "frame-ancestors *");
    next();
});

// Serve static files
app.use(express.static('.'));

// Main route
app.get('/', (req, res) => {
    try {
        // Try to read index.js file
        if (fs.existsSync('./index.js')) {
            const jsContent = fs.readFileSync('./index.js', 'utf8');
            
            // Create a simple HTML wrapper for the JavaScript
            const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript Implementation</title>
    <style>
        body {
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f2;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .js-content {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>JavaScript Implementation</h1>
        <p>This is the JavaScript version of the converted content.</p>
        <div id="content"></div>
        <div class="js-content">
            <h3>JavaScript Code:</h3>
            <pre><code>${jsContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
        </div>
    </div>
    <script>
        ${jsContent}
    </script>
</body>
</html>`;
            res.send(html);
        } else {
            res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript Service</title>
    <style>
        body {
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f2;
            text-align: center;
        }
        .container {
            max-width: 600px;
            margin: 5em auto;
            padding: 2em;
            background-color: #fdfdff;
            border-radius: 0.5em;
            box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>JavaScript Service</h1>
        <p>This is the JavaScript/Node.js implementation running on port 8012.</p>
        <p>No index.js file found in the project directory.</p>
    </div>
</body>
</html>`);
        }
    } catch (error) {
        console.error('Error:', error);
        res.status(500).send('Server error');
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`JavaScript service running on port ${PORT}`);
});
