import json

"""
Nada definitivo, sólo una prueba de cómo podría funcionar el registro
de elementos a las bases de datos.
"""

"""
custom_contents = {
    <title1> = {
            "keywords":<words to identify. (list)>,
            "urls":<urls related to it. (list)>,
            "files":<filenames, file_ids, urls_to_files. (list)>
            },
    }
"""
output_file = "resources/custom_contents.json"

with open(output_file, "r") as file:
    database = json.loads(file.read())
    file.close()

while True:
    title = input("Enter the title: ")
    print()
    keywords = input("Enter the keywords: ").lower().split(" ")
    print()
    urls = input("Enter the urls: ").split(" ")
    print()
    files = input("Enter the files: ").split(" ")
    print()
    print(f"Title: {title}\nKeywords: {keywords}\nUrls: {urls}\nFiles: {files}")
    save = input("Is the data right?(y/n) ")
    if save.lower() == "y":
        database[title] = {
                "keywords":keywords,
                "urls":urls,
                "files":files
                }
        with open(output_file, "w") as file:
            data = json.dumps(dic, indent = 4)
            file.write(data)
            file.close()
        break
    else:
        print("Vale")


