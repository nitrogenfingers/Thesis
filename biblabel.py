import sys
import os.path
import re

#The name of the unmodified bib file (and modified)
filename = ""
bibname = ""
#Whether or not to use verbose output
verbose = False
#Whether or not to delete the original file
delete_old = True
#How many authors to include in the citation before using 'et al'
et_al_num = 2
#Whether or not to output a key file
key_file = False
#The number of entries labelled
entry_count = 0

# Reads a bibentry from file, stores it and dynamically generates a label
def read_entry(file):
	open = True
	entry = []
	label = None
	year = None
	
	while open:
		line = file.readline()
		if line == "": 
			print("File terminated.")
			return None
		elif line == "\n": 
			continue
		elif line.startswith("}"):
			entry.append(line)
			open = False
			break
		#Removing LaTeX-breaking characters
		line = line.replace("&", "\&")
		
		
		
		#Year is extracted to append to end of entry
		entry.append(line)
		if line.strip().startswith("year"):
			year = re.split("{|}", line)[1]
		
		#Author names are appended to each label
		elif line.strip().startswith("author"):
			aline = re.split("{|}", line)[1].split(" ")
			author_next = True
			authors = []
			for i in range(len(aline)):
				if author_next:
					authors.append(aline[i].replace(",", ""))
					author_next = False
				elif aline[i] == "and":
					author_next = True
			if len(authors) <= et_al_num: label = ''.join(authors)
			else: label = authors[0] + "EtAl"
	
	if label == None:
		print("Error: entry " + str(entry_count) + " has no author field")
		file.close()
		sys.exit(0)
	elif year == None:
		print("Error: entry " + str(entry_count) + " has no year field")
		file.close()
		sys.exit(0)
	
	if verbose: print("Labelling article " + (label + year))
	entry[0] = entry[0][:-1] + " " + label + year + ",\n"
	
	global entry_count
	entry_count += 1
	return entry
	
# Writes the bib entry to the new file
def write_entry(file, entry):
	for line in entry:
		file.write(line)
	file.write("\n")
	
# Program must have at least one input, along with option command-line keys.
if len(sys.argv) <= 1 :
	print("No file provided. Use --help for usage")
	sys.exit()
	
argvr = iter(range(1, len(sys.argv)))
for i in argvr:
	if sys.argv[i] in ("-h", "--help"):
		print("usage: biblabel.py [file] [options | ...]")
		print("Options and arguments:")
		print("-h     : shows this usage screen")
		print("-v     : verbose; describes process")
		print("-r     : retains original copy of the file")
		print("-a num : Specifies how many authors to label before et al. Default is 2")
		print("-k     : Output a key to the citations, including label-name pairs. Saved as [file]key.txt")
		print("-o name: Specifies the name of the output file")
		sys.exit()
	elif sys.argv[i] in ("-v", "--verbose"):
		verbose = True
	elif sys.argv[i] in ("-r," "--retain"):
		delete_old = False
	elif sys.argv[i] == "-o":
		bibname = sys.argv[i+1]
		next(argvr)
	elif sys.argv[i] == "-a":
		try:
			et_al_num = int(sys.argv[i+1])
		except ValueError:
			print("Error: Argument following -a must be a number")
			sys.exit()
		next(argvr)
	elif sys.argv[i] in ("-k", "--key"):
		key_file = True
	else:
		if os.path.isfile(sys.argv[i]):
			filename = sys.argv[i]
		else:
			print("Error: \""+sys.argv[i]+"\" is not a valid file")
			sys.exit()

if bibname == "": bibname = filename.split(".")[0] + "lab.bib"
			
text = open(filename, "r")
bib = open(bibname, "w")

#Takes each entry and outputs to file
entry = read_entry(text)
while entry != None:
	write_entry(bib, entry)
	entry = read_entry(text)

#Cleanup
print("Labelling output to " + bibname + "(" + str(entry_count) + " entries)")
	
text.close()
bib.close()

if delete_old:
	os.remove(filename)
	print(filename + " deleted.")