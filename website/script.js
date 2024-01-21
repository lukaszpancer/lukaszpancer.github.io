
function setInnerHTML(elm, html) {
    elm.innerHTML = html;

    Array.from(elm.querySelectorAll("script"))
        .forEach(oldScriptEl => {
            const newScriptEl = document.createElement("script");

            Array.from(oldScriptEl.attributes).forEach(attr => {
                newScriptEl.setAttribute(attr.name, attr.value)
            });

            const scriptText = document.createTextNode(oldScriptEl.innerHTML);
            newScriptEl.appendChild(scriptText);

            oldScriptEl.parentNode.replaceChild(newScriptEl, oldScriptEl);
        });
}
const paths = {
    "#home": "website/home.html",
    "#snake": "website/snake.html",
    "#cannibals": "website/cannibals.html",
    "#chess": "website/chess.html",
    "#ai_chat": "website/ai_chat.html",
    "#ai_search": "website/ai_search.html",
    "#navbar": "website/navbar.html",
}
const render = (path, id) => {
    if (path in paths) {
        path = paths[path];
        fetch(path)
            .then(response => response.text())
            .then(text => {
                setInnerHTML(document.querySelector(id), text);
                // document.querySelector(id).innerHTML = text;
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