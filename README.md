 PDF Rename – Professional & User-Friendly PDF Renaming Solution

## Overview

**PDF Rename** is an extremely user-friendly application designed to automate the process of renaming PDF files using advanced OCR (Optical Character Recognition) technology. With a simple, intuitive interface, even non-technical users can batch rename PDFs in seconds. For power users and developers, a robust command-line version is also available.

---

## Key Features

- **One-Click PDF Renaming:** Effortlessly rename PDFs based on their content using OCR.
- **Automatic Organization:** Renamed PDFs are automatically placed into their respective folders, keeping your files organized.
- **No Technical Skills Required:** The PDF Rename executable is designed for everyone—just launch, select your files, and let the app do the rest.
- **Advanced Command-Line Support:** For automation and integration into workflows.

---

## How It Works

### User-Friendly Executable (PDF Rename)

1. Launch the PDF Rename application.
2. Select the PDFs you wish to rename.
3. The app scans each PDF, extracts relevant information (such as invoice numbers, dates, or custom fields), and renames the files accordingly.
4. Renamed PDFs are automatically moved to the designated `Renamed PDFs` folder, while originals remain untouched in the `PDFs to rename` folder.
5. The process is fast, accurate, and requires no manual intervention.

#### Folder Structure

- `PDFs to rename/`: Place your original PDF files here.
- `Renamed PDFs/`: Renamed files will appear here after processing.

---

## Technical Details: Command-Line Version

For advanced users, PDF Rename offers a command-line interface (CLI) for batch processing and integration into scripts or automated workflows.

### Prerequisites

- **Python 3.7+**
- **Tesseract OCR** ([Download](https://github.com/tesseract-ocr/tesseract))
- **Poppler for Windows** ([Download](http://blog.alivate.com.au/poppler-windows/))

### Installation Steps

1. **Clone or Download the Repository**
   - Download the project files to your local machine.

2. **Install Dependencies**
   - Open a terminal in the project directory.
   - Install required Python packages:
     ```sh
     pip install flask pytesseract pdf2image pillow
     ```

3. **Set Up External Tools**
   - Ensure the `poppler` and `tesseract` folders are present in the project directory.
   - Verify that `poppler/bin` and `tesseract/tesseract.exe` exist.

### Running the Command-Line Program

1. Open a terminal in the `OCR_PDF_RENAME` directory.
2. Run the renamer script:
   ```sh
   python ocr_rename.py
   ```
3. The script will process all PDFs in the `PDFs to rename` folder, rename them based on extracted content, and move them to the `Renamed PDFs` folder.

---

## Support

For questions or support, please refer to the documentation or open an issue on GitHub.
