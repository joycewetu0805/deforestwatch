.PHONY: help install collect train test api dashboard frontend seed report memoir monograph check-data docker clean

help:
	@echo "DeforestWatch-DRC — commandes disponibles :"
	@echo "  make install    Installe les dépendances Python"
	@echo "  make seed       Génère les données de démo (synthétiques)"
	@echo "  make collect    Lance la collecte de données (GEE + météo)"
	@echo "  make train      Entraîne les 3 modèles ML"
	@echo "  make test       Lance la suite de tests pytest"
	@echo "  make api        Démarre l'API FastAPI (port 8000)"
	@echo "  make dashboard  Démarre le dashboard Streamlit (port 8501)"
	@echo "  make frontend   Démarre le frontend React (port 5173)"
	@echo "  make report     Génère le rapport de synthèse"
	@echo "  make memoir     Génère le mémoire académique (.docx)"
	@echo "  make monograph  Génère la monographie UPC/FASI (.docx)"
	@echo "  make slides     Génère la présentation de soutenance (.pptx)"
	@echo "  make guide      Génère le guide complet (GUIDE.md + docs/GUIDE.pdf)"
	@echo "  make export-demo Écrit des GeoTIFF de test dans data/raw/"
	@echo "  make check-data Vérifie les vraies données dans data/raw/"
	@echo "  make demo       Bascule .env en mode démo (synthétique)"
	@echo "  make real       Bascule .env en mode réel (data/raw/)"
	@echo "  make mode       Affiche le mode de données courant"
	@echo "  make docker     Build + run via docker-compose"

install:
	pip install -r requirements.txt

seed:
	python -m scripts.seed_demo

collect:
	python -m scripts.collect_data

train:
	python -m scripts.train_all

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

api:
	uvicorn src.api.main:app --reload --port 8000

dashboard:
	streamlit run streamlit_app/app.py --server.port 8501

frontend:
	cd frontend && npm install && npm run dev

report:
	python -m scripts.generate_report

memoir:
	python -m scripts.generate_memoir

monograph:
	python -m scripts.generate_monograph

slides:
	python -m scripts.generate_slides

guide:
	python -m scripts.generate_guide

export-demo:
	python -m scripts.gee_export --demo-geotiff

check-data:
	python -m scripts.check_real_data

demo:
	python -m scripts.switch_mode demo

real:
	python -m scripts.switch_mode real

mode:
	python -m scripts.switch_mode status

docker:
	docker-compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage spark-warehouse
