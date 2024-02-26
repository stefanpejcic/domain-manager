#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <domain>"
  exit 1
fi

domain=$1
timestamp=$(date +"%Y-%m-%d-%H-%M-%S")
output_dir="whois_results/$domain"
temporary_file="$output_dir/temp_$timestamp"
output_file="$output_dir/$timestamp"

# Ensure the 'whois_results' directory exists
mkdir -p $output_dir

# Find the most recent report, excluding symlinks
latest_report=$(find $output_dir -type f -printf '%T+ %p\n' | sort -r | head -n 1 | cut -d' ' -f2-)

# Check if 'whois' command is available
if ! command -v whois &> /dev/null; then
  echo "'whois' command not found. Installing it..."
  sudo apt-get update
  sudo apt-get install -y whois
fi

# Check again if 'whois' is now available
if command -v whois &> /dev/null; then
  whois_result=$(whois "$domain")
  echo -e "$whois_result" > "$temporary_file"
  
  if [ -n "$latest_report" ]; then
    # Compare excluding the last line of both files
    diff_output=$(diff <(head -n -1 "$latest_report") <(head -n -1 "$temporary_file"))
    
    if [ -z "$diff_output" ]; then
      # No differences found (excluding the last line), so do not save the new file
      echo "No WHOIS changes found."
      rm "$temporary_file"
      mv "$latest_report" "$output_file" #to update the date only..
    else
      # Differences found, save the new report
      mv "$temporary_file" "$output_file"
      echo "Changes detected. WHOIS information saved to: $output_file"
    fi
  else
    # If this is the first report, save it
    mv "$temporary_file" "$output_file"
    echo "WHOIS information saved to: $output_file"
  fi
else
  echo "Failed to install 'whois'. Please install it manually and rerun the script."
  rm "$temporary_file" # Clean up the temporary file if 'whois' installation fails
fi
