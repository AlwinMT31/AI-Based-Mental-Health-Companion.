function sendMessage() {
    let input = document.getElementById("user-input").value.trim();
    if (!input) return;

    let chatBox = document.getElementById("chat-box");
    
    // Display user message
    chatBox.innerHTML += `<p class="user">You: ${input}</p>`;
    
    // Send to backend
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
    })
    .then(response => response.json())
    .then(data => {
        // Add bot message container
        let botMessage = document.createElement('p');
        botMessage.className = 'bot';
        chatBox.appendChild(botMessage);
        
        // Type out bot response word-by-word
        let words = data.response.split(' ');
        let index = 0;
        
        function typeWord() {
            if (index < words.length) {
                botMessage.textContent += (index === 0 ? 'Bot: ' : ' ') + words[index];
                index++;
                setTimeout(typeWord, 100); // Adjust speed (100ms per word)
            }
        }
        
        typeWord();
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
    })
    .catch(error => {
        chatBox.innerHTML += `<p class="bot">Bot: Sorry, something went wrong.</p>`;
        console.error(error);
    });
    
    document.getElementById("user-input").value = ""; // Clear input
}

// Allow Enter key to send message
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});