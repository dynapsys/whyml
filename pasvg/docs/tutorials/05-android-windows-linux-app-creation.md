# Tutorial 5: Android/Windows/Linux Application Creation using APK.yaml Manifest

## Overview
This tutorial demonstrates how to create cross-platform applications for Android, Windows, and Linux using WhyML manifests, with complete build pipelines, deployment configurations, and distribution packages.

## Prerequisites
- WhyML installed (`pip install whyml`)
- Docker and Docker Compose
- Android SDK (for Android builds)
- Electron CLI (for desktop builds)
- Node.js 18+ and npm

## Project Structure
```
cross-platform-apps/
├── manifests/
│   ├── apk.yaml              # Android application manifest
│   ├── windows-app.yaml      # Windows application manifest
│   ├── linux-app.yaml       # Linux application manifest
│   └── base-config.yaml      # Shared configuration
├── src/
│   ├── android/
│   │   ├── app/
│   │   ├── gradle/
│   │   └── build.gradle
│   ├── desktop/
│   │   ├── main.js
│   │   ├── renderer/
│   │   └── package.json
│   └── shared/
│       ├── assets/
│       ├── components/
│       └── utils/
├── build/
│   ├── android/
│   ├── windows/
│   └── linux/
├── scripts/
│   ├── build-android.sh
│   ├── build-windows.sh
│   ├── build-linux.sh
│   └── deploy-all.sh
├── docker/
│   ├── android-builder.dockerfile
│   ├── electron-builder.dockerfile
│   └── nginx-server.dockerfile
└── docker-compose.yml
```

## Step 1: Base Application Configuration

**manifests/base-config.yaml:**
```yaml
metadata:
  app_name: "WhyML Cross-Platform App"
  package_name: "com.whyml.crossplatform"
  version: "1.0.0"
  description: "Multi-platform application generated from web content"
  author: "WhyML Generator"
  license: "MIT"

config:
  build_tools:
    android: "gradle"
    desktop: "electron"
    web: "webpack"
  
  features:
    - offline_support
    - push_notifications
    - file_system_access
    - camera_access
    - geolocation

variables:
  app_title: "{{app_name}}"
  primary_color: "#2563eb"
  secondary_color: "#1e40af"
  background_color: "#ffffff"
  icon_path: "assets/icons/"

shared_dependencies:
  - "react@^18.0.0"
  - "react-dom@^18.0.0"
  - "axios@^1.0.0"
  - "localforage@^1.10.0"

platforms:
  android:
    min_sdk: 24
    target_sdk: 33
    permissions:
      - android.permission.INTERNET
      - android.permission.CAMERA
      - android.permission.ACCESS_FINE_LOCATION
  
  windows:
    min_version: "10.0.19041"
    architecture: ["x64", "arm64"]
    features:
      - notifications
      - file_associations
  
  linux:
    distributions: ["ubuntu", "debian", "fedora", "arch"]
    architecture: ["x64", "arm64"]
    package_formats: ["deb", "rpm", "appimage", "snap"]
```

## Step 2: Android Application Manifest

