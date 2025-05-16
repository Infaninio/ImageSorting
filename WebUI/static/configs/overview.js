// Function to send the viewport size to the server
function sendViewportSize() {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Send the viewport size via AJAX to the server
    fetch('/images/resize-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            width: viewportWidth,
            height: viewportHeight
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Viewport size sent successfully:', data);
        })
        .catch(error => {
            console.error('Error sending viewport size:', error);
        });
}

// Send the viewport size on page load
window.addEventListener('load', sendViewportSize);

// Send the viewport size on window resize
window.addEventListener('resize', sendViewportSize);

function openCollectionOverlay() {
    document.getElementById('overlay').style.display = 'flex';
}

function closeCollectionOverlay() {
    document.getElementById('overlay').style.display = 'none';
}

function getUsers(collectionId) {
    fetch('/configs/get_users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }, body: JSON.stringify({
            collectionId: collectionId
        })
    })

        .then(response => response.json())
        .then(data => {
            console.log('Users retrieved successfully:', data);
            // Handle the retrieved users data
            const formContainer = document.getElementById('userList');
            formContainer.innerHTML = ''; // Clear previous content

            data.forEach(user => {
                const checkboxLabel = document.createElement('label');

                const checkboxInput = document.createElement('input');
                checkboxInput.type = 'checkbox';
                checkboxInput.name = 'access[]';
                checkboxInput.userId = user.id;
                checkboxInput.checked = user.selected; // Set the checkbox checked state based on the data


                const labelText = document.createTextNode(user.name);

                checkboxLabel.appendChild(checkboxInput);
                checkboxLabel.appendChild(labelText);
                checkboxLabel.appendChild(document.createElement('br'));

                formContainer.appendChild(checkboxLabel);
            });
            const buttonContainer = document.getElementById('collectionForm');
            const buttons = Array.from(buttonContainer.getElementsByClassName('button'));
            buttons.forEach(button => {
                buttonContainer.appendChild(button);
            });
        });
}


var collectionId; // Declare a variable to store the selected collection ID

function openUserCollectionOverlay(collectionId, title) {
    getUsers(collectionId);
    document.getElementById('add_user_overlay').style.display = 'flex';
    document.getElementById('collectionTitle').innerText = title;

    this.collectionId = collectionId; // Store the selected collection ID
}

function addUserToCollection() {
    var selectedUsers = Array.from(document.querySelectorAll('input[name="access[]"]:checked')).map(input => input.userId);
    console.log(`Selected Users: ${selectedUsers}`);
    fetch(`/configs/add_user_to_collection`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }, body: JSON.stringify({
            collectionId: this.collectionId, // Use the stored collection ID
            users: selectedUsers
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            document.getElementById('overlay').style.display = 'none';
        })

    closeUserToCollectionOverlay();
}

function closeUserToCollectionOverlay() {
    document.getElementById('add_user_overlay').style.display = 'none';
}

function openNewUserOverlay() {
    document.getElementById('new_user_overlay').style.display = 'flex';
}

function closeNewUserOverlay() {
    document.getElementById('new_user_overlay').style.display = 'none';
}

function createNewUser() {
    const username = document.getElementById('new-username').value;
    const password = document.getElementById('new-password').value;
    console.log(username, password);

    fetch(`/auth/create_new_user`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }, body: JSON.stringify({
            username: username,
            password: password
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            closeNewUserOverlay();
        })
        .catch((error) => {
            console.error('Error:', error);
        })
};


document.getElementById('create-collection-btn').addEventListener('click', openCollectionOverlay);

document.getElementById('create-new-user-btn').addEventListener('click', openNewUserOverlay);

document.getElementById('collection-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const title = document.getElementById('title').value;
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    console.log(`Title: ${title}, Start Date: ${startDate}, End Date: ${endDate}`);

    // Here, you can add logic to handle the form submission,
    // such as sending data to a server or updating the UI.

    const newConfigData = {
        title: title,
        startDate: startDate,
        endDate: endDate,
    };

    fetch('/configs/new_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfigData) // Send viewport size as JSON
    })
        .then(response => response.json())
        .then(data => {
            // Handle the server response (optional, e.g., update UI or cache new image)
            if (data.success) {
                // Add new data to collection list
                console.log('New config added successfully!');
                const listItem = document.createElement('li');
                listItem.className = 'card';

                // Create the card image link and image
                const cardImageLink = document.createElement('a');
                cardImageLink.href = data.url;
                cardImageLink.className = 'card-image';

                const img = document.createElement('img');
                img.src = data.image_uri;
                img.alt = "A fox";

                cardImageLink.appendChild(img);

                // Create the card description
                const cardDescriptionLink = document.createElement('a');
                cardDescriptionLink.href = data.url;  // Assuming you want to keep this for consistency
                cardDescriptionLink.target = "_blank";
                cardDescriptionLink.className = 'card-description';

                const h2 = document.createElement('h2');
                h2.textContent = data.name;

                const p = document.createElement('p');
                p.textContent = `${data.start_date} - ${data.end_date}`;

                cardDescriptionLink.appendChild(h2);
                cardDescriptionLink.appendChild(p);

                // Create the card links
                const cardLinksDiv = document.createElement('div');
                cardLinksDiv.className = 'card-links';

                const galleryLink = document.createElement('a');
                galleryLink.href = data.view_uri;
                galleryLink.textContent = 'Gallerie';

                const reviewLink = document.createElement('a');
                reviewLink.href = data.url;
                reviewLink.textContent = 'Review';

                cardLinksDiv.appendChild(galleryLink);
                cardLinksDiv.appendChild(reviewLink);

                // Append all parts to the list item
                listItem.appendChild(cardImageLink);
                listItem.appendChild(cardDescriptionLink);
                listItem.appendChild(cardLinksDiv);
                var wholeList = document.getElementById('collection-list');
                wholeList.appendChild(listItem)



            } else {
                console.error('Error creating new collection');
                alert("You are not allowed to create a new collection. Please contact an administrator for assistance.")
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });


    closeCollectionOverlay();
});
