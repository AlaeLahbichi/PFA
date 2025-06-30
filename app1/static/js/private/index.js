let boxes = document.querySelectorAll('.location-box')
let input = document.querySelector('.search')

input.addEventListener('keyup', () => {
    boxes.forEach((e) => {
        let text = e.querySelector('.location-details .location-name').innerHTML
        console.log(input.value)
        if (text.toLowerCase().includes(input.value.toLowerCase())) {
            e.style.display = "grid"; 
        } else {
            e.style.display = "none";
        }
    })
})
