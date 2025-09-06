#!/bin/bash

# Push LucianMirror to GitHub
# Replace 'yourusername' with your actual GitHub username

echo "🚀 Pushing LucianMirror to GitHub..."
echo "Make sure you've created a new repo on GitHub first!"
echo ""
read -p "Enter your GitHub username: " username

# Add the remote origin
git remote add origin "https://github.com/${username}/LucianMirror.git"

# Set main as default branch
git branch -M main

# Push to GitHub
git push -u origin main

echo "✅ Done! Your project is now on GitHub at:"
echo "https://github.com/${username}/LucianMirror"