import argparse, os, json, shutil
from multiprocessing import Pool

def get_file_destination(filename):
	original_path = os.path.join(input_dir, filename)
	file = open(original_path)
	jsondata = json.load(file)

	if "Region" not in jsondata:
		raise Exception("Missing region data")
	region = jsondata["Region"]
	
	if not os.path.isdir(args.output + "/" + region):
		os.mkdir(os.path.join(output_dir, region))

	new_path = os.path.join(output_dir, region, filename)
	return (original_path, new_path)

def move_file(original_path, new_path):
	shutil.copyfile(original_path, new_path)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("input", help='Input directory containing corpus', action="store")
	parser.add_argument("output", help='Output directory for sorted corpus', action="store")
	args = parser.parse_args()

	global input_dir, output_dir
	input_dir = os.path.normpath(args.input)
	output_dir = os.path.normpath(args.output)

	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)

	filenames = []
	for _, _, files in os.walk(input_dir):
		for filename in files:
			if filename.endswith(".json"):
				filenames.append(filename)

	print("Loading files")
	pool = Pool()
	file_list = pool.map(get_file_destination, filenames)
	pool.close()
	pool.join()

	assert(len(file_list) == len(filenames))

	print("Moving files")
	pool = Pool()
	pool.starmap_async(move_file, file_list)
	pool.close()
	pool.join()
	