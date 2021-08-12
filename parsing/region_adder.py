import argparse, csv, os, json
from multiprocessing import Pool

def escape_htid(htid):
	htid = htid.replace(".", "_")
	htid = htid.replace("/", "=")
	htid = htid.replace(":", "+")
	return htid

def load_region_data():
	csv_file = open(csv_path, 'r')
	csv_data = csv.reader(csv_file)
	region_data = {}
	for row in csv_data:
		region = row[0]
		htid = escape_htid(row[1])
		region_data[htid] = region
	return region_data

def write_region_data(filename):
	original_path = os.path.join(input_dir, filename)
	file = open(original_path)
	jsondata = json.load(file)

	jsondata["Region"] = region_data[filename[:-5]]

	new_path = os.path.join(output_dir, filename)
	outfile = open(new_path, "w")
	outfile.write(json.dumps(jsondata))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("input", help='Input directory containing corpus', action="store")
	parser.add_argument("output", help='Output directory for region-annotated corpus', action="store")
	parser.add_argument("csv", help='Path to CSV file with region data', action="store")
	args = parser.parse_args()

	global input_dir, output_dir, csv_path
	input_dir = os.path.normpath(args.input)
	output_dir = os.path.normpath(args.output)
	csv_path = os.path.normpath(args.csv)

	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)

	filenames = []
	for _, _, files in os.walk(input_dir):
		for filename in files:
			if filename.endswith(".json"):
				filenames.append(filename)

	global region_data
	region_data = load_region_data()

	print("Processing files")
	pool = Pool()
	pool.map_async(write_region_data, filenames)
	pool.close()
	pool.join()