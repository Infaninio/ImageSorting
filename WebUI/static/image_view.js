let currentRating = 0; // Variable to store the current rating

// Function to update the star rating display
function updateRatingDisplay(rating) {
  const stars = document.querySelectorAll('.rate i');
  currentRating = rating; // Store the new rating

  stars.forEach((star, index) => {
    if (index < rating) {
      star.classList.add('selected'); // Highlight stars up to the rating
    } else {
      star.classList.remove('selected'); // Unhighlight remaining stars
    }
  });
}

// Function to set the rating state
function updateRating(selectedIndex) {
  const stars = document.querySelectorAll('.rate i');
  currentRating = selectedIndex + 1; // Store the selected rating (1-5)

  stars.forEach((star, index) => {
    if (index <= selectedIndex) {
      star.classList.add('selected');
    } else {
      star.classList.remove('selected');
    }
  });
}

// Add click event listeners to each star
document.querySelectorAll('.rate i').forEach((star, index) => {
  star.addEventListener('click', () => {
    updateRating(index);  // Update the rating state on click
  });
});

let preloadedImages = {}; // Cache for preloaded images and ratings
const MAX_PRELOADED_IMAGES = 10; // Max number of images to preload

function preloadAdjacentImages(currentImageId) {
  // Fetch adjacent image metadata (next and previous images)
  fetch(`/images/get_adjacent_images_extended/${currentImageId}`)
    .then(response => response.json())
    .then(data => {
      // Preload the next set of images
      data.next.forEach(imageData => {
        preloadImage(imageData.image_path, imageData.rating);
      });

      // Preload the previous set of images
      data.previous.forEach(imageData => {
        preloadImage(imageData.image_path, imageData.rating);
      });
    })
    .catch(error => console.error("Error preloading images:", error));
}

function preloadImage(imagePath, rating) {

  // Check if the image has already been preloaded
  if (preloadedImages[imagePath]) {
    console.log(`Image already preloaded: ${imagePath}`);
    return; // If the image is already preloaded, don't load it again
  }

  // Preload the image and store it in the preloadedImages object
  const img = new Image();
  img.src = imagePath;
  preloadedImages[imagePath] = { img, rating };

  console.log(`Preloading image: ${imagePath}`);

  // If the number of preloaded images exceeds the maximum limit, remove the oldest
  if (Object.keys(preloadedImages).length > MAX_PRELOADED_IMAGES) {
    // Remove the first inserted image (oldest)
    const oldestImageKey = Object.keys(preloadedImages)[0];
    delete preloadedImages[oldestImageKey];
  }
}



// Update the current image and preload the next set
function navigateImage(action) {
  const imageContainer = document.getElementById("image_container");
  const imageId = imageContainer.src.split("/").pop(); // Extract current image ID
  // Prepare form data
  const formData = new FormData();
  formData.append("page", action); // Action: 'next', 'previous', 'trash'
  formData.append("rating", currentRating);
  formData.append("image_id", imageId);

  // Send POST request to submit the review and get the next image
  fetch("/images/review", {
    method: "POST",
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const newImagePath = data.new_image_path;

        // Check if the image was preloaded
        if (preloadedImages[newImagePath]) {
          const { img, rating } = preloadedImages[newImagePath];
          imageContainer.src = img.src; // Use preloaded image
          updateRatingDisplay(data.rating); // Update rating
        } else {
          imageContainer.src = newImagePath; // Fallback to fetching new image
          updateRatingDisplay(data.rating);
        }

      } else if (data.redirect_url) {
        // Redirect if no more images are available
        window.location.href = data.redirect_url;
      } else {
        console.error("Failed to navigate to the next image.");
      }
    })
    .catch(error => console.error("Error:", error));
}

// Preload images when the current one loads
document.getElementById("image_container").addEventListener("load", () => {
  const currentImageId = document.getElementById("image_container").src.split("/").pop();
  preloadAdjacentImages(currentImageId);
});

// Attach navigation events
document.getElementById("left-arrow-box").addEventListener("click", () => navigateImage("previous"));
document.querySelector(".arrow:not(#left-arrow-box)").addEventListener("click", () => navigateImage("next"));
document.querySelector(".trash").addEventListener("click", () => navigateImage("trash"));


// Function to handle the window resize event
function handleResize() {
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;

  // Prepare the data to send to the server
  const resizeData = {
    width: viewportWidth,
    height: viewportHeight
  };

  // Send the resize data to the server via AJAX
  fetch('/images/resize-image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(resizeData) // Send viewport size as JSON
  })
    .then(response => response.json())
    .then(data => {
      // Handle the server response (optional, e.g., update UI or cache new image)
      if (data.success) {
        console.log('Image resized successfully');
        const currentImageId = document.getElementById("image_container").src.split("/").pop();
        preloadedImages = {}
        preloadAdjacentImages(currentImageId);
      } else {
        console.error('Error resizing image');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

// Add event listener for resize event
window.addEventListener('resize', handleResize);
