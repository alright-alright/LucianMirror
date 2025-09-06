import React from 'react';
import { Save, Check, Zap, DollarSign, Clock, Server } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface GenerationAPI {
  id: string;
  name: string;
  icon: React.ElementType;
  description: string;
  costPerImage: string;
  speed: string;
  quality: string;
  requiresKey: boolean;
  keyName?: string;
  active: boolean;
}

const availableAPIs: GenerationAPI[] = [
  {
    id: 'dalle',
    name: 'DALL-E 3',
    icon: Zap,
    description: 'OpenAI\'s latest image generation model',
    costPerImage: '$0.04',
    speed: '5-10s',
    quality: 'Excellent',
    requiresKey: true,
    keyName: 'OPENAI_API_KEY',
    active: true
  },
  {
    id: 'stable_diffusion',
    name: 'Stable Diffusion',
    icon: Server,
    description: 'Stability AI\'s open model',
    costPerImage: '$0.01',
    speed: '3-8s',
    quality: 'Very Good',
    requiresKey: true,
    keyName: 'STABILITY_API_KEY',
    active: true
  },
  {
    id: 'local_sd',
    name: 'Local SD',
    icon: Server,
    description: 'Self-hosted Stable Diffusion',
    costPerImage: 'Free',
    speed: '5-15s',
    quality: 'Good',
    requiresKey: false,
    active: false
  },
  {
    id: 'replicate',
    name: 'Replicate',
    icon: Zap,
    description: 'Access to Flux, SDXL, and more',
    costPerImage: '$0.02',
    speed: '8-12s',
    quality: 'Excellent',
    requiresKey: true,
    keyName: 'REPLICATE_API_TOKEN',
    active: true
  },
  {
    id: 'midjourney',
    name: 'Midjourney',
    icon: Zap,
    description: 'Coming soon',
    costPerImage: '$0.05',
    speed: '10-20s',
    quality: 'Excellent',
    requiresKey: true,
    keyName: 'MIDJOURNEY_KEY',
    active: false
  }
];

