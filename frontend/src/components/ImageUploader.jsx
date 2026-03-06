import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Camera, X, CheckCircle, AlertCircle, Image as ImageIcon } from 'lucide-react';

const ImageUploader = ({ onImageSelect, onQualityCheck, selectedImage }) => {
  const [quality, setQuality] = useState(null);
  const [checking, setChecking] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      onImageSelect(file);
      
      // Perform quality check
      setChecking(true);
      try {
        const result = await onQualityCheck(file);
        setQuality(result);
      } catch (error) {
        console.error('Quality check failed:', error);
      }
      setChecking(false);
    }
  }, [onImageSelect, onQualityCheck]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1,
    multiple: false,
  });

  const clearImage = () => {
    onImageSelect(null);
    setQuality(null);
  };

  return (
    <div className="space-y-6">
      <AnimatePresence mode="wait">
        {!selectedImage ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <div
              {...getRootProps()}
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 overflow-hidden ${
                isDragActive
                  ? 'border-neon-blue bg-neon-blue/10 scale-105'
                  : 'border-gray-600 hover:border-neon-blue hover:bg-neon-blue/5'
              }`}
            >
              <input {...getInputProps()} />

              {/* Animated Background */}
              <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {isDragActive && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-neon-blue/20 to-neon-purple/20"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  />
                )}
              </div>

              <div className="relative z-10">
                {/* Upload Icon */}
                <motion.div
                  animate={isDragActive ? { scale: 1.2, rotate: 10 } : { scale: 1, rotate: 0 }}
                  transition={{ type: 'spring', stiffness: 300 }}
                >
                  {isDragActive ? (
                    <Camera className="w-20 h-20 mx-auto mb-6 text-neon-blue" />
                  ) : (
                    <Upload className="w-20 h-20 mx-auto mb-6 text-gray-400" />
                  )}
                </motion.div>

                {/* Text */}
                <h3 className="font-tech text-2xl font-bold text-white mb-3">
                  {isDragActive ? 'Drop image here!' : 'Upload Vehicle Image'}
                </h3>
                
                <p className="text-gray-400 mb-6">
                  Drag & drop or click to select a vehicle image
                </p>

                {/* Supported Formats */}
                <div className="flex gap-3 justify-center flex-wrap">
                  {['JPG', 'PNG', 'JPEG'].map((format) => (
                    <span
                      key={format}
                      className="px-4 py-1 bg-carbon-800 border border-gray-700 rounded-full text-xs font-tech text-gray-400"
                    >
                      {format}
                    </span>
                  ))}
                </div>

                {/* Guidelines */}
                <div className="mt-8 grid grid-cols-3 gap-4 text-sm text-gray-500">
                  <div className="flex flex-col items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-neon-green" />
                    <span>Good Lighting</span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-neon-green" />
                    <span>Clear Focus</span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-neon-green" />
                    <span>Full View</span>
                  </div>
                </div>
              </div>

              {/* Scan Line Effect */}
              {isDragActive && (
                <motion.div
                  className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-neon-blue to-transparent"
                  animate={{ top: ['0%', '100%'] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                />
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="preview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="space-y-4"
          >
            {/* Image Preview */}
            <div className="relative rounded-2xl overflow-hidden border-2 border-neon-blue group">
              <img
                src={URL.createObjectURL(selectedImage)}
                alt="Selected vehicle"
                className="w-full h-96 object-cover"
              />

              {/* Remove Button */}
              <motion.button
                onClick={clearImage}
                className="absolute top-4 right-4 p-2 bg-racing-red rounded-full hover:scale-110 transition-transform"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X className="w-5 h-5 text-white" />
              </motion.button>

              {/* Checking Overlay */}
              {checking && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 bg-carbon-950/80 flex items-center justify-center backdrop-blur-sm"
                >
                  <div className="text-center">
                    <div className="spinner mx-auto mb-4" />
                    <p className="text-neon-blue font-tech font-bold">
                      Analyzing Image Quality...
                    </p>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ImageUploader;