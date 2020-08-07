import React from 'react';
import CzmlMap from "./CzmlMap";
import GeoJsonMap from "./components/GeoJsonMap"
import './App.css';

function App() {

  return (
    <div className="App">
      <GeoJsonMap url="data/huc4.geojson"/>
      {/* <CzmlMap url="data/test.czml"/> */}
    </div>
  );
}

export default App;