export const GenerationSettings: React.FC = () => {
  const [selectedAPI, setSelectedAPI] = React.useState('dalle');
  const [apiKeys, setApiKeys] = React.useState<Record<string, string>>({});
  const [saved, setSaved] = React.useState(false);
  const [testResults, setTestResults] = React.useState<Record<string, boolean>>({});

  // Load settings from localStorage
  React.useEffect(() => {
    const savedAPI = localStorage.getItem('generation_api') || 'dalle';
    const savedKeys = JSON.parse(localStorage.getItem('api_keys') || '{}');
    setSelectedAPI(savedAPI);
    setApiKeys(savedKeys);
  }, []);

  const handleSave = () => {
    localStorage.setItem('generation_api', selectedAPI);
    localStorage.setItem('api_keys', JSON.stringify(apiKeys));
    
    // Update API client
    window.dispatchEvent(new CustomEvent('generation-api-changed', {
      detail: { api: selectedAPI }
    }));
    
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const testAPIConnection = async (apiId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/test-connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          api: apiId,
          key: apiKeys[availableAPIs.find(a => a.id === apiId)?.keyName || '']
        })
      });
      
      const result = await response.json();
      setTestResults(prev => ({ ...prev, [apiId]: result.success }));
    } catch (error) {
      setTestResults(prev => ({ ...prev, [apiId]: false }));
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Current Selection */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Image Generation Settings</h2>
        <p className="text-white/80">
          Choose your preferred AI model for generating sprites and backgrounds.
          You can switch between providers at any time.
        </p>
        <div className="mt-4 flex items-center space-x-4">
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <span className="text-sm">Current API:</span>
            <span className="ml-2 font-bold">
              {availableAPIs.find(a => a.id === selectedAPI)?.name}
            </span>
          </div>
        </div>
      </div>

      {/* API Options */}
      <div className="grid gap-4">
        {availableAPIs.map((api, index) => (
          <motion.div
            key={api.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={clsx(
              'bg-gray-800 rounded-xl p-6 border-2 transition-all cursor-pointer',
              selectedAPI === api.id
                ? 'border-purple-500 shadow-lg shadow-purple-500/20'
                : 'border-gray-700 hover:border-gray-600',
              !api.active && 'opacity-50 cursor-not-allowed'
            )}
            onClick={() => api.active && setSelectedAPI(api.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className={clsx(
                  'w-12 h-12 rounded-lg flex items-center justify-center',
                  selectedAPI === api.id ? 'bg-purple-600' : 'bg-gray-700'
                )}>
                  <api.icon className="w-6 h-6 text-white" />
                </div>
                
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white flex items-center">
                    {api.name}
                    {!api.active && (
                      <span className="ml-2 px-2 py-1 bg-gray-700 text-xs rounded">
                        Coming Soon
                      </span>
                    )}
                    {selectedAPI === api.id && (
                      <Check className="ml-2 w-5 h-5 text-green-400" />
                    )}
                  </h3>
                  <p className="text-gray-400 text-sm mt-1">{api.description}</p>
                  
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div>
                      <span className="text-xs text-gray-500">Cost</span>
                      <div className="flex items-center text-white">
                        <DollarSign className="w-4 h-4 mr-1" />
                        {api.costPerImage}
                      </div>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Speed</span>
                      <div className="flex items-center text-white">
                        <Clock className="w-4 h-4 mr-1" />
                        {api.speed}
                      </div>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Quality</span>
                      <div className="text-white">{api.quality}</div>
                    </div>
                  </div>

                  {/* API Key Input */}
                  {api.requiresKey && api.active && (
                    <div className="mt-4">
                      <label className="block text-sm text-gray-400 mb-2">
                        API Key ({api.keyName})
                      </label>
                      <div className="flex space-x-2">
                        <input
                          type="password"
                          value={apiKeys[api.keyName || ''] || ''}
                          onChange={(e) => setApiKeys(prev => ({
                            ...prev,
                            [api.keyName || '']: e.target.value
                          }))}
                          className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                          placeholder="Enter your API key"
                        />
                        <button
                          onClick={() => testAPIConnection(api.id)}
                          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
                        >
                          Test
                        </button>
                      </div>
                      {testResults[api.id] !== undefined && (
                        <p className={clsx(
                          'mt-2 text-sm',
                          testResults[api.id] ? 'text-green-400' : 'text-red-400'
                        )}>
                          {testResults[api.id] ? '✅ Connection successful' : '❌ Connection failed'}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Additional Settings */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Generation Preferences</h3>
        
        <div className="space-y-4">
          <div>
            <label className="flex items-center justify-between">
              <span className="text-white">Auto-remove backgrounds</span>
              <input type="checkbox" defaultChecked className="toggle" />
            </label>
          </div>
          
          <div>
            <label className="flex items-center justify-between">
              <span className="text-white">Generate thumbnails</span>
              <input type="checkbox" defaultChecked className="toggle" />
            </label>
          </div>
          
          <div>
            <label className="flex items-center justify-between">
              <span className="text-white">Use caching</span>
              <input type="checkbox" defaultChecked className="toggle" />
            </label>
          </div>
          
          <div>
            <label className="block text-white mb-2">
              Concurrent generations
            </label>
            <select className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
              <option value="1">1 (Slowest, most stable)</option>
              <option value="3" selected>3 (Balanced)</option>
              <option value="5">5 (Fast, may hit rate limits)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className={clsx(
            'px-6 py-3 rounded-lg font-medium transition-all flex items-center',
            saved
              ? 'bg-green-600 text-white'
              : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700'
          )}
        >
          {saved ? (
            <>
              <Check className="w-5 h-5 mr-2" />
              Saved!
            </>
          ) : (
            <>
              <Save className="w-5 h-5 mr-2" />
              Save Settings
            </>
          )}
        </button>
      </div>
    </div>
  );
};