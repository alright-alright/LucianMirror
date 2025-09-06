import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Database, Cpu, Zap, TrendingUp, Activity, Layers, GitBranch } from 'lucide-react';

interface MetricData {
  mpu: {
    totalSprites: number;
    cacheHits: number;
    querySpeed: number;
    dimensions: string[];
  };
  ssp: {
    scenesProcessed: number;
    entitiesDetected: number;
    bindingAccuracy: number;
    activeBindings: string[];
  };
  hasr: {
    learningCycles: number;
    successRate: number;
    patterns: number;
    reinforcements: number;
  };
}

export const LucianMetrics: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricData>({
    mpu: { totalSprites: 0, cacheHits: 0, querySpeed: 0, dimensions: [] },
    ssp: { scenesProcessed: 0, entitiesDetected: 0, bindingAccuracy: 0, activeBindings: [] },
    hasr: { learningCycles: 0, successRate: 0, patterns: 0, reinforcements: 0 }
  });
  
  const [activeComponent, setActiveComponent] = useState<'mpu' | 'ssp' | 'hasr' | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/metrics`);
        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
        }
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Update every 5 seconds

    // Listen for processing events
    const handleProcessingStart = () => setIsProcessing(true);
    const handleProcessingEnd = () => setIsProcessing(false);
    
    window.addEventListener('lucian-processing-start' as any, handleProcessingStart);
    window.addEventListener('lucian-processing-end' as any, handleProcessingEnd);

    return () => {
      clearInterval(interval);
      window.removeEventListener('lucian-processing-start' as any, handleProcessingStart);
      window.removeEventListener('lucian-processing-end' as any, handleProcessingEnd);
    };
  }, []);

  const MetricCard = ({ 
    title, 
    icon: Icon, 
    value, 
    subValue, 
    color, 
    onClick,
    isActive 
  }: any) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`relative p-4 bg-gray-800/50 backdrop-blur-sm border rounded-xl cursor-pointer transition-all duration-300 ${
        isActive ? 'border-purple-500 shadow-lg shadow-purple-500/20' : 'border-gray-700 hover:border-gray-600'
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Icon className={`w-5 h-5 ${color}`} />
            <h3 className="text-sm font-semibold text-gray-300">{title}</h3>
          </div>
          <div className="text-2xl font-bold text-white">{value}</div>
          <div className="text-xs text-gray-400 mt-1">{subValue}</div>
        </div>
        
        {isActive && (
          <motion.div
            className={`w-2 h-2 rounded-full ${color.replace('text', 'bg')}`}
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}
      </div>
      
      {isProcessing && isActive && (
        <motion.div
          className="absolute inset-0 border-2 border-purple-500 rounded-xl opacity-30"
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      )}
    </motion.div>
  );

  return (
    <div className="space-y-4">
      {/* Main Metrics Grid */}
      <div className="grid grid-cols-3 gap-4">
        <MetricCard
          title="MPU Memory"
          icon={Database}
          value={metrics.mpu.totalSprites}
          subValue={`${metrics.mpu.cacheHits}% cache hits`}
          color="text-blue-400"
          onClick={() => setActiveComponent(activeComponent === 'mpu' ? null : 'mpu')}
          isActive={activeComponent === 'mpu'}
        />
        
        <MetricCard
          title="SSP Processing"
          icon={Brain}
          value={metrics.ssp.scenesProcessed}
          subValue={`${metrics.ssp.entitiesDetected} entities`}
          color="text-purple-400"
          onClick={() => setActiveComponent(activeComponent === 'ssp' ? null : 'ssp')}
          isActive={activeComponent === 'ssp'}
        />
        
        <MetricCard
          title="HASR Learning"
          icon={TrendingUp}
          value={`${metrics.hasr.successRate}%`}
          subValue={`${metrics.hasr.patterns} patterns`}
          color="text-green-400"
          onClick={() => setActiveComponent(activeComponent === 'hasr' ? null : 'hasr')}
          isActive={activeComponent === 'hasr'}
        />
      </div>

      {/* Detailed View */}
      <AnimatePresence>
        {activeComponent && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-xl p-4"
          >
            {activeComponent === 'mpu' && <MPUDetails metrics={metrics.mpu} />}
            {activeComponent === 'ssp' && <SSPDetails metrics={metrics.ssp} />}
            {activeComponent === 'hasr' && <HASRDetails metrics={metrics.hasr} />}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Processing Indicator */}
      {isProcessing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-2 px-3 py-2 bg-purple-900/20 border border-purple-700/30 rounded-lg"
        >
          <Activity className="w-4 h-4 text-purple-400 animate-pulse" />
          <span className="text-sm text-purple-300">LucianOS Processing...</span>
        </motion.div>
      )}
    </div>
  );
};