**manifests/apk.yaml:**
```yaml
metadata:
  name: "Android WhyML App"
  platform: "android"
  build_type: "release"

config:
  package_name: "{{package_name}}"
  version_code: 1
  version_name: "{{version}}"
  min_sdk_version: 24
  target_sdk_version: 33
  compile_sdk_version: 33

structure:
  main_activity: |
    package {{package_name}};

    import android.os.Bundle;
    import android.webkit.WebView;
    import android.webkit.WebViewClient;
    import android.webkit.WebSettings;
    import androidx.appcompat.app.AppCompatActivity;

    public class MainActivity extends AppCompatActivity {
        private WebView webView;

        @Override
        protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_main);

            webView = findViewById(R.id.webview);
            WebSettings webSettings = webView.getSettings();
            webSettings.setJavaScriptEnabled(true);
            webSettings.setDomStorageEnabled(true);
            webSettings.setAllowFileAccess(true);
            webSettings.setAllowContentAccess(true);

            webView.setWebViewClient(new WebViewClient());
            webView.loadUrl("file:///android_asset/index.html");
        }

        @Override
        public void onBackPressed() {
            if (webView.canGoBack()) {
                webView.goBack();
            } else {
                super.onBackPressed();
            }
        }
    }

  manifest_xml: |
    <?xml version="1.0" encoding="utf-8"?>
    <manifest xmlns:android="http://schemas.android.com/apk/res/android"
        package="{{package_name}}">

        <uses-permission android:name="android.permission.INTERNET" />
        <uses-permission android:name="android.permission.CAMERA" />
        <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
        <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />

        <application
            android:allowBackup="true"
            android:icon="@mipmap/ic_launcher"
            android:label="{{app_title}}"
            android:theme="@style/AppTheme">
            
            <activity
                android:name=".MainActivity"
                android:exported="true"
                android:launchMode="singleTop">
                <intent-filter>
                    <action android:name="android.intent.action.MAIN" />
                    <category android:name="android.intent.category.LAUNCHER" />
                </intent-filter>
            </activity>
        </application>
    </manifest>

  layout_main: |
    <?xml version="1.0" encoding="utf-8"?>
    <RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
        android:layout_width="match_parent"
        android:layout_height="match_parent">

        <WebView
            android:id="@+id/webview"
            android:layout_width="match_parent"
            android:layout_height="match_parent" />

    </RelativeLayout>

  build_gradle: |
    apply plugin: 'com.android.application'

    android {
        compileSdkVersion {{compile_sdk_version}}
        buildToolsVersion "33.0.0"

        defaultConfig {
            applicationId "{{package_name}}"
            minSdkVersion {{min_sdk_version}}
            targetSdkVersion {{target_sdk_version}}
            versionCode {{version_code}}
            versionName "{{version_name}}"
        }

        buildTypes {
            release {
                minifyEnabled false
                proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            }
        }
    }

    dependencies {
        implementation 'androidx.appcompat:appcompat:1.6.1'
        implementation 'com.google.android.material:material:1.8.0'
        implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    }

android_features:
  - name: "WebView Integration"
    description: "Seamless web content rendering in native Android app"
  - name: "File System Access"
    description: "Read/write access to device storage"
  - name: "Camera Integration"
    description: "Camera access for photo capture"
  - name: "Geolocation"
    description: "GPS location services"
```

## Step 3: Windows Application Manifest

