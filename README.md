# lavablend
Lava simulation processes and data in Blender

## Building Extension

To build the extension you first have to download the dependency wheels:

### Windows
Double click on `get_wheels.cmd`

### Linux/Mac
```bash
sh get_wheels.sh
```

Then you can run this command to build the addon zip file:
```bash
blender --command extension build --split-platform
```

See below if you don't have Blender available in your CLI.

## Adding Blender to CLI

### Prerequisites
- Download and install Blender from the [official website](https://www.blender.org/download/)

### Windows
1. During Blender installation, check the option to "Add Blender to system PATH"
2. If you missed this option or need to add it manually:
   - Find your Blender installation directory (typically `C:\Program Files\Blender Foundation\Blender X.X`)
   - Open Start menu and search for "Edit environment variables"
   - Click on "Environment Variables"
   - Under "System variables", find and select "Path", then click "Edit"
   - Click "New" and add your Blender installation directory
   - Click "OK" on all dialog boxes

### macOS
```bash
sudo ln -s /Applications/Blender.app/Contents/MacOS/Blender /usr/local/bin/blender
```

### Linux
If you installed Blender via package manager, the CLI should already be available.

If using a downloaded version, add Blender to your PATH:
```bash
export PATH=$PATH:/path/to/blender
```
Add this line to your `.bashrc` or `.zshrc` file to make it permanent.

### Verify Installation
Test that Blender CLI is working by opening a terminal/command prompt and typing:
```bash
blender --version
```
This should display the installed Blender version.


