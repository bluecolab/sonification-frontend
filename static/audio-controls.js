// Get a reference to the Plotly graph
var plotlyGraph = document.getElementById('graph-container'); // Updated to 'graph-container'

// Plotly restyle event listener
plotlyGraph.on('plotly_restyle', function(eventdata) {
  // Get all the audio elements
  var audioElements = document.getElementsByTagName('audio');

  // Get the updated visibility array
  var updatedVisibility = eventdata[0].visible;

  // Iterate through each trace
  for (var i = 0; i < updatedVisibility.length; i++) {
    if (updatedVisibility[i] === 'legendonly') {
      audioElements[i].muted = true; // Mute the audio if the trace is hidden
    } else {
      audioElements[i].muted = false; // Unmute the audio if the trace is visible
    }
  }
});

// Mute all function
function muteAll() {
  var audioElements = document.getElementsByTagName("audio");
  for (var i = 0; i < audioElements.length; i++) {
    audioElements[i].muted = true;
  }
}
