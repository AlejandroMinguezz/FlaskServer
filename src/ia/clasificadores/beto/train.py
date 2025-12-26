from src.ia.classifier import DocumentClassifier

# Dataset de ejemplo (luego lo cambias por tu CSV, Mongo o lo que quieras)
texts = [
    "Factura número 123 con importe 200 euros",
    "Recibo de la luz mes de enero",
    "Currículum Vitae Juan Pérez",
    "Contrato laboral indefinido",
    "Pagaré con vencimiento marzo",
]
labels = [
    "factura",
    "recibo",
    "cv",
    "contrato",
    "pagare",
]

if __name__ == "__main__":
    clf = DocumentClassifier()
    clf.train(texts, labels)
    print("Entrenamiento completado.")
