# MySQL Keeps Closing / Stopping Itself – Fix

When XAMPP’s MySQL (MariaDB) starts and then stops by itself, the data directory is often corrupted or in a bad state. Resetting it usually fixes the problem.

---

## Option 1: Reset using the script (recommended)

1. **Close XAMPP Control Panel** completely (so MySQL is not running).
2. In File Explorer go to:  
   `C:\xampp\htdocs\Stories-System\backend`
3. **Right‑click `reset_mysql_data.bat`** → **Run as administrator**.
4. When prompted, type **YES** and press Enter.
5. When it finishes:
   - Open XAMPP and **Start** MySQL (do **not** click Admin).
   - Double‑click **`setup_database.bat`** to create the `story_intelligence` database and tables.
   - Run the app: `python main.py`, then open http://localhost:5173

**Warning:** This deletes all existing MySQL databases and replaces them with a clean copy. You will need to run `setup_database.bat` again to recreate `story_intelligence`.

---

## Option 2: Reset manually

1. **Close XAMPP** (MySQL must be stopped).
2. Open File Explorer and go to: **`C:\xampp\mysql`**
3. **Rename** the folder **`data`** to **`data_old`**.
4. **Copy** the folder **`backup`** and **rename the copy** to **`data`**  
   (so you have `C:\xampp\mysql\data` with the contents of `backup`).
5. Open XAMPP, **Start** MySQL (do not click Admin).
6. Run **`setup_database.bat`** from `backend` to create `story_intelligence` and tables.
7. Start the app: `cd backend` then `python main.py`.

---

## After reset: avoid MySQL stopping again

- **Do not click “Admin”** in XAMPP for MySQL. Use the command line or `setup_database.bat` instead.
- To inspect the database, use:
  - Command line: `c:\xampp\mysql\bin\mysql.exe -u root`
  - Or a desktop client (e.g. HeidiSQL, MySQL Workbench) instead of phpMyAdmin.

If MySQL still stops after a reset, check the **last lines** of  
`C:\xampp\mysql\data\mysql_error.log` (or the `.err` file in `data`) for `[ERROR]` or `Aborting` and use that message to troubleshoot further.
