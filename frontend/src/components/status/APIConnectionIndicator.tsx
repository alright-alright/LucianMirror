import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Zap, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';

interface APIConnectionIndicatorProps {
  className?: string;
}

export const APIConnectionIndicator: React.FC<APIConnectionIndicatorProps> = ({ 
  className = '' 
}) => {
  const [provider, setProvider] = useState<string>('DALL-E');
  const [backendStatus, setBackendStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
  const [aiStatus, setAiStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
  const [lastCheck, setLastCheck] = useState<Date>(new Date());
  const [isRetrying, setIsRetrying] = useState(false);

  // Check both backend and AI provider connections
  useEffect(() => {
    const checkConnections = async () => {
      try {
        // Check backend API
        const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          setBackendStatus('connected');
          
          // Get the current generation API from settings
          const currentApi = localStorage.getItem('generation_api') || 'dalle';
          const apiNames: Record<string, string> = {
            'dalle': 'DALL-E 3',
            'stable_diffusion': 'Stable Diffusion',
            'local_sd': 'Local SD',
            'replicate': 'Replicate'
          };
          setProvider(apiNames[currentApi] || 'DALL-E 3');
          
          // Check if the AI service is properly configured
          if (data.components?.generation === 'ready') {
            setAiStatus('connected');
          } else {
            setAiStatus('connecting');
          }
        } else {
          setBackendStatus('disconnected');
          setAiStatus('disconnected');
        }
        
        setLastCheck(new Date());
      } catch (error) {
        console.error('Connection check failed:', error);
        setBackendStatus('disconnected');
        setAiStatus('disconnected');
      }
    };

    // Check immediately
    checkConnections();
    
    // Check every 30 seconds
    const interval = setInterval(checkConnections, 30000);
    
    // Listen for generation API changes
    const handleApiChange = (event: CustomEvent) => {
      checkConnections();
    };
    window.addEventListener('generation-api-changed' as any, handleApiChange);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('generation-api-changed' as any, handleApiChange);
    };
  }, []);

  const handleRetry = async () => {
    setIsRetrying(true);
    // Trigger a connection check
    const event = new CustomEvent('generation-api-changed');
    window.dispatchEvent(event);
    setTimeout(() => setIsRetrying(false), 1000);
  };

  const getOverallStatus = () => {
    if (backendStatus === 'connected' && aiStatus === 'connected') return 'connected';
    if (backendStatus === 'disconnected' || aiStatus === 'disconnected') return 'disconnected';
    return 'connecting';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'bg-green-500 shadow-green-500/50';
      case 'connecting':
        return 'bg-yellow-500 shadow-yellow-500/50';
      case 'disconnected':
        return 'bg-red-500 shadow-red-500/50';
      default:
        return 'bg-gray-500 shadow-gray-500/50';
    }
  };

  const getStatusIcon = () => {
    const status = getOverallStatus();
    switch (status) {
      case 'connected':
        return <Zap className="w-3.5 h-3.5" />;
      case 'connecting':
        return <AlertTriangle className="w-3.5 h-3.5" />;
      case 'disconnected':
        return <XCircle className="w-3.5 h-3.5" />;
      default:
        return <Zap className="w-3.5 h-3.5" />;
    }
  };

  const getTooltipContent = () => {
    const lines = [];
    lines.push(`Backend: ${backendStatus}`);
    lines.push(`AI Provider: ${provider} (${aiStatus})`);
    lines.push(`Last check: ${lastCheck.toLocaleTimeString()}`);
    return lines.join('\\n');
  };

  const overallStatus = getOverallStatus();

  return (
    <div className="relative group">
      <div
        className={`inline-flex items-center gap-2 px-3 py-1.5 bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-lg text-xs font-medium transition-all duration-300 hover:bg-gray-800/90 hover:border-gray-600/50 ${className}`}
        title={getTooltipContent()}
      >
        {/* Provider Name */}
        <span className="text-gray-300 select-none">{provider}</span>
        
        {/* Status Indicator */}
        <div className="flex items-center gap-1.5">
          <motion.div
            className={`w-2 h-2 rounded-full ${getStatusColor(overallStatus)}`}
            animate={
              overallStatus === 'connected' || overallStatus === 'connecting'
                ? { opacity: [1, 0.4, 1] }
                : {}
            }
            transition={
              overallStatus === 'connected'
                ? { duration: 3, repeat: Infinity, ease: 'easeInOut' }
                : overallStatus === 'connecting'
                ? { duration: 1, repeat: Infinity, ease: 'easeInOut' }
                : {}
            }
          />
          {getStatusIcon()}
        </div>

        {/* Retry Button */}
        {overallStatus === 'disconnected' && (
          <button
            onClick={handleRetry}
            className="p-1 hover:bg-gray-700/50 rounded transition-colors"
            disabled={isRetrying}
          >
            <RefreshCw 
              className={`w-3 h-3 ${isRetrying ? 'animate-spin' : ''}`} 
            />
          </button>
        )}
      </div>
      
      {/* Enhanced Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 border border-gray-700 text-white text-xs rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${getStatusColor(backendStatus)}`} />
            <span>Backend: {backendStatus}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${getStatusColor(aiStatus)}`} />
            <span>{provider}: {aiStatus}</span>
          </div>
          <div className="text-gray-400 text-[10px] pt-1 border-t border-gray-700">
            Last check: {lastCheck.toLocaleTimeString()}
          </div>
        </div>
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
          <div className="border-4 border-transparent border-t-gray-900" />
        </div>
      </div>
    </div>
  );
};