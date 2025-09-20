# Example Web Project

This tutorial demonstrates how to embed multiple files in a PASVG container.

## Project Structure

```
project/
├── index.html
├── styles.css
└── app.js
```

## index.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>PASVG Demo</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Welcome to PASVG</h1>
        <p>This content was embedded in a single SVG file!</p>
        <button id="demoBtn">Click Me</button>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

## styles.css
```css
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

button:hover {
    background-color: #45a049;
}
```

## app.js
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('demoBtn');
    if (button) {
        button.addEventListener('click', function() {
            alert('Hello from PASVG!');
        });
    }
});
```