**manifests/windows-app.yaml:**
```yaml
metadata:
  name: "Windows WhyML App"
  platform: "windows"
  build_type: "electron"

config:
  executable_name: "{{app_name}}.exe"
  install_directory: "Program Files/{{app_name}}"
  min_windows_version: "10.0.19041"

structure:
  main_js: |
    const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
    const path = require('path');
    const isDev = process.env.NODE_ENV === 'development';

    let mainWindow;

    function createMainWindow() {
      mainWindow = new BrowserWindow({
        title: '{{app_title}}',
        width: 1200,
        height: 800,
        icon: path.join(__dirname, 'assets/icons/icon.ico'),
        webPreferences: {
          nodeIntegration: true,
          contextIsolation: false,
          enableRemoteModule: true
        }
      });

      if (isDev) {
        mainWindow.webContents.openDevTools();
      }

      mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));

      mainWindow.on('closed', () => {
        mainWindow = null;
      });
    }

    app.whenReady().then(() => {
      createMainWindow();
      
      const template = [
        {
          label: 'File',
          submenu: [
            {
              label: 'New',
              accelerator: 'CmdOrCtrl+N',
              click: () => {
                // Handle new file
                console.log('New file clicked');
              }
            },
            {
              label: 'Open',
              accelerator: 'CmdOrCtrl+O',
              click: async () => {
                const result = await dialog.showOpenDialog(mainWindow, {
                  properties: ['openFile'],
                  filters: [
                    { name: 'All Files', extensions: ['*'] }
                  ]
                });
                
                if (!result.canceled) {
                  console.log('Selected file:', result.filePaths[0]);
                }
              }
            },
            { type: 'separator' },
            {
              label: 'Exit',
              accelerator: 'CmdOrCtrl+Q',
              click: () => {
                app.quit();
              }
            }
          ]
        },
        {
          label: 'Edit',
          submenu: [
            { role: 'undo' },
            { role: 'redo' },
            { type: 'separator' },
            { role: 'cut' },
            { role: 'copy' },
            { role: 'paste' }
          ]
        },
        {
          label: 'View',
          submenu: [
            { role: 'reload' },
            { role: 'forceReload' },
            { role: 'toggleDevTools' },
            { type: 'separator' },
            { role: 'resetZoom' },
            { role: 'zoomIn' },
            { role: 'zoomOut' },
            { type: 'separator' },
            { role: 'togglefullscreen' }
          ]
        },
        {
          label: 'Window',
          submenu: [
            { role: 'minimize' },
            { role: 'close' }
          ]
        },
        {
          label: 'Help',
          submenu: [
            {
              label: 'About {{app_title}}',
              click: () => {
                dialog.showMessageBox(mainWindow, {
                  type: 'info',
                  title: 'About {{app_title}}',
                  message: '{{app_title}}',
                  detail: 'Version {{version}}\nGenerated with WhyML'
                });
              }
            }
          ]
        }
      ];

      const menu = Menu.buildFromTemplate(template);
      Menu.setApplicationMenu(menu);

      app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
          createMainWindow();
        }
      });
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

  package_json: |
    {
      "name": "{{package_name}}",
      "version": "{{version}}",
      "description": "{{description}}",
      "main": "main.js",
      "scripts": {
        "start": "electron .",
        "build": "electron-builder",
        "build-win": "electron-builder --win",
        "build-mac": "electron-builder --mac",
        "build-linux": "electron-builder --linux"
      },
      "build": {
        "appId": "{{package_name}}",
        "productName": "{{app_title}}",
        "directories": {
          "output": "dist"
        },
        "files": [
          "main.js",
          "renderer/**/*",
          "assets/**/*",
          "node_modules/**/*"
        ],
        "win": {
          "target": "nsis",
          "icon": "assets/icons/icon.ico"
        },
        "nsis": {
          "oneClick": false,
          "allowToChangeInstallationDirectory": true
        }
      },
      "dependencies": {
        "electron": "^22.0.0"
      },
      "devDependencies": {
        "electron-builder": "^24.0.0"
      }
    }

  renderer_html: |
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{app_title}}</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div id="app">
            <header class="app-header">
                <h1>{{app_title}}</h1>
                <div class="controls">
                    <button id="file-btn">Open File</button>
                    <button id="settings-btn">Settings</button>
                </div>
            </header>
            
            <main class="app-content">
                <div class="content-area">
                    <h2>Welcome to {{app_title}}</h2>
                    <p>This Windows application was generated from web content using WhyML.</p>
                    
                    <div class="feature-list">
                        <div class="feature-item">
                            <h3>📁 File Management</h3>
                            <p>Open and manage files from your Windows system</p>
                        </div>
                        <div class="feature-item">
                            <h3>⚙️ System Integration</h3>
                            <p>Native Windows features and notifications</p>
                        </div>
                        <div class="feature-item">
                            <h3>🔒 Security</h3>
                            <p>Secure desktop environment with Electron</p>
                        </div>
                    </div>
                </div>
            </main>
            
            <footer class="app-footer">
                <p>Powered by WhyML + Electron | Version {{version}}</p>
            </footer>
        </div>
        
        <script src="app.js"></script>
    </body>
    </html>

windows_features:
  - name: "Native Menu Bar"
    description: "Standard Windows application menu with File, Edit, View, etc."
  - name: "File System Integration"
    description: "Open/save dialogs using native Windows APIs"
  - name: "System Notifications"
    description: "Windows toast notifications"
  - name: "Auto-Updater"
    description: "Automatic application updates via Electron"
```

## Step 4: Linux Application Manifest

