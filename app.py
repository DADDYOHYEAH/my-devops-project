# Flask needs sessions to remember “this user is logged in”.
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import requests
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Secret key for session management. Flask signs session cookies using secret_key
app.secret_key = os.environ.get("SECRET_KEY", "devopsflix-secret")

# Rate Limiting - Prevents API abuse and spam attacks
# High limits for classroom demo with 30+ students on same WiFi
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per day", "5000 per hour"],
    storage_uri="memory://"
)

# TMDB API Configuration
# API key loaded from environment variable with fallback for team development
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "c98a3689e4042e45c726454885e21739")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# In-memory watchlist storage   / temporary database to store the movie watchlist 
# A simple list to store the user's watchlist temporarily
watchlist = []

USERS = {
    "admin": "123"
}

@app.route("/health")
def health_check():
    """Simple health check for Kubernetes probes"""
    return jsonify({"status": "healthy"}), 200

def fetch_trending_movies():  # this fucntion ensures homepage always show fresh content without us havvng to update it manually or hardcoded into the code itself by hitting external api 
    """Fetch trending movies of the week from TMDB API"""
    url = f"{TMDB_BASE_URL}/trending/movie/week"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException:
        return []


def fetch_top_rated_movies():  # it fetches top rated movies like classic movies . it uses the same endpoint but uses different endpoints to categorize the content for the usetr 
    """Fetch top rated movies from TMDB API"""
    url = f"{TMDB_BASE_URL}/movie/top_rated"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException:
        return []


def search_multi(query):  # takes a user search and only return movies and tv series removing actors or other random data . 
    """Search movies and TV series by query from TMDB API (multi-search)"""
    url = f"{TMDB_BASE_URL}/search/multi"
    params = {"api_key": TMDB_API_KEY, "query": query}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        # Filter to only movies and TV series, exclude people
        filtered = [r for r in results if r.get("media_type") in ("movie", "tv")]
        return filtered
    except requests.RequestException:
        return []


def fetch_tv_details(tv_id): # gets the huge details for a tv show , cast season , episode anf the youtbe trailer that allows us tp embed the trailer into the detaoil page 
    """Fetch detailed TV series info including cast and crew"""
    url = f"{TMDB_BASE_URL}/tv/{tv_id}"
    params = {"api_key": TMDB_API_KEY, "append_to_response": "credits,videos"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant info
        tv_details = {
            "id": data.get("id"),
            "title": data.get("name"),
            "overview": data.get("overview"),
            "poster_path": data.get("poster_path"),
            "backdrop_path": data.get("backdrop_path"),
            "release_date": data.get("first_air_date"),
            "runtime": data.get("episode_run_time", [None])[0] if data.get("episode_run_time") else None,
            "vote_average": data.get("vote_average"),
            "vote_count": data.get("vote_count"),
            "genres": [g["name"] for g in data.get("genres", [])],
            "tagline": data.get("tagline"),
            "status": data.get("status"),
            "media_type": "tv",
            "number_of_seasons": data.get("number_of_seasons"),
            "number_of_episodes": data.get("number_of_episodes"),
        }
        
        # Get trailer video
        videos = data.get("videos", {}).get("results", [])
        trailer = None
        for video in videos:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                trailer = video.get("key")
                break
        tv_details["trailer_key"] = trailer
        
        # Get cast (top 10)
        credits = data.get("credits", {})
        cast = credits.get("cast", [])[:10]
        tv_details["cast"] = [{
            "name": c.get("name"),
            "character": c.get("character"),
            "profile_path": c.get("profile_path")
        } for c in cast]
        
        # Get crew (creators)
        creators = data.get("created_by", [])
        tv_details["directors"] = [{"name": c.get("name")} for c in creators]
        tv_details["writers"] = []
        
        return tv_details
    except requests.RequestException:
        return None


def fetch_movie_details(movie_id): # same as above but for movies
    """Fetch detailed movie info including cast and crew"""
    # Get movie details
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "append_to_response": "credits,videos"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant info
        movie_details = {
            "id": data.get("id"),
            "title": data.get("title"),
            "overview": data.get("overview"),
            "poster_path": data.get("poster_path"),
            "backdrop_path": data.get("backdrop_path"),
            "release_date": data.get("release_date"),
            "runtime": data.get("runtime"),
            "vote_average": data.get("vote_average"),
            "vote_count": data.get("vote_count"),
            "genres": [g["name"] for g in data.get("genres", [])],
            "tagline": data.get("tagline"),
            "status": data.get("status"),
            "budget": data.get("budget"),
            "revenue": data.get("revenue"),
        }
        
        # Get trailer video
        videos = data.get("videos", {}).get("results", [])
        trailer = None
        for video in videos:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                trailer = video.get("key")
                break
        movie_details["trailer_key"] = trailer
        
        # Get cast (top 10)
        credits = data.get("credits", {})
        cast = credits.get("cast", [])[:10]
        movie_details["cast"] = [{
            "name": c.get("name"),
            "character": c.get("character"),
            "profile_path": c.get("profile_path")
        } for c in cast]
        
        # Get crew (directors, writers)
        crew = credits.get("crew", [])
        directors = [c for c in crew if c.get("job") == "Director"]
        writers = [c for c in crew if c.get("department") == "Writing"][:3]
        movie_details["directors"] = [{"name": d.get("name")} for d in directors]
        movie_details["writers"] = [{"name": w.get("name"), "job": w.get("job")} for w in writers]
        
        return movie_details
    except requests.RequestException:
        return None

def fetch_watch_providers(media_type, media_id, title):
    """Fetch legal streaming providers and generate smart links"""
    url = f"{TMDB_BASE_URL}/{media_type}/{media_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("results", {})
        
        country_code = "SG" # Singapore
        
        if country_code in data:
            provider_data = data[country_code]
            
            # --- SMART LINK LOGIC ---
            # We add a custom 'link' to each provider
            if "flatrate" in provider_data:
                for provider in provider_data["flatrate"]:
                    name = provider["provider_name"]
                    encoded_title = requests.utils.quote(title)
                    
                    if "Netflix" in name:
                        provider["custom_link"] = f"https://www.netflix.com/search?q={encoded_title}"
                    elif "Amazon" in name or "Prime" in name:
                        provider["custom_link"] = f"https://www.amazon.com/s?k={encoded_title}&i=instant-video"
                    elif "Disney" in name:
                        provider["custom_link"] = f"https://www.disneyplus.com/search?q={encoded_title}"
                    elif "HBO" in name:
                        provider["custom_link"] = f"https://www.hbomax.com/search?q={encoded_title}"
                    elif "YouTube" in name:
                         provider["custom_link"] = f"https://www.youtube.com/results?search_query={encoded_title}"
                    else:
                        # Fallback to Google if we don't know the specific app
                        provider["custom_link"] = f"https://www.google.com/search?q=watch+{encoded_title}+on+{name}"
            
            return provider_data
            
        return None
    except requests.RequestException:
        return None

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("100 per minute")  # High limit for classroom demo
def login():
    # Read username and password from submitted HTML form
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # If credentials are valid, store username in session and redirect to index
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("index"))
        
        # If login fails, reload login page with error message
        return render_template("login.html", error="Invalid credentials")
    
    # Render login page on GET request
    return render_template("login.html")

