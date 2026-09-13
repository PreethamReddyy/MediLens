import { useRef, useState } from "react";
import {
  Camera,
  Upload,
  Sparkles,
  ShieldCheck,
  Volume2,
  Clock3,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Pill,
  X,
  RotateCcw,
  ShoppingCart,
  ExternalLink,
} from "lucide-react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [language, setLanguage] = useState("en");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const [reminders, setReminders] = useState([]);
  const [showReminder, setShowReminder] = useState(false);
  const [reminderTime, setReminderTime] = useState("09:00");
  const [reminderFrequency, setReminderFrequency] =
    useState("Once daily");

  const handleFile = (file) => {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please select an image file.");
      return;
    }

    setError("");
    setResult(null);
    setSelectedFile(file);

    const imageUrl = URL.createObjectURL(file);
    setPreview(imageUrl);
  };

  const handleFileInput = (event) => {
    const file = event.target.files?.[0];
    handleFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files?.[0];
    handleFile(file);
  };

  const clearImage = () => {
    setSelectedFile(null);
    setPreview("");
    setResult(null);
    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    if (cameraInputRef.current) {
      cameraInputRef.current.value = "";
    }
  };

  const scanMedicine = async () => {
    if (!selectedFile) {
      setError("Please upload or capture a medicine image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);
      formData.append("language", language);

      const response = await fetch(`${API_URL}/api/scan`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let message = "Something went wrong while scanning.";

        try {
          const data = await response.json();

          if (data?.detail) {
            message = data.detail;
          }
        } catch {
          // Keep default error message.
        }

        throw new Error(message);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.error ||
            "The medicine could not be identified clearly."
        );
      }

      setResult(data);

      setTimeout(() => {
        document
          .getElementById("results")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 100);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to MediLens.AI. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const addReminder = () => {
    if (!result?.medicines?.length) return;

    const medicine = result.medicines[0];

    const newReminder = {
      id: Date.now(),
      medicine: medicine.name,
      time: reminderTime,
      frequency: reminderFrequency,
    };

    setReminders((previous) => [
      ...previous,
      newReminder,
    ]);

    setShowReminder(false);
  };

  const removeReminder = (id) => {
    setReminders((previous) =>
      previous.filter((reminder) => reminder.id !== id)
    );
  };

  const getAudioUrl = (medicine) => {
    if (!medicine?.audio_url) return null;

    if (medicine.audio_url.startsWith("http")) {
      return medicine.audio_url;
    }

    return `${API_URL}${medicine.audio_url}`;
  };

  return (
    <div className="app">
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">
            <Pill size={19} strokeWidth={2.4} />
          </div>

          <span className="brand-name">MediLens</span>

          <span className="ai-badge">AI</span>
        </div>

        <div className="nav-right">
          <div className="status-pill">
            <span className="status-dot"></span>
            AI MEDICINE ASSISTANT
          </div>
        </div>
      </header>

      <main>
        {!result && (
          <section className="hero-section">
            <div className="hero-copy">
              <div className="eyebrow">
                <Sparkles size={15} />
                SMART MEDICINE RECOGNITION
              </div>

              <h1>
                Your medicine,
                <br />
                <span>understood.</span>
              </h1>

              <p className="hero-description">
                Turn a medicine strip or prescription into clear,
                understandable information — powered by OCR, medicine
                matching, and multilingual voice assistance.
              </p>

              <div className="hero-actions">
                <button
                  className="primary-button"
                  onClick={() =>
                    document
                      .getElementById("scanner")
                      ?.scrollIntoView({
                        behavior: "smooth",
                      })
                  }
                >
                  Scan a medicine
                  <ArrowRight size={18} />
                </button>

                <button
                  className="secondary-button"
                  onClick={() =>
                    document
                      .getElementById("how-it-works")
                      ?.scrollIntoView({
                        behavior: "smooth",
                      })
                  }
                >
                  How it works
                </button>
              </div>

              <div className="trust-row">
                <div>
                  <ShieldCheck size={16} />
                  <span>Safety-first matching</span>
                </div>

                <div>
                  <Volume2 size={16} />
                  <span>Voice assistance</span>
                </div>

                <div>
                  <Clock3 size={16} />
                  <span>Medication reminders</span>
                </div>
              </div>
            </div>

            <div
              className="scanner-wrapper"
              id="scanner"
            >
              <div className="scanner-card">
                <div className="scanner-header">
                  <div>
                    <p className="scanner-label">
                      MEDICINE SCANNER
                    </p>

                    <h2>
                      What would you like to understand?
                    </h2>
                  </div>

                  <div className="scanner-status">
                    <span></span>
                    READY
                  </div>
                </div>

                {!preview ? (
                  <>
                    <div
                      className="drop-zone"
                      onDragOver={(event) =>
                        event.preventDefault()
                      }
                      onDrop={handleDrop}
                      onClick={() =>
                        fileInputRef.current?.click()
                      }
                    >
                      <div className="upload-icon">
                        <Upload size={24} />
                      </div>

                      <h3>
                        Drop your medicine image here
                      </h3>

                      <p>
                        Upload a clear photo of the medicine
                        strip, packaging, or prescription.
                      </p>

                      <span className="browse-text">
                        Browse from your device
                      </span>
                    </div>

                    <div className="scanner-divider">
                      <span>OR</span>
                    </div>

                    <button
                      className="camera-button"
                      onClick={() =>
                        cameraInputRef.current?.click()
                      }
                    >
                      <Camera size={19} />
                      Capture with camera
                    </button>
                  </>
                ) : (
                  <div className="preview-container">
                    <div className="preview-image-wrapper">
                      <img
                        src={preview}
                        alt="Selected medicine"
                        className="preview-image"
                      />

                      <button
                        className="remove-image"
                        onClick={clearImage}
                        aria-label="Remove image"
                      >
                        <X size={17} />
                      </button>
                    </div>

                    <div className="selected-file">
                      <div className="file-check">
                        <CheckCircle2 size={18} />
                      </div>

                      <div>
                        <strong>
                          Image ready for scanning
                        </strong>

                        <span>
                          {selectedFile?.name}
                        </span>
                      </div>
                    </div>

                    <div className="language-section">
                      <span className="language-label">
                        VOICE LANGUAGE
                      </span>

                      <div className="language-selector">
                        <button
                          className={
                            language === "en"
                              ? "active"
                              : ""
                          }
                          onClick={() =>
                            setLanguage("en")
                          }
                        >
                          English
                        </button>

                        <button
                          className={
                            language === "te"
                              ? "active"
                              : ""
                          }
                          onClick={() =>
                            setLanguage("te")
                          }
                        >
                          తెలుగు
                        </button>

                        <button
                          className={
                            language === "hi"
                              ? "active"
                              : ""
                          }
                          onClick={() =>
                            setLanguage("hi")
                          }
                        >
                          हिन्दी
                        </button>
                      </div>
                    </div>

                    <button
                      className="scan-button"
                      onClick={scanMedicine}
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner"></span>
                          Analyzing medicine...
                        </>
                      ) : (
                        <>
                          <Sparkles size={18} />
                          Analyze medicine
                        </>
                      )}
                    </button>

                    <button
                      className="change-image"
                      onClick={clearImage}
                    >
                      <RotateCcw size={15} />
                      Choose another image
                    </button>
                  </div>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileInput}
                  hidden
                />

                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleFileInput}
                  hidden
                />
              </div>

              <div className="scanner-note">
                <ShieldCheck size={15} />
                MediLens provides informational assistance
                and does not replace professional medical
                advice.
              </div>
            </div>
          </section>
        )}

        {error && (
          <section className="error-section">
            <div className="error-card">
              <AlertTriangle size={21} />

              <div>
                <strong>Something went wrong</strong>
                <p>{error}</p>
              </div>

              <button onClick={() => setError("")}>
                <X size={17} />
              </button>
            </div>
          </section>
        )}

        {result && (
          <section
            className="results-section"
            id="results"
          >
            <div className="results-topbar">
              <div>
                <div className="eyebrow">
                  <Sparkles size={15} />
                  ANALYSIS COMPLETE
                </div>

                <h2>Medicine information</h2>

                <p>
                  MediLens identified the following medicine
                  from your image.
                </p>
              </div>

              <button
                className="new-scan-button"
                onClick={clearImage}
              >
                <RotateCcw size={16} />
                New scan
              </button>
            </div>

            <div className="result-layout">
              <div className="result-image-card">
                <div className="result-card-label">
                  SCANNED IMAGE
                </div>

                <img
                  src={preview}
                  alt="Scanned medicine"
                  className="result-image"
                />

                <div className="scan-complete">
                  <CheckCircle2 size={17} />
                  Analysis complete
                </div>
              </div>

              <div className="medicine-results">
                {result.medicines?.length > 0 ? (
                  result.medicines.map(
                    (medicine, index) => (
                      <MedicineCard
                        key={`${medicine.name}-${index}`}
                        medicine={medicine}
                        getAudioUrl={getAudioUrl}
                        onReminder={() =>
                          setShowReminder(true)
                        }
                      />
                    )
                  )
                ) : (
                  <div className="no-result-card">
                    <AlertTriangle size={28} />

                    <h3>
                      Medicine not identified
                    </h3>

                    <p>
                      MediLens could not identify a medicine
                      confidently from this image. Try a
                      clearer, closer photograph.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {reminders.length > 0 && (
              <section className="reminders-section">
                <div className="section-heading">
                  <div>
                    <span className="mini-label">
                      YOUR PLAN
                    </span>

                    <h3>Medication reminders</h3>
                  </div>
                </div>

                <div className="reminder-grid">
                  {reminders.map((reminder) => (
                    <div
                      className="reminder-card"
                      key={reminder.id}
                    >
                      <div className="reminder-icon">
                        <Clock3 size={18} />
                      </div>

                      <div className="reminder-content">
                        <strong>
                          {reminder.medicine}
                        </strong>

                        <span>
                          {reminder.time} ·{" "}
                          {reminder.frequency}
                        </span>
                      </div>

                      <button
                        onClick={() =>
                          removeReminder(reminder.id)
                        }
                        aria-label="Remove reminder"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </section>
        )}

        <section
          className="how-section"
          id="how-it-works"
        >
          <div className="section-intro">
            <div className="eyebrow">
              <Sparkles size={15} />
              HOW MEDILENS WORKS
            </div>

            <h2>
              From image to
              <br />
              <span>understanding.</span>
            </h2>

            <p>
              A simple experience on the outside, backed by
              multiple AI and software layers underneath.
            </p>
          </div>

          <div className="steps-grid">
            <Step
              number="01"
              title="Capture"
              text="Upload a medicine strip or capture a clear image using your camera."
              icon={<Camera size={22} />}
            />

            <Step
              number="02"
              title="Read"
              text="Image preprocessing and OCR extract readable medicine text from the image."
              icon={<Sparkles size={22} />}
            />

            <Step
              number="03"
              title="Match"
              text="The extracted text is compared against the medicine database using conservative matching."
              icon={<Pill size={22} />}
            />

            <Step
              number="04"
              title="Understand"
              text="MediLens presents medicine information and can explain it through multilingual voice."
              icon={<Volume2 size={22} />}
            />
          </div>
        </section>

        <section className="safety-section">
          <div className="safety-card">
            <div className="safety-icon">
              <ShieldCheck size={24} />
            </div>

            <div>
              <span className="mini-label">
                SAFETY FIRST
              </span>

              <h3>
                MediLens is designed to avoid confident
                guesses.
              </h3>

              <p>
                If the OCR result is unclear or medicine
                matching is ambiguous, the system can refuse
                to identify the medicine rather than
                presenting a potentially dangerous guess.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-brand">
          <div className="brand-icon">
            <Pill size={16} />
          </div>

          <span>MediLens.AI</span>
        </div>

        <p>
          Medicine recognition · Voice assistance · Safer
          understanding
        </p>
      </footer>

      {showReminder && (
        <div
          className="modal-backdrop"
          onClick={() => setShowReminder(false)}
        >
          <div
            className="reminder-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <button
              className="modal-close"
              onClick={() => setShowReminder(false)}
            >
              <X size={18} />
            </button>

            <div className="modal-icon">
              <Clock3 size={23} />
            </div>

            <span className="mini-label">
              MEDICATION REMINDER
            </span>

            <h3>Set a reminder</h3>

            <p>
              Create a simple reminder for the identified
              medicine.
            </p>

            <label>Time</label>

            <input
              type="time"
              value={reminderTime}
              onChange={(event) =>
                setReminderTime(event.target.value)
              }
            />

            <label>Frequency</label>

            <select
              value={reminderFrequency}
              onChange={(event) =>
                setReminderFrequency(
                  event.target.value
                )
              }
            >
              <option>Once daily</option>
              <option>Twice daily</option>
              <option>Three times daily</option>
              <option>As needed</option>
            </select>

            <button
              className="modal-save"
              onClick={addReminder}
            >
              <CheckCircle2 size={18} />
              Save reminder
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function MedicineCard({
  medicine,
  getAudioUrl,
  onReminder,
}) {
  const audioUrl = getAudioUrl(medicine);

  const medicineName =
    medicine?.name || "Unknown medicine";

  const getBuyUrl = () => {
    const searchQuery = encodeURIComponent(
      `buy ${medicineName} medicine`
    );

    return `https://www.google.com/search?q=${searchQuery}`;
  };

  return (
    <article className="medicine-card">
      <div className="medicine-card-top">
        <div>
          <span className="mini-label">
            IDENTIFIED MEDICINE
          </span>

          <h3>{medicineName}</h3>

          {medicine.category && (
            <span className="category-tag">
              {medicine.category}
            </span>
          )}
        </div>

        {medicine.match_score !== undefined && (
          <div className="confidence">
            <span>MATCH</span>

            <strong>
              {Math.round(medicine.match_score)}%
            </strong>
          </div>
        )}
      </div>

      <div className="info-grid">
        <InfoBox
          title="Commonly used for"
          value={
            medicine.commonly_used_for ||
            "Informational use not available"
          }
        />

        <InfoBox
          title="Typical dosage"
          value={
            medicine.typical_dosage ||
            "Follow the dosage prescribed by your doctor."
          }
        />

        <InfoBox
          title="Dosage form"
          value={
            medicine.dosage_forms ||
            "Not available"
          }
        />

        <InfoBox
          title="Side effects"
          value={
            medicine.common_side_effects ||
            "Side-effect information is not available."
          }
        />
      </div>

      {medicine.key_warning && (
        <div className="warning-box">
          <AlertTriangle size={18} />

          <div>
            <strong>Important warning</strong>

            <p>{medicine.key_warning}</p>
          </div>
        </div>
      )}

      <div className="medicine-actions">
        {audioUrl && (
          <div className="audio-player">
            <div className="audio-icon">
              <Volume2 size={18} />
            </div>

            <div className="audio-text">
              <span>
                Listen in selected language
              </span>

              <strong>
                Voice explanation
              </strong>
            </div>

            <audio controls src={audioUrl}>
              Your browser does not support audio
              playback.
            </audio>
          </div>
        )}

        <div className="action-row">
          <button
            className="reminder-action"
            onClick={onReminder}
          >
            <Clock3 size={17} />
            Add reminder
          </button>

          <a
            className="buy-medicine-action"
            href={getBuyUrl()}
            target="_blank"
            rel="noopener noreferrer"
          >
            <ShoppingCart size={17} />
            Find medicine online
            <ExternalLink size={14} />
          </a>
        </div>
      </div>

      <div className="disclaimer">
        <ShieldCheck size={14} />

        Information shown is for educational assistance
        and is not a prescription or diagnosis.
      </div>
    </article>
  );
}

function InfoBox({ title, value }) {
  return (
    <div className="info-box">
      <span>{title}</span>

      <p>{value}</p>
    </div>
  );
}

function Step({
  number,
  title,
  text,
  icon,
}) {
  return (
    <div className="step-card">
      <div className="step-top">
        <span>{number}</span>

        <div className="step-icon">
          {icon}
        </div>
      </div>

      <h3>{title}</h3>

      <p>{text}</p>
    </div>
  );
}

export default App;