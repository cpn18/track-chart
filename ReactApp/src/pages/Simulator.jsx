import React, { useState } from 'react';
import './Simulator.css';
import Footer from '../components/Footer';

/**
 * Simulator page:
 * Generate a simulated dataset
 * Upload an existing dataset
 * Start and stop the sim (click one of options above)
 */

const Simulator = () => {
  const [showInfo, setShowInfo] = useState(false); // state - toggle text visibility
  const [showUpload, setShowUpload] = useState(false); // state - toggle upload pop - up
  const [showGenerate, setShowGenerate] = useState(false); // state - toggle generate data

  const [open, setOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    validateAndSetFile(uploadedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const uploadedFile = event.dataTransfer.files[0];
    validateAndSetFile(uploadedFile);
  };

  const validateAndSetFile = (uploadedFile) => {
    if (uploadedFile && uploadedFile.type === "application/json") {
      setFile(uploadedFile);
      setError("");
    } else {
      setFile(null);
      setError("Invalid file type. Please upload a JSON file.");
    }
  };

  const handleUpload = () => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target.result);
          console.log("Uploaded JSON Data:", jsonData);
  
          // DAVID - this is where you need to handle upload!

          setOpen(false); // close after upload
        } catch (error) {
          setError("Invalid JSON format. Please upload a valid JSON file.");
        }
      };
      reader.readAsText(file);
    }
  };
  
  const toggleInfo = () => {
    setShowInfo(!showInfo);
  };

  const toggleUpload = () => {
    setShowUpload(!showUpload);
  };

  const toggleGenerate = () => {
    setShowGenerate(!showGenerate);
  };

  return (
    <div className="simulator-container">
      <div className="nav-container"></div>
      {/* question mark - toggling text */}
      <div className="toggle-info-icon" onClick={toggleInfo} title="Toggle Info">
        ?
      </div>

      {/* render info text (based on ? status) */}
      {showInfo && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Welcome to the PiRail Simulator!</h1>
              <p>
                If choosing to generate a JSON, a JSON file will be produced containing randomized information to be played through the PiRail UI.
              </p>
              <p>
                If choosing to input an existing JSON file, the app will ask the user to upload a JSON file. This will be loaded into the PiRail web app and displayed against the entirety of the UI <br></br>.
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
                <br></br>If using a generated JSON file, a pop-up will ask you if you wish to download the generated JSON file. Click yes to choose the download destination for the file, or no if you wish to end the simulation without saving the JSON file.
              </p>
              <p>
              <br></br>
              </p>
              <button className="modal-button cancel" onClick={toggleInfo}>
                CANCEL
              </button>
          </div>
        </div>
      )}

      {/* take file data in (input JSON for simulator) */}
      {showUpload && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Upload Data:</h1>
              <div
                className={`upload-container ${file ? "dragging" : ""}`}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => document.getElementById("fileInput").click()} // Clicking opens file dialog
              >
                {file ? (
                  <p className="file-name">{file.name} selected</p>
                ) : (
                  <p><b>Choose a file</b> or drag it here.</p>
                )}
              </div>
              <input
                type="file"
                accept="application/json"
                onChange={handleFileUpload}
                id="fileInput"
                className="hidden"
              />
              {error && <p className="upload-error">{error}</p>}
              <div className="modal-buttons">
                <button className="modal-button">
                  UPLOAD
                </button>
                <button className="modal-button cancel" onClick={toggleUpload}>
                  CANCEL
                </button>
              </div>
          </div>
        </div>
      )}

      {/* generate file data in (generate JSON for simulator) */}
      {showGenerate && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h1>Generate Data:</h1>
              <p>
               Are you sure you'd like to generate randomized JSON data?
              </p>
              <div className="modal-buttons">
                <button className="modal-button">
                  GENERATE
                </button>
                <button className="modal-button cancel" onClick={toggleGenerate}>
                  CANCEL
                </button>
              </div>
          </div>
        </div>
      )}

      {/* input or generate data buttons */}
      <h2>Choose a Setting:</h2>
      <div className='image-group'>
        {/* Upload & Generate images for their respective buttons */}
        <img className="upload" src='upload.jpg'></img>
        <img className="generate" src='generate.gif'></img>
      </div>
      <div className="button-group">
        {/* INSERT INPUT OF DATA FUNCTIONALITY HERE */}
        <button className="setting-button" onClick={toggleUpload} >INPUT DATA</button>
        {/* INSERT GENERATION OF DATA FUNCTIONALITY HERE */}
        <button className="setting-button" onClick={toggleGenerate} >GENERATE DATA</button>
      </div>
      <p>If there are any questions on how to use the simulator, click the "?" icon above.</p>
      <Footer />
    </div>
  );
};

export default Simulator;
