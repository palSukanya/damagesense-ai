import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Zap, Shield, Brain, TrendingUp, ArrowRight, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const HeroSection = () => {
  const navigate = useNavigate();
  const [currentStat, setCurrentStat] = useState(0);

  const stats = [
    { value: '92%', label: 'Accuracy', icon: Brain },
    { value: '<3s', label: 'Analysis Time', icon: Zap },
    { value: '₹50L+', label: 'Fraud Prevented', icon: Shield },
    { value: '99.9%', label: 'Time Saved', icon: TrendingUp },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStat((prev) => (prev + 1) % stats.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [stats.length]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.8,
        ease: [0.6, -0.05, 0.01, 0.99],
      },
    },
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-carbon-950 via-carbon-900 to-carbon-800">
      
      {/* Animated Grid Background */}
      <div className="absolute inset-0 grid-pattern opacity-20" />
      
      {/* Animated Scan Lines */}
      <div className="absolute inset-0 retro-lines pointer-events-none" />

      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-neon-blue rounded-full"
            initial={{ x: Math.random() * window.innerWidth, y: -20, opacity: 0 }}
            animate={{
              y: window.innerHeight + 20,
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 5,
              ease: 'linear',
            }}
          />
        ))}
      </div>

      <motion.div
        className="relative z-10 container mx-auto px-6 pt-32 pb-20"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Main Title */}
        <motion.div variants={itemVariants} className="text-center mb-12">
          
          <motion.div
            className="inline-block mb-4"
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          >
            <Sparkles className="w-12 h-12 text-neon-blue mx-auto mb-4" />
          </motion.div>
          
          <h1 className="font-display text-7xl md:text-8xl font-black mb-6 leading-tight">
            <span className="bg-gradient-to-r from-neon-blue via-neon-purple to-racing-red bg-clip-text text-transparent">
              DamageSense
            </span>
            <br />
            <span className="text-white">AI</span>
          </h1>
          
          <motion.p
            className="text-2xl md:text-3xl font-tech text-metal-chrome mb-8 max-w-3xl mx-auto"
            variants={itemVariants}
          >
            Intelligent Vehicle Damage Detection
            <span className="text-neon-blue font-bold"> Powered by AI</span>
          </motion.p>

          <motion.p
            className="text-lg text-gray-400 max-w-2xl mx-auto mb-12"
            variants={itemVariants}
          >
            Transform inspections from 7 days to 7 seconds. Detect fraud. Save millions.
            The future of automotive damage assessment is here.
          </motion.p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-6 justify-center mb-20"
        >
          <motion.button
            onClick={() => navigate('/analyze')}
            className="glow-button relative px-10 py-5 bg-gradient-to-r from-neon-blue to-neon-purple text-white font-tech text-xl font-bold rounded-lg overflow-hidden group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="relative z-10 flex items-center justify-center gap-2">
              Start Analysis
              <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </span>
          </motion.button>

          <motion.button
            onClick={() => navigate('/dashboard')}
            className="px-10 py-5 bg-transparent border-2 border-neon-blue text-neon-blue font-tech text-xl font-bold rounded-lg hover:bg-neon-blue hover:text-carbon-950 transition-all"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            View Dashboard
          </motion.button>
        </motion.div>

        {/* Stats Carousel */}
        <motion.div
          variants={itemVariants}
          className="glass rounded-2xl p-8 max-w-4xl mx-auto"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              const isActive = index === currentStat;

              return (
                <motion.div
                  key={index}
                  className={`relative p-6 rounded-xl transition-all duration-500 ${
                    isActive
                      ? 'bg-gradient-to-br from-neon-blue/20 to-neon-purple/20 border-2 border-neon-blue'
                      : 'bg-carbon-800/50'
                  }`}
                  animate={isActive ? { scale: 1.05 } : { scale: 1 }}
                >
                  <Icon
                    className={`w-8 h-8 mb-3 ${
                      isActive ? 'text-neon-blue' : 'text-gray-500'
                    }`}
                  />
                  <div
                    className={`font-display text-3xl font-bold mb-1 ${
                      isActive ? 'neon-text' : 'text-white'
                    }`}
                  >
                    {stat.value}
                  </div>
                  <div className="text-gray-400 font-tech text-sm">
                    {stat.label}
                  </div>
                  
                  {isActive && (
                    <motion.div
                      className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-neon-blue to-neon-purple rounded-b-xl"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ duration: 3 }}
                    />
                  )}
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Feature Pills */}
        <motion.div
          variants={itemVariants}
          className="flex flex-wrap gap-3 justify-center mt-12"
        >
          {[
            '🔍 AI Detection',
            '⚡ Real-time',
            '🛡️ Fraud Detection',
            '📊 Analytics',
            '💰 Cost Estimation',
            '🚀 Auto-Approval',
          ].map((feature, index) => (
            <motion.span
              key={index}
              className="px-6 py-2 bg-carbon-800 border border-neon-blue/30 rounded-full text-sm font-tech text-gray-300 hover:border-neon-blue hover:text-neon-blue transition-colors cursor-default"
              whileHover={{ scale: 1.1 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
            >
              {feature}
            </motion.span>
          ))}
        </motion.div>
      </motion.div>

      {/* Bottom Gradient Overlay */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-carbon-950 to-transparent pointer-events-none" />
    </div>
  );
};

export default HeroSection;