let btn_list = document.querySelector('.guest')
let list = document.querySelector('.list')

btn_list.addEventListener('click',(e)=>{
    let currentStyle = window.getComputedStyle(list).display
    if(currentStyle == "none")
    {
        list.style.display = "flex"
    }
    else if(currentStyle == "flex"){
        list.style.display = "none"
    }
})

document.addEventListener('click',(e)=>{
    if(!btn_list.contains(e.target) && !list.contains(e.target))
    {
        list.style.display = "none"
    }
})
