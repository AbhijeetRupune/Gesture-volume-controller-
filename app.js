const video = document.getElementById('video');
const constraints = { video: true };

navigator.mediaDevices.getUserMedia(constraints)
 .then(function(stream) {
    video.srcObject = stream;
    video.play();
  })
 .catch(function(err) {
    console.log('Error: ' + err);
  });

const ws = new WebSocket('ws://' + window.location.host);

ws.onmessage = function(event) {
  const image = new Image();
  image.src = 'data:image/jpeg;base64,' + event.data;
  video.src = URL.createObjectURL(image);
};

