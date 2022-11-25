document.addEventListener("DOMContentLoaded", function(event) {

  let Normal_btn = document.querySelectorAll('#Normal_btn');
  let initial_value = "";

  Normal_btn.forEach((Normal_btn, index)=>{
    Normal_btn.addEventListener('click', function(){
      let text = this.innerHTML;
      initial_value += text;
      console.log(initial_value);
      // result.innerHTML = initial_value;
      document.getElementById("result").value = initial_value;
    });
    });
  });
