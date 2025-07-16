# 🚗💨 WRC - 📊 Stage Times - 💾 Database
- ## 📝 Current and Historic records of your stage times

#
## This document provides instructions for setting up the program on your PC (Windows).

### 🔧 **Installation Requirements**

- #### 🐍 **`Python`** Use the latest version available for the best compatibility and features
- #### 🗃️ **`PostgreSQL`** Use the latest version...
- #### 📟 **`psql shell`** Included in PostgreSQL.
- #### 🖥️ **`Powershell`** Part of the Windows


#
### 🔧 **System Environment Variables (PATH)**

#### Make sure all 5 paths are added to your system's environment variables.
#### `...` represents your own path leading to following folders.
- ### 🐍 **Python**
    - #### `...\Python\Launcher\`
    - #### `...\Python\Python312\`
    - #### `...\Python\Python312\Scripts\`
    #### `Python312` may vary depending on your installed version
- ### 🗃️ **PostgreSQL**
    - #### `...\PostgreSQL\17\bin\`
    - #### `...\PostgreSQL\17\scripts\`
    #### `17` may vary depending on your installed version


#
### 🔧 **Add function 'rally' (optional)**

#### You will be able to run the program from anywhere in the terminal.
#### **For Windows using Powershell:**
- #### Create:
```powershell
C:\Users\<user>\Documents\Powershell\Microsoft.PowerShell_profile.ps1
```
- #### With following content:
```powershell
function rally {
    Set-Location -Path "...\RallyDatabase"
    python -u code/main.py
}
```
- #### `-Path` depends on your RallyDatabase folder location
#### You can start the program just by typing `rally` in terminal


#
### 🔧 **Add pgpass.conf (optional)**

#### You will be able to access database via `psql terminal` without typing password.
#### **File location for Windows:**
- #### `C:\Users\<user>\AppData\Roaming\postgresql\pgpass.conf`
- #### You might need to show hidden folders to access `AppData\`.
- #### If `postgresql\` doesn't exist, create it manually.

- #### **pgpass.conf:**
    ```cmd
    hostname:port:database:username:password
- #### **pgpass.conf Example:**
    ```cmd
    localhost:5432:Smiths:Brad:angelina
