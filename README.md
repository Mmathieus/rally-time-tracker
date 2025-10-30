# 🏁 **Rally Time Tracker**

**A powerful CLI application for serious rally enthusiasts who want to track their stage times, monitor improvements, and maintain a complete performance history.**

> ⚠️ **Platform:** This installation guide is designed for **Windows**. If you're using macOS or Linux, you'll need to adapt the setup process accordingly.

---

## 🎯 **Overview**

Rally Time Tracker is a **terminal-based application** featuring:

- ⏱️ **Record and store stage times** across different rallies and stages
- 📈 **Monitor improvements** with automatic personal best comparisons
- 🎮 **Multi-database support** with dedicated storage for each rally game
- 🛠️ **Full database control** giving you complete power over your data and operations
- 💻 **Comprehensive command suite** providing an extensive set of commands for complete application control

The application uses **PostgreSQL** for data storing and provides an **intuitive command-line interface** with smart autocomplete support.

---

## 📌 **Prerequisites**

Before you begin, ensure you have the following installed:

| Software | Minimum Version |
|----------|----------------|
| **Python** | any currently supported version |
| **PostgreSQL** (including **psql**) | any currently supported version |

> **Note:** `psql` (PostgreSQL command-line client) should be included with PostgreSQL installation.

---

## 📦 **Installation**

### **Step 1:** Clone the repository
```bash
   git clone https://github.com/Mmathieus/rally-time-tracker.git
```

### **Step 2:** Navigate to the project directory
```bash
   cd rally-time-tracker
```

### **Step 3:** Install required Python packages
```bash
   pip install -r requirements.txt
```

