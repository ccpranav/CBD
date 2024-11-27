import os
from flask import Flask, render_template, request
import re
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from tensorflow.keras import backend as K  # Import Keras backend for session clearing

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize Flask app
app = Flask(__name__)

# Global variables to store the model and tokenizer
model = None
tokenizer = None

# Load model and tokenizer only when needed
def load_model_and_tokenizer():
    global model, tokenizer
    if model is None or tokenizer is None:
        try:
            model = tf.keras.models.load_model('lstm_model.h5')
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            print("Model loaded successfully.")
        except Exception as e:
            model = None
            print(f"Error loading model: {e}")
        
        try:
            with open('tokenizer.pkl', 'rb') as f:
                tokenizer = pickle.load(f)
            print("Tokenizer loaded successfully.")
        except Exception as e:
            tokenizer = None
            print(f"Error loading tokenizer: {e}")

# Preprocessing function
def preprocess_comment(comment):
    comment = comment.lower()
    comment = re.sub(r'[^\w\s]', '', comment)
    return comment.strip()

@app.route('/', methods=['GET', 'POST'])
def detect_comment():
    prediction = None
    user_input = ""

    if request.method == 'POST':
        if 'detect' in request.form:
            user_input = request.form['comment']
            
            # Load model and tokenizer only when a prediction is requested
            load_model_and_tokenizer()
            
            if model and tokenizer:
                processed_comment = preprocess_comment(user_input)
                sequences = tokenizer.texts_to_sequences([processed_comment])
                max_len = model.input_shape[1] if model.input_shape else 100  # Default length if input_shape is not available
                padded_sequences = pad_sequences(sequences, maxlen=max_len)
                
                # Prediction (using a binary classification model)
                prediction_label = model.predict(padded_sequences)[0][0]
                prediction = "Cyberbullying" if prediction_label > 0.5 else "Non-Cyberbullying"

                # Clear Keras session after prediction to release memory
                K.clear_session()
            else:
                prediction = "Error: Model or tokenizer not loaded."
        elif 'delete' in request.form:
            user_input = ""
            prediction = None

    return render_template('index.html', user_input=user_input, prediction=prediction)

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