**manifests/linux-app.yaml:**
```yaml
metadata:
  name: "Linux WhyML App"
  platform: "linux"
  build_type: "appimage"

config:
  executable_name: "{{app_name}}"
  install_directory: "/opt/{{app_name}}"
  desktop_entry: true

structure:
  desktop_file: |
    [Desktop Entry]
    Name={{app_title}}
    Comment={{description}}
    Exec={{executable_name}}
    Icon={{app_name}}
    Terminal=false
    Type=Application
    Categories=Utility;Development;
    StartupNotify=true

  appimage_config: |
    {
      "appId": "{{package_name}}",
      "productName": "{{app_title}}",
      "directories": {
        "output": "dist"
      },
      "linux": {
        "target": [
          {
            "target": "AppImage",
            "arch": ["x64", "arm64"]
          },
          {
            "target": "deb",
            "arch": ["x64", "arm64"]
          },
          {
            "target": "rpm",
            "arch": ["x64", "arm64"]
          },
          {
            "target": "snap",
            "arch": ["x64", "arm64"]
          }
        ],
        "category": "Utility",
        "icon": "assets/icons/icon.png"
      },
      "snap": {
        "summary": "{{description}}",
        "plugs": ["desktop", "desktop-legacy", "home", "x11", "unity7", "browser-support", "network", "gsettings", "audio-playback", "pulseaudio", "opengl"]
      },
      "deb": {
        "depends": ["gconf2", "gconf-service", "libnotify4", "libappindicator1", "libxtst6", "libnss3"]
      }
    }

  systemd_service: |
    [Unit]
    Description={{app_title}} Service
    After=network.target

    [Service]
    Type=simple
    User=whyml
    WorkingDirectory=/opt/{{app_name}}
    ExecStart=/opt/{{app_name}}/{{executable_name}}
    Restart=always

    [Install]
    WantedBy=multi-user.target

linux_features:
  - name: "Multiple Package Formats"
    description: "Support for AppImage, Deb, RPM, and Snap packages"
  - name: "Desktop Integration"
    description: "Native Linux desktop entry and application menu integration"
  - name: "Systemd Service"
    description: "Optional system service for background operation"
  - name: "Distribution Support"
    description: "Compatible with Ubuntu, Debian, Fedora, Arch, and more"
```

## Step 5: Build Scripts

**scripts/build-android.sh:**
```bash
#!/bin/bash
set -e

echo "🤖 Building Android Application..."

# Setup Android environment
export ANDROID_HOME=${ANDROID_HOME:-$HOME/Android/Sdk}
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Create Android project structure
mkdir -p src/android/app/src/main/{java,res,assets}
mkdir -p src/android/app/src/main/res/{layout,values,mipmap-{hdpi,mdpi,xhdpi,xxhdpi,xxxhdpi}}

# Generate Android files from manifest
echo "📱 Generating Android source files..."
whyml convert manifests/apk.yaml \
  --platform android \
  --output src/android/ \
  --format gradle

# Copy web assets to Android assets
echo "📋 Copying web assets..."
cp -r src/shared/assets/* src/android/app/src/main/assets/

# Build APK
echo "🔨 Building APK..."
cd src/android
./gradlew assembleRelease

# Sign APK (if keystore available)
if [ -f "app/release.keystore" ]; then
    echo "✍️ Signing APK..."
    jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
        -keystore app/release.keystore \
        app/build/outputs/apk/release/app-release-unsigned.apk \
        release
    
    zipalign -v 4 \
        app/build/outputs/apk/release/app-release-unsigned.apk \
        ../../build/android/app-release.apk
else
    cp app/build/outputs/apk/release/app-release-unsigned.apk \
       ../../build/android/app-release.apk
fi

echo "✅ Android build complete: build/android/app-release.apk"
```

