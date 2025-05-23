# 3D Printing Quote Generator

A Streamlit application that generates quotes for 3D printing services based on STL file volume, printer selection, and material choice.

## Features

- Upload STL files and calculate their volume
- Select from different Formlabs printers
- Choose appropriate materials for each printer
- Automatic price calculation including support material costs for SLA printers
- Generate and download PDF quotes

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Usage

1. Upload your STL file using the file uploader
2. Select your preferred printer from the dropdown menu
3. Choose the material you want to use
4. View the calculated price
5. Click "Generate Quote" to create and download a PDF quote

## Note

The Formlabs logo needs to be added to the project directory as "formlabs_logo.png" for the PDF generation to include the logo. 