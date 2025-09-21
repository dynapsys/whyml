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
        let reactContent = '';
        let componentName = 'ExampleComponent';
        
        // Try to read React component file
        if (fs.existsSync('./index.tsx')) {
            reactContent = fs.readFileSync('./index.tsx', 'utf8');
        } else if (fs.existsSync('./index.jsx')) {
            reactContent = fs.readFileSync('./index.jsx', 'utf8');
        }
        
        // Create a simple HTML wrapper for the React component
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>React Implementation</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
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
        .react-content {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        #root {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>React Implementation</h1>
        <p>This is the React version of the converted content.</p>
        <div id="root"></div>
        ${reactContent ? `
        <div class="react-content">
            <h3>React Component Code:</h3>
            <pre><code>${reactContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
        </div>
        ` : ''}
    </div>
    
    <script type="text/babel">
        const { useState, useEffect } = React;
        
        function ExampleComponent() {
            return React.createElement('div', {
                style: {
                    width: '600px',
                    margin: '5em auto',
                    padding: '2em',
                    backgroundColor: '#fdfdff',
                    borderRadius: '0.5em',
                    boxShadow: '2px 3px 7px 2px rgba(0,0,0,0.02)',
                    fontFamily: '-apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif'
                }
            }, [
                React.createElement('h1', { key: 'title' }, 'Example Domain'),
                React.createElement('p', { key: 'description' }, 
                    'This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.'
                ),
                React.createElement('p', { key: 'link' }, 
                    React.createElement('a', {
                        href: 'https://www.iana.org/domains/example',
                        style: { color: '#38488f', textDecoration: 'none' }
                    }, 'More information...')
                )
            ]);
        }
        
        ReactDOM.render(React.createElement(ExampleComponent), document.getElementById('root'));
    </script>
</body>
</html>`;
        res.send(html);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).send('Server error');
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`React service running on port ${PORT}`);
});
