// Basic JavaScript for Preloader
document.addEventListener('DOMContentLoaded', () => {
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        // Simulating load time or waiting for assets
        window.addEventListener('load', () => {
            preloader.classList.add('hidden');
        });
        // Fallback for very fast loads or if 'load' event doesn't fire as expected
        setTimeout(() => {
            preloader.classList.add('hidden');
        }, 1500); // Hide after 1.5 seconds
    }

    // Basic JavaScript for Video Modal (mimicking ambiq.ai)
    const videoPopUp = document.querySelector('.video-pop-up');
    const closeVideoBtn = videoPopUp ? videoPopUp.querySelector('.close') : null;
    const videoEmbedContainer = videoPopUp ? videoPopUp.querySelector('.video') : null;

    document.querySelectorAll('.play-button').forEach(button => {
        button.addEventListener('click', () => {
            const videoId = button.dataset.videoId;
            if (videoId && videoPopUp && videoEmbedContainer) {
                // Using YouTube embed structure
                videoEmbedContainer.innerHTML = `
                    <iframe width="100%" height="100%" src="https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&showinfo=0&iv_load_policy=3" 
                            frameborder="0" allow="autoplay; encrypted-media; fullscreen" allowfullscreen>
                    </iframe>
                `;
                videoPopUp.classList.add('active');
            }
        });
    });

    if (closeVideoBtn) {
        closeVideoBtn.addEventListener('click', () => {
            if (videoEmbedContainer) {
                videoEmbedContainer.innerHTML = ''; // Stop video playback
            }
            videoPopUp.classList.remove('active');
        });
    }

    if (videoPopUp) {
        videoPopUp.addEventListener('click', (e) => {
            // Close if clicked on the background of the modal, not the video content
            if (e.target === videoPopUp || e.target.classList.contains('bg')) {
                if (videoEmbedContainer) {
                    videoEmbedContainer.innerHTML = '';
                }
                videoPopUp.classList.remove('active');
            }
        });
    }
});
