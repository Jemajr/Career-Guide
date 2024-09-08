# Career Guide

## Overview

**Career Guide** is a web application designed to enhance the operational efficiency of career centers at Historically Black Colleges and Universities (HBCUs). This platform aims to streamline the process of resume reviews and mentorship requests for students while allowing career centers to focus on other essential tasks.

![Demo 1](https://github.com/Jemajr/Career-Guide/blob/main/images/demo1.gif "Demo 1")

## Features

- **Student Login/Signup**: Students can create an account or log in to access personalized career services.
- **Resume Review**:
  - Upload and receive feedback on resumes through an AI-powered chatbot.
  - Ask specific questions related to resume improvements.
  - Save time by receiving initial feedback digitally and only seeking final reviews in-person.
- **Mentorship Requests**:
  - Submit detailed requests for mentorship based on their needs.
  - Track the status of their mentorship requests.
- **Career Center Admin Login**:
  - Review and manage mentorship requests from students.
  - Match students with appropriate alumni mentors from the school's network.
  - Track and update the status of mentorship requests.

## Technologies Used

- **Backend**:
  - **Python** with **Flask**: For handling server-side logic and routing.
  - **SQLAlchemy**: ORM for database interaction.
  - **PostgreSQL** on **Supabase**: For data storage and management.
  - **LangChain**: For building the AI-powered resume review chatbot.
  - **LangChain Community** and **LangChain OpenAI**: Integration with OpenAI’s API for natural language processing.
  - **PyMuPDF**: For handling PDF files, specifically resumes.
  - **Chroma**: For embedding and similarity search.

- **Frontend**:
  - **HTML**, **CSS**, **Bootstrap**: For designing and styling the web interface.

- **API**:
  - **OpenAI API**: For powering the AI chatbot used in resume reviews.


