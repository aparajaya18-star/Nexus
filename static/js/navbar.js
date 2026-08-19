const button = document.querySelector(".navbar");
const menu = document.querySelector(".navbar-options");

button.addEventListener("click", () => {
    menu.classList.toggle("open");
});

document.addEventListener("click", (e) => {

    if (
        !menu.contains(e.target) &&
        !button.contains(e.target)
    ){
        menu.classList.remove("open");
    }

});