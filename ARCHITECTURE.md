# LucianMirror Architecture

## 🎯 Dual Architecture Design

### 1. **API Service** (For MySunshineStories Integration)
- FastAPI backend
- RESTful endpoints
- Plug-and-play with any image generation service
- No UI required

### 2. **Standalone React App** (For Direct Users)
- Full-featured sprite editor
- Real-time preview
- Manual sprite placement
- Export for videos/games

## 📐 System Architecture

```
LucianMirror/
├── backend/                    # API Service
│   ├── api/                   # FastAPI routes
│   ├── core/                  # MPU, SSP, HASR
│   ├── services/              # Business logic
│   └── adapters/              # Image generation adapters
│
├── frontend/                   # React App
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/            # Main pages
│   │   ├── hooks/            # Custom React hooks
│   │   └── services/         # API client
│   └── public/
│
└── shared/                     # Shared types/utilities
    ├── types/
    └── constants/
```

## 🚀 Features

### Standalone App Features

#### Sprite Generation
- **Upload multiple reference photos**
- **Choose generation method** (DALL-E, SD, LoRA)
- **Select sprite variations** (poses, emotions, actions)
- **Real-time generation progress**
- **Preview all sprites in grid**

#### Sprite Editor
- **Individual sprite editing**
- **Regenerate specific sprites**
- **Crop/adjust sprites**
- **Remove backgrounds**
- **Batch operations**

#### Scene Composer
- **Drag-and-drop sprite placement**
- **Background generation**
- **Layer management**
- **Export options** (PNG, PSD, JSON)

#### Story Mode
- **Import story text**
- **Auto-scene detection** (SSP)
- **Smart sprite suggestions** (HASR)
- **Manual override options**
- **Export story package**

#### Video Builder (Future)
- **Timeline editor**
- **Sprite animation**
- **Transition effects**
- **Export MP4/GIF**

### API Features

#### Core Endpoints
```
POST /api/sprites/generate
POST /api/sprites/batch
GET  /api/sprites/{character_id}
POST /api/scenes/compose
POST /api/stories/process
GET  /api/learning/suggestions
```

## 🎨 UI Design Direction

Based on your examples, the React app will feature:

### Visual Style
- **Dark theme** with purple/blue accents
- **Glassmorphism** effects
- **Real-time metrics** and progress indicators
- **Multi-panel layout** with resizable sections
- **Smooth animations** and transitions

### Layout Components
- **Left Panel**: File browser, sprite library
- **Center Canvas**: Main work area with zoom/pan
- **Right Panel**: Properties, layers, tools
- **Bottom Panel**: Timeline (for video mode)
- **Top Bar**: Mode switcher, export options

### Interactive Elements
- **Drag-and-drop** everywhere
- **Context menus** for quick actions
- **Keyboard shortcuts** for power users
- **Undo/redo** with history
- **Auto-save** to local storage

## 🔧 Technology Stack

### Backend
- **FastAPI** - High-performance API
- **SQLAlchemy** - Database ORM
- **Redis** - Caching and queues
- **Celery** - Background jobs
- **Docker** - Containerization

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **React DnD** - Drag and drop
- **Zustand** - State management
- **React Query** - API integration

### Image Processing
- **Sharp** - Image manipulation
- **Canvas API** - Client-side editing
- **WebGL** - Performance rendering

## 📊 Workflow

### User Journey (Standalone App)

1. **Setup Character**
   - Upload reference photos
   - Enter character details
   - Choose art style

2. **Generate Sprites**
   - Select poses/emotions
   - Choose generation API
   - Review and edit results

3. **Create Scenes**
   - Import or write story
   - Auto-detect scenes
   - Place sprites on backgrounds

4. **Export Results**
   - Download sprite sheets
   - Export composed scenes
   - Save project file

### API Workflow (MySunshineStories)

1. **Initialize Character**
   ```
   POST /api/sprites/generate
   {
     "character_id": "sunshine_123",
     "reference_photos": [...],
     "style": "watercolor"
   }
   ```

2. **Process Story**
   ```
   POST /api/stories/process
   {
     "story_text": "...",
     "character_id": "sunshine_123"
   }
   ```

3. **Get Composed Scenes**
   ```
   GET /api/scenes/{story_id}
   Returns: Array of composed images
   ```

## 🎯 Implementation Priority

### Phase 1: Core API (Week 1-2)
- Basic sprite generation
- MPU/SSP/HASR integration
- DALL-E adapter

### Phase 2: React UI Foundation (Week 3-4)
- Project setup
- Basic layout
- Sprite uploader
- Preview grid

### Phase 3: Editor Features (Week 5-6)
- Sprite editor
- Scene composer
- Export functionality

### Phase 4: Advanced Features (Week 7-8)
- Story mode
- HASR learning
- Video timeline

## 🚀 Getting Started

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📝 API Documentation

Full API docs available at `/docs` when running the backend.

## 🎮 Export Formats

- **Sprite Sheets** - For game engines
- **Individual PNGs** - For direct use
- **JSON Manifest** - Sprite metadata
- **PSD Files** - For further editing
- **Video** - MP4, GIF formats
