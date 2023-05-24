document.querySelector("#load-more").addEventListener("click", function() {
    var button = this;
    var container = document.querySelector("#load-more-container");
    var page = this.dataset.page;

    container.style.display = 'none';

    fetch("?page=" + page, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(data => {
        if (data.trim() !== '') {
            document.querySelector("#contents").insertAdjacentHTML('beforeend', data);
            button.dataset.page = Number(page) + 1;
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    });
});
