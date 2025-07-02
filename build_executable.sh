#!/usr/bin/env bash

read -p "Enter version number: " VERSION

if [[ -z "$VERSION" ]]; then
  echo "Version number cannot be empty."
  exit 1
fi

# Build with PyInstaller (keep previous builds)
echo "Building executable..."
pyinstaller --onefile --name "kubectleNav-ver-$VERSION" main.py

if [[ $? -eq 0 ]]; then
  echo "Executable created: dist/kubectleNav-ver-$VERSION"
else
  echo "Build failed."
  exit 1
fi 