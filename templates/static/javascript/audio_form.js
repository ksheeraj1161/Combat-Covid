// let audioIN = {audio: true};
// // audio is true, for recording

// // Access the permission for use
// // the microphone
// navigator.mediaDevices
//   .getUserMedia(audioIN)

//   // 'then()' method returns a Promise
//   .then(function (mediaStreamObj) {
//     // Connect the media stream to the
//     // first audio element
//     let audio = document.querySelector("audio");
//     //returns the recorded audio via 'audio' tag

//     // 'srcObject' is a property which
//     // takes the media object
//     // This is supported in the newer browsers
//     // if ("srcObject" in audio) {
//     //   audio.srcObject = mediaStreamObj;
//     // } else {
//     //   // Old version
//     //   audio.src = window.URL.createObjectURL(mediaStreamObj);
//     // }

//     // // It will play the audio
//     // audio.onloadedmetadata = function (ev) {
//     //   // Play the audio in the 2nd audio
//     //   // element what is being recorded
//     //   audio.play();
//     // };

//     // Start record
//     let start = document.getElementById("btnStart");

//     // Stop record
//     let stop = document.getElementById("btnStop");

//     let recordingPrompt = document.getElementById("recordingPrompt");
//     let donePrompt = document.getElementById("donePrompt");

//   // if (x.style.display === "none") {
//   //   x.style.display = "block";
//   // } else {
//   //   x.style.display = "none";
//   // }

//     // 2nd audio tag for play the audio
//     // let playAudio = document.getElementById("adioPlay");

//     // This is the main thing to recorde
//     // the audio 'MediaRecorder' API
//     let mediaRecorder = new MediaRecorder(mediaStreamObj);
//     // Pass the audio stream

//     // Start event
//     start.addEventListener("click", function (ev) {
//       mediaRecorder.start();
//       // console.log(mediaRecorder.state);
//     });

//     // Stop event
//     stop.addEventListener("click", function (ev) {
//       mediaRecorder.stop();
//       // console.log(mediaRecorder.state);
//     });

//     // If audio data available then push
//     // it to the chunk array
//     mediaRecorder.ondataavailable = function (ev) {
//       dataArray.push(ev.data);
//     };

//     // Chunk array to store the audio data
//     let dataArray = [];

//     // Convert the audio data in to blob
//     // after stopping the recording
//     mediaRecorder.onstop = function (ev) {
//       // blob of type mp3
//       let audioData = new Blob(dataArray, {type: "audio/wav;"});

//       // After fill up the chunk
//       // array make it empty
//       dataArray = [];

//       // Creating audio url with reference
//       // of created blob named 'audioData'
//       let audioSrc = window.URL.createObjectURL(audioData);
//       const a = document.createElement("a");
//       a.style.display = "none";
//       a.href = audioSrc;
//       a.download = "audio.wav";
//       a.click();
//       // Pass the audio url to the 2nd video tag
//     //   playAudio.src = audioSrc;
//     };
//   })

//   // If any error occurs then handles the error
//   .catch(function (err) {
//     console.log(err.name, err.message);
//   });

//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; //stream from getUserMedia()
var rec; //Recorder.js object
var input; //MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

function startRecording() {
  console.log("recordButton clicked");

  /*
		Simple constraints object, for more advanced audio features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/

  var constraints = {audio: true, video: false};

  /*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

  recordButton.disabled = true;
  stopButton.disabled = false;
  pauseButton.disabled = false;

  /*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

  navigator.mediaDevices
    .getUserMedia(constraints)
    .then(function (stream) {
      console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

      /*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device
		*/
      audioContext = new AudioContext();

      //update the format
      // document.getElementById("formats").innerHTML = "Format: 1 channel pcm @ " + audioContext.sampleRate / 1000 + "kHz";

      /*  assign to gumStream for later use  */
      gumStream = stream;

      /* use the stream */
      input = audioContext.createMediaStreamSource(stream);

      /* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
      rec = new Recorder(input, {numChannels: 1});

      //start the recording process
      rec.record();

      console.log("Recording started");
    })
    .catch(function (err) {
      //enable the record button if getUserMedia() fails
      recordButton.disabled = false;
      stopButton.disabled = true;
      pauseButton.disabled = true;
    });
}

function pauseRecording() {
  console.log("pauseButton clicked rec.recording=", rec.recording);
  if (rec.recording) {
    //pause
    rec.stop();
  } else {
    //resume
    rec.record();
  }
}

function stopRecording() {
  console.log("stopButton clicked");

  //disable the stop button, enable the record too allow for new recordings
  stopButton.disabled = true;
  recordButton.disabled = false;
  pauseButton.disabled = true;

  //tell the recorder to stop the recording
  rec.stop();

  //stop microphone access
  gumStream.getAudioTracks()[0].stop();

  //create the wav blob and pass it on to createDownloadLink
  rec.exportWAV(createDownloadLink);
}

async function createDownloadLink(blob) {
  var url = URL.createObjectURL(blob);
  var link = document.createElement("a");

  //name of .wav file to use during upload and download (without extendion)
  var filename = "audio";

  //save to disk link
  link.href = url;
  link.download = filename + ".wav"; //download forces the browser to donwload the file using the  filename
  link.click();
  await sleep(10000);
  var iframe = document.getElementsByTagName("iframe")[0];
  iframe.src = "{{url_for('static', filename='document.pdf')}}#toolbar=0";
}
