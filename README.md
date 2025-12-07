<div align="center">
  <img src="assets/program/logo.png" alt="Retail Operations Suite Logo" width="150"/>
  <h1>Retail Operations Suite</h1>
  <p>
    A comprehensive desktop application for managing retail price tags, inventory status, and administrative tasks, built with PyQt6 and Firebase.
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.14+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Qt-6-green.svg" alt="Qt6">
    <img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="License">
  </p>
</div>

---

The **Retail Operations Suite** is a powerful, real-time tool designed to streamline in-store operations for retail environments. It provides a robust interface for generating dynamic price tags, managing product data, and offers a suite of administrative tools for comprehensive oversight.

> [!IMPORTANT]
> **Note on Release Versions:** The pre-compiled installers available in the GitHub Releases section are configured specifically for **pcshop.ge** (the author's workplace). They utilize specific Firebase credentials and hardcoded assets (logos).
>
> **To use this software for your own business**, you must clone the repository, set up your own Firebase project, and replace the specific brand assets in the `assets/` folder with your own.

## ✨ Key Features

*   **🏷️ Dynamic Price Tag Generation**:
    *   **Versatile Layouts**: Create price tags in multiple customizable sizes, including standard A4 grids, compact "accessory-style" tags, and a specialized "Keyboard" layout.
    *   **Rich Theming Engine**: Choose from various themes like **"Winter"** (snow effects ❄️), **"Back to School"** (with educational icons 🎒), and **"Black Friday"** (caution tape styling 🚧).
    *   **Modern Brand Designs**: Automatically applies specific, high-quality 3D-style branding designs for major brands (e.g., Asus, Logitech, Razer) based on the product name.
    *   **Dual-Language Support**: Auto-generates paired English and Georgian tags side-by-side.
    *   **Automatic QR Codes**: Automatically scrapes and generates QR codes linking to the product page. *(Note: Auto-scraping is currently specific to pcshop.ge; for other environments, the software will prompt you to manually enter a URL for each item).*

*   **🖨️ Advanced Print Queue**:
    *   A powerful batch-processing tool available to all users.
    *   **Persistent Queue**: Items added to the queue remain saved until printed or removed, even if the application is closed.
    *   **Excel Import**: Bulk import lists of SKUs directly from Excel files to populate the queue instantly.
    *   **Saved Lists**: Create and save named lists of items (e.g., "Front Window Display", "Weekly Sale") for quick reloading and re-printing in the future.
    *   **Batch Generation**: Generate and print PDF grids for dozens of items in a single click.

*   **🎨 Ultimate Customization & Control**:
    *   **Live Layout Modularity**: Every section of the price tag (Title, Price, Specs, Logo, SKU) can be individually scaled using precision sliders in the **Layout Settings**.
    *   **Real-Time Data Editing**: Edit raw product data (Name, Price, Specifications) directly within the program to generate tags with updated info immediately, without waiting for backend database updates.
    *   **Live Preview**: See exactly how the price tag will look as you edit details, switch themes, or adjust layout sliders.
    *   **Visual Verification**: Automatically fetches and displays the product image to ensure the operator is working on the correct item. *(Note: Automatic fetching is currently hardcoded for pcshop.ge; support for general web image fetching is planned for future updates).*
    *   **Recent History**: Keeps a local history of recently viewed and generated items for instant access.

*   **📦 Logistics & Inventory Management**:
    *   **Dedicated Logistics Tab**: A specialized interface for warehouse staff to instantly check item locations (On Display vs. In Storage) across specific branches via SKU scanning.
    *   **Stock Export**: Capabilities to filter and export stock data for specific categories and branches to Excel.
    *   **Quick Stock Checker**: Instantly view inventory levels for an item across all branches in a single dialog.

*   **⚡ Real-Time Operations**:
    *   **Firebase Integration**: Real-time synchronization of product data, display statuses, and user profiles.
    *   **Auto-Update System**: Integrated mechanism that checks GitHub for releases and automatically downloads/installs updates.

*   **🏪 Display Management**:
    *   **Display Tracker**: Track which items are currently on display in each branch and how long they have been there.
    *   **Replacements Manager**: A tool to handle item returns, automatically suggesting in-stock replacements from the same category to fill the empty spot on the shelf.

## 🛠️ Admin Tools

Admins have access to a suite of powerful tools to manage the application and data:

*   **🎨 Data & Template Customization**:
    *   **Template Manager**: Define product categories and specification templates to standardize new item registration.
    *   **Custom Size Manager**: Define new custom print sizes with specific dimensions and constraints.
    *   **Column Mapping Manager**: Map raw database columns to user-friendly display names or hide internal technical fields.

*   **👁️ System Oversight**:
    *   **Admin Dashboard**: At-a-glance statistics for display counts and a powerful "Low Stock" monitoring table with filtering.
    *   **User Management**: Promote users to Admin roles and oversee accounts.
    *   **Activity Log**: Detailed audit trail of user actions (logins, edits, printing).
    *   **Master List Sync**: Upload a master `.txt` or CSV file to perform a full database synchronization.

## 📸 Screenshots

|               Main Generator Window                |                      Admin Dashboard                       |
|:--------------------------------------------------:|:----------------------------------------------------------:|
| ![Main Window](assets/screenshots/main-window.png) | ![Admin Dashboard](assets/screenshots/admin-dashboard.png) |

|                        Custom Size Manager                        |                        Quick Stock Checker                         |
|:-----------------------------------------------------------------:|:------------------------------------------------------------------:|
| ![Custom Size Manager](assets/screenshots/custom-size-dialog.png) | ![Quick Stock Checker](assets/screenshots/quick-stock-checker.png) |


## 💻 Technology Stack

*   **Framework**: PyQt6
*   **Database**: Firebase Realtime Database & Auth
*   **Data Analysis**: Pandas
*   **Image Processing**: Pillow, CairoSVG
*   **Data Parsing**: Beautiful Soup 4
*   **Languages**: Python

## 📦 Setup and Installation

To get the project running locally for your own environment, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tnicko1/Retail-Operations-Suite
    cd Retail-Operations-Suite
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Firebase:**
    *   In the project root, you will find a file named `config.template.json`.
    *   **Make a copy** of this file and rename it to `config.json`.
    *   Open `config.json` and fill in your actual Firebase project configuration credentials.
    *   *Note: `config.json` is ignored by git to protect your secrets.*

5.  **Customize Assets**:
    *   Replace the logo files in `assets/` with your own company branding to ensure generated tags reflect your identity.

6.  **Run the application:**
    ```bash
    python main.py
    ```

## 📜 Licensing

This project is dual-licensed to accommodate both open-source and commercial needs.

#### Open-Source License

The **Retail Operations Suite** is free software, licensed under the **GNU General Public License v3.0 (GPLv3)**. You are free to use, modify, and redistribute this software under the terms of the GPLv3. A full copy of the license is available in the `LICENSE` file.

#### Commercial License

If you wish to use this software in a proprietary, closed-source commercial product without being bound by the copyleft terms of the GPLv3, a commercial license is required.

For commercial licensing options, please contact the author directly.

## 👨‍💻 Author

This project was created with passion by **Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი)**.

For inquiries, please contact: `nikoloz@taturashvili.com`