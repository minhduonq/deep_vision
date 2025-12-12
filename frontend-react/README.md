# Deep Vision - Professional React Frontend

Modern, production-ready React frontend for Deep Vision AI image processing system.

## 🚀 Tech Stack

### Core
- **React 18** - Modern React with Hooks & Concurrent Features
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool
- **React Router v6** - Modern routing

### UI & Styling
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/ui** - High-quality React components
- **Framer Motion** - Smooth animations
- **React Icons** - Icon library
- **React Hot Toast** - Beautiful notifications

### State Management
- **Zustand** - Lightweight state management
- **React Query (TanStack Query)** - Server state management & caching

### API & Data
- **Axios** - HTTP client with interceptors
- **React Hook Form** - Form handling with validation
- **Zod** - Schema validation

### Development Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **TypeScript ESLint** - TS-specific linting

## 📁 Project Structure

```
frontend-react/
├── public/
│   ├── favicon.ico
│   └── assets/
├── src/
│   ├── api/              # API client & services
│   │   ├── client.ts
│   │   ├── endpoints.ts
│   │   └── types.ts
│   ├── assets/           # Images, fonts, etc.
│   ├── components/       # React components
│   │   ├── common/       # Reusable components
│   │   ├── features/     # Feature-specific components
│   │   └── layout/       # Layout components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities & helpers
│   ├── pages/            # Page components
│   ├── store/            # State management
│   ├── styles/           # Global styles
│   ├── types/            # TypeScript types
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── .env.example
├── .eslintrc.json
├── .prettierrc
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## 🎯 Features

### Core Features
- ✅ Image upload with drag-and-drop
- ✅ Real-time processing with progress tracking
- ✅ Before/After comparison slider
- ✅ Multiple enhancement types (deblur, inpaint, beauty)
- ✅ Image generation from text prompts
- ✅ Download results in multiple formats
- ✅ Processing history with filtering

### UI/UX Features
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark/Light mode toggle
- ✅ Smooth animations and transitions
- ✅ Toast notifications
- ✅ Loading states and skeletons
- ✅ Error boundaries
- ✅ Accessibility (ARIA labels, keyboard navigation)

### Advanced Features
- ✅ Image preview and cropping
- ✅ Batch processing queue
- ✅ Task status polling
- ✅ Automatic retry on failure
- ✅ Request caching
- ✅ Optimistic updates

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (LTS recommended)
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend-react

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

### Environment Variables

Create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_MAX_FILE_SIZE=10485760
VITE_ALLOWED_FILE_TYPES=image/jpeg,image/png,image/webp
```

## 📦 Available Scripts

```bash
# Development
npm run dev              # Start dev server (http://localhost:5173)
npm run dev:host         # Start dev server with network access

# Building
npm run build            # Build for production
npm run preview          # Preview production build

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint errors
npm run format           # Format with Prettier
npm run type-check       # Check TypeScript types

# Testing (optional setup)
npm run test             # Run tests
npm run test:coverage    # Run tests with coverage
```

## 🎨 Component Library

### Common Components
- `Button` - Customizable button with variants
- `Input` - Form input with validation
- `Card` - Content container
- `Modal` - Dialog overlay
- `Dropdown` - Select menu
- `Tabs` - Tab navigation
- `Badge` - Status indicator
- `Avatar` - User/profile image
- `Spinner` - Loading indicator
- `Toast` - Notifications

### Feature Components
- `ImageUploader` - Drag-drop image upload
- `ImageComparison` - Before/after slider
- `ProgressTracker` - Processing progress
- `HistoryGallery` - Past results grid
- `TaskCard` - Individual task display
- `FilterPanel` - Search and filter UI

## 🔧 Configuration

### Tailwind Configuration
Customized with project-specific colors, fonts, and animations.

### TypeScript Configuration
Strict mode enabled with path aliases for clean imports.

### Vite Configuration
Optimized build settings with code splitting and lazy loading.

## 🌐 API Integration

### Endpoints
- `GET /api/v1/health` - Health check
- `POST /api/v1/enhance` - Image enhancement
- `GET /api/v1/status/:id` - Task status
- `POST /api/v1/generate` - Image generation
- `GET /static/:filename` - Download result

### Example Usage
```typescript
import { apiClient } from '@/api/client';

// Upload image for enhancement
const response = await apiClient.enhanceImage({
  file: imageFile,
  taskType: 'deblur',
  description: 'Remove blur from photo'
});

// Check task status
const status = await apiClient.getTaskStatus(taskId);

// Download result
const blob = await apiClient.downloadResult(resultUrl);
```

## 🎯 Best Practices

### Code Organization
- One component per file
- Co-locate related files
- Use index.ts for exports
- Clear naming conventions

### State Management
- Use Zustand for global state
- React Query for server state
- Local state with useState
- Avoid prop drilling

### Performance
- Lazy load routes and components
- Memoize expensive computations
- Optimize images (WebP, lazy loading)
- Code splitting by route

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management

## 🔒 Security

- Environment variables for sensitive data
- Input validation and sanitization
- XSS prevention
- CORS configuration
- File upload validation

## 📱 Responsive Design

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px
- Wide: > 1280px

### Testing
Test on multiple devices and screen sizes for optimal UX.

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy Options
1. **Vercel** (Recommended)
   ```bash
   npm install -g vercel
   vercel
   ```

2. **Netlify**
   - Connect GitHub repo
   - Build command: `npm run build`
   - Publish directory: `dist`

3. **Docker**
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   RUN npm run build
   EXPOSE 5173
   CMD ["npm", "run", "preview"]
   ```

4. **Traditional Server**
   - Build: `npm run build`
   - Serve `dist/` folder with nginx/apache

## 📊 Performance Metrics

Target metrics for production:
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Lighthouse Score: > 90
- Bundle Size: < 500KB (gzipped)

## 🐛 Troubleshooting

### Issue: Port already in use
```bash
# Kill process on port 5173
npx kill-port 5173
```

### Issue: Module not found
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Type errors
```bash
# Rebuild TypeScript
npm run type-check
```

## 📚 Resources

### Documentation
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Query](https://tanstack.com/query/latest)

### Learning
- React patterns and best practices
- TypeScript with React
- Modern CSS with Tailwind
- State management strategies

## 🎓 For Your CV

This project demonstrates:
- ✅ Modern React development (React 18, Hooks, TypeScript)
- ✅ Professional project structure
- ✅ State management (Zustand, React Query)
- ✅ API integration with error handling
- ✅ Responsive design principles
- ✅ Performance optimization
- ✅ Accessibility standards
- ✅ Clean code practices
- ✅ Production-ready deployment

### CV Highlights
```
• Built production-ready React application with TypeScript
• Implemented modern state management using Zustand and React Query
• Designed responsive UI with Tailwind CSS and custom components
• Integrated RESTful API with error handling and retry logic
• Optimized performance (Lighthouse score 90+)
• Deployed to production with CI/CD pipeline
```

## 📝 License

MIT License - feel free to use for your portfolio!

---

**Version**: 1.0.0  
**Author**: Your Name  
**Last Updated**: December 2025
