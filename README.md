# B2B Invoice Generator - ScrapK Ventures Pvt. Ltd. 🪙

A professional full-stack B2B invoice and bill generator web application built for **ScrapK Ventures Pvt. Ltd.** to manage bulk material scrap collections, execute precise tax calculations, store invoices securely in a local database, and generate professional PDF receipts.

---

## 📂 Project Directory Structure

```text
scrapk-invoice-generator/
│
├── backend/
│   ├── database.py             # SQLAlchemy connection & session setup
│   ├── invoices.db             # Local SQLite database (auto-created)
│   ├── main.py                 # FastAPI Application Entrypoint & Startup
│   ├── requirements.txt        # Python backend dependencies
│   ├── models/
│   │   └── invoice.py          # SQLAlchemy Database Models (Invoice, InvoiceItem)
│   ├── schemas/
│   │   └── invoice.py          # Pydantic Schemas for requests/responses
│   └── routers/
│       └── invoice.py          # REST API endpoints & tax logic engine
│
├── frontend/
│   ├── index.html              # Modern Tailwind UI, Ledger list & PDF compiler
│   └── logo.png                # Corporate brand logo asset
│
├── main.py                     # Root entry point shortcut
├── requirements.txt            # Root requirements shortcut
├── .gitignore                  # Git untracked files specification
└── README.md                   # Setup and execution instructions (this file)
```

---

## 🚀 Setup & Execution Instructions

### A. Start the Backend Server (FastAPI)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment**:
   - **Windows (PowerShell/CMD)**:
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```bash
     source venv/bin/activate
     ```
4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Uvicorn development server**:
   ```bash
   uvicorn main:app --reload
   ```
   *The API engine will run on [http://127.0.0.1:8000](http://127.0.0.1:8000). On first run, it will automatically initialize the local `invoices.db` SQLite database.*

---

### B. Launch the Frontend Application

Choose one of these simple methods to run the frontend client interface:

#### Method 1: Python HTTP Server (Recommended)
From the project root directory, run:
```bash
python -m http.server 5500
```
Then open your browser and navigate to:
[http://localhost:5500/frontend/index.html](http://localhost:5500/frontend/index.html)

#### Method 2: Direct File Open
Open the `frontend/index.html` file directly in any web browser. 
*(Note: If the backend API server is offline, the interface will gracefully fallback to a client-side calculation engine, though database features like saving and history will be deactivated).*

---

## ⚙️ Calculation & Business Rules

Our backend handles calculations under three business cases:

### Case 1: Apply GST is False (`apply_gst = false`)
- GST is treated as 0%, and tax inclusive settings are ignored.
- **Formula**:
  - `Subtotal = sum(weight * rate)`
  - `Taxable Value = Subtotal`
  - `GST Amount = 0`
  - `Grand Total = Subtotal + External Fare`
  - `Bill Type = "NORMAL_BILL"`

### Case 2: Apply GST is True & Exclusive Tax (`tax_inclusive = false`)
- GST is added on top of the scrap item values.
- **Formula**:
  - `Subtotal = sum(weight * rate)`
  - `Taxable Value = Subtotal`
  - `GST Amount = Taxable Value * (GST % / 100)`
  - `Grand Total = Subtotal + GST Amount + External Fare`
  - `Bill Type = "GST_INVOICE"`

### Case 3: Apply GST is True & Inclusive Tax (`tax_inclusive = true`)
- Entered item rates already include the tax. The taxable base is backed out.
- **Formula**:
  - `Inclusive Total = sum(weight * rate)`
  - `Subtotal = Inclusive Total`
  - `Taxable Value = Inclusive Total / (1 + GST % / 100)`
  - `GST Amount = Inclusive Total - Taxable Value`
  - `Grand Total = Inclusive Total + External Fare`
  - `Bill Type = "GST_INVOICE"`

---

## 🛠️ API Documentation

Once the backend is running, you can explore and test the endpoints interactively via the OpenAPI/Swagger docs:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Endpoint Routes Summary:
- `POST /api/calculate`: Process dynamic inputs and return instant calculations without database writing.
- `POST /api/invoices`: Calculate, generate a serial auto-incremented invoice number (e.g. `SKV-GST-2026-0001` or `SKV-BILL-2026-0001`), save the record into SQLite, and return the details.
- `GET /api/invoices`: Retrieve the full list of all saved invoices (sorted latest first).
- `GET /api/invoices/{invoice_id}`: Retrieve a single invoice with its nested item lines.
- `DELETE /api/invoices/{invoice_id}`: Delete an invoice and its cascade item lines from the database.

---

## 🌐 Production Deployment (Vercel + Neon)

This application is configured for serverless deployment on **Vercel** connected to a free **Neon PostgreSQL** database.

### 1. Database Setup (Neon)
1. Go to [neon.tech](https://neon.tech) and sign up for a free account.
2. Create a new project (e.g., `scrapk-ledger`).
3. In the Neon dashboard, copy your **Connection String** (select SQLAlchemy or Direct Connection).
4. The connection string will look like: `postgresql://user:password@ep-host-name.pooler.aws.neon.tech/neondb?sslmode=require`

### 2. Vercel Deployment
1. Push this project folder to your GitHub account:
   ```bash
   git add .
   git commit -m "Initialize project and Vercel setup"
   # Add your remote and push
   ```
2. Go to [Vercel](https://vercel.com) and click **Add New > Project**.
3. Import your GitHub repository.
4. Under the **Environment Variables** configuration, add the following environment variable:
   - **Key/Name:** `DATABASE_URL`
   - **Value:** Paste your Neon PostgreSQL connection string.
5. Click **Deploy**.

Vercel will automatically build the backend, deploy it serverless, and serve the frontend assets. Once completed, you will receive a public URL (e.g., `https://your-project.vercel.app`) to access the generator on your mobile phone or share it with delivery partners.
