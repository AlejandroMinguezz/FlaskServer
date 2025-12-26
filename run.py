import os, sys, socket, logging
os.environ.pop("FLASK_APP", None)
os.environ.pop("FLASK_ENV", None)
os.environ.pop("FLASK_DEBUG", None)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app import create_app

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

app = create_app()

# Logging del arranque
logging.info("Flask app inicializada correctamente.")

port = int(os.getenv("PORT", "5000"))
local_ip = get_local_ip()

logging.info("Rutas registradas en Flask:")
for rule in app.url_map.iter_rules():
    logging.info(f" -> {rule.rule} [{','.join(sorted(rule.methods))}]")

if __name__ == "__main__":
    logging.info("Iniciando servidor Flask...")
    app.run(host="0.0.0.0", port=port, debug=False)