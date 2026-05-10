# Sonification Frontend

Frontend for sonification

## Adding a new data set 

1. Create the audio files and .csv file. Make sure to follow names of existing files.
2. Create a new folder in `/static/data` for the new files. Make sure to follow the scheme `set_n`, n being next number.
3. Put .csv in the folder and audio files in `/audio`.
4. Create `metadata.json` in folder with name of label you want to see in front end. Add all the other required fields by following example of already existing files.
5. In the index.html, update the `dataset-controls` HTML element with new folder.
6. In `/static/js/plotly-graph.js` line 3 should have:
```js
  const defaultDataset = 'set_2';
```
Update it with new folder name.