### **Step 4:** Configure PostgreSQL authentication

   > ⚠️ **Before running the script:** If you set a custom password during PostgreSQL installation (other than `1234`), you **must** edit the script first. [See instructions below](#password-configuration).
   
   > ⚠️ **Important:** This script will **overwrite** existing `pgpass.conf` file at `%APPDATA%\postgresql\pgpass.conf`
``` bash
   .\setup-pgpass.ps1
```
   
   > 💡 **What does this do?** This script creates a `pgpass.conf` file so you won't be prompted for your database password every time the application connects to PostgreSQL.

---

<a id="password-configuration"></a>
### **🔐 Password Configuration**

**If you set a custom password** during PostgreSQL installation you need to update the script with your actual password:

1. Open `setup-pgpass.ps1` in any text editor
2. Locate **line 11** (the `$credentials` array)
3. Change the **last value** from `"1234"` to your password:
```powershell
   # Before
   @("localhost", "5432", "rallydb", "postgres", "1234"),
   
   # After (example with password "mypassword")
   @("localhost", "5432", "rallydb", "postgres", "mypassword"),
```

4. Save the file and run the script

---

### **🗄️ Additional Databases**

If you want to **use a different or add another database** simply add new entries to the `$credentials` array in `setup-pgpass.ps1` and run the script again.

> **Note:** Adding database(s) here only skips password prompts. To actually use multiple databases in the application, you must also add the database name to the `"available_databases"` list in `config.json` (explained in config details further below)
```powershell
   @("localhost", "5432", "wrc9db", "postgres", "mypassword"),
   @("localhost", "5432", "wrc10db", "postgres", "mypassword")
```

---

## 🚀 **Quick Start**

Once installation is complete, follow these steps to get started with application:

### **Step 1:** Launch the application
```bash
   python main.py
```

### **Step 2:** Create database and tables
```
   💬 create .
```

### **Step 3:** Display the dashboard
```
   💬 dashboard
```
*You should see database and both tables (main and history) created.*

### **Step 4:** Insert first stage time
```
   💬 insert first-rally first-stage first-car 3:33:333
```

### **Step 5:** View record
```
   💬 select .
```

### **Step 6:** Insert an improved stages time
```
   💬 insert first-rally first-stage first-car 3:30:000
```

### **Step 7:** Check improvement history
```
   💬 history .
```

### **Step 8:** Export data
```
   💬 export . gui
```
*This opens a file dialog to choose where to save your CSV files.*

### **Step 9:** Exit the application
```
   💬 end
```

> 💡 **Tip:** Type `help` to see available commands, or `help [command]` for detailed usage.

---

## ⚙️ **Configuration**

The application's behavior and response can be customized through `config.json`. Most settings are self-explanatory, but here are the key rules and considerations:

### **General Rules**
- **No empty values**: All settings must have a value (nothing can be left empty)
- **Data types**: Each setting must maintain its original data type (strings remain strings, numbers remain numbers, etc.)
- **Arrays (`[]`)**: Must contain at least one value
- **Configuration changes**: Any changes made to `config.json` will only take effect **after restarting the application**

### **Database Configuration**
- The `"database"` field specifies the database available at startup.
- The `"available_databases"` list contains all databases you can switch between and work with.

The `"database"` **must** be in the `"available_databases"` list.

**❌ Incorrect**
```json
"credentials": {
   "user": "postgres",
   "database": "rallydb"
},
"available_databases": ["wrc9db", "wrc10db"]
```

**✅ Correct**
```json
"credentials": {
   "user": "postgres",
   "database": "rallydb"
},
"available_databases": ["rallydb", "wrc9db", "wrc10db"]
```

Additional notes:
- Use **lowercase** for all database names (no capitals or uppercase)
- The application automatically detects duplicate database names

---

## 📋 **Usage Guidelines**

To ensure smooth operation and avoid common issues, please follow these guidelines:

### **Menu Selection**
- You don't need to match the exact capitalization shown in menus and prompts
- Simply type everything in **lowercase** and it will work correctly
- The application displays options with specific formatting, but accepts any case

### **Multi-word Arguments**
When inserting records, use **hyphens (`'-'`)** to connect words **instead of spaces**.

- `monte carlo` ❌
- `monte-carlo` ✅

### **Canceling Input Prompts**
If you're in the middle of an interactive prompt and want to abort the current command before completing it:

- Simply press **Enter** without typing anything (empty input)
- The application will cancel the current operation and return you to the main menu

> 💡 **Example:** If you run `delete main` and the app prompts for an ID, but you change your mind — just press Enter to abort.

---

## ⚡ **Automatic Features**

Understanding these automatic features will help you work with the application effectively:

### **Name Formatting**
Rally and stage names are **automatically formatted** during insertion:
- **First letter** is capitalized
- **Every letter after a hyphen** (`'-'`) is capitalized
- Custom formatting (like all-uppercase) is not preserved

**Example:**

| You Type | Stored As |
|----------|-----------|
| **kenya** | `Kenya` |
|**monte-carlo** | `Monte-Carlo` |
| **WALES** | `Wales` |
| **col-de-braus** | `Col-De-Braus` |

### **Config Path Structure**
The `config.json` contains `{database}` placeholder in import/export paths to enable **default import/export operations across multiple databases**.

**Import paths**
```json
"default_file_path": {
   "primary_table": "data/{database}/main.csv",
   "history_table": "data/{database}/history.csv"
}
```

**Export paths**
```json
"default_folder_path": {
   "primary_table": "data/{database}",
   "history_table": "data/{database}"
}
```

- The application **automatically replaces** `{database}` with the currently used database name
- Paths are **relative to the project root** by default - feel free to replace them with **absolute paths** for custom locations

---

## 📖 **Commands & Arguments**

The application provides a comprehensive command system with built-in help and flexible argument handling.

### **Getting Help**

**View all available commands:**
```
💬 help
```

**View specific command usage:**
```
💬 help [command]
```
This displays the command's syntax, including all available arguments and their order.

---

### **Understanding Command Syntax**

When you view help for a specific command (e.g., `import`), you'll see this:
```
╔═════════════════════════════════════════╗
║           📥 IMPORT ARGUMENTS           ║
╚═════════════════════════════════════════╝

import <table|all>.......................#1

import <table|all> [method]..............#2

import <table|all> [method] [override]...#3
```

#### **Argument Types**

| Symbol | Meaning | Example |
|--------|---------|---------|
| `<`...`>` | **Required** argument | `<table\|all>` |
| `[`...`]` | **Optional** argument | `[method]` / `[override]` |
| `\|` | Alternative option available | `<table\|database\|all>` |

#### **Argument Labels vs Actual Values**

> ⚠️ **Important:** Argument labels in help output are **descriptive placeholders**, not literal values.

**Example:** `<table|database|all>` means:
- You need to choose **one** option
- The **actual values** to choose from are:
   - `main` - from ***table.reference.primary_table***
   - `history` - from ***table.reference.history_table***
   - `db` - from ***database.reference***
   - `.` - from ***other_reference.everything***

   (These values are defined in `config.json`)

**Other arguments mapping:**

| Help Label | Config Location | Config Value(s) |
|----------------|-----------------------------------------------------|------------|
| `[time_order]` | ***commands.select.record_order.\****               | `[oldest, ...]`, `[newest, ...]` |
| `[preserve]`   | ***commands.refresh.data_handling.\****             | `[y, ...]`, `[n, ...]` |
| `[override]`   | ***commands.import.existing_data_options.\****      | `[y, ...]`, `[n, ...]` |
| `[method]`     | ***commands.import__export.location_selection.\**** | `gui`, `default` |


> 💡 **Tip:** Check `config.json` to see all available values for each argument. You can also customize these values to your preference.

---

### **Argument Rules**

#### **1. Argument Order Must Be Preserved**

Arguments must be provided in the **exact order** shown in the help text.

**Example:**

```
💬  help insert

    ╔═══════════════════════════════════════╗
    ║          ✏️ INSERT ARGUMENTS          ║
    ╚═══════════════════════════════════════╝

    insert.................................#0

    insert <rally> <stage> <car> <time>....#4
```

❌ **Incorrect**
```
insert f-rally f-stage 3:33:333 f-car    # time and car swapped
insert f-stage f-rally f-car 3:33:333    # rally and stage swapped
```

✅ **Correct**
```
insert first-rally first-stage first-car 3:33:333
```

#### **2. Cannot Skip Required Arguments**

You cannot provide a later argument without providing all the required arguments that come before it.

**Example:**

```
💬  help select

    ╔═══════════════════════════════════════════════════════╗
    ║                  🔍 SELECT ARGUMENTS                  ║
    ╚═══════════════════════════════════════════════════════╝

    select.................................................#0

    select [search_term|all]...............................#1

    select [search_term|all] [time_order]..................#2

    select [search_term|all] [time_order] [order_limit]....#3
```


❌ **Incorrect**
```
select latest 5    # missing search_term
select 5 latest    # arguments out of order
```

✅ **Correct:**
```
select . latest 5
```

#### **3. Interactive Prompts for Missing Arguments**

Some arguments, while marked as **optional** in the syntax, will trigger an **interactive prompt** if omitted.

**Example:**

```
💬  help delete

    ╔═══════════════════════════╗
    ║    🗑️ DELETE ARGUMENTS    ║
    ╚═══════════════════════════╝

    delete <table|all>.........#1

    delete <table|all> [id]....#2
```

If you run `delete main` without specifying an ID:
```
💬 delete main
◇ ID: |
```

The application will prompt you to provide the missing `[id]` argument interactively.

> 💡 This design allows flexibility: you can provide arguments upfront for quick operations, or let the application guide you interactively.

#### **4. Default Values from Config**

Certain optional arguments use **predefined defaults** from `config.json` when not explicitly specified.

| Command | Parameter | Config Setting | Default Value |
|---------|----------|----------------|---------------|
| `refresh` | `[preserve]` | ***command.refresh.keep_data_on_refresh*** | `true` |
| `import` | `[override]` | ***command.import.override_data_on_import*** | `false` |

These default settings make common tasks easier, but you can change them if needed.

---

## 🤝 **Contributing & Feedback**

Your feedback and contributions are valuable for improving Rally Time Tracker!

### **Have a Question?**
Ask anything in [Discussions](https://github.com/Mmathieus/rally-time-tracker/discussions) - whether it's about usage, features, or troubleshooting.

### **Found a Bug?**
Please report them via [Issues](https://github.com/Mmathieus/rally-time-tracker/issues).

### **Missing Information in README?**
Feel free to suggest improvements via [Issues](https://github.com/Mmathieus/rally-time-tracker/issues).

### **Want to Contribute?**
Contributions are welcome via pull requests for bug fixes, documentation improvements, or new features.

---

### Hope you find this application useful on your journey to perfect stage times.
