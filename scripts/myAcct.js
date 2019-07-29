let markSeenBtns=document.querySelectorAll(".markSeen");
console.log(markSeenBtns);

const updateWatchLater = (markSeenBtn) => {
  let ind=markSeenBtn.id;
  let seenMovie=document.getElementById("mov"+ind);
  let markSeenDiv=document.getElementById("markSeenDiv");
  markSeenDiv.appendChild(seenMovie);
  markSeenBtn.remove();


  var xhr = new XMLHttpRequest(); //python and datastore stuff

  console.log(ind);
  let movie_title=document.getElementById('movie_title'+ind).value;
  let movie_id=document.getElementById('id'+ind).value;
  let movie_poster=document.getElementById('movie_poster'+ind).src;
  xhr.open("POST", "/markSeenMovie", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr_dict="movie_title="+movie_title+"&movie_id="+movie_id+"&movie_poster="+movie_poster;
  xhr.send(xhr_dict);
}

markSeenBtns.forEach(markSeenBtn => {
  markSeenBtn.addEventListener("click",function(){
    updateWatchLater(markSeenBtn);
  })
});
