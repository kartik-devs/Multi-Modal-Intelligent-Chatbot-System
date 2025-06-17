@echo off
echo ========== Git Commands for Chatbot Project ==========
echo.

echo --- Adding all modified files ---
git add .

echo.
echo --- Committing changes ---
git commit -m "Prepare project for Render deployment with API key security"

echo.
echo --- Pushing to GitHub (make sure your repository is private) ---
git push

echo.
echo --- Completed ---
echo If you see any errors, please ensure Git is installed and in your PATH
echo If successful, your changes are now on GitHub
echo.
pause 