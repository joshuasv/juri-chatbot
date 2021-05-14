function loadCanvas (cont, inputCallbackFn, chatObject) {
  let canvas = document.getElementById('canvas'+cont);
  canvas.style.margin = '0px';
  canvas.width = 300;
  canvas.height = 100;
  let ctx = canvas.getContext('2d');

  let coords = [];
  let coordsTouches = [];

  let colorValue = 'black';
  let widthValue = '3';

  let clearButton = document.querySelector('#clear'+cont);
  let saveButton = document.querySelector('#save'+cont);

  canvas.ontouchstart = (e) => {
    //ONLY 1 TOUCH...
    if (e.touches.length > 1) {
      canvas.ontouchmove = null;
      return;
    }  else {
      ctx.beginPath();
      ctx.strokeStyle = colorValue;
      ctx.lineWidth = widthValue;
      ctx.linejoin = 'miter';
      ctx.miterLimit = 1;
      ctx.lineCap = 'round';
      
      coordsTouches.push('down','down');

      canvas.ontouchmove = (e) => {
        let x = e.changedTouches['0'].clientX;
        let y = e.changedTouches['0'].clientY;

        coordsTouches.push(x,y);

        ctx.lineTo(x,y);
        ctx.stroke();

        canvas.ontouchend = () => {
          canvas.ontouchmove = null;
          ctx.beginPath();
          coordsTouches.push('up','up');
        };
      };
    }
    return false;
  }; 
  canvas.onmousedown = () => {
    ctx.beginPath();
    ctx.strokeStyle = colorValue;
    ctx.lineWidth = widthValue;
    ctx.linejoin = 'miter';
    ctx.miterLimit = 1;
    ctx.lineCap = 'round';

    coords.push('down','down');

    canvas.onmousemove = (e) => {
      
      let x = e.clientX - canvas.getBoundingClientRect().x;
      let y = e.clientY - canvas.getBoundingClientRect().y;
      

      coords.push(x,y);

      ctx.lineTo(x,y);
      ctx.stroke();

      canvas.onmouseup = canvas.onmouseleave = () => {
        canvas.onmousemove = null;
        ctx.beginPath();
        coords.push('up','up');
      };
    };
    return false;
  };
  
  clearButton.onclick = () => {
    ctx.clearRect(0,0,canvas.width,canvas.height);
  };

  saveButton.onclick = () => {
    var base64 = canvas.toDataURL("image/png", 1).split("base64,")[1];
    chatObject['input'] = base64;
    inputCallbackFn(chatObject);
  }
};

//SAVE IMAGE JAVASCRIPT
/*
var link = document.createElement('a');
link.innerHTML = 'SAVE IMAGE';
link.addEventListener('click', function(ev) {
    link.href = canvas.toDataURL();
    link.download = "MYPAINTING.png";
    }, false);
document.body.appendChild(link);
*/
//loadCanvas();
