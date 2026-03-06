import React from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  Shield,
  AlertOctagon,
  Zap,
} from 'lucide-react';

const AnalysisResults = ({ results }) => {
  if (!results) return null;

  const { 
    inspection_id,
    damages_detected,
    detections,
    overall_assessment,
    estimated_repair_time_hours,
    recommendations,
    historical_comparison,
  } = results;

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'text-neon-green',
      medium: 'text-racing-orange',
      high: 'text-racing-red',
      critical: 'text-purple-500',
    };
    return colors[severity] || 'text-gray-400';
  };

  const getSeverityBg = (severity) => {
    const colors = {
      low: 'bg-neon-green/10 border-neon-green/30',
      medium: 'bg-racing-orange/10 border-racing-orange/30',
      high: 'bg-racing-red/10 border-racing-red/30',
      critical: 'bg-purple-500/10 border-purple-500/30',
    };
    return colors[severity] || 'bg-gray-500/10 border-gray-500/30';
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5 },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header Card */}
      <motion.div
        variants={itemVariants}
        className="glass rounded-2xl p-8 border-2 border-neon-blue relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-neon-blue/20 to-transparent rounded-full blur-3xl" />
        
        <div className="relative z-10">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="font-display text-3xl font-bold text-white mb-2">
                Analysis Complete
              </h2>
              <p className="text-gray-400 font-tech">
                Inspection ID: <span className="text-neon-blue font-bold">{inspection_id}</span>
              </p>
            </div>
            
            <motion.div
              className="flex items-center gap-2 px-6 py-3 bg-neon-green/20 border border-neon-green rounded-full"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <CheckCircle className="w-6 h-6 text-neon-green" />
              <span className="text-neon-green font-tech font-bold">VERIFIED</span>
            </motion.div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-carbon-800 rounded-xl">
              <div className="text-4xl font-display font-bold text-neon-blue mb-1">
                {damages_detected}
              </div>
              <div className="text-sm text-gray-400">Damages Found</div>
            </div>

            <div className="text-center p-4 bg-carbon-800 rounded-xl">
              <div className={`text-4xl font-display font-bold ${getSeverityColor(overall_assessment.overall_severity)} mb-1`}>
                {overall_assessment.overall_severity.toUpperCase()}
              </div>
              <div className="text-sm text-gray-400">Overall Severity</div>
            </div>

            <div className="text-center p-4 bg-carbon-800 rounded-xl">
              <div className="text-4xl font-display font-bold text-racing-orange mb-1">
                ₹{overall_assessment.total_estimated_cost.toLocaleString()}
              </div>
              <div className="text-sm text-gray-400">Est. Cost</div>
            </div>

            <div className="text-center p-4 bg-carbon-800 rounded-xl">
              <div className="text-4xl font-display font-bold text-neon-purple mb-1">
                {estimated_repair_time_hours}h
              </div>
              <div className="text-sm text-gray-400">Repair Time</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Damage List */}
      {detections && detections.length > 0 && (
        <motion.div variants={itemVariants} className="glass rounded-2xl p-6">
          <h3 className="font-tech text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-racing-orange" />
            Detected Damages
          </h3>

          <div className="space-y-4">
            {detections.map((damage, index) => (
              <motion.div
                key={index}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`p-5 border-2 rounded-xl ${getSeverityBg(damage.severity)} backdrop-blur-sm`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="px-3 py-1 bg-carbon-900 rounded-full text-sm font-tech text-white">
                        #{index + 1}
                      </span>
                      <h4 className="font-tech text-lg font-bold text-white capitalize">
                        {damage.damage_type.replace('_', ' ')}
                      </h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-tech font-bold ${getSeverityColor(damage.severity)}`}>
                        {damage.severity.toUpperCase()}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Category</div>
                        <div className="text-sm text-white font-tech capitalize">
                          {damage.damage_category}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Confidence</div>
                        <div className="text-sm text-neon-blue font-tech font-bold">
                          {(damage.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Area</div>
                        <div className="text-sm text-white font-tech">
                          {damage.area_percentage.toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Est. Cost</div>
                        <div className="text-sm text-racing-orange font-tech font-bold">
                          ₹{damage.estimated_repair_cost.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <motion.div variants={itemVariants} className="glass rounded-2xl p-6">
          <h3 className="font-tech text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Zap className="w-6 h-6 text-neon-blue" />
            Recommendations
          </h3>

          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <motion.div
                key={index}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-start gap-3 p-4 bg-carbon-800 rounded-lg border border-gray-700"
              >
                <TrendingUp className="w-5 h-5 text-neon-blue flex-shrink-0 mt-0.5" />
                <p className="text-gray-300 font-tech">{rec}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Auto Approval */}
      <motion.div
        variants={itemVariants}
        className={`p-6 rounded-2xl border-2 ${
          overall_assessment.auto_approve_eligible
            ? 'bg-neon-green/10 border-neon-green'
            : 'bg-racing-orange/10 border-racing-orange'
        }`}
      >
        <div className="flex items-center gap-4">
          {overall_assessment.auto_approve_eligible ? (
            <CheckCircle className="w-12 h-12 text-neon-green" />
          ) : (
            <XCircle className="w-12 h-12 text-racing-orange" />
          )}
          <div>
            <h4 className="font-tech text-xl font-bold text-white mb-1">
              {overall_assessment.auto_approve_eligible
                ? 'Eligible for Auto Approval'
                : 'Manual Review Required'}
            </h4>
            <p className="text-gray-400 text-sm">
              {overall_assessment.auto_approve_eligible
                ? 'This claim meets auto approval criteria.'
                : 'This claim needs manual adjuster review.'}
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AnalysisResults;