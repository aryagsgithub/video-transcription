# Video Learning Platform

A Flask-based web application for video learning with transcription and key phrase extraction capabilities.

## Features

- Video playback with transcripts
- Key phrase extraction using RAKE algorithm
- Search functionality across video content
- Module-based organization
- AWS S3 integration for video storage
- Responsive web interface

## Prerequisites

- Python 3.8+
- AWS Account with S3 bucket
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aryagsgithub/video-transcription.git
cd video-transcription
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with:
S3_BASE_URL=your_s3_bucket_url
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
```

## Running the Application

```bash
python appF.py
```

The application will be available at `http://localhost:5000`

## AWS Deployment

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Configure AWS credentials:
```bash
aws configure
```

3. Deploy to Elastic Beanstalk:
```bash
eb init -p python-3.8 video-learning-platform --region us-east-1
eb create video-learning-env
eb deploy
```

## Project Structure

```
video-learning-platform/
├── application.py
├── appF.py
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
├── .ebextensions/
│   └── 01_flask.config
├── templates/
│   └── index.html
├── static/
│   └── css/
│       └── style.css
└── data/
    └── transcriptions_with_key_phrases.csv
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 