# Clears user session and logs the user out
@app.route("/logout")
def logout():
    session.pop("user", None) # Removes 'user' from session
    return redirect(url_for("index")) # Redirects back to homepage


@app.route("/signup", methods=["GET", "POST"])
@limiter.limit("200 per hour")  # Allow classroom demo with 30+ students
def signup():
    """Handle user registration"""
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation checks
        if not all([email, username, password, confirm_password]):
            return render_template("signup.html", error="All fields are required")
        
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")
        
        if len(password) < 4:
            return render_template("signup.html", error="Password must be at least 4 characters")
        
        if username in USERS:
            return render_template("signup.html", error="Username already exists")
        
        # Add new user to USERS dictionary (in-memory, resets on server restart)
        USERS[username] = password
        
        # Redirect to login page with success message
        return render_template("signup.html", success="Account created successfully! You can now sign in.")
    
    # Render signup page on GET request
    return render_template("signup.html")


@app.route("/") # it gets the trending and top rated dats and also picks the #1 movie for the hero banner image at the top of the homepage anfd sends it all to index.htm; 
def index():
    """Main page with trending, top rated movies and watchlist"""
    trending = fetch_trending_movies()
    top_rated = fetch_top_rated_movies()
    
    # Select a featured movie for the hero banner (first trending movie)
    hero_movie = trending[0] if trending else None
    
    return render_template(
        "index.html",
        trending=trending,
        top_rated=top_rated,
        watchlist=watchlist,
        hero_movie=hero_movie,
        image_base=TMDB_IMAGE_BASE
    )


@app.route("/search")  # simopl l0ads the dedicatedn search page
def search_page():
    """Render the dedicated search page"""
    trending = fetch_trending_movies()
    return render_template(
        "search.html",
        trending=trending,
        image_base=TMDB_IMAGE_BASE
    )

@app.route("/api/search")  # created a dedicaeted API endpoint for search . this returns json data instead of html . this allows the frontend to update search result as instantly as the user types without haveing to reload the whole page
@limiter.limit("500 per minute")  # High limit for classroom demo with 30+ students
def search():
    """Search endpoint for querying movies and TV series"""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"results": []})
    
    results = search_multi(query)
    return jsonify({"results": results, "image_base": TMDB_IMAGE_BASE})


@app.route("/movie/<int:movie_id>")
def get_movie_details(movie_id):
    """Render full movie detail page with Streaming Providers"""
    details = fetch_movie_details(movie_id)


    # SAFETY CHECK: Stop here if movie isn't found
    if not details:
        return render_template("404.html"), 404
    
    # NEW: Fetch where to watch this movie
    providers = fetch_watch_providers("movie", movie_id, details.get("title"))
    
    if details:
        return render_template(
            "movie_detail.html",
            movie=details,
            providers=providers,  # <--- Pass the new data to HTML
            image_base=TMDB_IMAGE_BASE
        )
    return render_template("404.html"), 404


