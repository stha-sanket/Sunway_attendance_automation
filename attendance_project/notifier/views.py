# notifier/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .tasks import process_and_send_emails # Import the function
import threading # Import threading

def index(request):
    """Displays the main page with the button."""
    return render(request, 'notifier/index.html')

def run_email_task_thread():
    """Target function for the thread."""
    # This function runs in a separate thread
    # Be careful with Django model access or state changes here
    # For this specific task (external APIs), it's generally okay.
    print("Background thread started for sending emails...")
    results = process_and_send_emails()
    print(f"Background thread finished. Results: {results}")
    # Note: You cannot directly use Django messages framework from a background thread
    # You would need a more complex mechanism (like websockets, polling, or storing results in DB/cache)
    # to notify the user upon completion in real-time.

def trigger_email_process(request):
    """Starts the email sending process in a background thread."""
    if request.method == 'POST':
        try:
            # Start the email sending process in a background thread
            thread = threading.Thread(target=run_email_task_thread, daemon=True)
            thread.start()
            messages.success(request, 'Email sending process started in the background. Check server logs for progress.')
        except Exception as e:
            messages.error(request, f'Failed to start email process: {e}')
        return redirect('notifier:index') # Redirect back to index page
    else:
        # If accessed via GET, just redirect to index
        return redirect('notifier:index')