**scripts/build-windows.sh:**
```bash
#!/bin/bash
set -e

echo "🪟 Building Windows Application..."

# Setup Windows build environment
mkdir -p src/desktop/renderer
mkdir -p build/windows

# Generate Electron app from manifest
echo "⚡ Generating Electron application..."
whyml convert manifests/windows-app.yaml \
  --platform windows \
  --output src/desktop/ \
  --format electron

# Copy shared assets
echo "📋 Copying assets..."
cp -r src/shared/assets src/desktop/
cp -r src/shared/components src/desktop/renderer/

# Install dependencies
echo "📦 Installing dependencies..."
cd src/desktop
npm install

# Build Windows executable
echo "🔨 Building Windows executable..."
npm run build-win

# Copy to build directory
cp -r dist/win-unpacked/* ../../build/windows/
cp dist/*.exe ../../build/windows/ 2>/dev/null || true

echo "✅ Windows build complete: build/windows/"
```

**scripts/build-linux.sh:**
```bash
#!/bin/bash
set -e

echo "🐧 Building Linux Application..."

# Setup Linux build environment
mkdir -p build/linux/{appimage,deb,rpm,snap}

# Generate Linux app from manifest
echo "🔧 Generating Linux application..."
whyml convert manifests/linux-app.yaml \
  --platform linux \
  --output src/desktop/ \
  --format electron

# Build all Linux formats
echo "📦 Building Linux packages..."
cd src/desktop

# AppImage
npm run build-linux -- --linux AppImage
cp dist/*.AppImage ../../build/linux/appimage/

# Debian package
npm run build-linux -- --linux deb
cp dist/*.deb ../../build/linux/deb/

# RPM package
npm run build-linux -- --linux rpm
cp dist/*.rpm ../../build/linux/rpm/

# Snap package (if snapcraft available)
if command -v snapcraft &> /dev/null; then
    npm run build-linux -- --linux snap
    cp dist/*.snap ../../build/linux/snap/
fi

echo "✅ Linux builds complete: build/linux/"
```

## Step 6: Docker Build Environment

**docker/android-builder.dockerfile:**
```dockerfile
FROM openjdk:11-jdk

# Install Android SDK
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Setup Android SDK
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH=${PATH}:${ANDROID_SDK_ROOT}/tools:${ANDROID_SDK_ROOT}/platform-tools

RUN mkdir -p ${ANDROID_SDK_ROOT} && \
    cd ${ANDROID_SDK_ROOT} && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip

# Accept licenses and install required packages
RUN yes | ${ANDROID_SDK_ROOT}/cmdline-tools/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} \
    "platform-tools" \
    "build-tools;33.0.0" \
    "platforms;android-33"

WORKDIR /workspace
COPY . .

CMD ["./scripts/build-android.sh"]
```

**docker/electron-builder.dockerfile:**
```dockerfile
FROM electronuserland/builder:wine

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install WhyML
RUN pip3 install whyml

WORKDIR /workspace
COPY . .

# Build for all platforms
CMD ["./scripts/build-all.sh"]
```

## Step 7: Deployment Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  android-builder:
    build:
      context: .
      dockerfile: docker/android-builder.dockerfile
    volumes:
      - .:/workspace
      - android-build-cache:/root/.gradle
    environment:
      - ANDROID_HOME=/opt/android-sdk

  electron-builder:
    build:
      context: .
      dockerfile: docker/electron-builder.dockerfile
    volumes:
      - .:/workspace
      - electron-cache:/root/.cache/electron
      - electron-builder-cache:/root/.cache/electron-builder
    environment:
      - NODE_ENV=production

  release-server:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./build:/usr/share/nginx/html
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - android-builder
      - electron-builder

volumes:
  android-build-cache:
  electron-cache:
  electron-builder-cache:
```

## Step 8: Complete Build Pipeline

**scripts/deploy-all.sh:**
```bash
#!/bin/bash
set -e

echo "🚀 Starting cross-platform build pipeline..."

# Parse command line arguments
PLATFORMS=${1:-"android,windows,linux"}
BUILD_TYPE=${2:-"release"}

echo "📋 Building for platforms: $PLATFORMS"
echo "🔧 Build type: $BUILD_TYPE"

