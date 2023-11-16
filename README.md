# FRIDAY - AI ChatBot with Multilingual Voice Assistance

## Description

FRIDAY is an advanced AI chatbot designed to provide seamless multilingual voice assistance. It's equipped with cutting-edge technologies, including Generative AI and WhisperVoice™, enabling natural and contextually relevant conversations.

## Key Features

- Multilingual Voice Support: FRIDAY offers voice-based interactions in multiple languages, making it accessible to a global audience and promoting inclusivity.

- Generative AI-Powered Conversations: FRIDAY utilizes advanced Generative AI to generate human-like responses, ensuring natural and contextually relevant conversations across various domains.

- Context Comprehension: FRIDAY understands and maintains context during conversations, providing coherent and meaningful responses in any interaction.

- User Data Management: FRIDAY's user data management system personalizes responses based on individual preferences, previous interactions, and historical data, creating tailored experiences.

- Versatile Use Cases: FRIDAY's capabilities extend beyond specific sectors, offering versatile applications in various domains such as customer support, productivity enhancement, and more.

## Getting Started

Instructions to setup and run the project 

### Setup
1. Clone the repository:  
```git
git clone git@github.com:Meghna-bits/voice-chatbot.git
```
  
2. Setup Virtual Environment:  
```python
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:  
```python
pip install -r requirements.txt
```

4. Populate the environment variables
```
cp env.template .env
```
Copy the template and fill in all the required environment variables

5. Run migrations

&nbsp;&nbsp;&nbsp;&nbsp; Before running migration install postgres in your local and create Database using this command:
```
CREATE DATABASE chatbot;
```
```python
python manage.py makemigrations
python manage.py migrate
```

6. Other prerequisites

- To use ffmpeg in your application for audio processing tasks, you need to have the ffmpeg tool installed on the machine.
- Websocket functioning requires redis-server to be running

7. Run the development server:  
```python
python manage.py runserver
```

The server is accessible in this endpoint - http://localhost:8000 

### API Endpoints

The api endpoints are stored as a json collection in the root directory.

## Documentation

The api documentation is accessible through swagger and also in postman collection documentation.

## Maintainer:
- Meghna Iyer D L <2021mt93670@wilp.bits-pilani.ac.in>
