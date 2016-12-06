StepSteg
========
A simple Stenography tool used to encode data within the LSB of PNG pixel data, as well as extract hidden data from within PNG files.

Dependencies
------------
This program requires the PIL Librarie to run.  
You can install PIL using pip as shown below:  
`pip install PIL`

Command-line
------------
```
> python stepSteg.py -h
usage:  stepSteg.py encrypt [-h] -i <image> (-d <message> | -D <file>) [-o output]
        stepSteg.py extract [-h] -i <image> [-o output]
        stepSteg.py ([-h] | [--help] | [--version])

Hide data within an image!

positional arguments:
  {encrypt,extract}

Arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit

> python stepSteg.py encrypt -h
usage: stepSteg.py encrypt [-h] -i <image> (-d <message> | -D <file>) [-o output]

Arguments:
  -h, --help    show this help message and exit
  -i <image>    Carrier file (.png Image)
  -d <message>  Data to be hidden (String)
  -D <file>     data to be hidden (file)
  -o [output]   Output filename

> python stepSteg.py extract -h
usage: stepSteg.py extract [-h] -i <image> [-o output]

Arguments:
  -h, --help   show this help message and exit
  -i <image>   Carrier file (.png Image)
  -o [output]  Output filename
```
Hide message/file:
```
> python stepSteg.py encrypt -i demo.png -d "I am a hidden message" -o hasSecretMsg.png
[+] Hiding data in: demo.png
[+] Output: hasSecretMsg.png

> python stepSteg.py encrypt -i demo.png -D hiddenFile.zip -o hasSecretFile.png
[+] Hiding data in: demo.png
[+] Output: hasSecretFile.png
```
Extract message/file:
```
> python stepSteg.py extract -i hasSecretMsg.png
[+] Data Extracted:
I am a hidden message

> python stepSteg.py extract -i hasSecretFile.png -o output.zip
[+] Data Extracted:
[+] Written to file: output.zip
```

License
-------
This software is MIT-Licensed.