# Create build directories
mkdir -p build/{android,windows,linux}

# Build Android if requested
if [[ $PLATFORMS == *"android"* ]]; then
    echo "🤖 Building Android application..."
    if command -v docker &> /dev/null; then
        docker-compose run --rm android-builder
    else
        ./scripts/build-android.sh
    fi
fi

# Build Windows if requested
if [[ $PLATFORMS == *"windows"* ]]; then
    echo "🪟 Building Windows application..."
    if command -v docker &> /dev/null; then
        docker-compose run --rm electron-builder ./scripts/build-windows.sh
    else
        ./scripts/build-windows.sh
    fi
fi

# Build Linux if requested
if [[ $PLATFORMS == *"linux"* ]]; then
    echo "🐧 Building Linux applications..."
    if command -v docker &> /dev/null; then
        docker-compose run --rm electron-builder ./scripts/build-linux.sh
    else
        ./scripts/build-linux.sh
    fi
fi

# Create release packages
echo "📦 Creating release packages..."
cd build

# Create Android release
if [ -d "android" ] && [ "$(ls -A android)" ]; then
    tar -czf android-release.tar.gz android/
    echo "✅ Android release: build/android-release.tar.gz"
fi

# Create Windows release
if [ -d "windows" ] && [ "$(ls -A windows)" ]; then
    zip -r windows-release.zip windows/
    echo "✅ Windows release: build/windows-release.zip"
fi

# Create Linux releases
if [ -d "linux" ] && [ "$(ls -A linux)" ]; then
    tar -czf linux-release.tar.gz linux/
    echo "✅ Linux release: build/linux-release.tar.gz"
fi

# Start release server
echo "🌐 Starting release server..."
if command -v docker &> /dev/null; then
    docker-compose up -d release-server
    echo "📥 Download releases at: http://localhost:8080"
else
    python3 -m http.server 8080 --directory build &
    echo "📥 Download releases at: http://localhost:8080"
fi

echo "🎉 Cross-platform build pipeline completed successfully!"
echo "📱 Android APK: build/android/"
echo "🪟 Windows EXE: build/windows/"
echo "🐧 Linux packages: build/linux/"
```

## Step 9: Usage Examples

### Generate Android APK
```bash
# Simple Android build
whyml convert manifests/apk.yaml --platform android --output build/

# Full pipeline with Docker
./scripts/deploy-all.sh android

# Manual build
./scripts/build-android.sh
```

### Generate Windows Application
```bash
# Windows Electron app
whyml convert manifests/windows-app.yaml --platform windows --output build/

# Build with installer
./scripts/build-windows.sh

# Docker build
docker-compose run --rm electron-builder ./scripts/build-windows.sh
```

### Generate Linux Packages
```bash
# All Linux formats
./scripts/build-linux.sh

# Specific format
whyml convert manifests/linux-app.yaml --platform linux --format appimage --output build/
```

### Build All Platforms
```bash
# Complete cross-platform build
./scripts/deploy-all.sh

# Specific platforms
./scripts/deploy-all.sh "android,windows" release

# Development build
./scripts/deploy-all.sh "linux" debug
```

## Features Demonstrated

1. **Cross-Platform Compatibility**: Single manifest generates Android, Windows, and Linux applications
2. **Native Integration**: Platform-specific features and APIs
3. **Package Management**: Multiple distribution formats (APK, EXE, AppImage, Deb, RPM, Snap)
4. **Build Pipeline**: Docker-based build environment for consistent results
5. **Release Automation**: Complete CI/CD pipeline with automated packaging
6. **Asset Management**: Shared resources across platforms
7. **Configuration Management**: Platform-specific configurations and permissions

## Distribution

- **Android**: Google Play Store, F-Droid, or direct APK distribution
- **Windows**: Microsoft Store, direct EXE, or MSI installer
- **Linux**: Distribution repositories, AppImage, Snap Store, or Flatpak

This tutorial demonstrates the complete workflow from WhyML manifest to deployed cross-platform applications on Android, Windows, and Linux systems.
