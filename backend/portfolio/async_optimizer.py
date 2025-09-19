"""
Truly asynchronous image optimization system
Uses a simple file-based queue to avoid blocking HTTP responses
"""

import json
import os
import time
import threading
import logging
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from .image_optimizer import ImageOptimizer

logger = logging.getLogger(__name__)

class AsyncImageOptimizer:
    """
    Manages asynchronous image optimization using a simple file-based queue
    This prevents any database blocking during HTTP responses
    """
    
    QUEUE_DIR = Path(settings.BASE_DIR) / 'media' / '.optimization_queue'
    PROCESSING_DIR = Path(settings.BASE_DIR) / 'media' / '.optimization_processing'
    
    @classmethod
    def _ensure_dirs(cls):
        """Ensure queue directories exist"""
        cls.QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        cls.PROCESSING_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def queue_project_optimization(cls, project_id, operation_type='update'):
        """
        Queue a project for optimization without any blocking operations
        """
        try:
            cls._ensure_dirs()
            
            task = {
                'type': 'project',
                'project_id': project_id,
                'operation': operation_type,
                'queued_at': timezone.now().isoformat(),
                'priority': 'normal'
            }
            
            # Use timestamp + random for unique filename
            import uuid
            filename = f"project_{project_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}.json"
            filepath = cls.QUEUE_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(task, f)
            
            logger.info(f"Queued project optimization: {project_id} (file: {filename})")
            
            # Start processor if not running (non-blocking check)
            cls._start_processor_if_needed()
            
        except Exception as e:
            logger.error(f"Failed to queue project optimization for {project_id}: {e}")
    
    @classmethod
    def queue_file_cleanup(cls, model_type, model_id, old_file_path):
        """
        Queue file cleanup without any blocking operations
        """
        try:
            cls._ensure_dirs()
            
            task = {
                'type': 'cleanup',
                'model_type': model_type,
                'model_id': model_id,
                'old_file_path': old_file_path,
                'queued_at': timezone.now().isoformat(),
                'priority': 'low'
            }
            
            import uuid
            filename = f"cleanup_{model_type}_{model_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}.json"
            filepath = cls.QUEUE_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(task, f)
            
            logger.info(f"Queued file cleanup: {old_file_path} (file: {filename})")
            
            # Start processor if not running (non-blocking check)
            cls._start_processor_if_needed()
            
        except Exception as e:
            logger.error(f"Failed to queue file cleanup for {old_file_path}: {e}")

    @classmethod
    def queue_service_optimization(cls, service_id, operation_type='update'):
        """
        Queue a service for optimization without any blocking operations
        """
        try:
            cls._ensure_dirs()
            
            task = {
                'type': 'service',
                'service_id': service_id,
                'operation': operation_type,
                'queued_at': timezone.now().isoformat(),
                'priority': 'normal'
            }
            
            import uuid
            filename = f"service_{service_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}.json"
            filepath = cls.QUEUE_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(task, f)
            
            logger.info(f"Queued service optimization: {service_id} (file: {filename})")
            
            # Start processor if not running (non-blocking check)
            cls._start_processor_if_needed()
            
        except Exception as e:
            logger.error(f"Failed to queue service optimization for {service_id}: {e}")
    
    @classmethod
    def _start_processor_if_needed(cls):
        """
        Start the background processor if it's not already running
        Uses file-based locking to prevent multiple processors
        """
        try:
            lock_file = cls.PROCESSING_DIR / 'processor.lock'
            
            # Check if processor is already running
            if lock_file.exists():
                # Check if the process is still active
                try:
                    with open(lock_file, 'r') as f:
                        data = json.load(f)
                        pid = data.get('pid')
                        started = data.get('started')
                        
                    # If lock is older than 5 minutes, assume process died
                    if started and time.time() - started > 300:
                        logger.warning("Removing stale processor lock")
                        lock_file.unlink(missing_ok=True)
                    else:
                        # Processor is running
                        return
                except:
                    # Corrupted lock file, remove it
                    lock_file.unlink(missing_ok=True)
            
            # Start new processor
            thread = threading.Thread(target=cls._background_processor, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Error starting processor: {e}")
    
    @classmethod
    def _background_processor(cls):
        """
        Background processor that continuously processes the optimization queue
        """
        import os
        
        lock_file = cls.PROCESSING_DIR / 'processor.lock'
        
        try:
            # Create lock file
            with open(lock_file, 'w') as f:
                json.dump({
                    'pid': os.getpid(),
                    'started': time.time()
                }, f)
            
            logger.info("Background optimization processor started")
            
            while True:
                try:
                    # Process all files in queue
                    queue_files = list(cls.QUEUE_DIR.glob('*.json'))
                    
                    if not queue_files:
                        # No work to do, sleep and check again
                        time.sleep(2)
                        continue
                    
                    # Process oldest file first
                    queue_files.sort(key=lambda f: f.stat().st_mtime)
                    
                    for queue_file in queue_files:
                        try:
                            cls._process_task_file(queue_file)
                        except Exception as e:
                            logger.error(f"Error processing task {queue_file}: {e}")
                            # Move failed task to processing dir for debugging
                            try:
                                failed_file = cls.PROCESSING_DIR / f"failed_{queue_file.name}"
                                queue_file.rename(failed_file)
                            except:
                                pass
                
                except Exception as e:
                    logger.error(f"Error in background processor: {e}")
                    time.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Fatal error in background processor: {e}")
        finally:
            # Clean up lock file
            lock_file.unlink(missing_ok=True)
            logger.info("Background optimization processor stopped")
    
    @classmethod
    def _process_task_file(cls, task_file):
        """
        Process a single optimization task
        """
        # Move to processing dir first
        processing_file = cls.PROCESSING_DIR / task_file.name
        task_file.rename(processing_file)
        
        try:
            with open(processing_file, 'r') as f:
                task = json.load(f)
            
            start_time = time.time()
            
            if task['type'] == 'project':
                cls._optimize_project_task(task)
            elif task['type'] == 'service':
                cls._optimize_service_task(task)
            elif task['type'] == 'cleanup':
                cls._cleanup_task(task)
            else:
                logger.error(f"Unknown task type: {task['type']}")
                return
            
            elapsed = time.time() - start_time
            logger.info(f"Completed optimization task for {task['type']} {task.get('project_id', task.get('service_id'))} in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing task file {processing_file}: {e}")
            raise
        finally:
            # Clean up task file
            processing_file.unlink(missing_ok=True)
    
    @classmethod
    def _optimize_project_task(cls, task):
        """
        Optimize a project (runs in background thread)
        """
        from .models import Project
        
        project_id = task['project_id']
        
        try:
            project = Project.objects.get(id=project_id)
            ImageOptimizer.optimize_project_images(project)
            logger.info(f"Successfully optimized project: {project.title}")
        except Project.DoesNotExist:
            logger.warning(f"Project {project_id} not found for optimization")
        except Exception as e:
            logger.error(f"Failed to optimize project {project_id}: {e}")
    
    @classmethod
    def _cleanup_task(cls, task):
        """
        Clean up old files (runs in background thread)
        """
        old_file_path = task['old_file_path']
        model_type = task['model_type']
        model_id = task['model_id']
        
        try:
            from .image_optimizer import ImageOptimizer
            
            # Create a mock object with the file path for cleanup
            class MockFile:
                def __init__(self, path):
                    self.name = path
                    
            mock_file = MockFile(old_file_path)
            ImageOptimizer.delete_image_file(mock_file)
            
            logger.info(f"Successfully cleaned up old file: {old_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to clean up file {old_file_path}: {e}")

    @classmethod
    def _optimize_service_task(cls, task):
        """
        Optimize a service (runs in background thread)
        """
        from .models import Service
        
        service_id = task['service_id']
        
        try:
            service = Service.objects.get(id=service_id)
            ImageOptimizer.optimize_service_images(service)
            logger.info(f"Successfully optimized service: {service.name}")
        except Service.DoesNotExist:
            logger.warning(f"Service {service_id} not found for optimization")
        except Exception as e:
            logger.error(f"Failed to optimize service {service_id}: {e}")
    
    @classmethod
    def get_queue_status(cls):
        """
        Get current queue status for monitoring
        """
        cls._ensure_dirs()
        
        queued = len(list(cls.QUEUE_DIR.glob('*.json')))
        processing = len(list(cls.PROCESSING_DIR.glob('*.json')))
        
        lock_file = cls.PROCESSING_DIR / 'processor.lock'
        processor_running = lock_file.exists()
        
        return {
            'queued_tasks': queued,
            'processing_tasks': processing,
            'processor_running': processor_running
        }
