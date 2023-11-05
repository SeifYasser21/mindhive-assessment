// Get references to HTML elements
const searchForm = document.getElementById('search-form');
const userInput = document.getElementById('user-input');
const chatLog = document.getElementById('chat-log');

// Add an event listener to the search form
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent the default form submission behavior

    // Get the user's input from the input field
    const user_input = userInput.value;

    // Send a POST request to the server to get product recommendations
    const response = await fetch('/get_recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `user_input=${user_input}`,
    });

    // Parse the response data as JSON
    const data = await response.json();

    // Clear the chat log
    chatLog.innerHTML = '';

    // Add a chat message at the top of the chat log
    chatLog.innerHTML += `<p class="chat-log">Product Information: ${user_input}</p><p class="chat-log">Chatbot: According to the description provided, here are some products I recommend:</p>`;

    // Loop through the product recommendations and display them in the chat log
    data.forEach((product, index) => {
        chatLog.innerHTML += `
            <div class="product" style="background-color: #311b92;">
                <p class="product-header"><strong>${index + 1}</strong></p>
                <p class="product-detail"><u>Product Name:</u><br><em>${product['Product Name']}</em></p>
                <p class="product-detail"><u>Category:</u><br><em>${product['Category']}</em></p>
                <p class="product-detail"><u>Description:</u><br><em>${product['Description']}</em></p>
                <p class="product-detail"><u>Price:</u><br><em>${"$" + product['Price']}</em></p>
            </div>
        `;
    });

    // Clear the user input field
    userInput.value = '';
});
