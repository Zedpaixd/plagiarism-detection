import os
from collections import defaultdict

class FileSimilarity:

    def __init__(self, path):
        self.path = path
        self.subfolders = []
        self.folder_files = {}  # mapping from folder to list of files
        self.similar_pairs = []
        self.groups = []
        self.file_sets = {}

    def get_subfolders(self):
        # Get all subfolders in the main directory
        self.subfolders = [
            os.path.join(self.path, f)
            for f in os.listdir(self.path)
            if os.path.isdir(os.path.join(self.path, f))
        ]

    def collect_files(self):
        # Collect all files recursively from each subfolder
        for folder in self.subfolders:
            file_list = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_list.append(os.path.join(root, file))
            self.folder_files[folder] = file_list

    def file_to_set(self, filepath):
        # Read a file and convert its lines into a set
        # ignores spaces and newlines
        lines_set = set()
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    stripped_line = line.strip().replace(" ", "")
                    if len(stripped_line) > 0:
                        lines_set.add(stripped_line)
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
        return lines_set

    def compute_similarity(self, set1, set2):
        # Compute the percentage similarity between two sets
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        if len(union) == 0:
            return 0.0
        similarity = len(intersection) / len(union) * 100
        return similarity

    def compare_files(self, delta):
        # Compare files from different folders and record similar pairs
        file_sets = {}  # Cache file contents to avoid re-reading
        similar_pairs = []
        all_files = []
        for files in self.folder_files.values():
            all_files.extend(files)
        total_files = len(all_files)
        for idx1 in range(total_files):
            file1 = all_files[idx1]
            if file1 not in file_sets:
                file_sets[file1] = self.file_to_set(file1)
            set1 = file_sets[file1]
            for idx2 in range(idx1 + 1, total_files):
                file2 = all_files[idx2]
                if file2 not in file_sets:
                    file_sets[file2] = self.file_to_set(file2)
                set2 = file_sets[file2]
                similarity = self.compute_similarity(set1, set2)
                if similarity >= delta:
                    similar_pairs.append((file1, file2, similarity))
        self.similar_pairs = similar_pairs
        self.file_sets = file_sets  # Save for later use

    def build_similarity_graph(self, delta):
        # Build a graph where nodes are files and edges represent similarity above delta
        graph = defaultdict(set)
        for file1, file2, similarity in self.similar_pairs:
            graph[file1].add((file2, similarity))
            graph[file2].add((file1, similarity))
        self.graph = graph

    def find_connected_components(self):
        # Find connected components in the similarity graph
        visited = set()
        groups = []

        for file in self.graph:
            if file not in visited:
                stack = [file]
                group = []
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        group.append(current)
                        neighbors = [neighbor for neighbor, sim in self.graph[current]]
                        stack.extend(neighbors)
                groups.append(group)
        self.groups = groups

    def run(self, delta):
        self.get_subfolders()
        self.collect_files()
        self.compare_files(delta)
        self.build_similarity_graph(delta)
        self.find_connected_components()
        return self.groups

    def find_plagiarism(self, delta):
        self.run(delta)
        i = 1
        for group in self.groups:
            if not group:
                continue
            # Choose a central file (e.g., the one with the most connections)
            central_file = max(group, key=lambda f: len(self.graph[f]))
            print(f"Case of possible plagiarism no. {i}")
            i += 1
            print(central_file)
            for other_file in group:
                if other_file == central_file:
                    continue
                similarity = self.compute_similarity(
                    self.file_sets[central_file], self.file_sets[other_file]
                )
                print(f"{other_file}   [-- {similarity:.0f}% similar]")
            print()