@app.route("/tv/<int:tv_id>")
def get_tv_details(tv_id):
    """Render full TV Show detail page"""
    details = fetch_tv_details(tv_id)
    
    # FIX 1: Safety Check - If TV show isn't found, stop here (Prevents 500 Error)
    if not details:
        return render_template("404.html"), 404

    # FIX 2: TV Shows use "name", Movies use "title". This handles both.
    tv_title = details.get("name", details.get("title"))
    
    # Now it is safe to fetch providers
    providers = fetch_watch_providers("tv", tv_id, tv_title)
    
    return render_template(
        "movie_detail.html",
        movie=details,
        providers=providers,
        image_base=TMDB_IMAGE_BASE
    )


@app.route("/watch/movie/<int:movie_id>")  # pass the correct movie id to the player template , which embed the third party video player vidking 
def watch_movie(movie_id):
    """Render movie player page with VidKing embed"""
    details = fetch_movie_details(movie_id)
    if details:
        return render_template(
            "player.html",
            title=details.get("title", "Movie"),
            tmdb_id=movie_id,
            media_type="movie"
        )
    return render_template("404.html"), 404


@app.route("/watch/tv/<int:tv_id>/<int:season>/<int:episode>") #  pass the correct tv show  id to the player template , which embed the third party video player vidking
def watch_tv(tv_id, season, episode):
    """Render TV player page with VidKing embed"""
    details = fetch_tv_details(tv_id)
    if details:
        return render_template(
            "player.html",
            title=details.get("title", "TV Series"),
            tmdb_id=tv_id,
            media_type="tv",
            season=season,
            episode=episode,
            total_seasons=details.get("number_of_seasons", 1)
        )
    return render_template("404.html"), 404


@app.route("/api/movie/<int:movie_id>") # provide raw json detail so user can see deytauks quicly wihtut lewving the home page
def get_movie_details_api(movie_id):
    """API endpoint for movie details (JSON)"""
    details = fetch_movie_details(movie_id)
    if details:
        return jsonify({"success": True, "movie": details, "image_base": TMDB_IMAGE_BASE})
    return jsonify({"success": False, "message": "Movie not found"}), 404


@app.route("/api/tv/<int:tv_id>")  # provide raw json data to show tv show detail
def get_tv_details_api(tv_id):
    """API endpoint for TV series details (JSON)"""
    details = fetch_tv_details(tv_id)
    if details:
        return jsonify({"success": True, "movie": details, "image_base": TMDB_IMAGE_BASE})
    return jsonify({"success": False, "message": "TV series not found"}), 404


@app.route("/watchlist/add", methods=["POST"])   # validation logic here to prevent duplicate entry . returns 400 error if aalready in the list 
@limiter.limit("200 per minute")  # High limit for classroom demo
def add_to_watchlist():
    """Add a movie to the watchlist"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    movie_id = data.get("id")
    title = data.get("title")
    poster_path = data.get("poster_path")
    
    if not all([movie_id, title]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    # Check if movie already in watchlist
    for movie in watchlist:
        if movie["id"] == movie_id:
            return jsonify({"success": False, "message": "Movie already in watchlist"}), 400
    
    movie_entry = {
        "id": movie_id,
        "title": title,
        "poster_path": poster_path
    }
    watchlist.append(movie_entry)
    
    return jsonify({"success": True, "message": "Movie added to watchlist", "watchlist": watchlist})


@app.route("/watchlist/remove", methods=["POST"])  # removes a movie form watchlist . if id isnt ffound it returns 404 error
def remove_from_watchlist():
    """Remove a movie from the watchlist"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    movie_id = data.get("id")
    
    if not movie_id:
        return jsonify({"success": False, "message": "Movie ID required"}), 400
    
    original_length = len(watchlist)
    # Find and remove the movie in place (don't reassign the list)
    for i, movie in enumerate(watchlist):
        if movie["id"] == movie_id:
            watchlist.pop(i)
            break
    
    if len(watchlist) == original_length:
        return jsonify({"success": False, "message": "Movie not found in watchlist"}), 404
    
    return jsonify({"success": True, "message": "Movie removed from watchlist", "watchlist": watchlist})


@app.route("/watchlist")  # allows rhe full list as json data .
def get_watchlist():
    """Get current watchlist"""
    return jsonify({"watchlist": watchlist})


# ============================================================
# ERROR HANDLERS - Custom error pages for better UX
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors - page not found"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors - internal server error"""
    return render_template("500.html"), 500


if __name__ == "__main__":
    # Get the PORT from Render, or use 5000 if running locally
    port = int(os.environ.get("PORT", 5000))
    # Turn off debug mode in production (optional, but good practice)
    app.run(host="0.0.0.0", port=port)

