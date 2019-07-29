console.log("hi");
let toWatchBtns=document.querySelectorAll(".toWatchBtn")
console.log(toWatchBtns)

const updateWatchLater = (toWatchBtn) => {
  var xhr = new XMLHttpRequest();
  let ind=toWatchBtn.id;
  let movie_title=document.getElementById('movie_title'+ind).value;
  let movie_id=document.getElementById('id'+ind).value;
  let movie_poster=document.getElementById('movie_poster'+ind).src;
  let type=document.getElementById('type'+ind).value;
  xhr.open("POST", "/updateMyAccount", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr_dict="movie_title="+movie_title+"&movie_id="+movie_id+"&movie_poster="+movie_poster+"&type="+type;
  xhr.send(xhr_dict)
  // console.log("updatingggggggggggg")
}

toWatchBtns.forEach(toWatchBtn => {
  toWatchBtn.addEventListener("click",function(){
    updateWatchLater(toWatchBtn);
  })
});

function goBack() { //goes back without actually reloading the page :D
  window.history.go(-1);
}
