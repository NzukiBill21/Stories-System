# Use MySQL Without Opening phpMyAdmin

If **MySQL stops as soon as you click "Admin"** in XAMPP, you can set up and use the database from the command line instead. Do **not** open phpMyAdmin for this project.

---

## Why clicking Admin can stop MySQL

When you click "Admin", XAMPP opens phpMyAdmin in your browser. phpMyAdmin then connects to MySQL and runs several queries (list databases, tables, etc.). If MySQL is unstable or the data is corrupted, that first load can trigger a crash and MySQL stops. Using the command-line client avoids that.

---

## Setup (one-time)

### 1. Start MySQL only

- Open **XAMPP Control Panel**.
- Click **Start** next to **MySQL**.
- **Do not click "Admin"**. Leave the panel open so MySQL keeps running.

### 2. Create the database and tables

**Option A – Batch script (easiest)**

1. Open File Explorer and go to:  
   `C:\xampp\htdocs\Stories-System\backend`
2. Double‑click **`setup_database.bat`**.
3. If it asks for a password, press Enter (XAMPP default is no password).  
   If your root user has a password, use Option B instead.

**Option B – Command Prompt**

1. Open **Command Prompt** (cmd).
2. Run:

   ```bat
   c:\xampp\mysql\bin\mysql.exe -u root < c:\xampp\htdocs\Stories-System\backend\schema.sql
   ```

   If MySQL root has a password:

   ```bat
   c:\xampp\mysql\bin\mysql.exe -u root -p < c:\xampp\htdocs\Stories-System\backend\schema.sql
   ```
   (Enter the password when prompted.)

**Option C – Python**

From the project backend folder:

```bat
cd c:\xampp\htdocs\Stories-System\backend
python init_db.py
```

(This creates tables and adds sample sources; it needs MySQL running and will connect from Python.)

### 3. Run the app

- Start the backend: `cd backend` then `python main.py`.
- Open the dashboard at: `http://localhost:5173`.

You do **not** need to open phpMyAdmin for the Story Intelligence app to work.

---

## If you need to inspect the database later

- Use **command-line MySQL**:

  ```bat
  c:\xampp\mysql\bin\mysql.exe -u root
  ```

  Then:

  ```sql
  USE story_intelligence;
  SHOW TABLES;
  SELECT COUNT(*) FROM stories;
  ```

- Or install a desktop client (e.g. **HeidiSQL**, **MySQL Workbench**) and connect to `localhost`, user `root`, database `story_intelligence`. Those use a single connection and often work when phpMyAdmin’s many queries cause MySQL to stop.

---

## Fixing “Admin” stopping MySQL (optional)

If you want phpMyAdmin to work again:

1. **Reset MySQL data** (see main README): back up `C:\xampp\mysql\data`, then replace it with a copy of `C:\xampp\mysql\backup` renamed to `data`. This wipes all databases and gives you a clean MySQL; then run `setup_database.bat` or `schema.sql` again.
2. **Check the error log** right after MySQL stops:  
   XAMPP → MySQL → **Logs** → **mysql_error.log** → scroll to the **bottom** and look for `[ERROR]` or `Aborting`. That message will say why it crashed (e.g. corruption, port conflict).

Until then, use the steps above and avoid clicking "Admin"; the app will work with the command-line setup.
