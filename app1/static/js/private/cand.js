let input = document.querySelector('.adresse');
let boxes = document.querySelectorAll('.applications');

input.addEventListener('keyup', () => {
    let searchValue = input.value.toLowerCase().trim();
    console.log(searchValue)
    boxes.forEach(box => {
        let boxText = box.querySelector('.application-title').textContent.toLowerCase();
        if (boxText.includes(searchValue)) {
            box.style.display = "grid";
        } else {
            box.style.display = "none";
        }
    });
});
