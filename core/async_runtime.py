"""
REAPER Async Runtime

This module implements async/concurrent execution for the Reaper language.
Uses threading for concurrent execution of breach blocks.
"""

import threading
import queue
import time
from typing import Any, Callable, List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, Future
from .reaper_error import ReaperRuntimeError


class AsyncTask:
    """Represents an async task."""
    
    def __init__(self, task_id: str, func: Callable, args: tuple = (), kwargs: dict = None):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.future: Optional[Future] = None
        self.result = None
        self.exception = None
        self.completed = False
    
    def execute(self, executor: ThreadPoolExecutor):
        """Execute the task in the executor."""
        self.future = executor.submit(self._run)
        return self.future
    
    def _run(self):
        """Run the task function."""
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.completed = True
            return self.result
        except Exception as e:
            self.exception = e
            self.completed = True
            raise
    
    def wait(self, timeout: Optional[float] = None) -> Any:
        """Wait for task to complete and return result."""
        if self.future:
            try:
                self.result = self.future.result(timeout=timeout)
                self.completed = True
                return self.result
            except Exception as e:
                self.exception = e
                self.completed = True
                raise
        return None
    
    def is_done(self) -> bool:
        """Check if task is complete."""
        if self.future:
            return self.future.done()
        return self.completed


class ReaperAsyncRuntime:
    """
    Async runtime for Reaper language.
    
    Manages concurrent execution of breach blocks using a thread pool.
    """
    
    def __init__(self, max_workers: int = 10):
        """
        Initialize async runtime.
        
        Args:
            max_workers: Maximum number of concurrent threads
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, AsyncTask] = {}
        self.task_counter = 0
        self.lock = threading.Lock()
    
    def submit(self, func: Callable, args: tuple = (), kwargs: dict = None) -> AsyncTask:
        """
        Submit an async task for execution.
        
        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            AsyncTask object
        """
        with self.lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
        
        task = AsyncTask(task_id, func, args, kwargs)
        task.execute(self.executor)
        
        with self.lock:
            self.tasks[task_id] = task
        
        return task
    
    def wait_all(self, tasks: List[AsyncTask], timeout: Optional[float] = None) -> List[Any]:
        """
        Wait for all tasks to complete.
        
        Args:
            tasks: List of AsyncTask objects
            timeout: Optional timeout in seconds
            
        Returns:
            List of results
        """
        results = []
        for task in tasks:
            try:
                result = task.wait(timeout=timeout)
                results.append(result)
            except Exception as e:
                results.append(None)
                # Store exception in task
                task.exception = e
        
        return results
    
    def wait_any(self, tasks: List[AsyncTask], timeout: Optional[float] = None) -> Optional[Any]:
        """
        Wait for any task to complete.
        
        Args:
            tasks: List of AsyncTask objects
            timeout: Optional timeout in seconds
            
        Returns:
            Result from first completed task, or None if timeout
        """
        start_time = time.time()
        
        while True:
            # Check if any task is done
            for task in tasks:
                if task.is_done():
                    return task.wait()
            
            # Check timeout
            if timeout and (time.time() - start_time) >= timeout:
                return None
            
            # Small sleep to avoid busy waiting
            time.sleep(0.01)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the async runtime.
        
        Args:
            wait: Whether to wait for pending tasks
        """
        self.executor.shutdown(wait=wait)
    
    def get_task(self, task_id: str) -> Optional[AsyncTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

