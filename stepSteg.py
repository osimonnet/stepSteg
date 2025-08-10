from PIL import Image
import re, argparse
import os.path

# Convert Binary String into ASCII
def binToAscii(binary):
    return ''.join(chr(int(byte, 2)) for byte in re.findall(8*'.', binary))

# Convert ASCII to Binary
def asciiToBin(ascii):
    return ''.join(str(bin(ord(byte)))[2:].zfill(8) for byte in ascii)

# Return the LSB of a value
def getLSB(value):
    return str(bin(value))[-1]

# Alter the LSB of a value
def setLSB(target, value):
    binary = str(bin(target))[2:].zfill(8)  # Ensure it's 8-bit binary
    binary = binary[:-1] + value  # Replace LSB
    return int(binary, 2)  # Convert back to integer

# Hide Data within the Alpha channel of a PNG image
def hide(img, data, outName):
    header, trailer = 2*"11001100", 2*"11001100"  # Headers to mark start & end
    dataBin = header + asciiToBin(data) + trailer
    pixels = list(img.getdata())  
    newPixels = []

    data_index = 0  

    for i in range(len(pixels)):
        newPixel = list(pixels[i])  

        for channel in range(4):  
            if data_index < len(dataBin):  
                newPixel[channel] = setLSB(newPixel[channel], dataBin[data_index])
                if data_index == 0:
                    print(f"[DEBUG] First Bit Stored at Pixel {i}, Channel {channel}")
                data_index += 1

        newPixels.append(tuple(newPixel))

    img.putdata(newPixels)
    img.save(outName, "PNG")
    print(f"[+] Hidden message saved to: {outName}")

# Extract data from an image's Alpha channel
def extract(img, outName):
    header, trailer = 2*"11001100", 2*"11001100"  # Headers to find hidden data
    binary, data, found = "", "", False
    pixels = list(img.getdata())

    for pixel in pixels:
        for channel in pixel:  # Read from R, G, B, A
            binary += getLSB(channel)

        if not found and len(binary) >= len(header):
            if binary[:len(header)] != header:
                print("[-] No Hidden Data Found!")
                exit(0)
            else:
                found = True
                binary = binary[len(header):]  # Remove header from binary string

        if found and binary.endswith(trailer):
            print("[+] Data Extracted!")
            break  

    data = binToAscii(binary[:-len(trailer)])  # Convert binary to ASCII

    if outName:
        with open(outName, "wb") as outFile:
            outFile.write(data.encode())  
        data = f"[+] Written to file: {outName}"

    return data

# Confirm Data Fits in Carrier Image
def fits(img, data): 
    carrierSpace = img.size[0] * img.size[1]  # Number of pixels
    dataSize = len(data[0]) * 8 if data[1] is None else int(os.path.getsize(data[1])) * 8
    return dataSize < carrierSpace

# Error Handling
def checkErrors(parser):
    args = parser.parse_args()
    if not os.path.exists(args.i): 
        return f"{parser.prog}: error: No such file: {args.i}"
    
    img = Image.open(args.i)

    # Force RGBA
    img = img.convert("RGBA")
    img.save(args.i)
    img = Image.open(args.i)

    if img.format != "PNG":
        return f"{parser.prog}: error: Carrier file must be PNG: {args.i} )({img.format})"
    
    if img.mode not in ["RGBA"]:  # Ensure Alpha channel exists
        return f"{parser.prog}: error: Carrier file must be RGBA, not {img.mode}"
    
    if args.mode == "encode":
        if args.D is None and args.d is None:
            return f"{parser.prog}: error: Please provide some data!"
        if args.D and not os.path.exists(args.D): 
            return f"{parser.prog}: error: No such file: {args.D}"
        if not fits(img, [args.d, args.D]):
            return f"{parser.prog}: error: Data too large for Carrier"

    return None

# Main function
def main():
    parser = argparse.ArgumentParser(description="Hide data within an image!")
    subparsers = parser.add_subparsers(dest="mode")

    # Encode Mode
    parser_enc = subparsers.add_parser('encode')
    parser_enc.add_argument('-i', help='Carrier file (.png Image)', metavar="<image>", required=True)
    parser_enc.add_argument('-d', help='Data to be hidden (String)', metavar="<message>")
    parser_enc.add_argument('-D', help='Data to be hidden (file)', metavar="<file>")
    parser_enc.add_argument('-o', help="Output filename", metavar="[output]")
    parser_enc.usage = "%(prog)s [-h] -i <image> (-d <message> | -D <file>) [-o output]"
    parser_enc._optionals.title = "Arguments"

    # Extract Mode
    parser_ext = subparsers.add_parser('extract')
    parser_ext.add_argument('-i', help='Carrier file (.png Image)', metavar="<image>", required=True)
    parser_ext.add_argument('-o', help="Output filename", metavar="[output]")
    parser_ext.usage = "%(prog)s [-h] -i <image> [-o output]"
    parser_ext._optionals.title = "Arguments"

    # Help Info
    parser.usage = "\
    %(prog)s encode [-h] -i <image> (-d <message> | -D <file>) [-o output]\n\
    %(prog)s extract [-h] -i <image> [-o output]\n\
    %(prog)s ([-h] | [--help] | [--version])"

    parser._optionals.title = "Arguments"
    args = parser.parse_args()

    # Check for errors
    error = checkErrors(parser)
    if error:
        if args.mode == "encode": parser_enc.print_usage()
        elif args.mode == "extract": parser_ext.print_usage()
        else: parser.print_usage()
        print(error)
        exit(1)

    # Encode Mode
    if args.mode == "encode":
        print(f"[+] Hiding data in: {args.i}")
        if args.D:
            with open(args.D, 'r') as dataFile: 
                data = dataFile.read()
        else: 
            data = args.d

        # Set output filename
        outName = "output.png" if args.o is None else (args.o + ".").split(".")[0] + ".png"

        img = Image.open(args.i).convert("RGBA")  # Ensure image has Alpha channel
        hide(img, data, outName)

    # Extract Mode
    elif args.mode == "extract":
        img = Image.open(args.i)
        print(extract(img, args.o))

    exit(0)

if __name__ == "__main__":
    main()
