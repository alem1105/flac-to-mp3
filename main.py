from pydub import AudioSegment
from mutagen.flac import FLAC
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import os, shutil, sys

# Get the metadata of the song
def get_tags(flac_path):
    metadata = FLAC(flac_path)
    tags = {}
    for data in metadata:
        tags[data] = metadata[data][0]
    return tags

# Save the new file
def export_file(flac_path, file_name, out_dir):
    song = AudioSegment.from_file(flac_path, 'flac')
    file_name = file_name.replace('.flac', '.mp3')
    song.export(f'{out_dir}/{file_name}', format='mp3', bitrate='320k', tags=get_tags(flac_path))

# Choose what to do if the file is a dir, a .flac or another type of file
def process_file(file, directory, out_dir, threads):
    file_dir = f'{directory}/{file}'
    if os.path.isdir(file_dir):
        os.makedirs(f'{out_dir}/{file}', exist_ok=True)
        main(file_dir, f'{out_dir}/{file}', threads)
    elif file_dir.endswith('.flac'):
        export_file(file_dir, file, out_dir)
    else:
        shutil.copy2(file_dir, out_dir)

# Get all the files and start all the threads
def main(directory, out_dir, threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        files = os.listdir(directory)
        futures = []
        for file in files:
            futures.append(executor.submit(process_file, file, directory, out_dir, threads))
        
        for future in tqdm(futures, desc=f"Processing {directory}", ncols=100, ascii='-#', leave=False):
            future.result()

# Choose what to do if the program is launched from the terminal or not
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 3:
        path = args[1]
        threads = int(args[2])
    elif len(args) == 2:
        path = args[1]
        threads = 4
    else:
        path = input("Path: ")
        threads = int(input("N. of threads to use: "))
    output = f'{path}_converted'
    os.makedirs(output, exist_ok=True)
    main(path, output, threads)
    print(f"\033[92mDone!, new folder at: {output}\033[0m")