from flask import Flask, render_template, request, jsonify, send_file, Response
import pandas as pd
import os
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
S3_BASE_URL = "https://arya-geetha-nlp.s3.us-east-1.amazonaws.com/"
DATA_FILE = 'transcriptions_with_key_phrases.csv'
PORT = 8080

def load_data():
    """Load the video transcription data"""
    try:
        print(f"Loading data from {DATA_FILE}...")
        df = pd.read_csv(DATA_FILE)
        print(f"Successfully loaded {len(df)} rows")
        print("Columns:", df.columns.tolist())
        print("\nSample video names:")
        print(df['video'].head())
        print("\nUnique video prefixes:")
        print(df['video'].str[:5].unique())
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['video', 'transcription', 'key_phrases'])

def get_module_videos(df, module_number):
    """Get videos for a specific module"""
    try:
        # Format the module prefix correctly (e.g., 'Mod01' for module 1)
        module_prefix = f"Mod{module_number:02d}"
        print(f"\nLooking for videos with prefix: {module_prefix}")
        
        # Filter videos that start with the module prefix by checking only first 5 characters
        module_videos = df[df['video'].str[:5] == module_prefix]
        print(f"Found {len(module_videos)} videos for module {module_number}")
        
        if len(module_videos) > 0:
            print("Sample video names found:", module_videos['video'].head().tolist())
        else:
            print("No videos found for this module")
            print("Available video names:", df['video'].head().tolist())
            
        return module_videos
    except Exception as e:
        print(f"Error in get_module_videos: {e}")
        return pd.DataFrame()

@app.route('/')
def index():
    """Render the main dashboard page"""
    df = load_data()
    return render_template('index.html', port=PORT)

@app.route('/api/videos/<int:module_number>')
def get_videos(module_number):
    """Get videos for a specific module"""
    try:
        df = load_data()
        print(f"\nLooking for videos in module {module_number}")
        print(f"Total rows in CSV: {len(df)}")
        print("Sample video names:", df['video'].head().tolist())
        
        module_videos = get_module_videos(df, module_number)
        
        videos = []
        for _, row in module_videos.iterrows():
            video_name = row['video']
            # Extract a more readable title from the video name
            title = video_name.replace(f"Mod{module_number:02d}", "").replace(".mp4", "").strip()
            videos.append({
                'id': video_name,
                'title': title,
                'transcript': row['key_phrases'][:200] + '...' if len(row['key_phrases']) > 200 else row['key_phrases'],
                'url': S3_BASE_URL + video_name
            })
        
        print(f"Returning {len(videos)} videos")
        return jsonify({'videos': videos})
    except Exception as e:
        print(f"Error in get_videos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<video_id>')
def download_transcript(video_id):
    """Download transcript as a text file"""
    df = load_data()
    video = df[df['video'] == video_id]
    
    if video.empty:
        return jsonify({'error': 'Video not found'}), 404
    
    transcript = video.iloc[0]['key_phrases']
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
    with open(temp_file.name, 'w') as f:
        f.write(transcript)
    
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=f"{video_id}_transcript.txt",
        mimetype='text/plain'
    )

