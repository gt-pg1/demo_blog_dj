document.querySelector("#load-more").addEventListener("click", function() {
    var button = this;
    var container = document.querySelector("#load-more-container");
    var page = this.dataset.page;

    fetch("?page=" + page, {
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
})
.then(response => response.json())
.then(data => {
    document.querySelector("#contents").insertAdjacentHTML('beforeend', data.html);
    if (data.has_next) {
        button.dataset.page = Number(page) + 1;
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
});
});
