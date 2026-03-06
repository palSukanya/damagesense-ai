import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Scan, Loader } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ImageUploader from '../components/ImageUploader';
import AnalysisResults from '../components/AnalysisResults';
import { damageAPI } from '../services/api';

const AnalyzePage = () => {
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState(null);
  const [vehicleId, setVehicleId] = useState('');
  const [inspectionType, setInspectionType] = useState('general');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleImageSelect = (file) => {
    setSelectedImage(file);
    setResults(null);
    setError(null);
  };

  const handleQualityCheck = async (file) => {
    try {
      const response = await damageAPI.checkImageQuality(file);
      return response.data;
    } catch (error) {
      console.error('Quality check failed:', error);
      return null;
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage || !vehicleId) {
      setError('Please provide both image and vehicle ID');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const response = await damageAPI.analyzeDamage(
        selectedImage,
        vehicleId,
        inspectionType,
        true
      );

      setResults(response.data);
    } catch (error) {
      console.error('Analysis failed:', error);
      setError(error.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setVehicleId('');
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-carbon-950 via-carbon-900 to-carbon-800 relative overflow-hidden">

      {/* Background Effects */}
      <div className="absolute inset-0 grid-pattern opacity-10" />
      <div className="absolute inset-0 retro-lines pointer-events-none" />

      <div className="relative z-10 container mx-auto px-6 py-8">

        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex items-center justify-between mb-8"
        >
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-6 py-3 glass rounded-xl hover:bg-neon-blue/10 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-neon-blue" />
            <span className="font-tech text-white">Back</span>
          </button>

          <h1 className="font-display text-4xl font-bold text-white">
            <span className="text-neon-blue">Damage</span> Analysis
          </h1>

          <div className="w-32" />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">

          {/* LEFT COLUMN */}
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >

            {/* Upload Section */}
            <div className="glass rounded-2xl p-6">
              <h2 className="font-tech text-2xl font-bold text-white mb-6">
                Upload Vehicle Image
              </h2>

              <ImageUploader
                onImageSelect={handleImageSelect}
                onQualityCheck={handleQualityCheck}
                selectedImage={selectedImage}
              />
            </div>

            {/* Inspection Form */}
            {selectedImage && !results && (
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="glass rounded-2xl p-6"
              >

                <h2 className="font-tech text-2xl font-bold text-white mb-6">
                  Inspection Details
                </h2>

                <div className="space-y-4">

                  <div>
                    <label className="block text-gray-400 font-tech text-sm mb-2">
                      Vehicle ID
                    </label>
                    <input
                      type="text"
                      value={vehicleId}
                      onChange={(e) => setVehicleId(e.target.value.toUpperCase())}
                      placeholder="e.g. KA01AB1234"
                      className="w-full px-4 py-3 bg-carbon-800 border border-gray-700 rounded-lg text-white font-tech focus:border-neon-blue focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-400 font-tech text-sm mb-2">
                      Inspection Type
                    </label>

                    <select
                      value={inspectionType}
                      onChange={(e) => setInspectionType(e.target.value)}
                      className="w-full px-4 py-3 bg-carbon-800 border border-gray-700 rounded-lg text-white font-tech focus:border-neon-blue"
                    >
                      <option value="general">General Inspection</option>
                      <option value="claim">Insurance Claim</option>
                      <option value="intake">Dealership Intake</option>
                      <option value="service">Service Check-in</option>
                      <option value="resale">Resale Evaluation</option>
                    </select>
                  </div>

                  <motion.button
                    onClick={handleAnalyze}
                    disabled={analyzing || !vehicleId}
                    className={`w-full py-4 rounded-xl font-tech text-lg font-bold flex items-center justify-center gap-3 ${
                      analyzing || !vehicleId
                        ? 'bg-gray-700 text-gray-500'
                        : 'bg-gradient-to-r from-neon-blue to-neon-purple text-white'
                    }`}
                    whileHover={!analyzing && vehicleId ? { scale: 1.02 } : {}}
                  >
                    {analyzing ? (
                      <>
                        <Loader className="w-6 h-6 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Scan className="w-6 h-6" />
                        Start Analysis
                      </>
                    )}
                  </motion.button>

                </div>

                {error && (
                  <div className="mt-4 p-4 bg-racing-red/10 border border-racing-red rounded-lg">
                    <p className="text-racing-red font-tech text-sm">{error}</p>
                  </div>
                )}

              </motion.div>
            )}

          </motion.div>

          {/* RIGHT COLUMN */}
          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >

            <AnimatePresence mode="wait">

              {analyzing && (
                <motion.div
                  key="analyzing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="glass rounded-2xl p-12 flex flex-col items-center justify-center min-h-[600px]"
                >

                  <Scan className="w-24 h-24 text-neon-blue animate-pulse mb-6" />

                  <h3 className="font-tech text-2xl font-bold text-white mb-2">
                    Analyzing Vehicle Damage
                  </h3>

                  <p className="text-gray-400">
                    AI is scanning the image...
                  </p>

                </motion.div>
              )}

              {!analyzing && results && (
                <motion.div
                  key="results"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <AnalysisResults results={results} />

                  <div className="mt-6 flex gap-4">
                    <button
                      onClick={handleReset}
                      className="flex-1 px-6 py-4 bg-carbon-800 border-2 border-gray-700 text-white font-tech font-bold rounded-xl"
                    >
                      New Analysis
                    </button>
                  </div>

                </motion.div>
              )}

            </AnimatePresence>

          </motion.div>

        </div>
      </div>
    </div>
  );
};

export default AnalyzePage;