// Get elements
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const resultSection = document.getElementById('result');

// Event listener for the upload button
uploadBtn.addEventListener('click', function() {
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select an image first!");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Send the image to the server for prediction
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultSection.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
        } else {
            const skinTone = data.skin_tone;
            const makeupRecommendation = data.makeup_recommendation;
            const imageUrl = data.image_url;

            console.log("Image URL: ", imageUrl);  // Debugging line

            let recommendationsHTML = '<h3>Makeup Recommendations:</h3><ul>';
            for (let category in makeupRecommendation) {
                recommendationsHTML += `<li><strong>${category}:</strong><ul>`;
                makeupRecommendation[category].forEach(product => {
                    recommendationsHTML += `<li>${product}</li>`;
                });
                recommendationsHTML += '</ul></li>';
            }
            recommendationsHTML += '</ul>';

            resultSection.innerHTML = `
                <h3>Predicted Skin Tone: ${skinTone}</h3>
                <img src="${imageUrl}" alt="Uploaded Image" style="max-width: 300px; margin-top: 20px;">
                ${recommendationsHTML}
            `;
        }
    })
    .catch(error => {
        resultSection.innerHTML = `<p style="color:red;">An error occurred: ${error.message}</p>`;
    });
});
