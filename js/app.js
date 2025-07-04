// Initialize Speech Recognition
function startRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = function(event) {
        const userInput = event.results[0][0].transcript;
        document.getElementById('response').innerText = "You asked: " + userInput;

        // Send text input to the backend
        fetch('/api/voice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: userInput })
        })
        .then(response => response.json())
        .then(data => {
            const assistantResponse = data.response || data.error;
            document.getElementById('response').innerText = "Assistant says: " + assistantResponse;
            
            // Optional: Use Web Speech API to speak response on the frontend
            const speechSynthesis = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(assistantResponse);
            speechSynthesis.speak(utterance);
        })
        .catch(err => {
            console.error("Error:", err);
            document.getElementById('response').innerText = "Sorry, something went wrong.";
        });
    };

    recognition.onerror = function(event) {
        console.error('Speech Recognition Error:', event.error);
        document.getElementById('response').innerText = "There was an issue with voice recognition.";
    };
}
