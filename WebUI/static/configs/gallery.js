// Function to handle the window resize event
const preloadImages = 25
var columnCnt = 0;
var images = [];
var lastImageId = NaN
var columns = [];
var all_images = false;
var busyLoading = 0;
async function fetchImageBatch() {
    if (!all_images && busyLoading <= 0) {
        busyLoading = busyLoading + preloadImages;
        for (let index = 0; index < preloadImages; index++) {
            await new Promise(r => setTimeout(r, 20));
            addNewImage();
        }
    }

}

function buildWebsite() {
    var gallery = document.getElementById("gallery");
    columns = []
    newChildren = []

    for (let index = 0; index < columnCnt; index++) {
        var column = document.createElement("div");
        column.className = "gallery-column";
        columns.push([column, 0]);
        newChildren.push(column)
        // gallery.appendChild(column);
    }
    gallery.replaceChildren(...newChildren)
}

function addNewImage() {
    fetch(`/images/get_next_gallery_image/${lastImageId}`)
        .then(response => response.json())
        .then(data => {
            // Preload the next set of images
            if (data.relativeHeight < 0) {
                all_images = true;
            } else {
                images.push([data.imagePath, data.relativeHeight, data.rating]);
                addImageToColumn(data.imagePath, data.relativeHeight, data.rating)
                lastImageId = data.id
            }

            busyLoading = busyLoading - 1;

        })
        .catch(error => console.error("Error preloading images:", error));

}

function getRatingOverlay(stars) {
    var overlay = document.createElement("div");
    overlay.className = "image-overlay";
    var rateSpan = document.createElement("span");
    rateSpan.className = "staticRate";
    for (let index = 0; index < 5; index++) {
        var star = document.createElement("i");
        if (index < stars) {
            star.className = "selected";
        }
        star.textContent = "★";
        rateSpan.appendChild(star)
    }
    overlay.appendChild(rateSpan);
    return overlay;
}

function addImageToColumn(imagePath, height, rating) {
    var imageDiv = document.createElement("div");
    imageDiv.className = "gallery-image";
    var image = document.createElement("img")

    image.src = imagePath;
    imageDiv.appendChild(image);

    image.onload = () => {
        // Optionally, handle actions after image loads (e.g., adding margin-bottom if needed)
        if (rating > 0) {
            var overlay = getRatingOverlay(rating);
            imageDiv.appendChild(overlay);
        }
    };

    // Choose smallest column
    col = 0
    smallest_val = columns[0][1]
    for (let index = 0; index < columns.length; index++) {
        const element = columns[index];
        if (element[1] < smallest_val) {
            col = index;
            smallest_val = element[1];
        }
    }
    columns[col][0].appendChild(imageDiv);
    columns[col][1] = columns[col][1] + height
}

function resortImages() {
    for (let index = 0; index < images.length; index++) {
        const element = images[index]
        addImageToColumn(element[0], element[1], element[2])
    }
}

function handleResize() {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const maxWidth = 400;
    columnCnt = Math.ceil(viewportWidth / maxWidth);
    var gallery = document.getElementById("gallery");
    gallery.style.gridTemplateColumns = "1fr ".repeat(columnCnt);
    buildWebsite();
    resortImages();
}

function getVerticalScrollPercentage(elm) {
    let p = elm.parentNode || document.body
    return (elm.scrollTop || p.scrollTop) / (p.scrollHeight - p.clientHeight) * 100
}

function onScrollLoad(ev) {
    const scrollPercent = getVerticalScrollPercentage(document.body);
    if (scrollPercent > 80) {
        console.log("Scrolled around edge of page, loading more")
        fetchImageBatch();
    }
}

currentRating = 0;
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


function download_files() {
    var ratingFilter = currentRating;
    var bestOfTheDayFilter = document.getElementById('best-of-the-day-filter').value;

    // Show the loading overlay
    var loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.style.display = 'flex';

    fetch('/configs/download_gallery', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "minRating": ratingFilter, "bestOfDay": bestOfTheDayFilter }) // Send viewport size as JSON
    })
        .then(response => response.blob())
        .then(blob => {
            // Hide the loading spinner
            loadingOverlay.style.display = 'none';
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = "YourImages.zip";
            document.body.appendChild(link); // Trigger the download
            link.click();
            document.body.removeChild(link);
        })
        .catch(error => {
            loadingOverlay.style.display = 'none';
            console.error('Error:', error);
        });
}

document.getElementById('apply-filters-btn').addEventListener('click', function () {
    var ratingFilter = currentRating;
    var bestOfTheDayFilter = document.getElementById('best-of-the-day-filter').value;
    console.log("ratingFilter", ratingFilter, "bestoftheday", bestOfTheDayFilter)
    // Send these values to your backend and update the gallery view with filtered images.

    fetch('/configs/filter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "minRating": ratingFilter, "bestOfDay": bestOfTheDayFilter }) // Send viewport size as JSON
    })
        .then(response => response.json())
        .then(data => {
            // Handle the server response (optional, e.g., update UI or cache new image)
            if (data.success) {
                console.log('Filter applied successfully!');
                images = [];
                all_images = false;
                busyLoading = 0;
                handleResize();
                fetchImageBatch();
            } else {
                console.error('Error resizing image');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
handleResize();
fetchImageBatch();
window.addEventListener('resize', handleResize);
window.addEventListener("scrollend", onScrollLoad);
