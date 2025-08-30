# CDN Configuration for Alex Design Portfolio

## Recommended CDN Setup (Choose One)

### Option 1: AWS CloudFront (Recommended)
```javascript
// CloudFront Distribution Settings
{
  "Origins": [
    {
      "DomainName": "your-lightsail-ip",
      "Id": "alex-design-origin",
      "CustomOriginConfig": {
        "HTTPPort": 80,
        "OriginProtocolPolicy": "http-only"
      }
    }
  ],
  "DefaultCacheBehavior": {
    "TargetOriginId": "alex-design-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "optimized-for-images",
    "TTL": {
      "DefaultTTL": 86400,  // 1 day
      "MaxTTL": 31536000    // 1 year
    }
  },
  "CacheBehaviors": [
    {
      "PathPattern": "/media/*",
      "TTL": {
        "DefaultTTL": 2592000,  // 30 days
        "MaxTTL": 31536000      // 1 year
      },
      "Compress": true
    },
    {
      "PathPattern": "/static/*",
      "TTL": {
        "DefaultTTL": 31536000,  // 1 year
        "MaxTTL": 31536000       // 1 year
      },
      "Compress": true
    }
  ]
}
```

### Option 2: Cloudflare (Free Tier Available)
```nginx
# Add to your domain's DNS:
# Type: CNAME
# Name: cdn
# Content: your-lightsail-domain.com
# Proxy status: Proxied (orange cloud)

# Page Rules:
# 1. Rule: *.your-domain.com/media/*
#    Settings: Cache Level: Cache Everything, Edge Cache TTL: 1 month
# 
# 2. Rule: *.your-domain.com/static/*
#    Settings: Cache Level: Cache Everything, Edge Cache TTL: 1 year
```

### Option 3: Simple S3 + CloudFront for Media Only
```bash
# Upload media files to S3
aws s3 sync /home/ubuntu/alex-design/backend/media/ s3://alex-design-media/ --cache-control "max-age=2592000"

# Update Django settings
# MEDIA_URL = 'https://your-cloudfront-domain.com/'
```

## Implementation Steps

### 1. For CloudFront:
1. Create CloudFront distribution
2. Point origin to your Lightsail instance
3. Update `MEDIA_URL` in Django settings to CloudFront domain
4. Configure cache behaviors for `/media/` and `/static/`

### 2. For Cloudflare:
1. Add your domain to Cloudflare
2. Update DNS to point to Cloudflare nameservers  
3. Configure page rules for caching
4. Enable "Speed" optimizations in dashboard

### 3. Verification:
```bash
# Test cache headers
curl -I https://your-cdn-domain.com/media/projects/test-image.webp

# Should return:
# Cache-Control: max-age=2592000
# CF-Cache-Status: HIT (if using Cloudflare)
```

## Benefits:
- **50-80% faster image loading** globally
- **Reduced server bandwidth** costs
- **Better SEO scores** due to faster loading
- **Automatic compression** and optimization
- **DDoS protection** (Cloudflare)
