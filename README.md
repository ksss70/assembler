# assembler

## What is it?
assembler is an assembler and interpreter for a learning virtual machine


## Examples

### Input File
```
A=15,B=596,C=611
A=14,B=158,C=358
A=8,B=827,C=460
A=12,B=946,C=395,D=261
```
### Example for interpreter
```
main.py interpret output.bin --result_file result.json --memory_range 0:10
```

### Example for assembler
```
main.py assemble input.txt --output_file output.bin --log_file log.json
```
