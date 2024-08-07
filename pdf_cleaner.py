import os
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageStat
import tempfile
from pdf2image import convert_from_path
from tqdm import tqdm
from multiprocessing import Pool, cpu_count, Manager

def is_blank_page(page_image_path, size_threshold=1000, pixel_threshold=500):
	"""
	Prüft, ob eine Seite leer ist, indem die Bildgröße und die mittlere Helligkeit analysiert werden.

	:param page_image_path: Pfad zur Bilddatei der Seite
	:param size_threshold: Schwellenwert für die Dateigröße in Bytes
	:param pixel_threshold: Schwellenwert für die mittlere Helligkeit
	:return: True, wenn die Seite leer ist, sonst False
	"""
	try:
		image = Image.open(page_image_path).convert("L")  # In Graustufen konvertieren
		bbox = image.getbbox()  # Begrenzungsrahmen der nicht-weißen Bereiche abrufen
		if bbox is None:
			return True
		
		# Prüfen, ob die Dateigröße unter dem Schwellenwert liegt
		file_size = os.path.getsize(page_image_path)
		if file_size < size_threshold:
			return True

		# Mittlere Helligkeit überprüfen
		stat = ImageStat.Stat(image)
		mean_brightness = stat.mean[0]
		if mean_brightness > 250:  # Sehr hohe Helligkeit deutet auf eine leere Seite hin
			return True

		return False
	except Exception as e:
		print(f"Fehler beim Verarbeiten des Bildes {page_image_path}: {e}")
		return False

def extract_page_as_image(pdf_path, page_number, output_image_path):
	"""
	Extrahiert eine Seite aus einer PDF-Datei und speichert sie als Bild.

	:param pdf_path: Pfad zur PDF-Datei
	:param page_number: Seitennummer, die extrahiert werden soll
	:param output_image_path: Pfad zur Ausgabe-Bilddatei
	"""
	try:
		images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
		for i, image in enumerate(images):
			image.save(f"{output_image_path}-{i + 1}.png", "PNG")
	except Exception as e:
		print(f"Fehler beim Extrahieren der Seite {page_number} als Bild: {e}")

def process_pdf(file_paths, progress_dict, results):
	"""
	Verarbeitet eine PDF-Datei, entfernt leere Seiten und speichert die bereinigte PDF-Datei.

	:param file_paths: Tuple mit Pfaden zur Eingabe- und Ausgabedatei
	:param progress_dict: Dictionary zur Verwaltung der Fortschrittsbalkenpositionen
	:param results: Liste zur Speicherung der Ergebnisse
	"""
	input_pdf_path, output_pdf_path = file_paths
	reader = PdfReader(input_pdf_path)
	writer = PdfWriter()
	blank_pages_count = 0

	with tempfile.TemporaryDirectory() as tmpdirname:
		position = progress_dict[input_pdf_path]
		for page_number in tqdm(range(len(reader.pages)), desc=f"Processing {os.path.basename(input_pdf_path)}", position=position, leave=False):
			image_prefix = os.path.join(tmpdirname, f"page_{page_number + 1}")
			image_path = f"{image_prefix}-1.png"
			extract_page_as_image(input_pdf_path, page_number + 1, image_prefix)
			
			if os.path.exists(image_path):
				if not is_blank_page(image_path):
					writer.add_page(reader.pages[page_number])
				else:
					blank_pages_count += 1

		with open(output_pdf_path, "wb") as output_file:
			writer.write(output_file)

	results.append((os.path.basename(input_pdf_path), blank_pages_count))

def process_pdfs_in_folder(input_folder, output_folder):
	"""
	Verarbeitet alle PDF-Dateien in einem Ordner und speichert die bereinigten Dateien in einem anderen Ordner.

	:param input_folder: Pfad zum Eingabeordner
	:param output_folder: Pfad zum Ausgabeordner
	"""
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	
	pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
	file_paths = [(os.path.join(input_folder, pdf), os.path.join(output_folder, pdf)) for pdf in pdf_files]

	manager = Manager()
	progress_dict = manager.dict()
	for i, pdf in enumerate(pdf_files):
		progress_dict[os.path.join(input_folder, pdf)] = i

	results = manager.list()

	with Pool(cpu_count()) as pool:
		pool.starmap(process_pdf, [(file_path, progress_dict, results) for file_path in file_paths])

	for result in results:
		print(f"Processed {result[0]}: Removed {result[1]} blank pages")

if __name__ == "__main__":
	# Anpassbare Ordnerpfade für Eingabe- und Ausgabedateien
	input_folder = "input"
	output_folder = "output"
	process_pdfs_in_folder(input_folder, output_folder)