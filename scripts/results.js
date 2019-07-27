console.log("hi");
let toWatchBtns=document.querySelectorAll(".toWatchBtn")
console.log(toWatchBtns)

const updateWatchLater = (toWatchBtn) => {
  var xhr = new XMLHttpRequest();
  let ind=toWatchBtn.id;
  let movieInfo=document.getElementById('movieInfo'+ind).value
  xhr.open("POST", "/updateMyAccount", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr_dict="movie_info="+movieInfo;
  xhr.send(xhr_dict)
  // console.log("updatingggggggggggg")
}

toWatchBtns.forEach(toWatchBtn => {
  toWatchBtn.addEventListener("click",function(){
    updateWatchLater(toWatchBtn);
  })
});
