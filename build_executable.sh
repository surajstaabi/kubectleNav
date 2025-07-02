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
  DIST_PATH="$(pwd)/dist"
  BASHRC="$HOME/.bashrc"
  EXPORT_LINE="export PATH=\"$DIST_PATH:\$PATH\""
  # Create or update generic symlink
  ln -sf "kubectleNav-ver-$VERSION" "$DIST_PATH/kubectleNav"
  echo "Symlink created/updated: dist/kubectleNav -> dist/kubectleNav-ver-$VERSION"
  # Add to .bashrc if not already present
  if ! grep -Fxq "$EXPORT_LINE" "$BASHRC"; then
    echo "$EXPORT_LINE" >> "$BASHRC"
    echo "Added $DIST_PATH to PATH in $BASHRC."
    source "$BASHRC"
    echo "Reloaded $BASHRC."
  else
    echo "$DIST_PATH already in PATH in $BASHRC."
  fi
else
  echo "Build failed."
  exit 1
fi 