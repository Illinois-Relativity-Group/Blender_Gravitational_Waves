input_file = "bh_radius.txt"      # Replace with your input file name
output_file = "update_bh_radius.txt"    # Replace with your desired output file name

start_id = 1053 #time/(time of each frame), here is 3707.721/3.52

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for i, line in enumerate(infile):
        if i % 4 == 0:
            columns = line.strip().split()
            if len(columns) >= 8:
                outfile.write(f"{start_id} {columns[7]}\n")
                start_id += 1
