from zipfile import ZipFile, ZIP_LZMA

if __name__ == '__main__':
    zip_file_name = 'lastfm.zip'
    csv_file_name = 'lastfm2.csv'
    with ZipFile(zip_file_name, mode='w', compression=ZIP_LZMA) as zip_object:
        zip_object.write(csv_file_name)
