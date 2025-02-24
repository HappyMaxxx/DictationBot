# DictationBot

DictationBot is a Telegram bot developed for the Faculty of Intelligent Information Technologies and Automation (FІITA) at Vinnytsia National Technical University (VNTU). This bot was created by a second-year student Max Patyk for the "Vechornytsi" event. It allows an administrator to conduct a poetry dictation, where participants submit their versions of a selected verse.

## Features
- **Room-based dictation**: The administrator creates a room and selects a poem.
- **Submission control**: Users submit poems, but their messages remain hidden.
- **Administrator actions**:
  - Close the room to prevent new participants from joining.
  - End the dictation to stop further submissions.

## Installation
### Prerequisites
- Python 3.x
- Virtual environment (recommended)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/HappyMaxxx/DictationBot.git
   cd DictationBot
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Configure the bot (set your bot token in an `.env` file or as an environment variable).
5. Run the bot:
   ```sh
   python bot.py
   ```

## Usage
1. The administrator starts the bot and creates a room.
2. Participants join and submit their versions of the poem.
3. The administrator can close the room to lock participation.
4. At the end of the dictation, submissions are stopped.

## License
This project is open-source. Feel free to contribute and improve it!

