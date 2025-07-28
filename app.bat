@echo off

start cmd /k "cd back && python app.py"
start cmd /k "cd frontend && npm run dev"
start cmd /k "cd predict_service && python predict.py"

timeout /t 5 > nul
start chrome http://localhost:5173

@REM @echo off
@REM docker-compose up --build
@REM timeout /t 5 > nul

@REM start chrome http://localhost:5173
