# Flask Blog

A simple blog application built with Flask, allowing users to register, log in, create and manage posts, favorite posts, and view their profiles. This project demonstrates Python web development with Flask, SQLite database management, and deployment on PythonAnywhere.

## Features
- **User Authentication**: Register, log in, and log out with secure password hashing.
- **Blog Posts**:
  - Create, edit, and delete posts (with optional image uploads).
  - View all posts on the homepage or individual post pages.
  - Search posts by title, content, or author username.
- **Favorite Posts**: Logged-in users can favorite/unfavorite posts with a heart icon (red when favorited, grey when not).
- **User Profile**: Displays user details, their posts, and favorited posts.
- **Image Upload**: Supports PNG, JPG, JPEG, GIF images (max 16MB), stored in the database.

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite with Flask-SQLAlchemy
- **Forms**: Flask-WTF for form handling and CSRF protection
- **Frontend**: Bootstrap for styling, custom CSS for the heart icon
- **Deployment**: PythonAnywhere

## Project Structure
