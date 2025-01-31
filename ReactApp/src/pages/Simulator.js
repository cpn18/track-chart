// src/pages/Simulator.js
import React from 'react';
import './Simulator.css';

const Simulator = () => {
  return (
    <div className="simulator-container">
      <h1>Welcome to the PiRail Simulator!</h1>
      <p>
        If choosing to generate a JSON, a JSON file will be produced containing randomized information to be played through the PiRail UI.
      </p>
      <p>
        If choosing to input an existing JSON file, the app will ask the user to upload a JSON file. This will be loaded into the PiRail web app and displayed against the entirety of the UI.
      </p>
      <p>
        The START SIMULATOR button will now be transferred to END SIMULATOR.
      </p>
      <h2>To end the simulator:</h2>
      <p>
        When done simulating, click the END SIMULATOR button.
      </p>
      <p>
        If using an input JSON file, a pop-up will ask you confirming you would like to end the simulation. Click yes to end the simulation, or no if you wish to continue.
      </p>
      <p>
        If using a generated JSON file, a pop-up will ask you if you wish to download the generated JSON file. Click yes to choose the download destination for the file, or no if you wish to end the simulation without saving the JSON file.
      </p>

      {/* sec for "Choose a setting" */}
      <h2>Choose a Setting:</h2>
      <div className="button-group">
        <button className="setting-button">INPUT JSON</button>
        <button className="setting-button">GENERATE JSON</button>
      </div>
    </div>
  );
};

export default Simulator;
