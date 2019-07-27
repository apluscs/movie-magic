console.log("hi");
let toWatchBtns=document.querySelectorAll(".toWatchBtn")
console.log(toWatchBtns)

const updateWatchLater = () => {
  var xhr = new XMLHttpRequest();
  let movieInfo=document.getElementById('movieInfo').value
  xhr.open("POST", "/updateMyAccount", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr_dict="movie_info="+movieInfo;
  xhr.send(xhr_dict)
  // console.log("updatingggggggggggg")
  // request.open('GET', 'https://ghibliapi.herokuapp.com/films', true)
}

toWatchBtns.forEach(toWatchBtn => {
  toWatchBtn.addEventListener("click",updateWatchLater)
});