@app.route('/api/search')
def search_videos():
    """Search videos by title or transcript"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'videos': []})
            
        df = load_data()
        # Search in both video names and transcripts
        mask = (
            df['video'].str.lower().str.contains(query, na=False) |
            df['key_phrases'].str.lower().str.contains(query, na=False)
        )
        matching_videos = df[mask]
        
        videos = []
        for _, row in matching_videos.iterrows():
            video_name = row['video']
            # Extract module number from video name
            module_num = video_name[3:5]  # Get the number part from 'ModXX'
            title = video_name.replace(f"Mod{module_num}", "").replace(".mp4", "").strip()
            videos.append({
                'id': video_name,
                'title': title,
                'transcript': row['key_phrases'][:200] + '...' if len(row['key_phrases']) > 200 else row['key_phrases'],
                'url': S3_BASE_URL + video_name,
                'module': f"Module {int(module_num)}"
            })
        
        return jsonify({'videos': videos})
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates folder if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create index.html template
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Machine Learning Basics</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --background-color: #f5f6fa;
            --card-background: #ffffff;
            --text-color: #2c3e50;
            --border-radius: 12px;
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 3rem 0;
            margin-bottom: 3rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .modules-container {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .module-button {
            background: var(--card-background);
            border: none;
            padding: 1.5rem 2rem;
            border-radius: var(--border-radius);
            font-size: 1.2rem;
            color: var(--primary-color);
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            min-width: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .module-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            background: linear-gradient(135deg, #ffffff, #f8f9fa);
        }

        .module-button.active {
            background: var(--secondary-color);
            color: white;
        }

        .videos-container {
            display: none;
            margin-top: 2rem;
        }

        .videos-container.active {
            display: block;
        }

        .videos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }

        .video-card {
            background: var(--card-background);
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: var(--transition);
        }

        .video-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .video-player {
            width: 100%;
            aspect-ratio: 16/9;
            background: #000;
        }

        .video-player video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .video-info {
            padding: 1.5rem;
        }

        .video-title {
            font-size: 1.2rem;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }

        .transcript {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: var(--border-radius);
            margin: 1rem 0;
            max-height: 150px;
            overflow-y: auto;
            font-size: 0.9rem;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.8rem 1.5rem;
            background: var(--secondary-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            text-decoration: none;
            transition: var(--transition);
            font-size: 0.9rem;
        }

        .btn:hover {
            background: var(--primary-color);
            transform: translateY(-2px);
        }

        .loading {
            text-align: center;
            padding: 2rem;
            font-size: 1.2rem;
            color: var(--secondary-color);
        }

        .error {
            background: #fee2e2;
            color: var(--accent-color);
            padding: 1rem;
            border-radius: var(--border-radius);
            margin: 1rem 0;
        }

        .back-button {
            margin-bottom: 2rem;
            background: var(--accent-color);
        }

        .hidden {
            display: none;
        }

        .search-container {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            justify-content: center;
        }

        .search-input {
            padding: 1rem;
            border: 2px solid var(--secondary-color);
            border-radius: var(--border-radius);
            font-size: 1rem;
            width: 50%;
            max-width: 500px;
            transition: var(--transition);
        }

        .search-input:focus {
            outline: none;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }

        .search-button {
            padding: 1rem 2rem;
            background: var(--secondary-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: var(--transition);
        }

        .search-button:hover {
            background: var(--primary-color);
            transform: translateY(-2px);
        }

        .module-tag {
            display: inline-block;
            background: var(--secondary-color);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: var(--border-radius);
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1><i class="fas fa-brain"></i> Machine Learning Basics</h1>
            <p>Learn the fundamentals of machine learning through interactive video modules</p>
        </div>
    </header>

    <div class="container">
        <div class="search-container">
            <input type="text" id="search-input" placeholder="Search videos..." class="search-input">
            <button id="search-button" class="search-button">
                <i class="fas fa-search"></i> Search
            </button>
        </div>
        <div class="modules-container">
            {% for i in range(1, 8) %}
            <button class="module-button" data-module="{{ i }}">
                <i class="fas fa-book"></i>
                Module {{ i }}
            </button>
            {% endfor %}
        </div>

        <div class="videos-container" id="videos-container">
            <button class="btn back-button" id="back-button">
                <i class="fas fa-arrow-left"></i> Back to Modules
            </button>
            
            <div class="loading hidden" id="loading">
                <i class="fas fa-spinner fa-spin"></i> Loading videos...
            </div>
            
            <div class="error hidden" id="error"></div>
            
            <div class="videos-grid" id="videos-grid"></div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const moduleButtons = document.querySelectorAll('.module-button');
            const videosContainer = document.getElementById('videos-container');
            const videosGrid = document.getElementById('videos-grid');
            const loadingIndicator = document.getElementById('loading');
            const errorElement = document.getElementById('error');
            const backButton = document.getElementById('back-button');
            const baseUrl = `https://nlp-lr.notebook.us-east-1.sagemaker.aws/proxy/8080`;

            let currentModule = null;

            moduleButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const moduleNumber = this.dataset.module;
                    if (currentModule !== moduleNumber) {
                        currentModule = moduleNumber;
                        loadModuleVideos(moduleNumber);
                    }
                });
            });

            backButton.addEventListener('click', function() {
                videosContainer.classList.remove('active');
                moduleButtons.forEach(btn => btn.classList.remove('active'));
                currentModule = null;
            });

            function loadModuleVideos(moduleNumber) {
                loadingIndicator.classList.remove('hidden');
                errorElement.classList.add('hidden');
                videosGrid.innerHTML = '';
                videosContainer.classList.add('active');
                
                moduleButtons.forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.module === moduleNumber);
                });

                console.log(`Loading videos for module ${moduleNumber}`);
                fetch(`${baseUrl}/api/videos/${moduleNumber}`)
                    .then(response => {
                        if (!response.ok) {
                            return response.text().then(text => {
                                throw new Error(`Network response was not ok: ${response.status} ${text}`);
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        loadingIndicator.classList.add('hidden');
                        
                        if (data.error) {
                            errorElement.textContent = data.error;
                            errorElement.classList.remove('hidden');
                            return;
                        }

                        if (!data.videos || data.videos.length === 0) {
                            errorElement.textContent = 'No videos found in this module.';
                            errorElement.classList.remove('hidden');
                            return;
                        }

                        console.log(`Found ${data.videos.length} videos for module ${moduleNumber}`);
                        data.videos.forEach(video => {
                            const videoCard = document.createElement('div');
                            videoCard.className = 'video-card';
                            videoCard.innerHTML = `
                                <div class="video-player">
                                    <video controls>
                                        <source src="${video.url}" type="video/mp4">
                                        Your browser does not support the video element.
                                    </video>
                                </div>
                                <div class="video-info">
                                    <h3 class="video-title">${video.title}</h3>
                                    <div class="transcript">${video.transcript}</div>
                                    <a href="${baseUrl}/api/download/${video.id}" class="btn">
                                        <i class="fas fa-download"></i> Download Transcript
                                    </a>
                                </div>
                            `;
                            videosGrid.appendChild(videoCard);
                        });
                    })
                    .catch(error => {
                        console.error('Error loading videos:', error);
                        loadingIndicator.classList.add('hidden');
                        errorElement.textContent = `Error loading videos: ${error.message}`;
                        errorElement.classList.remove('hidden');
                    });
            }

            const searchInput = document.getElementById('search-input');
            const searchButton = document.getElementById('search-button');

            function searchVideos() {
                const query = searchInput.value.trim();
                if (!query) return;
                
                loadingIndicator.classList.remove('hidden');
                errorElement.classList.add('hidden');
                videosGrid.innerHTML = '';
                videosContainer.classList.add('active');
                
                // Remove active state from module buttons
                moduleButtons.forEach(btn => btn.classList.remove('active'));
                
                console.log(`Searching for: ${query}`);
                fetch(`${baseUrl}/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => {
                        if (!response.ok) {
                            return response.text().then(text => {
                                throw new Error(`Network response was not ok: ${response.status} ${text}`);
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        loadingIndicator.classList.add('hidden');
                        
                        if (data.error) {
                            errorElement.textContent = data.error;
                            errorElement.classList.remove('hidden');
                            return;
                        }

                        if (!data.videos || data.videos.length === 0) {
                            errorElement.textContent = 'No videos found matching your search.';
                            errorElement.classList.remove('hidden');
                            return;
                        }

                        console.log(`Found ${data.videos.length} videos matching search`);
                        data.videos.forEach(video => {
                            const videoCard = document.createElement('div');
                            videoCard.className = 'video-card';
                            videoCard.innerHTML = `
                                <div class="video-player">
                                    <video controls>
                                        <source src="${video.url}" type="video/mp4">
                                        Your browser does not support the video element.
                                    </video>
                                </div>
                                <div class="video-info">
                                    <h3 class="video-title">${video.title}</h3>
                                    <div class="module-tag">${video.module}</div>
                                    <div class="transcript">${video.transcript}</div>
                                    <a href="${baseUrl}/api/download/${video.id}" class="btn">
                                        <i class="fas fa-download"></i> Download Transcript
                                    </a>
                                </div>
                            `;
                            videosGrid.appendChild(videoCard);
                        });
                    })
                    .catch(error => {
                        console.error('Error searching videos:', error);
                        loadingIndicator.classList.add('hidden');
                        errorElement.textContent = `Error searching videos: ${error.message}`;
                        errorElement.classList.remove('hidden');
                    });
            }

            searchButton.addEventListener('click', searchVideos);
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchVideos();
                }
            });
        });
    </script>
</body>
</html>'''

    with open('templates/index.html', 'w') as f:
        f.write(html_content)
    
    print("Flask app is ready to run!")
    print(f"1. Make sure your CSV file is named 'transcriptions_with_key_phrases.csv' in the same directory")
    print(f"2. Run the app with: python appF.py")
    print(f"3. Access the dashboard at: http://127.0.0.1:{PORT}/")
    
    try:
        import flask_cors
    except ImportError:
        print("\nNOTE: You need to install flask-cors:")
        print("pip install flask-cors")
    
    app.run(debug=True, port=PORT)