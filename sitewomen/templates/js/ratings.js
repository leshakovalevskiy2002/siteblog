function attachRatingHandlers() {
    const ratingButtons = document.querySelectorAll('.rating-button');
    ratingButtons.forEach(button => {
        button.addEventListener('click', event => {
            const value = parseInt(event.target.dataset.value);
            const postId = parseInt(event.target.dataset.post);
            const container = button.closest('.rating-buttons');
            const ratingSum = container.querySelector('.rating-sum');

            const activePageElement = document.querySelector('.page-item.active span.page-link');
            const activePage = activePageElement ? activePageElement.textContent.trim() : null;

            const formData = new FormData();
            formData.append('post_id', postId);
            formData.append('value', value);

            const currentLang = "/" + container.getAttribute('data-lang');
            const url = `${currentLang}/rating/`;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                ratingSum.textContent = data.rating_sum;
                const image1 = container.querySelector('.btn-1');
                const image2 = container.querySelector('.btn-2');

                image1.src = data.value === 1
                    ? `/static/women/images/like_click.png`
                    : `/static/women/images/like.png`;

                image2.src = data.value === -1
                    ? `/static/women/images/dislike_click.png`
                    : `/static/women/images/dislike.png`;
            })
            .catch(error => console.error("Ошибка рейтинга:", error));
        });
    });
}

// Навешиваем обработчики при загрузке
document.addEventListener('DOMContentLoaded', attachRatingHandlers);

// Навешиваем обработчики после HTMX-перерисовки
document.body.addEventListener('htmx:afterSwap', attachRatingHandlers);