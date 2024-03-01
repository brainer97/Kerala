from flask import Flask, render_template, request, redirect, url_for, session
import openai
import elevenlabs
from gtts import gTTS
from googletrans import Translator

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user data for demonstration purposes (replace with a database in a real application)
users = {
    'demo_user': {
        'name': 'Demo User',
        'email': 'demo@example.com',
        'password': 'password123'
    }
}
# Set up OpenAI API credentials
openai.api_key = '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'

# Set your API key securely
ELEVENLABS_API_KEY = "33b05fc0cf62eb2d5f0783bf50a12add"
elevenlabs.set_api_key(ELEVENLABS_API_KEY)

# Define a list of voice IDs and their corresponding names
voice_ids = [
    {"id": "oWAxZDx7w5VEj9dCyTzz", "name": "Grace"},
    {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam"},
    # Add more voice IDs as needed
]

# Define the /ttsindex route for the TTS index page
@app.route('/ttsindex', methods=['GET', 'POST'])
def tts_index():
    if request.method == 'POST':
        # Get the text input and selected voice ID from the form
        user_text = request.form['user_text']
        selected_voice_id = request.form['voice_id']

        # Find the selected voice settings based on the voice ID
        selected_voice_settings = next((v for v in voice_ids if v['id'] == selected_voice_id), None)

        if selected_voice_settings:
            try:
                # Create a Voice object with the selected settings
                voice = elevenlabs.Voice(
                    voice_id=selected_voice_settings['id'],
                    settings=elevenlabs.VoiceSettings(
                        stability=selected_voice_settings.get('stability', 0),
                        similarity_boost=selected_voice_settings.get('similarity_boost', 0.75)
                    )
                )

                # Generate audio from user input text using the selected voice
                audio = elevenlabs.generate(
                    text=user_text,
                    voice=selected_voice_settings['name']
                )

                # Save the audio to a file in the 'static' folder
                elevenlabs.save(audio, "static/audio.mp3")

                # Render a template or return a response
                return render_template('ttsindex.html', user_text=user_text, voice_ids=voice_ids, selected_voice_id=selected_voice_id)

            except Exception as e:
                # Handle API request errors
                return render_template('error.html', error_message=str(e))

    # Render the initial form on GET request
    return render_template('ttsindex.html', user_text=None, voice_ids=voice_ids, selected_voice_id=voice_ids[0]['id'])

# Define the / route to return the index.html file
@app.route('/')
def index():
    return render_template('index.html')

# Define the /app1index route for the app1 index page
@app.route("/app1index")
def app1index():
    return render_template("app1index.html")

# Define the /api route to handle POST requests
@app.route("/api", methods=["POST"])
def api():
    if request.method == "POST":
        # Get the message from the POST request
        message = request.json.get("message")
        # Send the message to OpenAI's API and receive the response

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        if completion.choices[0].message is not None:
            return completion.choices[0].message
        else:
            return 'Failed to Generate response!'

    # Handle cases where the method is not allowed
    return "Method Not Allowed", 405

# Other routes from app.py
@app.route('/signin')
def sign():
    return render_template('signin.html')

@app.route('/home')
def home():
    try:
        if 'username' in session:
            user = users.get(session['username'])
            if user:
                return render_template('pricingtable.html', user_name=user['name'])
        return redirect(url_for('login'))
    except Exception as e:
        # Log or print the exception details for debugging
        print(f"An error occurred: {str(e)}")
        return 'Internal Server Error'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email]['password'] == password:
            session['username'] = email
            return redirect(url_for('home'))

        return 'Invalid email or password'

    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if email not in users:
        users[email] = {'name': name, 'email': email, 'password': password}
        session['username'] = email
        return redirect(url_for('home'))

    return 'Email already registered'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/Main')
def Main():
    return render_template('Main.html')

@app.route('/img')
def img():
    return render_template('img.html')

@app.route('/Chatboat')
def Chatboat():
    return render_template('chatboat.html')


@app.route('/transalator')
def transalator():
    return render_template('transalator.html')

@app.route('/', methods=['POST'])
def convert():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']

        translator = Translator()
        translated_text = translator.translate(text, dest=language).text

        tts = gTTS(translated_text, lang=language)
        tts.save('static/output.mp3')  # Save the generated audio file

        return render_template('transalator.html', text=translated_text, audio_file='static/output.mp3')


if __name__ == '__main__':
    app.run()
