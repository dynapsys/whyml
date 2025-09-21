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
        let tsContent = '';
        
        // Try to read TypeScript file
        if (fs.existsSync('./index.ts')) {
            tsContent = fs.readFileSync('./index.ts', 'utf8');
        }
        
        // Create a simple HTML wrapper for the TypeScript code
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TypeScript Implementation</title>
    <script src="https://unpkg.com/typescript@4.9.5/lib/typescript.js"></script>
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
        .ts-content {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .output {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: #fdfdff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>TypeScript Implementation</h1>
        <p>This is the TypeScript version of the converted content.</p>
        <div class="output">
            <div style="width: 600px; margin: 5em auto; padding: 2em; background-color: #fdfdff; border-radius: 0.5em; box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);">
                <h1>Example Domain</h1>
                <p>This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.</p>
                <p><a href="https://www.iana.org/domains/example" style="color: #38488f; text-decoration: none;">More information...</a></p>
            </div>
        </div>
        ${tsContent ? `
        <div class="ts-content">
            <h3>TypeScript Code:</h3>
            <pre><code>${tsContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
        </div>
        ` : ''}
    </div>
    
    <script>
        // Simple TypeScript-like functionality demonstration
        class ExampleDomainComponent {
            constructor(private container: HTMLElement) {
                this.render();
            }
            
            render(): void {
                console.log('TypeScript component rendered');
            }
        }
        
        // Initialize component
        const outputElement = document.querySelector('.output');
        if (outputElement) {
            new ExampleDomainComponent(outputElement as HTMLElement);
        }
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
    console.log(`TypeScript service running on port ${PORT}`);
});
