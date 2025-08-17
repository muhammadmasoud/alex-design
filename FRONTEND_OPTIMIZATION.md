# Frontend Optimization Guide for Alex Design Portfolio

## Image Loading Optimizations

### 1. Update Image Components to Use Lazy Loading

Add the following to your image components in React:

```jsx
// For regular images
<img 
  src={imageUrl} 
  alt={altText}
  loading="lazy"
  style={{ 
    maxWidth: '100%', 
    height: 'auto',
    transition: 'opacity 0.3s ease'
  }}
  onLoad={(e) => e.target.style.opacity = 1}
  onError={(e) => {
    e.target.style.opacity = 0.5;
    e.target.src = '/placeholder.svg'; // fallback image
  }}
/>

// For gallery/portfolio images with skeleton loading
const ImageWithSkeleton = ({ src, alt, className }) => {
  const [loaded, setLoaded] = useState(false);
  
  return (
    <div className={`relative ${className}`}>
      {!loaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded" />
      )}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        className={`transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
        onLoad={() => setLoaded(true)}
        onError={(e) => {
          e.target.src = '/placeholder.svg';
          setLoaded(true);
        }}
      />
    </div>
  );
};
```

### 2. Add Skeleton Loaders

Create skeleton components for loading states:

```jsx
// SkeletonCard.jsx
export const SkeletonCard = () => (
  <div className="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
    <div className="h-48 bg-gray-200"></div>
    <div className="p-4">
      <div className="h-4 bg-gray-200 rounded mb-2"></div>
      <div className="h-3 bg-gray-200 rounded w-3/4"></div>
    </div>
  </div>
);

// Usage in your components
{loading ? (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
  </div>
) : (
  // Your actual content
)}
```

### 3. Implement Progressive Image Loading

```jsx
const ProgressiveImage = ({ src, alt, className }) => {
  const [currentSrc, setCurrentSrc] = useState('/placeholder.svg');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      setCurrentSrc(src);
      setLoading(false);
    };
    img.src = src;
  }, [src]);

  return (
    <div className={`relative ${className}`}>
      <img
        src={currentSrc}
        alt={alt}
        className={`transition-all duration-300 ${loading ? 'blur-sm' : 'blur-0'}`}
      />
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}
    </div>
  );
};
```

### 4. Optimize API Calls with Pagination

```jsx
// useInfiniteProjects.js
import { useState, useEffect, useCallback } from 'react';

export const useInfiniteProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);

  const loadProjects = useCallback(async (pageNum = 1, reset = false) => {
    if (loading) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/projects/?page=${pageNum}&page_size=12`);
      const data = await response.json();
      
      if (reset) {
        setProjects(data.results);
      } else {
        setProjects(prev => [...prev, ...data.results]);
      }
      
      setHasMore(!!data.next);
      setPage(pageNum);
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setLoading(false);
    }
  }, [loading]);

  const loadMore = () => {
    if (hasMore && !loading) {
      loadProjects(page + 1);
    }
  };

  useEffect(() => {
    loadProjects(1, true);
  }, []);

  return { projects, loading, hasMore, loadMore, refresh: () => loadProjects(1, true) };
};
```

### 5. Add Client-Side File Validation

```jsx
// fileUtils.js
export const validateImageFile = (file) => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  const maxSize = 25 * 1024 * 1024; // 25MB

  if (!validTypes.includes(file.type)) {
    throw new Error('Please select a valid image file (JPEG, PNG, GIF, WebP)');
  }

  if (file.size > maxSize) {
    throw new Error('File size must be less than 25MB');
  }

  return true;
};

// ImageUpload component
const ImageUpload = ({ onUpload, multiple = false }) => {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    
    try {
      // Validate each file
      files.forEach(validateImageFile);
      
      // Create previews
      if (!multiple && files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(files[0]);
      }

      setUploading(true);
      await onUpload(multiple ? files : files[0]);
    } catch (error) {
      alert(error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <input
        type="file"
        accept="image/*"
        multiple={multiple}
        onChange={handleFileSelect}
        disabled={uploading}
        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
      />
      
      {preview && (
        <img src={preview} alt="Preview" className="max-w-xs h-auto rounded" />
      )}
      
      {uploading && (
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          <span>Uploading...</span>
        </div>
      )}
    </div>
  );
};
```

### 6. Environment Configuration

Update your environment files:

```env
# .env.production
VITE_API_URL=http://52.47.162.66/api
VITE_MEDIA_URL=http://52.47.162.66/media
VITE_ENABLE_LAZY_LOADING=true
VITE_IMAGE_PLACEHOLDER=/placeholder.svg

# .env.development
VITE_API_URL=http://localhost:8000/api
VITE_MEDIA_URL=http://localhost:8000/media
VITE_ENABLE_LAZY_LOADING=true
VITE_IMAGE_PLACEHOLDER=/placeholder.svg
```

### 7. Build Optimization

Update your `vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-button'], // your UI libraries
        },
      },
    },
    target: 'esnext',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});
```

## Performance Best Practices

1. **Lazy Load Components**: Use React.lazy() for route-based code splitting
2. **Memoization**: Use React.memo, useMemo, and useCallback appropriately
3. **Virtual Scrolling**: For large lists of images, consider react-window
4. **Service Worker**: Add a service worker for caching static assets
5. **WebP Support**: Serve WebP images where supported

## Testing Performance

After implementing these optimizations:

1. Use Chrome DevTools Performance tab
2. Test with slow 3G network simulation
3. Use Lighthouse for performance audits
4. Monitor Core Web Vitals (LCP, FID, CLS)

## Deployment Notes

- Always run `npm run build` before deployment
- Enable gzip compression on your server
- Set appropriate cache headers
- Use a CDN for static assets if traffic grows
