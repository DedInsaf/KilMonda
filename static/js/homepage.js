const slider = document.querySelector('.slider');
    const slides = Array.from(slider.querySelectorAll('img'));
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');
    let currentIndex = 0;

    function updateSlider() {
      slides.forEach((slide, index) => {
        slide.classList.remove('active', 'left', 'right');
        if (index === currentIndex) {
          slide.classList.add('active');
        } else if (index === (currentIndex - 1 + slides.length) % slides.length) {
          slide.classList.add('left');
        } else if (index === (currentIndex + 1) % slides.length) {
          slide.classList.add('right');
        }
      });
    }

    function showPreviousSlide() {
      currentIndex = (currentIndex - 1 + slides.length) % slides.length;
      updateSlider();
    }

    function showNextSlide() {
      currentIndex = (currentIndex + 1) % slides.length;
      updateSlider();
    }

    prevButton.addEventListener('click', showPreviousSlide);
    nextButton.addEventListener('click', showNextSlide);

    slides.forEach(slide => {
        slide.addEventListener('click', () => {
            const url = slide.dataset.url;
            if (url) {
                window.location.href = url; // Открывает ссылку в новой вкладке
            }
        });
    });


    updateSlider();

	document.addEventListener('DOMContentLoaded', function() {
    var buttons = document.querySelectorAll('button');

    //Работа кнопок
    buttons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            var targetUrl = event.target.dataset.url;
            if (targetUrl) {
                window.location.href = targetUrl;
            }
        });
    });
  });