
const paths = {
    "#home": "website/home.html",
    "#snake": "website/snake.html",
    "#navbar": "website/navbar.html",
}
const render = (path, id) => {
    if (path in paths) {
        path = paths[path];
        fetch(path)
            .then(response => response.text())
            .then(text => {
                document.querySelector(id).innerHTML = text;
            }).then(() => {
                var tiltElements = document.querySelectorAll('[data-tilt]');
                console.log(tiltElements);
                tiltElements.forEach((element) => {
                    VanillaTilt.init(element);
                });
            });

    }
};
render('#navbar', '#navbar');
window.onhashchange = evt => render(window.location.hash, '#app');
window.location.hash = window.location.hash || "#home";
render(window.location.hash, '#app');
const tiltElements = document.querySelectorAll('.jumbo-container');
console.log(tiltElements);
tiltElements.forEach((element) => {
    VanillaTilt.init(element);
});