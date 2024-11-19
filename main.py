import os
from fileproperties import FileProperties
from filesimilarity import FileSimilarity


if __name__ == '__main__':

    if not os.path.exists('submissions'):
        os.makedirs('submissions')
        print("Created submissions folder. Please put all .zip and .rar submissions in there.")
        exit(0)

    # fileprops = FileProperties(os.path.join(os.getcwd(), 'submissions'))
    # fileprops.copy_paste_plagiarism()

    filesim = FileSimilarity(os.path.join(os.getcwd(), 'submissions'))
    filesim.find_plagiarism(42)