// MPU Details Component
const MPUDetails: React.FC<{ metrics: any }> = ({ metrics }) => (
  <div className="space-y-3">
    <h4 className="text-sm font-semibold text-blue-400 flex items-center gap-2">
      <Database className="w-4 h-4" />
      Memory Processing Unit Details
    </h4>
    
    <div className="grid grid-cols-2 gap-3">
      <div className="bg-gray-900/50 rounded-lg p-3">
        <div className="text-xs text-gray-400">Query Speed</div>
        <div className="text-lg font-bold text-white">{metrics.querySpeed}ms</div>
      </div>
      <div className="bg-gray-900/50 rounded-lg p-3">
        <div className="text-xs text-gray-400">Dimensions</div>
        <div className="text-lg font-bold text-white">{metrics.dimensions.length}</div>
      </div>
    </div>
    
    <div className="bg-gray-900/50 rounded-lg p-3">
      <div className="text-xs text-gray-400 mb-2">Active Dimensions</div>
      <div className="flex flex-wrap gap-2">
        {metrics.dimensions.map((dim: string) => (
          <span key={dim} className="px-2 py-1 bg-blue-900/30 text-blue-300 text-xs rounded">
            {dim}
          </span>
        ))}
      </div>
    </div>
  </div>
);

// SSP Details Component
const SSPDetails: React.FC<{ metrics: any }> = ({ metrics }) => (
  <div className="space-y-3">
    <h4 className="text-sm font-semibold text-purple-400 flex items-center gap-2">
      <Brain className="w-4 h-4" />
      Symbolic Sense Processor Details
    </h4>
    
    <div className="grid grid-cols-2 gap-3">
      <div className="bg-gray-900/50 rounded-lg p-3">
        <div className="text-xs text-gray-400">Binding Accuracy</div>
        <div className="text-lg font-bold text-white">{metrics.bindingAccuracy}%</div>
      </div>
      <div className="bg-gray-900/50 rounded-lg p-3">
        <div className="text-xs text-gray-400">Active Bindings</div>
        <div className="text-lg font-bold text-white">{metrics.activeBindings.length}</div>
      </div>
    </div>
    
    {metrics.activeBindings.length > 0 && (
      <div className="bg-gray-900/50 rounded-lg p-3">
        <div className="text-xs text-gray-400 mb-2">Current Bindings</div>
        <div className="space-y-1">
          {metrics.activeBindings.slice(0, 3).map((binding: string, i: number) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center gap-2"
            >
              <GitBranch className="w-3 h-3 text-purple-400" />
              <span className="text-xs text-gray-300">{binding}</span>
            </motion.div>
          ))}
        </div>
      </div>
    )}
  </div>
);

// HASR Details Component
const HASRDetails: React.FC<{ metrics: any }> = ({ metrics }) => (
  <div className="space-y-3">
    <h4 className="text-sm font-semibold text-green-400 flex items-center gap-2">
      <TrendingUp className="w-4 h-4" />
      Hebbian Reinforcement Details
    </h4>
    
    <div className="grid grid-cols-2 gap-3">
      <div className="bg-gray-900/50 rounded-lg p-3">
        <div className="text-xs text-gray-400">Learning Cycles</div>
        <div className="text-lg font-bold text-white">{metrics.learningCycles}</div>
      </div>
      <div className="bg-gray-900/50 rounded-lg p-3">
        <div className="text-xs text-gray-400">Reinforcements</div>
        <div className="text-lg font-bold text-white">{metrics.reinforcements}</div>
      </div>
    </div>
    
    <div className="bg-gray-900/50 rounded-lg p-3">
      <div className="text-xs text-gray-400 mb-2">Success Rate Trend</div>
      <div className="h-16 flex items-end gap-1">
        {[65, 70, 72, 78, 82, 85, 88, metrics.successRate].map((value, i) => (
          <motion.div
            key={i}
            initial={{ height: 0 }}
            animate={{ height: `${value}%` }}
            transition={{ delay: i * 0.05 }}
            className="flex-1 bg-gradient-to-t from-green-600 to-green-400 rounded-t"
          />
        ))}
      </div>
    </div>
  </div>
);