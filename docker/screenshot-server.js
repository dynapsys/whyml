const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Enable CORS
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// Screenshot endpoint
app.get('/screenshot', async (req, res) => {
    const url = req.query.url;
    
    if (!url) {
        return res.status(400).json({ error: 'URL parameter is required' });
    }

    let browser;
    try {
        console.log(`Taking screenshot of: ${url}`);
        
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();
        
        // Set viewport
        await page.setViewport({
            width: 1200,
            height: 800,
            deviceScaleFactor: 1
        });

        // Navigate to URL with timeout
        await page.goto(url, {
            waitUntil: 'networkidle2',
            timeout: 10000
        });

        // Wait a bit for content to render
        await page.waitForTimeout(2000);

        // Take screenshot
        const screenshot = await page.screenshot({
            type: 'png',
            fullPage: false,  // Just the viewport
            quality: 90
        });

        res.setHeader('Content-Type', 'image/png');
        res.setHeader('Cache-Control', 'no-cache');
        res.send(screenshot);

    } catch (error) {
        console.error('Screenshot error:', error);
        res.status(500).json({ 
            error: 'Failed to take screenshot', 
            details: error.message 
        });
    } finally {
        if (browser) {
            await browser.close();
        }
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        service: 'screenshot-service',
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Screenshot service running on port ${PORT}`);
});
