# LUKHΛS Website Deployment Guide

## 🚀 Quick Deployment (Recommended)

### Option 1: Upload Production Files
1. Navigate to the `dist/` folder in this package
2. Upload ALL contents of the `dist/` folder to your web server's public directory
3. Your website will be live immediately!

**Important**: Upload the CONTENTS of the `dist/` folder, not the folder itself.

### Option 2: Use a Static Hosting Service

#### Netlify (Free)
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop the `dist/` folder onto their deployment area
3. Get instant HTTPS URL

#### Vercel (Free)
1. Go to [vercel.com](https://vercel.com)
2. Import the project or drag the `dist/` folder
3. Get instant deployment

#### GitHub Pages
1. Create a new repository on GitHub
2. Upload the contents of `dist/` folder
3. Enable GitHub Pages in repository settings

## 🛠 Development Setup (For Modifications)

If you want to modify the website:

1. **Install Node.js** (version 18 or higher)
2. **Install dependencies**:
   ```bash
   pnpm install
   # or
   npm install
   ```
3. **Start development server**:
   ```bash
   pnpm run dev
   # or
   npm run dev
   ```
4. **Build for production**:
   ```bash
   pnpm run build
   # or
   npm run build
   ```

## 🌐 Domain Configuration

### For lukhas.eu domain:
1. Point your domain's DNS to your hosting provider
2. Upload the `dist/` folder contents to your server
3. Configure HTTPS (most hosting providers do this automatically)

### DNS Settings:
- **A Record**: Point to your server's IP address
- **CNAME**: Point www.lukhas.eu to lukhas.eu

## 📁 File Structure

```
dist/
├── index.html          # Main HTML file
├── assets/
│   ├── index-[hash].css # Compiled CSS
│   ├── index-[hash].js  # Compiled JavaScript
│   └── [images]         # Optimized images
└── journey-images/      # Geographic journey images
```

## ⚡ Performance Tips

- The website is already optimized for production
- Images are compressed and optimized
- CSS and JavaScript are minified
- All animations are hardware-accelerated

## 🔧 Troubleshooting

### Website not loading?
- Check that you uploaded the CONTENTS of `dist/`, not the folder itself
- Ensure `index.html` is in the root directory of your web server

### Images not showing?
- Verify that the `journey-images/` folder was uploaded correctly
- Check that your server supports the image formats (WebP, JPG, PNG)

### Animations not working?
- Ensure JavaScript is enabled in the browser
- Check browser console for any errors

## 📞 Support

The website includes:
- ✅ Responsive design (mobile & desktop)
- ✅ Cross-browser compatibility
- ✅ SEO optimization
- ✅ Performance optimization
- ✅ Accessibility features

---

Your sophisticated LUKHΛS website is ready for deployment! 🎉
