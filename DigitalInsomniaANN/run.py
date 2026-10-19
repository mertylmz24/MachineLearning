import sys
import io
import uvicorn

# Ensure utf-8 encoding for console prints on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    print("=" * 60)
    print("  🌙 Digital Insomnia ANN - FastAPI & Web UI Sunucusu")
    print("  🌐 Arayüz:  http://127.0.0.1:8000")
    print("  📚 API Dökümantasyonu: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
