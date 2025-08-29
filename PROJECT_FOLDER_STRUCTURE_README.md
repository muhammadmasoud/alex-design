# Project Folder Structure Implementation

This document describes the new automatic project folder structure that has been implemented in your portfolio website.

## Overview

The system now automatically creates project-specific folders when you add new projects, organizing images in a clean and structured way:

```
media/
├── projects/
│   ├── project_1/           # Project with ID 1
│   │   ├── main_image.webp  # Main project image
│   │   ├── thumbnails/      # Optimized thumbnails
│   │   │   ├── main_image_xs.webp
│   │   │   ├── main_image_sm.webp
│   │   │   └── main_image_md.webp
│   │   └── album/           # Project album images
│   │       ├── album_img1.webp
│   │       ├── album_img2.webp
│   │       └── thumbnails/  # Album image thumbnails
│   │           ├── album_img1_xs.webp
│   │           ├── album_img1_sm.webp
│   │           └── album_img1_md.webp
│   ├── project_2/           # Project with ID 2
│   │   ├── main_image.webp
│   │   ├── thumbnails/
│   │   └── album/
│   └── project_3/           # Project with ID 3
│       ├── main_image.webp
│       ├── thumbnails/
│       └── album/
└── services/
    └── ... (existing structure)
```

## How It Works

### 1. Automatic Folder Creation

When you create a new project (either through Django admin or the frontend dashboard):

1. **Project is saved** to the database first
2. **Folders are created** automatically:
   - `media/projects/project_X/` (where X is the project ID)
   - `media/projects/project_X/album/`
3. **Images are uploaded** to the appropriate folders
4. **Thumbnails are generated** in `thumbnails/` subfolders

### 2. Image Organization

- **Main Project Image**: Stored in `media/projects/project_X/`
- **Album Images**: Stored in `media/projects/project_X/album/`
- **Thumbnails**: Automatically generated in `thumbnails/` subfolders

### 3. Automatic Optimization

- All images are automatically converted to WebP format
- Multiple thumbnail sizes are generated for responsive design
- Original files are cleaned up after optimization
- Image paths are automatically updated in the database

## Usage

### Creating Projects via Django Admin

1. Go to Django Admin → Projects → Add Project
2. Fill in project details and upload images
3. Save the project
4. Folders are created automatically

### Creating Projects via Frontend Dashboard

1. Go to Admin Dashboard → Project Management
2. Click "Add Project"
3. Fill in project details and upload images
4. Click "Create Project"
5. Folders are created automatically

### Adding Album Images

1. **Via Django Admin**: Use the inline ProjectImage forms
2. **Via Frontend**: Upload multiple images in the album section
3. **Via API**: Use the bulk upload endpoint

## Migration from Old Structure

If you have existing projects with the old folder structure, you can migrate them using the provided management command:

```bash
# First, run a dry-run to see what would be changed
python manage.py migrate_to_project_folders --dry-run

# Then run the actual migration
python manage.py migrate_to_project_folders
```

This will:
- Create new project-specific folders
- Move existing images to the new structure
- Update database records with new paths
- Clean up old files

## Testing

To test the new folder structure, you can run the test script:

```bash
cd backend
python test_project_folders.py
```

This will:
- Create a test project
- Upload test images
- Verify folder creation
- Clean up test data

## Benefits

### 1. **Better Organization**
- Each project has its own folder
- Clear separation between main images and album images
- Easy to locate and manage project assets

### 2. **Improved Performance**
- Automatic WebP conversion
- Multiple thumbnail sizes for responsive design
- Optimized image delivery

### 3. **Easier Maintenance**
- Clear folder structure
- Automatic cleanup of old files
- Easy to backup specific projects

### 4. **Scalability**
- No more cluttered media folder
- Easy to add new projects
- Better file management

## Technical Details

### Models Updated

- `Project`: Added folder creation and path update methods
- `ProjectImage`: Updated to handle new folder structure
- `EnhancedImageOptimizer`: Updated to work with new paths

### Signals Added

- `create_project_folders_signal`: Creates folders after project creation
- `create_album_folders_signal`: Ensures album folders exist

### Upload Paths

- **Main Images**: `projects/project_X/filename`
- **Album Images**: `projects/project_X/album/filename`
- **Thumbnails**: `projects/project_X/thumbnails/filename` or `projects/project_X/album/thumbnails/filename`

## Troubleshooting

### Common Issues

1. **Folders not created**: Check if the project was saved successfully
2. **Images not moving**: Verify file permissions and storage settings
3. **Thumbnails not generating**: Check image optimization settings

### Debugging

- Check Django logs for error messages
- Verify folder permissions in the media directory
- Use the test script to verify functionality

## Future Enhancements

- **Automatic cleanup** of empty project folders
- **Backup/restore** functionality for individual projects
- **Image versioning** and rollback capabilities
- **Bulk operations** for multiple projects

## Support

If you encounter any issues:

1. Check the Django logs for error messages
2. Verify the folder structure manually
3. Run the test script to identify problems
4. Check file permissions in the media directory

The system is designed to be robust and handle edge cases gracefully, but if you need assistance, the test script and management command should help identify and resolve most issues.
