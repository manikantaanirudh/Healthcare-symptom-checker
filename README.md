# Healthcare Symptom Checker

> **⚠️ IMPORTANT DISCLAIMER**: This application is for **educational purposes only** and is **NOT a substitute for professional medical advice, diagnosis, or treatment**. Always consult with qualified healthcare professionals for proper medical care.

## Overview

The Healthcare Symptom Checker is a web application that accepts symptom descriptions as input and returns probable medical conditions with recommended next steps. It's designed purely for educational purposes to help users understand potential causes of their symptoms and learn about appropriate next steps.

## Features

- **Symptom Analysis**: Input free-text symptom descriptions with optional metadata (age, sex, duration, severity)
- **Probable Conditions**: Get up to 5 probable medical conditions with confidence scores and rationales
- **Next Steps**: Receive recommended actions categorized by urgency (self-care, see physician, urgent care)
- **Red Flag Detection**: Automatic detection of symptoms that require immediate medical attention
- **Query History**: Store and retrieve previous symptom analysis queries
- **Safety First**: Comprehensive disclaimers and safety measures throughout the application

## Architecture

### Backend (FastAPI)
- **REST API**: Clean, well-documented API endpoints
- **LLM Integration**: Google Gemini integration with structured prompts
- **Database**: SQLite database for storing query history
- **Safety Features**: Red flag detection, comprehensive disclaimers
- **Modular Design**: Clear separation of concerns (Controller → Service → LLM Client → Model)

### Frontend (React + TypeScript)
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **User Experience**: Intuitive symptom input form with clear result presentation
- **Safety Messaging**: Prominent educational disclaimers throughout the interface

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

4. **Run the backend**:
   ```bash
   python run.py
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install --legacy-peer-deps
   ```

3. **Set up environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if you need to change the API URL
   ```

4. **Run the frontend**:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## API Documentation

### Endpoints

#### `POST /api/v1/check`
Analyze symptoms and return probable conditions with recommendations.

**Request Body**:
```json
{
  "symptoms": "I have a headache and fever",
  "age": 30,
  "sex": "male",
  "duration_days": 2,
  "severity": "moderate",
  "context": "Started after a cold"
}
```

**Response**:
```json
{
  "probable_conditions": [
    {
      "condition": "Viral infection",
      "confidence": 0.7,
      "rationale": "Headache and fever are common symptoms of viral infections"
    }
  ],
  "recommended_next_steps": [
    {
      "type": "self_care",
      "text": "Rest, stay hydrated, and monitor symptoms"
    },
    {
      "type": "see_physician",
      "text": "See a doctor if symptoms worsen or persist"
    }
  ],
  "red_flags": [],
  "disclaimer": "This is educational information only and not a substitute for professional medical advice.",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### `GET /api/v1/history`
Retrieve query history with pagination.

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)

#### `GET /api/v1/history/{query_id}`
Retrieve a specific query by ID.

#### `DELETE /api/v1/history/{query_id}`
Delete a specific query from history.

### Health Check
- `GET /health`: Service health status

## Safety Features

### Red Flag Detection
The system automatically detects and flags symptoms that require urgent medical attention, including:
- Chest pain or pressure
- Severe difficulty breathing
- Signs of stroke
- Severe abdominal pain
- High fever with rash
- Signs of severe dehydration
- And more...

### Educational Disclaimers
Every response includes clear disclaimers that this tool is for educational purposes only and is not a substitute for professional medical advice.

### Conservative Recommendations
The system is designed to err on the side of caution, always recommending professional medical consultation for serious symptoms.

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Development

### Code Quality
- **Type Safety**: Full TypeScript implementation in frontend
- **Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Unit tests for critical functionality
- **Documentation**: Well-documented code with docstrings

### Project Structure
```
healthcare-symptom-checker/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # Business logic
│   │   ├── utils/         # Utilities
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Test files
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main app component
│   └── package.json       # Node dependencies
└── README.md
```

##Project Live link
https://healthcare-symptom-checker-frontend.onrender.com/

## Project Demo Video

Watch the demo: https://drive.google.com/file/d/13epNAiPS3F1xyWl8lLFTnc0thY5uFGO9/view?usp=sharing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is for educational purposes only. Please ensure you comply with all applicable laws and regulations when using this software.

## Support

For questions or issues, please create an issue in the repository.

---

**Remember**: This tool is for educational purposes only and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for proper medical care.
