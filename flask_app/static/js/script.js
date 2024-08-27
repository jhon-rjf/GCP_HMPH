function sendMessage() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();

    if (userMessage === "") return;

    // Create User Message Element
    const userMessageElement = document.createElement('div');
    userMessageElement.classList.add('message', 'user-message');
    userMessageElement.innerHTML = `<div class="message-content">${userMessage}</div><div class="timestamp">${new Date().toLocaleTimeString()}</div>`;
    chatBox.appendChild(userMessageElement);

    // Clear the input
    userInput.value = "";

    // Create thinking... bot message element
    const thinkingMessageElement = document.createElement('div');
    thinkingMessageElement.classList.add('message', 'bot-message');
    thinkingMessageElement.innerHTML = `<div class="message-content">thinking...</div><div class="timestamp">${new Date().toLocaleTimeString()}</div>`;
    chatBox.appendChild(thinkingMessageElement);

    // Scroll to the bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send request to Flask server
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userMessage })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Update the thinking message with actual response
        if (data.error) {
            thinkingMessageElement.innerHTML = `<div class="message-content">An error occurred: ${data.error}</div><div class="timestamp">${new Date().toLocaleTimeString()}</div>`;
        } else {
            thinkingMessageElement.innerHTML = `<div class="message-content">${data.response}</div><div class="timestamp">${new Date().toLocaleTimeString()}</div>`;
        }

        // Scroll to the bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        thinkingMessageElement.innerHTML = `<div class="message-content">An error occurred while processing your request.</div><div class="timestamp">${new Date().toLocaleTimeString()}</div>`;
        
        // Scroll to the bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // Scroll to the bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Enter 키로 메시지 전송을 처리하고 기본 동작을 막는 함수
document.getElementById('user-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // 기본 동작(폼 제출)을 방지
        sendMessage(); // sendMessage 함수 호출
    }
});
