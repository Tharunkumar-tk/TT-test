# FitVision - AI-Powered Workout Analysis

An offline-first fitness tracking application with real-time pose detection and workout analysis.

## 🎯 Features

- **Offline Processing** - All analysis happens locally, no cloud required
- **Real-time Pose Detection** - Using MediaPipe for accurate form tracking
- **Multiple Activities** - Push-ups, Pull-ups, Vertical Jump, Shuttle Run, and more
- **Detailed Metrics** - Rep counting, form accuracy, timing, and performance data
- **Video Upload & Live Recording** - Flexible input methods
- **Annotated Output** - Get videos with pose overlay and rep counters

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Webcam (for live recording)

### Installation

1. **Clone and install frontend**
   ```bash
   npm install
   ```

2. **Setup Python backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running the App

**Terminal 1 - Backend:**
```bash
cd backend
./start.sh  # Windows: start.bat
```
Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
npm run dev
```
Frontend runs on `http://localhost:5173`

📖 **See [SETUP.md](./SETUP.md) for detailed installation and troubleshooting**

## 📊 Supported Activities

| Activity | Video | Live | Metrics |
|----------|-------|------|---------|
| Push-ups | ✅ | ✅ | Reps, Form Accuracy, Timing |
| Pull-ups | ✅ | ✅ | Reps, Form Accuracy, Timing |
| Vertical Jump | ✅ | ✅ | Height, Air Time, Count |
| Shuttle Run | ✅ | ✅ | Distance, Time, Laps |
| Sit-ups | ✅ | ❌ | Reps, Timing |
| Sit & Reach | ✅ | ❌ | Reach Distance |
| Standing Broad Jump | ✅ | ❌ | Distance, Count |

## 🏗️ Architecture

```
Frontend (React) → API (FastAPI) → Python Scripts → MediaPipe → Results
```

All processing happens locally on your device.

## 📁 Project Structure

```
├── backend/              # Python FastAPI server
│   ├── server.py        # API endpoints
│   ├── processor.py     # Workout processing logic
│   └── requirements.txt # Python dependencies
├── scripts/             # Workout analysis scripts
│   ├── run_pushup_video.py
│   ├── pullup_video.py
│   └── ...
├── src/
│   ├── components/      # React components
│   ├── services/        # API client
│   └── pages/          # App screens
└── package.json

```

## 🔧 Technologies

**Frontend:**
- React + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

**Backend:**
- Python 3.8+
- FastAPI
- MediaPipe
- OpenCV
- Pandas

## 📝 How to Use

1. **Select Activity** - Choose from supported exercises
2. **Upload or Record** - Provide video input
3. **Processing** - AI analyzes pose and form (15-30 seconds)
4. **View Results** - Get metrics, annotated video, and CSV log

## 🔒 Privacy

- **100% Offline** - No data sent to external servers
- **Local Processing** - All analysis on your device
- **No Tracking** - Your workout data stays private

## 🐛 Troubleshooting

**Backend won't start?**
```bash
pip install -r backend/requirements.txt
```

**Frontend can't connect?**
- Check backend is running on port 8000
- Verify `.env` has `VITE_BACKEND_URL=http://localhost:8000`

**No pose detected?**
- Ensure good lighting
- Keep full body in frame
- Check camera angle

See [SETUP.md](./SETUP.md) for more troubleshooting.

## 📖 Documentation

- [Setup Guide](./SETUP.md) - Detailed installation instructions
- [Backend README](./backend/README.md) - API documentation

---

## Project info

**URL**: https://lovable.dev/projects/08737ad9-f564-47e3-807e-3374d954b89f

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/08737ad9-f564-47e3-807e-3374d954b89f) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/08737ad9-f564-47e3-807e-3374d954b89f) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
