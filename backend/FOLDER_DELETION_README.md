# Automatic Folder Deletion for Projects and Services

This document explains how the automatic folder deletion system works when projects or services are deleted from the database.

## Overview

When you delete a project or service from Django admin (or programmatically), the system automatically removes the entire media folder associated with that project/service, including all original images, optimized WebP versions, and thumbnails.

## How It Works

### 1. Signal-Based Deletion

The system uses Django signals to automatically trigger folder deletion:

- **`post_delete` signal**: Fires when a Project or Service is deleted
- **Signal handler**: Calls the appropriate deletion method from `ImageOptimizer`
- **Automatic cleanup**: Removes the entire folder structure

### 2. Folder Structure

Projects and services are organized in the following structure:

```
media/
├── projects/
│   ├── proj1/
│   │   ├── main_image.jpg
│   │   ├── album/
│   │   │   ├── album_image1.jpg
│   │   │   └── album_image2.jpg
│   │   └── webp/
│   │       ├── main_image.webp
│   │       ├── main_image_small.webp
│   │       ├── main_image_medium.webp
│   │       ├── main_image_large.webp
│   │       └── album/
│   │           ├── album_image1.webp
│   │           ├── album_image1_small.webp
│   │           ├── album_image1_medium.webp
│   │           └── album_image1_large.webp
│   └── proj2/
│       └── ...
└── services/
    ├── service1/
    │   ├── icon.jpg
    │   ├── album/
    │   └── webp/
    └── service2/
        └── ...
```

### 3. Deletion Process

When a project is deleted:

1. **Django triggers `post_delete` signal**
2. **Signal handler calls `ImageOptimizer.delete_project_folder(project)`**
3. **Method gets project folder path using `_get_project_folder(project)`**
4. **Entire folder is deleted using `shutil.rmtree()`**
5. **All files and subfolders are removed recursively**
6. **No orphaned files remain**

## Code Implementation

### Signal Registration

Signals are automatically registered in `portfolio/apps.py`:

```python
def ready(self):
    import portfolio.signals
```

### Delete Signal Handlers

Located in `portfolio/signals.py`:

```python
@receiver(post_delete, sender=Project)
def cleanup_project_images_on_delete(sender, instance, **kwargs):
    """Clean up entire project folder when a project is deleted"""
    try:
        success = ImageOptimizer.delete_project_folder(instance)
        if success:
            logger.info(f"Successfully deleted project folder for: {instance.title}")
        else:
            logger.warning(f"Project folder deletion failed or folder didn't exist for: {instance.title}")
    except Exception as e:
        logger.error(f"Error deleting project folder for {instance.title}: {str(e)}")
```

### Deletion Methods

Located in `portfolio/image_optimizer.py`:

```python
@classmethod
def delete_project_folder(cls, project):
    """Completely delete a project folder and all its contents"""
    try:
        project_folder = cls._get_project_folder(project)
        
        if os.path.exists(project_folder):
            import shutil
            shutil.rmtree(project_folder)
            logger.info(f"Completely deleted project folder: {project_folder}")
            return True
        else:
            logger.info(f"Project folder does not exist: {project_folder}")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting project folder for {project.title}: {str(e)}")
        return False
```

## Testing

### Run the Test Script

```bash
cd backend
python test_folder_deletion.py
```

This script will:
- Show current media folder structure
- Check if signals are properly registered
- Demonstrate how deletion would work
- Provide instructions for testing

### Manual Testing

1. **Start Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Access Django admin**:
   - Go to `http://localhost:8000/admin/`
   - Login with admin credentials

3. **Delete a project**:
   - Find a project in the Projects section
   - Click on it and select "Delete"
   - Confirm deletion

4. **Verify folder deletion**:
   - Check that the project folder is completely removed from `media/projects/`
   - Verify no orphaned files remain

## Benefits

- **Automatic cleanup**: No manual folder deletion required
- **Complete removal**: All files and subfolders are deleted
- **No orphaned files**: Prevents storage bloat
- **Consistent behavior**: Same deletion logic for all projects/services
- **Error handling**: Graceful fallback if deletion fails
- **Logging**: All operations are logged for debugging

## Troubleshooting

### Signals Not Working

If folder deletion is not working:

1. **Check signal registration**:
   ```bash
   python test_folder_deletion.py
   ```

2. **Verify apps.py configuration**:
   ```python
   def ready(self):
       import portfolio.signals
   ```

3. **Check Django logs** for error messages

### Permission Issues

If you get permission errors:

1. **Check file permissions** on media folder
2. **Ensure Django has write access** to media directory
3. **Check if files are locked** by other processes

### Partial Deletion

If only some files are deleted:

1. **Check Django logs** for error messages
2. **Verify disk space** is sufficient
3. **Check for file locks** or permissions

## Configuration

The folder deletion system is configured through:

- **`portfolio/signals.py`**: Signal handlers and deletion logic
- **`portfolio/image_optimizer.py`**: Deletion methods and folder utilities
- **`portfolio/apps.py`**: Signal registration
- **`portfolio/models.py`**: Model definitions and relationships

## Logging

All deletion operations are logged with appropriate log levels:

- **INFO**: Successful deletions
- **WARNING**: Deletion failures or missing folders
- **ERROR**: Critical errors during deletion

Check Django logs to monitor deletion operations and troubleshoot issues.
