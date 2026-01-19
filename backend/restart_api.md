# Restart API Server

The backend API server needs to be restarted to pick up the latest changes.

## Steps to Restart

1. **Stop the current backend server:**
   - Find the terminal window running `python main.py`
   - Press `Ctrl+C` to stop it

2. **Restart the backend:**
   ```bash
   cd backend
   python main.py
   ```

3. **Verify it's working:**
   ```bash
   curl http://localhost:8000/api/health
   curl http://localhost:8000/api/stories?limit=5
   ```

The 404 error is because the server is running an old version of the code. After restart, the `/api/stories` endpoint will work correctly.
