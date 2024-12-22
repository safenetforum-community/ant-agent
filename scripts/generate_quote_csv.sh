#!/bin/bash

# Define the output CSV file name
csv_filename="file_metadata.csv"

# Function to generate a random seed
generate_seed() {
  echo $((RANDOM * RANDOM))
}

# Function to calculate MD5 hash
calculate_md5() {
  local file_size=$1
  local seed=$2
  local size=$3
  echo -n "${file_size}${seed}${size}" | md5sum | awk '{print $1}'
}

# Create the CSV file and add the header
echo "fileSize,seed,size,md5" > $csv_filename

# Define file sizes and corresponding byte sizes
declare -A file_sizes
file_sizes=( ["tiny"]=65536 ["small"]=3145728 ["medium"]=31457280 ["large"]=60850048 ["huge"]=838860800 ["giga"]=2147483648 )

# Generate metadata for each file size
for file_size in "${!file_sizes[@]}"
do
  seed=$(generate_seed)
  size=${file_sizes[$file_size]}
  md5_hash=$(calculate_md5 $file_size $seed $size)
  echo "${file_size},${seed},${size},${md5_hash}" >> $csv_filename
done

# Print a message to indicate the file has been created
echo "CSV file '$csv_filename' has been created with generated seeds and MD5 hashes."
