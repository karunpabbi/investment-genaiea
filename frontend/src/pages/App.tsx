import React, { useMemo, useState } from 'react';
import axios from 'axios';

type AnalysisResponse = {
  startup_name: string;
  total_score: number;
  score_breakdown: Record<string, number>;
  strengths: string[];
  risks: string[];
  benchmarks: Record<string, number>;
  summary_note: string;
  detailed_note: string;
  founder_profile_note: string;
  artifacts: { label: string; url: string }[];
};

type StartupForm = {
  name: string;
  sector: string;
  headquarters: string;
  description: string;
  notes: string;
};

type WeightKey = 'market' | 'team' | 'traction' | 'technology' | 'financials' | 'regulatory';

const WEIGHT_LABELS: Record<WeightKey, string> = {
  market: 'Market Size',
  team: 'Founders & Team',
  traction: 'Traction & Growth',
  technology: 'Technology Edge',
  financials: 'Financial Quality',
  regulatory: 'Regulatory Fit'
};

const initialWeights: Record<WeightKey, number> = {
  market: 30,
  team: 25,
  traction: 20,
  technology: 10,
  financials: 10,
  regulatory: 5
};

const App: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [weights, setWeights] = useState<Record<WeightKey, number>>(initialWeights);
  const [startupForm, setStartupForm] = useState<StartupForm>({
    name: '',
    sector: '',
    headquarters: '',
    description: '',
    notes: ''
  });

  const totalWeight = useMemo(() => Object.values(weights).reduce((acc, val) => acc + val, 0), [weights]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;
    setSelectedFiles(Array.from(event.target.files));
  };

  const handleWeightChange = (key: WeightKey, value: number) => {
    setWeights((prev) => ({ ...prev, [key]: value }));
  };

  const handleStartupField = (field: keyof StartupForm, value: string) => {
    setStartupForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleAnalyze = async () => {
    setError(null);
    setAnalysisResult(null);
    if (!startupForm.name) {
      setError('Startup name is required.');
      return;
    }
    if (selectedFiles.length === 0) {
      setError('Upload at least one file to run the analysis.');
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      selectedFiles.forEach((file) => formData.append('files', file));
      const uploadResponse = await axios.post<{ document_ids: string[] }>('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setUploading(false);
      setAnalyzing(true);

      const payload = {
        document_ids: uploadResponse.data.document_ids,
        preferences: {
          startup_name: startupForm.name,
          sector: startupForm.sector,
          headquarters: startupForm.headquarters,
          description: startupForm.description,
          notes: startupForm.notes,
          focus_weights: weights
        }
      };

      const analysisResponse = await axios.post<AnalysisResponse>('/api/analysis/run', payload);
      setAnalysisResult(analysisResponse.data);
    } catch (err) {
      console.error(err);
      setError('Unable to run analysis. Please check backend logs or configuration.');
    } finally {
      setUploading(false);
      setAnalyzing(false);
    }
  };

  const renderScoreBreakdown = () => {
    if (!analysisResult) return null;
    return Object.entries(analysisResult.score_breakdown).map(([key, value]) => (
      <div key={key} className="slider-control">
        <div className="slider-label">
          <span>{WEIGHT_LABELS[key as WeightKey] || key}</span>
          <span>{(value * 100).toFixed(1)} pts</span>
        </div>
        <div className="badge">Weight {weights[key as WeightKey]}%</div>
      </div>
    ));
  };

  return (
    <div className="app-shell">
      <header>
        <div>
          <h1>GenAI Analyst Workbench</h1>
          <p>Upload founder material, tune investment focus and generate investor-ready intelligence.</p>
        </div>
        <div>
          <button className="secondary" type="button" onClick={() => window.open('https://cloud.google.com/vertex-ai', '_blank')}>
            View Vertex AI Docs
          </button>
        </div>
      </header>

      <div className="card">
        <h2>1. Founder Material Ingestion</h2>
        <p>Upload pitch decks, models, transcripts or emails. PDF, DOCX, PPTX, XLSX, CSV, JSON and image formats supported.</p>
        <label className="upload-dropzone">
          <input type="file" multiple onChange={handleFileChange} />
          <p>{selectedFiles.length ? `${selectedFiles.length} files selected` : 'Drag and drop or browse files'}</p>
        </label>
      </div>

      <div className="card">
        <h2>2. Investor Focus Calibration</h2>
        <p>Set the weighting for what matters most in this deal. Total weight: {totalWeight}%</p>
        <div className="weights-grid">
          {Object.entries(WEIGHT_LABELS).map(([key, label]) => (
            <div key={key} className="slider-control">
              <div className="slider-label">
                <span>{label}</span>
                <span>{weights[key as WeightKey]}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={weights[key as WeightKey]}
                onChange={(event) => handleWeightChange(key as WeightKey, Number(event.target.value))}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>3. Startup Context</h2>
        <div className="weights-grid">
          <label className="slider-control">
            <span className="slider-label">Startup Name</span>
            <input
              type="text"
              value={startupForm.name}
              onChange={(event) => handleStartupField('name', event.target.value)}
              placeholder="e.g. Lattice Biosciences"
            />
          </label>
          <label className="slider-control">
            <span className="slider-label">Sector</span>
            <input
              type="text"
              value={startupForm.sector}
              onChange={(event) => handleStartupField('sector', event.target.value)}
              placeholder="e.g. Digital Health"
            />
          </label>
          <label className="slider-control">
            <span className="slider-label">Headquarters</span>
            <input
              type="text"
              value={startupForm.headquarters}
              onChange={(event) => handleStartupField('headquarters', event.target.value)}
              placeholder="e.g. Singapore"
            />
          </label>
          <label className="slider-control">
            <span className="slider-label">Notes to Analyst</span>
            <textarea
              value={startupForm.notes}
              onChange={(event) => handleStartupField('notes', event.target.value)}
              placeholder="Share diligence priorities or bespoke focus areas"
              rows={4}
            />
          </label>
        </div>
        <label className="slider-control" style={{ marginTop: '16px' }}>
          <span className="slider-label">Short Description</span>
          <textarea
            value={startupForm.description}
            onChange={(event) => handleStartupField('description', event.target.value)}
            placeholder="One paragraph elevator pitch."
            rows={4}
          />
        </label>
      </div>

      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>4. Generate AI Analyst Reports</h2>
          <p>Summarized and detailed reports plus founder dossier will be created automatically.</p>
          {error && <p style={{ color: '#dc2626' }}>{error}</p>}
        </div>
        <div>
          <button
            className="primary"
            type="button"
            disabled={uploading || analyzing}
            onClick={handleAnalyze}
          >
            {(uploading || analyzing) ? 'Processing…' : 'Generate Intelligence'}
          </button>
        </div>
      </div>

      {analysisResult && (
        <div className="card">
          <h2>Investment Output</h2>
          <div className="results-grid">
            <div>
              <h3>Scorecard</h3>
              <p className="badge">Total Score {(analysisResult.total_score * 100).toFixed(1)} / 100</p>
              {renderScoreBreakdown()}
            </div>
            <div>
              <h3>Strengths & Risks</h3>
              <div>
                <h4>Strengths</h4>
                <ul>
                  {analysisResult.strengths.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4>Risks</h4>
                <ul>
                  {analysisResult.risks.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div>
              <h3>Reports</h3>
              <div>
                <h4>Summary Note</h4>
                <p>{analysisResult.summary_note}</p>
              </div>
              <div>
                <h4>Detailed Note</h4>
                <p>{analysisResult.detailed_note}</p>
              </div>
              <div>
                <h4>Founder Dossier</h4>
                <p>{analysisResult.founder_profile_note}</p>
              </div>
              <div>
                <h4>Download PDFs</h4>
                <ul>
                  {analysisResult.artifacts.map((artifact) => (
                    <li key={artifact.label}>
                      <a href={artifact.url} target="_blank" rel="noreferrer">
                        {artifact.label.toUpperCase()} Report
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      <footer>
        <p>
          Built for multi-modal diligence. Integrates Gemini, Vertex AI, Cloud Vision OCR, BigQuery benchmarks, Firebase artifact
          delivery and agentic orchestration.
        </p>
      </footer>
    </div>
  );
};

export default App;
