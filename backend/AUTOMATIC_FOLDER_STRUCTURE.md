# Automatic Folder Structure for Projects

This document explains how the new automatic folder structure system works for projects in your portfolio application.

## 🎯 What Happens Automatically

When you create a new project (either through Django admin or the frontend dashboard), the system automatically:

1. **Creates a project folder** based on the project title
2. **Creates an album subfolder** for storing album images
3. **Organizes images** in the correct locations
4. **Cleans up** when projects are deleted

## 📁 Folder Structure

```
media/projects/
├── modern-architecture-project/          # Project folder (slugified title)
│   ├── main_image.webp                  # Main project image
│   ├── thumbnails/                      # Generated thumbnails
│   │   ├── main_image_xs.webp          # 150x150px
│   │   ├── main_image_sm.webp          # 300x300px
│   │   ├── main_image_md.webp          # 600x600px
│   │   ├── main_image_lg.webp          # 800x800px
│   │   ├── main_image_xl.webp          # 1200x1200px
│   │   └── main_image_full.webp        # 1920x1080px
│   └── album/                           # Album images subfolder
│       ├── album_image_1.webp          # Album image 1
│       ├── album_image_2.webp          # Album image 2
│       └── thumbnails/                 # Album image thumbnails
│           ├── album_image_1_xs.webp
│           ├── album_image_1_sm.webp
│           └── ...
├── another-project/                     # Another project folder
│   ├── main_image.webp
│   ├── thumbnails/
│   └── album/
└── ...
```

## 🔧 How It Works

### 1. Project Creation
- **Trigger**: When a `Project` model is saved for the first time
- **Action**: Calls `_create_project_folders()` method
- **Result**: Creates both project and album folders

### 2. Image Upload
- **Main Image**: Stored directly in `media/projects/{project_name}/`
- **Album Images**: Stored in `media/projects/{project_name}/album/`
- **Thumbnails**: Generated automatically in `thumbnails/` subfolders

### 3. Automatic Cleanup
- **On Project Delete**: Entire project folder is removed
- **On Image Update**: Old images are deleted before new ones are saved
- **On ProjectImage Delete**: Individual album images are removed

## 📝 Code Implementation

### Models
- **Project Model**: Has `_create_project_folders()` method
- **ProjectImage Model**: Has `_ensure_album_folder_exists()` method
- **Upload Paths**: Automatically generate correct folder structure

### Signals
- **pre_save**: Ensures folders exist before saving
- **post_delete**: Cleans up folders when models are deleted

### Image Optimization
- **WebP Conversion**: All images are converted to WebP format
- **Thumbnail Generation**: Multiple sizes are created automatically
- **Storage Management**: Original files are cleaned up after optimization

## 🚀 Usage Examples

### Creating a Project via Django Admin
1. Go to Django admin
2. Create a new Project
3. Set title (e.g., "Modern Architecture Project")
4. Upload main image
5. Save the project
6. **Result**: Folders are created automatically

### Creating a Project via Frontend Dashboard
1. Use the admin dashboard in your frontend
2. Fill in project details
3. Upload images
4. **Result**: Folders are created automatically

### Adding Album Images
1. Go to project detail page
2. Upload album images
3. **Result**: Images are stored in the correct album folder

## 🧪 Testing

### Test Command
```bash
cd backend
python manage.py test_folder_structure --project-title "Test Project"
```

### Test Script
```bash
cd backend
python test_folder_creation.py
```

## ⚠️ Important Notes

1. **Folder Names**: Project folders use slugified titles (spaces become hyphens, special characters removed)
2. **Permissions**: Ensure the `media/` directory has write permissions
3. **Cleanup**: Folders are automatically deleted when projects are removed
4. **Backup**: Always backup your media folder before testing

## 🔍 Troubleshooting

### Folders Not Created
- Check if `MEDIA_ROOT` is properly configured
- Verify file permissions on the media directory
- Check Django logs for error messages

### Images Not Saving
- Ensure the project has a title before saving
- Check if the image validation passes
- Verify the upload paths are correct

### Cleanup Issues
- Check if the project title exists when deleting
- Verify file permissions for deletion
- Check Django logs for cleanup errors

## 📚 Related Files

- `portfolio/models.py` - Model definitions and folder creation methods
- `portfolio/signals.py` - Automatic folder creation signals
- `portfolio/enhanced_image_optimizer.py` - Image optimization and thumbnail generation
- `portfolio/management/commands/test_folder_structure.py` - Testing command
- `test_folder_creation.py` - Test script

## 🎉 Benefits

1. **Automatic Organization**: No manual folder management needed
2. **Clean Structure**: Each project has its own organized space
3. **Easy Cleanup**: Deleting projects removes all related files
4. **Scalable**: Works with any number of projects and images
5. **Consistent**: Same structure for all projects
6. **Maintainable**: Clear separation of concerns
