# LLM-based Language Exchange Chatbot

This project investigates how large language models (LLMs) can be designed as conversational partners for language learning. The system was developed using a Design Science Research (DSR) methodology (Peffers et al.) and evaluated through qualitative user studies.

Research findings were published at DESRIST 2025.  
DOI: [10.1007/978-3-031-93976-1_15](https://doi.org/10.1007/978-3-031-93976-1_15)

---

## Project Overview

The application is a Streamlit-based web application that enables users to practice English conversation with a large language model acting as a native-speaking chat partner.

Model used: `gpt-4o-2024-08-06`

The system combines:

- Role-based conversational prompting
- CEFR-based language level adaptation
- Structured output generation using Pydantic schemas
- Automatic detection and correction of linguistic errors
- Visual highlighting of corrections

The chatbot produces both:
1. A conversational reply
2. A corrected version of the user's input (if linguistic errors are detected)

---

## Installation

1. Clone the repository

2. Install Dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Insert your OpenAI API Key:

   ```bash
   client = OpenAI(api_key="<INSERT API KEY HERE>")
   ```
   Alternatively, you may configure it using environment variables.

3. Run the Streamlit application in your default web browser:

   ```bash
   streamlit run app.py
   ```
## License

   This repository is provided for academic and research purposes.



