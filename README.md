# Quick Alert - Disaster Alert System

A real-time disaster alert system that leverages social media data and machine learning to detect and notify users about potential disasters.

## Features

- Real-time disaster detection using social media data
- Machine learning-powered disaster classification
- Interactive map visualization with alert markers
- Real-time notifications via WebSocket
- Minimalist design with earth tone palette
- Responsive and mobile-friendly interface

## Tech Stack

### Backend
- Python 3.9+
- FastAPI
- TensorFlow/BERT for NLP
- WebSocket for real-time updates
- Social media APIs (Twitter, Facebook, Instagram)

### Frontend
- React.js
- Styled Components
- React Map GL
- Socket.io Client
- Axios

## Project Structure

```
quick-alert/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   └── services/
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── styles/
│       └── services/
└── docs/
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 14 or higher
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/quick-alert.git
cd quick-alert
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Create a .env file in the root directory with your API keys:
```
TWITTER_API_KEY=your_twitter_api_key
FACEBOOK_API_KEY=your_facebook_api_key
INSTAGRAM_API_KEY=your_instagram_api_key
```

### Running the Application

#### Without Docker

1. Start the backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend:
```bash
cd frontend
npm start
```

#### With Docker

```bash
docker-compose up
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Color Palette

- Primary: #8B7355 (Light brown)
- Secondary: #556B2F (Olive green)
- Tertiary: #CD853F (Peru/tan)
- Background: #F5F5DC (Beige)
- Text: #3E2723 (Dark brown)
- Alert: #B22222 (Fire brick red)
- Success: #2E8B57 (Sea green)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 