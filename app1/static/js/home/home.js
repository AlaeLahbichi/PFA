let btn_filter = document.querySelector('.filtres')
let btn_close = document.querySelector('#close')
let box = document.querySelector('.box-filter')

btn_filter.addEventListener('click',(e)=>{
    e.preventDefault();
    box.style.display = "flex";
})

btn_close.addEventListener('click',(e)=>{
    e.preventDefault();
    box.style.display = "none";
})