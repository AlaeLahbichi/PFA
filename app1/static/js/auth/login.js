let btn = document.querySelector('#close')
let box = document.querySelector('.mdp_content')
let mdp = document.querySelector('#forgotPasswordLink')

btn.addEventListener('click',(e)=>{
    box.style.display = "none";
})

mdp.addEventListener('click',(e)=>{
    e.preventDefault();
    box.style.display = "flex";
})