from PIL import Image
import re, argparse
import os.path

# Convert Binary String into ASCII
def binToAscii(binary):
	return ''.join(chr(int(byte, 2)) for byte in re.findall(8*'.',binary))

# Convert ASCII to binart
def asciiToBin(ascii):
	return ''.join(str(bin(ord(byte)))[2:].zfill(8) for byte in ascii)

# Return the LSB of a value
def getLSB(value):
	return str(bin(value))[-1]

# Alter the LSB of a value
def setLSB(target, value):
	binary = str(bin(target))[2:]
	if binary[-1] != value:
		binary = binary[:-1] + value
	return int(binary, 2)

# Hide Data within a PNG image
def hide(img, data, outName):
	# Header and trailer are used to identify start and end of hidden data
	header, trailer = 2*"11001100",2*"0101010100000000"
	dataBin = header+asciiToBin(data)+trailer
	pixels, mode = list(img.getdata()), img.mode
	newPixels = []

	for i in range(len(dataBin)):
		newPixel = list(pixels[i])
		newPixel[i%len(mode)] = setLSB(newPixel[i%len(mode)], dataBin[i])
		newPixels.append(tuple(newPixel))

	newData = newPixels + pixels[len(newPixels):]

	img.putdata(newData)
	img.save(outName, "PNG")
	print "[+] Output: " + outName

# Extract data from a carrier PNG image
def extract(img, outName):
	# Header and trailer are used to identify start and end of hidden data
	header, trailer = 2*"11001100",2*"0101010100000000"
	binary, data, found = "", "", False
	pixels, mode = list(img.getdata()), img.mode

	for i in range(len(pixels)):
		binary += getLSB(pixels[i][i%len(mode)])
		if not found and len(binary) == len(header):
			if binary != header:
				print "[-] No Hidden Data Found!"
				exit(0)
			else:
				found, binary = True, "";
		if binary.endswith(trailer):
			print "[+] Data Extracted: "
			break

	data = binToAscii(binary)[:-4]

	if outName != None:
		outFile = open(outName, "wb")
		outFile.write(data)
		data = "[+] Written to file: " + outName

	return data

# Confirm Data fits into Carrier file
def fits(img, data): 
	carrierSpace, dataSize = img.size[0]*img.size[1], 0
	if data[1] == None: dataSize = len(data[0])*8
	else: dataSize = int(str(os.path.getsize(data[1]))[:-1])*8
	return dataSize < carrierSpace

# Error handeling
def checkErrors(parser):
	args = parser.parse_args()
	if not os.path.exists(args.i): 
		return parser.prog + ": error: No such file: " + args.i
	img = Image.open(args.i)
	if img.format != "PNG":
		return parser.prog + ": error: Carrier file must be PNG: " + args.i
	if img.mode not in ["RGB", "RGBA"]:
		return parser.prog + ": error: Carrier file must be RGB(A): " + img.mode
	if args.mode == "encrypt":
		if args.D is None and args.d is None:
			return parser.prog + ": error: Please provide some data!"
		if args.D != None and not os.path.exists(args.D): 
			return parser.prog + ": error: No such file: " + args.D
		if not fits(img, [args.d, args.D]):
			return parser.prog + ": error: Data too large for Carrier"

	return None

def main():
	# Setup argument handeling
	parser = argparse.ArgumentParser(description="Hide data within an image!", version="1.0")
	subparsers = parser.add_subparsers(dest="mode")

	parser_enc = subparsers.add_parser('encrypt')
	parser_enc.add_argument('-i', help='Carrier file (.png Image)', metavar="<image>", required=True)
	parser_enc.add_argument('-d', help='Data to be hidden (String)', metavar="<message>")
	parser_enc.add_argument('-D', help='data to be hidden (file)', metavar="<file>")
	parser_enc.add_argument('-o', help="Output filename", metavar="[output]")
	parser_enc.usage="%(prog)s [-h] -i <image> (-d <message> | -D <file>) [-o output]"
	parser_enc._optionals.title = "Arguments"

	parser_ext = subparsers.add_parser('extract')
	parser_ext.add_argument('-i', help='Carrier file (.png Image)', metavar="<image>", required=True)
	parser_ext.add_argument('-o', help="Output filename", metavar="[output]")
	parser_ext.usage="%(prog)s [-h] -i <image> [-o output]"
	parser_ext._optionals.title = "Arguments"
	
	parser.usage="\
	%(prog)s encrypt [-h] -i <image> (-d <message> | -D <file>) [-o output]\n\
	%(prog)s extract [-h] -i <image> [-o output]\n\
	%(prog)s ([-h] | [--help] | [--version])"

	parser._optionals.title = "Arguments"
	args = parser.parse_args()

	# Check for argument errors
	error = checkErrors(parser)
	if error != None:
		if args.mode == "encrypt": parser_enc.print_usage()
		elif args.mode == "extract": parser_ext.print_usage()
		else: parser.print_usage()
		print error; exit(1)

	# Init encrypt mode
	if args.mode == "encrypt":
		print "[+] Hiding data in: " + args.i
		if args.D != None:
			with open(args.D, 'r') as dataFile: 
				data = dataFile.read()
		else: data = args.d

		# Reformat output name if necessary
		if args.o == None: outName = "output.png"
		else: outName = (args.o+".").split(".")[0]+".png"

		img = Image.open(args.i)
		# Call hide function
		hide(img, data, outName)

	# Init extract mode
	elif args.mode == "extract":
		img = Image.open(args.i)
		# Call extract function
		print extract(img, args.o)
	
	exit(0)

if __name__ == "__main__":
	main()