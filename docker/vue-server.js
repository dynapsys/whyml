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
        let vueContent = '';
        
        // Try to read Vue component file
        if (fs.existsSync('./index.vue')) {
            vueContent = fs.readFileSync('./index.vue', 'utf8');
        }
        
        // Create a simple HTML wrapper for the Vue component
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue.js Implementation</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
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
        .vue-content {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .example-domain-wrapper {
            width: 600px;
            margin: 5em auto;
            padding: 2em;
            background-color: #fdfdff;
            border-radius: 0.5em;
            box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);
        }
        .example-link {
            color: #38488f;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Vue.js Implementation</h1>
        <p>This is the Vue.js version of the converted content.</p>
        <div id="app"></div>
        ${vueContent ? `
        <div class="vue-content">
            <h3>Vue Component Code:</h3>
            <pre><code>${vueContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
        </div>
        ` : ''}
    </div>
    
    <script>
        const { createApp } = Vue;
        
        const ExampleDomainComponent = {
            template: \`
                <div class="example-domain-wrapper">
                    <h1>Example Domain</h1>
                    <p>This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.</p>
                    <p><a href="https://www.iana.org/domains/example" class="example-link">More information...</a></p>
                </div>
            \`,
            mounted() {
                console.log('Vue component mounted');
            }
        };
        
        createApp(ExampleDomainComponent).mount('#app');
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
    console.log(`Vue service running on port ${PORT}`);
});
