# Fix "MySQL shutdown unexpectedly" – Do this

Your log says:

- **Table 'global_priv' is marked as crashed** and repair failed  
- **Database page corruption** in system tables  

So the MySQL **data directory is corrupted**. You need to replace it with a clean copy.

---

## Steps (about 2 minutes)

### 1. Close XAMPP
- Quit XAMPP Control Panel completely so MySQL is not running.

### 2. Run the reset script as Administrator
- Open File Explorer → go to: **`C:\xampp\htdocs\Stories-System\backend`**
- **Right‑click `reset_mysql_data.bat`** → **Run as administrator**
- When it asks, type **YES** and press Enter  
- Wait until it says "Done. Data folder is now a clean copy."

### 3. Start MySQL again (do not click Admin)
- Open XAMPP Control Panel
- Click **Start** next to **MySQL**  
- Leave it running; **do not click "Admin"**.

### 4. Create the app database
- In the same `backend` folder, double‑click **`setup_database.bat`**
- Press any key when it asks; wait until it finishes.

### 5. Run the app
```bat
cd c:\xampp\htdocs\Stories-System\backend
python main.py
```
Then open **http://localhost:5173** in your browser.

---

**Note:** Step 2 removes all current MySQL databases and replaces them with a clean set. Your app database is recreated in step 4. After this, MySQL should start and stay running.
