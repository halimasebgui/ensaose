/*fetch()
.then(Response=> Response.json())
.then(Response2=> console.log(Response2))*/


function displayimg(src) {
    content = document.querySelector('.content-data');
    content.innerHTML = `<img src="${src}" >`;
}


function def(){
    fetch("http://127.0.0.1:8000/test")
    .then(response=> response.json())
    .then(data=> {
        console.log(data)
        
        var div_data = document.querySelector('.sidebar-data');
        div_data.innerHTML = ""

        data.forEach(item => {
            div_data.innerHTML += `<div onclick="displayimg('page${item.page}.jpg')" class="${item.status}"> ${item.ov} <img width="150px" src="page${item.page}.jpg"> </div onclick="displayimg()">`
        });

    })
}